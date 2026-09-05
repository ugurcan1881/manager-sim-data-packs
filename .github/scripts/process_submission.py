#!/usr/bin/env python3
"""Validate an issue-form Data Pack submission and create its pack record."""

from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import os
import re
import stat
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


MAX_ZIP_BYTES = 256 * 1024 * 1024
MAX_EXTRACTED_BYTES = 512 * 1024 * 1024
MAX_ENTRIES = 12_000
MAX_DATA_FILE_BYTES = 32 * 1024 * 1024
MAX_IMAGE_FILE_BYTES = 16 * 1024 * 1024
MAX_PLAYER_OVERRIDES = 200_000
MAX_IDENTITY_OVERRIDES = 50_000

ROOT_JSON_FILES = {
    "manifest.json",
    "players.json",
    "clubs.json",
    "competitions.json",
    "countries.json",
}
ROOT_CSV_FILES = {
    "players.csv",
    "player-map.csv",
    "clubs.csv",
    "stadiums.csv",
    "competitions.csv",
    "countries.csv",
}
DATA_MODULE_FILES = {
    "players.json", "players.csv", "clubs.json", "clubs.csv", "stadiums.csv",
    "competitions.json", "competitions.csv", "countries.json", "countries.csv",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
BLOCKED_EXTENSIONS = {
    ".exe", ".dll", ".apk", ".dex", ".so", ".js", ".sh", ".bat", ".cmd",
    ".com", ".msi", ".ps1", ".vbs", ".vb", ".jar", ".py", ".rb", ".php",
    ".scr", ".app", ".dmg", ".pkg", ".deb", ".rpm", ".elf", ".bin", ".zip",
}
REQUIRED_CONFIRMATIONS = {
    "I am responsible for the content included in this Data Pack.",
    "I confirm that I have the necessary rights or permissions to distribute the content included in this Data Pack.",
    "I understand that this Data Pack may be removed if it violates the rules or receives a valid copyright, trademark or other rights complaint.",
}
FORM_FIELDS = {
    "Mod Name": "name",
    "Author": "author",
    "Description": "description",
    "GitHub Release URL": "release_url",
    "Confirmation": "confirmation",
}
SAFE_VERSION_RE = re.compile(r"^[A-Za-z0-9._-]{1,32}$")
RELEASE_PATH_RE = re.compile(r"^/([^/]+)/([^/]+)/releases/tag/(.+)$")


class SubmissionError(Exception):
    """A user-facing validation failure."""


def is_safe_identity(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and len(value) <= 256
        and not any(unicodedata.category(character) == "Cc" for character in value)
    )


def is_optional_display_text(value: object, maximum: int) -> bool:
    if value is None or value == "":
        return True
    if not isinstance(value, str) or len(value) > maximum:
        return False
    return not any(unicodedata.category(character) == "Cc" and character not in "\n\r\t" for character in value)


def is_safe_display_text(value: object, maximum: int) -> bool:
    return isinstance(value, str) and bool(value.strip()) and is_optional_display_text(value, maximum)


def is_safe_token(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and len(value) <= 80
        and all(
            unicodedata.category(character).startswith("L")
            or unicodedata.category(character) == "Nd"
            or character in "-_"
            for character in value
        )
    )


def is_valid_author_display_name(value: object) -> bool:
    if not isinstance(value, str) or not value.strip() or len(value) > 50:
        return False
    return all(
        unicodedata.category(character).startswith("L")
        or unicodedata.category(character) == "Nd"
        or character in " -_."
        for character in value
    )


def api_request(url: str, token: str, *, method: str = "GET", payload: dict | None = None) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "manager-sim-data-pack-bot",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise SubmissionError(f"GitHub API request failed ({error.code}): {detail}") from error
    except urllib.error.URLError as error:
        raise SubmissionError(f"GitHub API request failed: {error.reason}") from error
    return json.loads(body.decode("utf-8")) if body else {}


def parse_issue_form(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    matches = list(re.finditer(r"(?m)^###\s+(.+?)\s*$", body or ""))
    for index, match in enumerate(matches):
        label = match.group(1).strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        value = body[match.end():end].strip()
        if label in FORM_FIELDS:
            if label in sections:
                raise SubmissionError(f"The issue contains the '{label}' field more than once.")
            sections[label] = value

    missing = [label for label in FORM_FIELDS if not sections.get(label) or sections[label] == "_No response_"]
    if missing:
        raise SubmissionError("Missing required issue-form field(s): " + ", ".join(missing))

    result = {target: sections[label].strip() for label, target in FORM_FIELDS.items()}
    if (
        not is_safe_display_text(result["name"], 120)
        or not is_valid_author_display_name(result["author"])
        or not is_optional_display_text(result["description"], 4000)
    ):
        raise SubmissionError("One or more submission fields contain invalid text or exceed the allowed length.")

    checked = {
        match.group(1).strip()
        for match in re.finditer(r"(?mi)^\s*-\s*\[[xX]\]\s*(.+?)\s*$", result["confirmation"])
    }
    unchecked = {
        match.group(1).strip()
        for match in re.finditer(r"(?mi)^\s*-\s*\[\s\]\s*(.+?)\s*$", result["confirmation"])
    }
    if unchecked & REQUIRED_CONFIRMATIONS or not REQUIRED_CONFIRMATIONS.issubset(checked):
        raise SubmissionError("All required confirmation checkboxes must be checked.")
    return result


def parse_release_url(value: str) -> tuple[str, str, str, str]:
    if len(value) > 500:
        raise SubmissionError("The GitHub Release URL is too long.")
    parsed = urllib.parse.urlsplit(value.strip())
    try:
        port = parsed.port
    except ValueError as error:
        raise SubmissionError("The GitHub Release URL contains an invalid port.") from error
    if parsed.scheme != "https" or parsed.hostname != "github.com" or port not in (None, 443):
        raise SubmissionError("GitHub Release URL must be a public https://github.com URL.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise SubmissionError("GitHub Release URL must not contain credentials, query parameters, or a fragment.")
    match = RELEASE_PATH_RE.fullmatch(parsed.path.rstrip("/"))
    if not match:
        raise SubmissionError("GitHub Release URL must use https://github.com/<owner>/<repo>/releases/tag/<tag>.")
    owner, repository, encoded_tag = match.groups()
    tag = urllib.parse.unquote(encoded_tag)
    if not tag or "\x00" in tag or len(tag) > 200:
        raise SubmissionError("The GitHub Release tag is invalid.")
    normalized_path = f"/{owner}/{repository}/releases/tag/{urllib.parse.quote(tag, safe='/')}"
    return owner, repository, tag, f"https://github.com{normalized_path}"


def get_public_release(owner: str, repository: str, tag: str) -> dict:
    encoded_owner = urllib.parse.quote(owner, safe="")
    encoded_repository = urllib.parse.quote(repository, safe="")
    encoded_tag = urllib.parse.quote(tag, safe="")
    url = f"https://api.github.com/repos/{encoded_owner}/{encoded_repository}/releases/tags/{encoded_tag}"
    # This request is intentionally unauthenticated. A successful response proves
    # that the submitted repository and release are publicly accessible.
    release = api_request(url, "")
    if not isinstance(release, dict) or release.get("draft"):
        raise SubmissionError("The supplied GitHub Release is not public.")
    return release


def select_zip_asset(release: dict, owner: str, repository: str) -> dict:
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise SubmissionError("The GitHub Release asset list could not be read.")
    zip_assets = [
        asset for asset in assets
        if isinstance(asset, dict) and str(asset.get("name", "")).lower().endswith(".zip")
    ]
    if not zip_assets:
        raise SubmissionError("No ZIP file was found in the supplied GitHub Release.")
    if len(zip_assets) > 1:
        explicit = [
            asset for asset in zip_assets
            if re.search(r"(?:data[-_ ]?pack|datapack)", str(asset.get("name", "")), re.IGNORECASE)
        ]
        if len(explicit) != 1:
            raise SubmissionError("More than one ZIP asset was found and the Data Pack ZIP is ambiguous.")
        zip_assets = explicit
    asset = zip_assets[0]
    size = asset.get("size")
    url = asset.get("browser_download_url")
    if not isinstance(size, int) or size <= 0 or size > MAX_ZIP_BYTES:
        raise SubmissionError("The Data Pack ZIP size is missing or exceeds the 256 MB limit.")
    if not isinstance(url, str):
        raise SubmissionError("The ZIP direct download URL is missing from the GitHub Release API response.")
    parsed = urllib.parse.urlsplit(url)
    expected_prefix = f"/{owner}/{repository}/releases/download/".casefold()
    if parsed.scheme != "https" or parsed.hostname != "github.com" or not parsed.path.casefold().startswith(expected_prefix):
        raise SubmissionError("The GitHub Release API returned an unexpected ZIP download URL.")
    return asset


def download_asset(asset: dict, destination: Path) -> str:
    request = urllib.request.Request(
        asset["browser_download_url"],
        headers={"User-Agent": "manager-sim-data-pack-bot"},
    )
    digest = hashlib.sha256()
    total = 0
    try:
        with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as stream:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_ZIP_BYTES:
                    raise SubmissionError("The downloaded ZIP exceeds the 256 MB limit.")
                stream.write(chunk)
                digest.update(chunk)
    except urllib.error.URLError as error:
        raise SubmissionError(f"The ZIP could not be downloaded: {error.reason}") from error
    if total != asset["size"]:
        raise SubmissionError(f"ZIP size verification failed: GitHub reported {asset['size']} bytes, downloaded {total} bytes.")
    return digest.hexdigest()


def normalize_zip_path(name: str) -> str:
    if not name or "\x00" in name or name.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", name):
        raise SubmissionError(f"Unsafe absolute ZIP path: {name!r}")
    normalized = name.replace("\\", "/").rstrip("/")
    parts = normalized.split("/")
    if not normalized or any(not part.strip() or part in (".", "..") for part in parts) or ":" in normalized:
        raise SubmissionError(f"Unsafe relative ZIP path: {name!r}")
    return normalized


def validate_csv(name: str, data: bytes, image_paths: set[str]) -> None:
    requirements = {
        "players.csv": ("playerId", {"playerId", "name"}, MAX_PLAYER_OVERRIDES),
        "player-map.csv": ("playerId", {"playerId", "sourceId"}, MAX_PLAYER_OVERRIDES),
        "clubs.csv": ("clubId", {"clubId"}, MAX_IDENTITY_OVERRIDES),
        "stadiums.csv": ("clubId", {"clubId", "stadiumName"}, MAX_IDENTITY_OVERRIDES),
        "competitions.csv": ("competitionId", {"competitionId", "name", "logo", "trophyImage"}, MAX_IDENTITY_OVERRIDES),
        "countries.csv": ("countryId", {"countryId", "name", "logo"}, MAX_IDENTITY_OVERRIDES),
    }
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise SubmissionError(f"{name} is not valid UTF-8.") from error
    reader = csv.DictReader(io.StringIO(text, newline=""))
    raw_headers = reader.fieldnames or []
    headers = [header.strip() if isinstance(header, str) else "" for header in raw_headers]
    header_lookup = {header.casefold(): raw for header, raw in zip(headers, raw_headers)}
    if not headers or any(not header for header in headers):
        raise SubmissionError(f"{name} has an invalid or empty CSV header.")
    if len(headers) != len({header.casefold() for header in headers}):
        raise SubmissionError(f"{name} contains duplicate CSV headers.")
    identity_field, required_headers, maximum_rows = requirements[name]
    missing_headers = {header for header in required_headers if header.casefold() not in header_lookup}
    if missing_headers:
        raise SubmissionError(f"{name} is missing required column(s): {', '.join(sorted(missing_headers))}")
    seen: set[str] = set()
    count = 0
    image_columns = {"logo", "trophyImage"}

    def value(row: dict, key: str) -> str:
        raw_header = header_lookup.get(key.casefold())
        raw_value = row.get(raw_header, "") if raw_header is not None else ""
        return raw_value.strip() if isinstance(raw_value, str) else ""

    try:
        for row in reader:
            count += 1
            if count > maximum_rows:
                raise SubmissionError(f"{name} contains too many rows.")
            if None in row:
                raise SubmissionError(f"{name} row {count + 1} contains more values than headers.")
            if any(isinstance(cell, str) and ("\r" in cell or "\n" in cell) for cell in row.values()):
                raise SubmissionError(f"{name} row {count + 1} contains a multiline CSV value unsupported by the game.")
            identity = value(row, identity_field)
            if not is_safe_identity(identity):
                raise SubmissionError(f"{name} row {count + 1} has an invalid {identity_field}.")
            duplicate_key = identity
            reject_duplicates = name in {"players.csv", "player-map.csv", "stadiums.csv"}
            if name == "players.csv":
                source_id = value(row, "sourceId")
                if source_id and not is_safe_identity(source_id):
                    raise SubmissionError(f"{name} row {count + 1} has an invalid sourceId.")
                duplicate_key = source_id or identity
            elif name == "player-map.csv":
                source_id = value(row, "sourceId")
                if not is_safe_identity(source_id):
                    raise SubmissionError(f"{name} row {count + 1} has an invalid sourceId.")
            if reject_duplicates and duplicate_key.casefold() in seen:
                raise SubmissionError(f"{name} contains duplicate effective {identity_field}: {duplicate_key}")
            if reject_duplicates:
                seen.add(duplicate_key.casefold())

            field_limits = {
                "players.csv": {"name": (160, True), "position": (16, False), "secondaryPosition": (16, False), "birthDate": (32, False), "nationality": (80, False), "heightCm": (16, False), "overall": (16, False), "potential": (16, False)},
                "clubs.csv": {"name": (160, False), "shortName": (24, False), "stadiumName": (160, False)},
                "stadiums.csv": {"stadiumName": (160, False)},
                "competitions.csv": {"name": (160, False)},
                "countries.csv": {"name": (160, False)},
            }.get(name, {})
            for field, (maximum, required) in field_limits.items():
                field_value = value(row, field)
                valid = is_safe_display_text(field_value, maximum) if required else is_optional_display_text(field_value, maximum)
                if not valid:
                    raise SubmissionError(f"{name} row {count + 1} has an invalid {field}.")

            for column in image_columns:
                if column.casefold() not in header_lookup:
                    continue
                reference = value(row, column).replace("\\", "/")
                if reference and reference.casefold() not in image_paths:
                    raise SubmissionError(f"{name} references a missing image: {reference}")
    except csv.Error as error:
        raise SubmissionError(f"{name} could not be parsed as CSV: {error}") from error
    if count == 0:
        raise SubmissionError(f"{name} contains no data rows.")


def json_array(data: object, key: str, name: str) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get(key), list):
        return data[key]
    raise SubmissionError(f"{name} must be a JSON array or an object containing '{key}'.")


def validate_json_module(name: str, data: bytes, image_paths: set[str]) -> None:
    try:
        document = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SubmissionError(f"{name} is not valid UTF-8 JSON: {error}") from error
    schemas = {
        "players.json": ("players", "playerId", MAX_PLAYER_OVERRIDES),
        "clubs.json": ("clubs", "clubId", MAX_IDENTITY_OVERRIDES),
        "competitions.json": ("competitions", "competitionId", MAX_IDENTITY_OVERRIDES),
        "countries.json": ("countries", "countryId", MAX_IDENTITY_OVERRIDES),
    }
    key, identity_field, maximum = schemas[name]
    rows = json_array(document, key, name)
    if not rows or len(rows) > maximum:
        raise SubmissionError(f"{name} contains no overrides or too many overrides.")
    seen: set[str] = set()
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise SubmissionError(f"{name} item {index} is not an object.")
        identity = row.get(identity_field)
        if not is_safe_identity(identity):
            raise SubmissionError(f"{name} item {index} has an invalid {identity_field}.")
        duplicate_key = identity
        if name == "players.json":
            source_id = row.get("sourceId")
            if source_id not in (None, "") and not is_safe_identity(source_id):
                raise SubmissionError(f"{name} item {index} has an invalid sourceId.")
            duplicate_key = source_id or identity
            if duplicate_key.casefold() in seen:
                raise SubmissionError(f"{name} contains duplicate effective playerId: {duplicate_key}")
            seen.add(duplicate_key.casefold())

        field_limits = {
            "players.json": {"name": (160, True), "position": (16, False), "secondaryPosition": (16, False), "birthDate": (32, False), "nationality": (80, False), "heightCm": (16, False), "overall": (16, False), "potential": (16, False)},
            "clubs.json": {"name": (160, False), "shortName": (24, False), "stadiumName": (160, False)},
            "competitions.json": {"name": (160, False)},
            "countries.json": {"name": (160, False)},
        }[name]
        for field, (maximum_length, required) in field_limits.items():
            field_value = row.get(field)
            valid = is_safe_display_text(field_value, maximum_length) if required else is_optional_display_text(field_value, maximum_length)
            if not valid:
                raise SubmissionError(f"{name} item {index} has an invalid {field}.")
        for column in ("logo", "trophyImage"):
            reference = row.get(column)
            if reference not in (None, "") and not isinstance(reference, str):
                raise SubmissionError(f"{name} item {index} has an invalid {column}.")
            if isinstance(reference, str) and reference.strip():
                normalized = reference.strip().replace("\\", "/").casefold()
                if normalized not in image_paths:
                    raise SubmissionError(f"{name} references a missing image: {reference}")


def validate_manifest(data: bytes) -> dict:
    try:
        manifest = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SubmissionError(f"manifest.json is not valid UTF-8 JSON: {error}") from error
    schema_version = manifest.get("schemaVersion") if isinstance(manifest, dict) else None
    if not isinstance(manifest, dict) or isinstance(schema_version, bool) or schema_version != 1:
        raise SubmissionError("manifest.json has an unsupported schemaVersion.")
    if not is_safe_token(manifest.get("id")) or str(manifest.get("id")).casefold() == "builtin":
        raise SubmissionError("manifest.json contains an invalid Data Pack id.")
    for field in ("name", "author"):
        value = manifest.get(field)
        if not is_safe_display_text(value, 120):
            raise SubmissionError(f"manifest.json contains an invalid {field}.")
    if not is_optional_display_text(manifest.get("description"), 4000):
        raise SubmissionError("manifest.json contains an invalid description.")
    if not SAFE_VERSION_RE.fullmatch(str(manifest.get("version", ""))):
        raise SubmissionError("manifest.json contains an invalid version.")
    return manifest


def validate_zip(path: Path) -> dict:
    if not zipfile.is_zipfile(path):
        raise SubmissionError("The downloaded file is not a valid ZIP archive.")
    try:
        with zipfile.ZipFile(path, "r") as archive:
            infos = archive.infolist()
            if len(infos) > MAX_ENTRIES:
                raise SubmissionError("The ZIP contains too many entries.")
            normalized_infos: dict[str, zipfile.ZipInfo] = {}
            extracted_total = 0
            for info in infos:
                normalized = normalize_zip_path(info.filename)
                normalized_key = normalized.casefold()
                if normalized_key in normalized_infos:
                    raise SubmissionError(f"The ZIP contains a duplicate path: {normalized}")
                normalized_infos[normalized_key] = info
                unix_type = stat.S_IFMT(info.external_attr >> 16)
                if unix_type == stat.S_IFLNK:
                    raise SubmissionError(f"Symbolic links are not allowed in Data Packs: {normalized}")
                if info.flag_bits & 0x1:
                    raise SubmissionError(f"Encrypted ZIP entries are not allowed: {normalized}")
                if info.is_dir():
                    if normalized_key != "images" and not normalized_key.startswith("images/"):
                        raise SubmissionError(f"Unsupported directory in ZIP: {normalized}")
                    continue
                extension = PurePosixPath(normalized).suffix.lower()
                if extension in BLOCKED_EXTENSIONS:
                    raise SubmissionError(f"Blocked file type in ZIP: {normalized}")
                is_root_data = "/" not in normalized and normalized_key in ROOT_JSON_FILES | ROOT_CSV_FILES
                is_image = normalized_key.startswith("images/") and extension in IMAGE_EXTENSIONS
                if not is_root_data and not is_image:
                    raise SubmissionError(f"Unsupported file in ZIP: {normalized}")
                per_file_limit = MAX_IMAGE_FILE_BYTES if is_image else MAX_DATA_FILE_BYTES
                if info.file_size < 0 or info.file_size > per_file_limit:
                    raise SubmissionError(f"ZIP entry exceeds its size limit: {normalized}")
                extracted_total += info.file_size
                if extracted_total > MAX_EXTRACTED_BYTES:
                    raise SubmissionError("The extracted ZIP exceeds the 512 MB limit.")

            if "manifest.json" not in normalized_infos:
                raise SubmissionError("manifest.json is required at the ZIP root.")
            present_files = {key for key, info in normalized_infos.items() if not info.is_dir()}
            if not present_files & DATA_MODULE_FILES:
                raise SubmissionError("The Data Pack contains no supported override module.")
            image_paths = {path for path in present_files if path.startswith("images/")}

            payloads: dict[str, bytes] = {}
            actual_total = 0
            for normalized_key, info in normalized_infos.items():
                if info.is_dir():
                    continue
                chunks: list[bytes] = []
                actual_size = 0
                with archive.open(info, "r") as stream:
                    while True:
                        chunk = stream.read(1024 * 1024)
                        if not chunk:
                            break
                        actual_size += len(chunk)
                        actual_total += len(chunk)
                        if actual_size > info.file_size or actual_total > MAX_EXTRACTED_BYTES:
                            raise SubmissionError(f"ZIP entry expanded beyond its declared size: {info.filename}")
                        if normalized_key in ROOT_JSON_FILES | ROOT_CSV_FILES:
                            chunks.append(chunk)
                if actual_size != info.file_size:
                    raise SubmissionError(f"ZIP entry size verification failed: {info.filename}")
                if chunks:
                    payloads[normalized_key] = b"".join(chunks)

            manifest = validate_manifest(payloads["manifest.json"])
            for stem in ("players", "clubs", "competitions", "countries"):
                if f"{stem}.csv" in present_files and f"{stem}.json" in present_files:
                    raise SubmissionError(f"Use either {stem}.csv or {stem}.json, not both.")
            for name in sorted(present_files & ROOT_CSV_FILES):
                validate_csv(name, payloads[name], image_paths)
            for name in sorted((present_files & ROOT_JSON_FILES) - {"manifest.json"}):
                validate_json_module(name, payloads[name], image_paths)
            return manifest
    except zipfile.BadZipFile as error:
        raise SubmissionError(f"The ZIP archive is corrupt: {error}") from error
    except (RuntimeError, OSError, EOFError) as error:
        raise SubmissionError(f"The ZIP archive could not be validated: {error}") from error


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(character for character in normalized if not unicodedata.combining(character))
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.casefold()).strip("-")
    return (slug or "data-pack")[:80].rstrip("-")


def release_key_from_url(value: object) -> tuple[str, str, str] | None:
    if not isinstance(value, str):
        return None
    try:
        owner, repository, tag, _ = parse_release_url(value)
    except SubmissionError:
        return None
    return owner.casefold(), repository.casefold(), tag


def existing_packs() -> list[dict]:
    records: list[dict] = []
    for path in sorted(Path("packs").glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SubmissionError(f"Existing pack metadata could not be read: {path}: {error}") from error
        if isinstance(record, dict):
            records.append(record)
    return records


def ensure_not_duplicate_release(records: list[dict], source_url: str) -> None:
    release_key = release_key_from_url(source_url)
    if release_key is None:
        raise SubmissionError("The normalized GitHub Release URL is invalid.")
    if any(release_key_from_url(record.get("sourceUrl")) == release_key for record in records):
        raise SubmissionError("This GitHub repository and release tag are already present in the catalog.")


def unique_pack_id(name: str, owner: str, repository: str, tag: str, records: list[dict]) -> str:
    existing_ids = {str(record.get("id", "")).casefold() for record in records}
    base = slugify(name)
    if base.casefold() not in existing_ids:
        return base
    suffix = slugify(f"{owner}-{repository}-{tag}")
    candidate = f"{base[:max(1, 79 - len(suffix))]}-{suffix}"[:80].rstrip("-")
    if candidate.casefold() not in existing_ids:
        return candidate
    digest = hashlib.sha256(f"{owner}/{repository}@{tag}".encode("utf-8")).hexdigest()[:8]
    candidate = f"{base[:71]}-{digest}".rstrip("-")
    if candidate.casefold() in existing_ids:
        raise SubmissionError("A unique Data Pack ID could not be generated for this submission.")
    return candidate


def version_from_release(release: dict, manifest: dict) -> str:
    raw = str(release.get("tag_name") or "").strip()
    if raw[:1].casefold() == "v":
        raw = raw[1:]
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-._")[:32]
    if SAFE_VERSION_RE.fullmatch(cleaned):
        return cleaned
    fallback = str(manifest.get("version", ""))
    if SAFE_VERSION_RE.fullmatch(fallback):
        return fallback
    raise SubmissionError("A safe version could not be derived from the GitHub Release tag.")


def write_output(name: str, value: object) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    text = str(value).replace("\r", " ").replace("\n", " ")
    with open(output_path, "a", encoding="utf-8") as stream:
        stream.write(f"{name}={text}\n")


def issue_api_url(repository: str, issue_number: int, suffix: str = "") -> str:
    return f"https://api.github.com/repos/{repository}/issues/{issue_number}{suffix}"


def comment_failure(repository: str, issue_number: int, token: str, reason: str) -> None:
    safe_reason = html.escape(reason[:2000], quote=False).replace("@", "@\u200b")
    message = "Submission could not be published:\n\n<pre>" + safe_reason + "</pre>"
    api_request(issue_api_url(repository, issue_number, "/comments"), token, method="POST", payload={"body": message})


def format_size(size_bytes: int) -> str:
    value = float(size_bytes)
    for unit in ("bytes", "KB", "MB", "GB"):
        if value < 1024.0 or unit == "GB":
            return f"{int(value)} {unit}" if unit == "bytes" else f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{size_bytes} bytes"


def finalize(repository: str, issue_number: int, token: str, result_path: Path) -> None:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    message = (
        "Data Pack successfully validated and added to the community catalog.\n\n"
        f"Pack ID: `{result['id']}`  \n"
        f"Version: `{result['version']}`  \n"
        f"Size: `{format_size(int(result['sizeBytes']))}` (`{result['sizeBytes']}` bytes)  \n"
        f"SHA-256: `{result['sha256']}`"
    )
    api_request(issue_api_url(repository, issue_number, "/comments"), token, method="POST", payload={"body": message})
    api_request(issue_api_url(repository, issue_number), token, method="PATCH", payload={"state": "closed", "state_reason": "completed"})


def process(event_path: Path, result_path: Path) -> None:
    event = json.loads(event_path.read_text(encoding="utf-8"))
    issue = event.get("issue") or {}
    title = str(issue.get("title") or "")
    issue_number = int(issue.get("number") or 0)
    if not title.startswith("[DATA PACK]"):
        raise SubmissionError("Only issues whose title starts with [DATA PACK] can be processed.")
    form = parse_issue_form(str(issue.get("body") or ""))
    owner, release_repository, requested_tag, source_url = parse_release_url(form["release_url"])
    records = existing_packs()
    ensure_not_duplicate_release(records, source_url)

    release = get_public_release(owner, release_repository, requested_tag)
    actual_tag = str(release.get("tag_name") or "")
    if actual_tag != requested_tag:
        raise SubmissionError("The GitHub Release tag returned by the API does not match the submitted URL.")
    asset = select_zip_asset(release, owner, release_repository)

    with tempfile.TemporaryDirectory(prefix="manager-sim-pack-") as temporary_directory:
        zip_path = Path(temporary_directory) / "submission.zip"
        sha256 = download_asset(asset, zip_path)
        manifest = validate_zip(zip_path)

    pack_id = unique_pack_id(form["name"], owner, release_repository, actual_tag, records)
    version = version_from_release(release, manifest)
    record = {
        "id": pack_id,
        "name": form["name"],
        "author": form["author"],
        "version": version,
        "description": form["description"],
        "downloadUrl": asset["browser_download_url"],
        "sourceUrl": source_url,
        "sizeBytes": asset["size"],
        "sha256": sha256,
        "gameVersion": str(manifest.get("gameVersion") or ""),
        "minimumGameVersion": str(manifest.get("minimumGameVersion") or ""),
        "databaseVersion": str(manifest.get("databaseVersion") or ""),
        "downloadCount": 0,
    }
    Path("packs").mkdir(exist_ok=True)
    output_path = Path("packs") / f"{pack_id}.json"
    temporary_path = output_path.with_suffix(".json.tmp")
    temporary_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary_path.replace(output_path)
    result_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key in ("id", "version", "sizeBytes", "sha256"):
        write_output(key, record[key])
    write_output("pack_file", output_path.as_posix())


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN", "")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    event_path = Path(os.environ.get("GITHUB_EVENT_PATH", ""))
    result_path = Path(os.environ.get("SUBMISSION_RESULT_PATH", ".submission-result.json"))
    issue_number = 0
    if len(sys.argv) == 2 and sys.argv[1] == "--finalize":
        event = json.loads(event_path.read_text(encoding="utf-8"))
        issue_number = int((event.get("issue") or {}).get("number") or 0)
        finalize(repository, issue_number, token, result_path)
        return 0
    try:
        event = json.loads(event_path.read_text(encoding="utf-8"))
        issue_number = int((event.get("issue") or {}).get("number") or 0)
        process(event_path, result_path)
        return 0
    except SubmissionError as error:
        print(f"Submission rejected: {error}", file=sys.stderr)
        if repository and token and issue_number:
            try:
                comment_failure(repository, issue_number, token, str(error))
            except SubmissionError as comment_error:
                print(f"Failure comment could not be posted: {comment_error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"Unexpected submission processing failure: {error}", file=sys.stderr)
        if repository and token and issue_number:
            try:
                comment_failure(repository, issue_number, token, "An internal validation error occurred. Please check the workflow log.")
            except SubmissionError:
                pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
