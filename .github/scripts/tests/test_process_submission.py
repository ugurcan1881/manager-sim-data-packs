from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "process_submission.py"
SPEC = importlib.util.spec_from_file_location("process_submission", SCRIPT)
submission = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(submission)


CONFIRMATIONS = "\n".join(f"- [x] {text}" for text in sorted(submission.REQUIRED_CONFIRMATIONS))


def issue_body(url: str = "https://github.com/example/mod/releases/tag/v1.2.3") -> str:
    return f"""### Mod Name

Unofficial 2026/27 Data Pack

### Author

ExampleAuthor

### Description

Updates player names.

### GitHub Release URL

{url}

### Confirmation

{CONFIRMATIONS}
"""


def make_zip(path: Path, extra: dict[str, bytes] | None = None) -> None:
    manifest = {
        "schemaVersion": 1,
        "id": "test-data-pack",
        "name": "Test Data Pack",
        "author": "Tester",
        "version": "1.0.0",
        "gameVersion": "1.0.0",
        "minimumGameVersion": "1.0.0",
        "databaseVersion": "2",
    }
    files = {
        "manifest.json": json.dumps(manifest).encode(),
        "players.csv": b"playerId,name\n0,Test Player\n",
    }
    files.update(extra or {})
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)


class SubmissionTests(unittest.TestCase):
    def test_issue_form_and_release_url(self) -> None:
        parsed = submission.parse_issue_form(issue_body())
        self.assertEqual(parsed["name"], "Unofficial 2026/27 Data Pack")
        self.assertEqual(
            submission.parse_release_url(parsed["release_url"])[:3],
            ("example", "mod", "v1.2.3"),
        )

    def test_malformed_release_url_is_rejected(self) -> None:
        with self.assertRaises(submission.SubmissionError):
            submission.parse_release_url("https://github.com:bad/example/mod/releases/tag/v1")

    def test_missing_confirmation_is_rejected(self) -> None:
        body = issue_body().replace("- [x]", "- [ ]", 1)
        with self.assertRaisesRegex(submission.SubmissionError, "confirmation"):
            submission.parse_issue_form(body)

    def test_safe_zip_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pack.zip"
            make_zip(path)
            manifest = submission.validate_zip(path)
            self.assertEqual(manifest["id"], "test-data-pack")

    def test_nested_zip_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pack.zip"
            make_zip(path, {"images/nested.zip": b"not a zip"})
            with self.assertRaisesRegex(submission.SubmissionError, "Blocked file type"):
                submission.validate_zip(path)

    def test_path_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pack.zip"
            make_zip(path, {"../escape.png": b"bad"})
            with self.assertRaisesRegex(submission.SubmissionError, "Unsafe relative ZIP path"):
                submission.validate_zip(path)

    def test_empty_zip_path_segment_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pack.zip"
            make_zip(path, {"images//club.png": b"bad"})
            with self.assertRaisesRegex(submission.SubmissionError, "Unsafe relative ZIP path"):
                submission.validate_zip(path)

    def test_executable_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pack.zip"
            make_zip(path, {"images/tool.exe": b"bad"})
            with self.assertRaisesRegex(submission.SubmissionError, "Blocked file type"):
                submission.validate_zip(path)

    def test_duplicate_competition_ids_match_game_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pack.zip"
            make_zip(
                path,
                {
                    "players.csv": b"playerId,name\n0,Test Player\n",
                    "competitions.csv": (
                        b"competitionId,name,logo,trophyImage\n"
                        b"league_test,Test League,,\n"
                        b"league_test,Test League Alias,,\n"
                    ),
                },
            )
            self.assertEqual(submission.validate_zip(path)["id"], "test-data-pack")

    def test_slug_and_version(self) -> None:
        self.assertEqual(submission.slugify("Unofficial 2026/27 Data Pack"), "unofficial-2026-27-data-pack")
        self.assertEqual(submission.version_from_release({"tag_name": "v1.2.3"}, {"version": "1.2.3"}), "1.2.3")

    def test_owner_updates_same_release_or_new_tag(self):
        record = {"id": "existing", "sourceUrl": "https://github.com/example/mod/releases/tag/v1"}
        for tag in ("v1", "v2"):
            self.assertIs(submission.find_existing_pack([record], "https://github.com/example/mod/releases/tag/" + tag, "example"), record)

    def test_release_owner_can_update_pack_submitted_by_another_user(self):
        record = {"id": "existing", "submittedBy": "contributor", "sourceUrl": "https://github.com/example/mod/releases/tag/v1"}
        self.assertIs(submission.find_existing_pack([record], record["sourceUrl"], "example"), record)

    def test_other_user_cannot_overwrite_pack(self):
        record = {"id": "existing", "sourceUrl": "https://github.com/example/mod/releases/tag/v1"}
        with self.assertRaisesRegex(submission.SubmissionError, "Only"):
            submission.find_existing_pack([record], record["sourceUrl"], "attacker")

    def test_manifest_version_beats_reused_release_tag(self):
        self.assertEqual(submission.version_from_release({"tag_name": "v1.0.0"}, {"version": "1.2.0"}), "1.2.0")

    def test_process_creates_pack_metadata_from_release(self) -> None:
        release = {
            "tag_name": "v1.2.3",
            "draft": False,
            "assets": [
                {
                    "name": "manager-sim-data-pack.zip",
                    "size": 1234,
                    "browser_download_url": "https://github.com/example/mod/releases/download/v1.2.3/manager-sim-data-pack.zip",
                }
            ],
        }

        def fake_download(asset: dict, destination: Path) -> str:
            self.assertEqual(asset["size"], 1234)
            make_zip(destination)
            return "a" * 64

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event_path = root / "event.json"
            result_path = root / "result.json"
            event_path.write_text(
                json.dumps({"issue": {"number": 2, "title": "Test [DATA PACK]", "body": issue_body(), "user": {"login": "example"}}}),
                encoding="utf-8",
            )
            previous = Path.cwd()
            os.chdir(root)
            try:
                with mock.patch.object(submission, "get_public_release", return_value=release), mock.patch.object(
                    submission, "download_asset", side_effect=fake_download
                ):
                    submission.process(event_path, result_path)
            finally:
                os.chdir(previous)

            record = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(record["id"], "unofficial-2026-27-data-pack")
            self.assertEqual(record["version"], "1.0.0")
            self.assertEqual(record["sizeBytes"], 1234)
            self.assertEqual(record["sha256"], "a" * 64)
            self.assertEqual(record["downloadCount"], 0)
            self.assertTrue((root / "packs" / "unofficial-2026-27-data-pack.json").is_file())

    def test_update_preserves_identity_and_downloads(self):
        release = {"tag_name": "v1", "assets": [{"name": "pack.zip", "size": 1234,
            "browser_download_url": "https://github.com/example/mod/releases/download/v1/pack.zip"}]}
        def download(asset, destination):
            make_zip(destination)
            return "b" * 64
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "packs").mkdir()
            record = {"id": "original-id", "sourceUrl": "https://github.com/example/mod/releases/tag/v0",
                      "version": "0.9.0", "downloadCount": 25}
            (root / "packs/original-id.json").write_text(json.dumps(record))
            event = root / "event.json"
            event.write_text(json.dumps({"issue": {"number": 6, "title": "No prefix",
                "body": issue_body("https://github.com/example/mod/releases/tag/v1"),
                "user": {"login": "example"}}}))
            old = Path.cwd()
            os.chdir(root)
            try:
                with mock.patch.object(submission, "get_public_release", return_value=release), mock.patch.object(submission, "download_asset", side_effect=download):
                    submission.process(event, root / "result.json")
                    submission.process(event, root / "result.json")
                    self.assertEqual(len(list((root / "packs").glob("*.json"))), 1)
                    updated = json.loads((root / "result.json").read_text())
                    self.assertEqual(updated["id"], "original-id")
                    self.assertEqual(updated["downloadCount"], 25)
                    updated["version"] = "9.0.0"
                    (root / "packs/original-id.json").write_text(json.dumps(updated))
                    with self.assertRaisesRegex(submission.SubmissionError, "older"):
                        submission.process(event, root / "result.json")
            finally:
                os.chdir(old)

    def test_manual_reprocessing_loads_selected_issue(self):
        with tempfile.TemporaryDirectory() as directory:
            event = Path(directory) / "event.json"
            event.write_text(json.dumps({"inputs": {"issue_number": "6"}}))
            with mock.patch.object(submission, "api_request", return_value={"number": 6}), mock.patch.dict(os.environ, {"GITHUB_REPOSITORY": "owner/repo"}):
                self.assertEqual(submission.load_event_issue(event)["number"], 6)


if __name__ == "__main__":
    unittest.main()
