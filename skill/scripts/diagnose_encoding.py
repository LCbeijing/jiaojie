#!/usr/bin/env python3
from __future__ import annotations

import locale
import os
import sys
import tempfile
from pathlib import Path


SAMPLE = "中文编码自检：交接文档健康"


def main() -> int:
    print("Python encoding diagnostics")
    print(f"- sys.getdefaultencoding(): {sys.getdefaultencoding()}")
    print(f"- sys.getfilesystemencoding(): {sys.getfilesystemencoding()}")
    print(f"- sys.stdout.encoding: {sys.stdout.encoding}")
    print(f"- locale.getpreferredencoding(False): {locale.getpreferredencoding(False)}")
    try:
        print(f"- os.device_encoding(1): {os.device_encoding(1)}")
    except OSError:
        print("- os.device_encoding(1): <unavailable>")

    tmp_dir = Path(tempfile.gettempdir())
    probe = tmp_dir / "codex-jiaojie-encoding-probe.txt"
    probe.write_text(SAMPLE, encoding="utf-8")
    text = probe.read_text(encoding="utf-8")
    data = probe.read_bytes()

    print("\nUTF-8 probe")
    print(f"- probe_path: {probe}")
    print(f"- utf8_roundtrip_ok: {text == SAMPLE}")
    print(f"- byte_prefix: {data[:24]!r}")
    print(f"- text: {text}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
