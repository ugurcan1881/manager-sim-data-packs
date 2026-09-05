#!/usr/bin/env python3
"""Build catalog.json from packs/*.json and featured.json."""

from __future__ import annotations

import glob
import json
from pathlib import Path


def main() -> None:
    featured_path = Path("featured.json")
    featured_ids: set[str] = set()
    if featured_path.exists():
        with featured_path.open("r", encoding="utf-8") as stream:
            featured_data = json.load(stream)
        featured_ids = set(featured_data.get("packs", []))

    packs: list[dict] = []
    seen_ids: set[str] = set()
    for file_path in sorted(glob.glob("packs/*.json")):
        with open(file_path, "r", encoding="utf-8") as stream:
            pack = json.load(stream)
        pack_id = pack.get("id")
        if not isinstance(pack_id, str) or not pack_id:
            raise ValueError(f"Pack file has no valid id: {file_path}")
        if pack_id.casefold() in seen_ids:
            raise ValueError(f"Duplicate pack id: {pack_id}")
        seen_ids.add(pack_id.casefold())
        pack["featured"] = pack_id in featured_ids
        packs.append(pack)

    catalog = {"packs": packs}
    with Path("catalog.json").open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(catalog, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(f"Catalog generated with {len(packs)} Data Pack(s).")


if __name__ == "__main__":
    main()
