#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skill"
DIST_DIR = ROOT / "dist"


def git_value(*args: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def release_version() -> str:
    described = git_value("describe", "--tags", "--always", "--dirty")
    if described:
        return described.replace("/", "-")
    return "manual"


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
    version = release_version()
    archive_base = DIST_DIR / f"jiaojie-skill-{version}"
    archive_path = shutil.make_archive(str(archive_base), "zip", SKILL_DIR.parent, SKILL_DIR.name)
    archive = Path(archive_path)
    checksum_path = archive.with_suffix(".zip.sha256")
    checksum = sha256(archive)
    checksum_path.write_text(f"{checksum}  {archive.name}\n", encoding="utf-8")
    manifest_path = archive.with_suffix(".json")
    manifest = {
        "archive": archive.name,
        "version": version,
        "git_head": git_value("rev-parse", "HEAD"),
        "git_head_short": git_value("rev-parse", "--short", "HEAD"),
        "sha256": checksum,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[archive] {archive}")
    print(f"[sha256]  {checksum_path}")
    print(f"[manifest] {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
