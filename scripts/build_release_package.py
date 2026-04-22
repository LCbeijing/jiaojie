#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skill"
DIST_DIR = ROOT / "dist"

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archive_name(version: str | None) -> str:
    if version:
        normalized = version.strip().replace(" ", "-").replace("/", "-")
        return f"jiaojie-skill-{normalized}"
    return "jiaojie-skill"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a simple distributable zip for the jiaojie skill.")
    parser.add_argument("--version", help="Optional release version, for example v0.1.0")
    args = parser.parse_args()

    if not SKILL_DIR.is_dir():
        raise SystemExit(f"Missing skill directory: {SKILL_DIR}")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    archive_base = DIST_DIR / archive_name(args.version)
    archive_path = shutil.make_archive(str(archive_base), "zip", SKILL_DIR.parent, SKILL_DIR.name)
    archive = Path(archive_path)
    checksum_path = archive.with_suffix(".zip.sha256")
    checksum = sha256(archive)
    checksum_path.write_text(f"{checksum}  {archive.name}\n", encoding="utf-8")

    print(f"[archive] {archive}")
    print(f"[sha256]  {checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
