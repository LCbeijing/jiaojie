#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skill"
DIST_DIR = ROOT / "dist"
ARCHIVE_BASE = DIST_DIR / "jiaojie-skill"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    if not SKILL_DIR.is_dir():
        raise SystemExit(f"Missing skill directory: {SKILL_DIR}")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = shutil.make_archive(str(ARCHIVE_BASE), "zip", SKILL_DIR.parent, SKILL_DIR.name)
    archive = Path(archive_path)
    checksum_path = archive.with_suffix(".zip.sha256")
    checksum_path.write_text(f"{sha256(archive)}  {archive.name}\n", encoding="utf-8")

    print(f"[archive] {archive}")
    print(f"[sha256]  {checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
