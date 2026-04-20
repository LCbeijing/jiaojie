#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_handoff import classify, decode_text, parse_input


NEGATIVE_MARKERS = [
    "已损坏",
    "真实损坏",
    "当前已损坏",
    "需后续重建",
    "不要作为首要可信来源",
    "不要作为下一线程的首要可信来源",
    "不能继续作为高可信主文档",
    "最后重建",
]

SAFE_MARKERS = [
    "已重建并通过校验",
    "重建并通过校验",
    "当前健康",
    "可作为可信来源",
    "可作为可信主文档",
    "已通过校验",
    "通过校验",
    "状态一致",
    "旧状态过期",
    "结论已过期",
    "历史结论已过期",
]


def stale_line_for_healthy_doc(doc_name: str, line: str) -> bool:
    if doc_name not in line:
        return False
    if any(marker in line for marker in SAFE_MARKERS):
        return False
    if any(marker in line for marker in NEGATIVE_MARKERS):
        return True
    if "重建" in line and "已重建" not in line and "重建时间" not in line:
        return True
    return False


def scan_handoff_doc(path: Path, healthy_doc_names: set[str]) -> list[dict]:
    text, encoding = decode_text(path)
    findings: list[dict] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        for doc_name in healthy_doc_names:
            if stale_line_for_healthy_doc(doc_name, line):
                findings.append(
                    {
                        "path": str(path),
                        "encoding": encoding,
                        "line_number": line_number,
                        "doc_name": doc_name,
                        "line": line,
                        "reason": "stale-negative-status-for-healthy-doc",
                    }
                )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit whether handoff docs still contain stale damage/rebuild descriptions for healthy main docs."
    )
    parser.add_argument("--main-docs", nargs="+", required=True, help="Main project docs to classify")
    parser.add_argument("--handoff-docs", nargs="+", required=True, help="Handoff docs to scan for stale status lines")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    main_reports = []
    exit_code = 0
    for raw in args.main_docs:
        path, kind = parse_input(raw)
        if not path.exists():
            main_reports.append({"path": str(path), "kind": kind, "status": "error", "reasons": ["missing-file"]})
            exit_code = 1
            continue
        report = classify(path, kind=kind)
        main_reports.append(report)
        if report["status"] != "ok":
            exit_code = 1

    healthy_doc_names = {Path(item["path"]).name for item in main_reports if item.get("status") == "ok"}

    findings = []
    for raw in args.handoff_docs:
        path, _ = parse_input(raw)
        if not path.exists():
            findings.append(
                {
                    "path": str(path),
                    "reason": "missing-handoff-doc",
                }
            )
            exit_code = 1
            continue
        findings.extend(scan_handoff_doc(path, healthy_doc_names))

    if findings:
        exit_code = 1

    if args.json:
        print(
            json.dumps(
                {
                    "main_reports": main_reports,
                    "findings": findings,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return exit_code

    print("Main docs:")
    for report in main_reports:
        print(f"- {report['path']}: {report['status']}")

    if findings:
        print("\nStale status findings:")
        for item in findings:
            line_number = item.get("line_number")
            if line_number is None:
                print(f"- {item['path']}: {item['reason']}")
            else:
                print(f"- {item['path']}:{line_number} [{item['doc_name']}] {item['line']}")
    else:
        print("\nNo stale damage/rebuild descriptions found in handoff docs.")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
