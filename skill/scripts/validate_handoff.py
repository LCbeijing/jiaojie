#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


KIND_REQUIREMENTS = {
    "handoff": ["# 项目交接总账", "## 1. 项目目标", "## 2. 基线定义"],
    "current-phase": ["# 当前阶段进展", "## 1. 当前阶段目标", "## 6. 下一步最优先动作"],
    "next-thread": ["先读取以下文件", "当前阶段目标", "关键限制"],
    "project-intel": ["# 项目摸底 / 评估梳理", "## 1. 项目目标与业务背景", "## 2. 基线判断与权威来源"],
    "project-dev-plan": ["# 开发规划主文档", "## 1. 总体执行原则", "## 4. 执行阶段总览"],
    "project-prd": ["# 产品需求文档（PRD）", "## 1. 产品定位", "## 5. 产品信息架构"],
    "project-db-design": ["# 数据库设计", "## 1. 设计目标", "## 4. 目标核心模型"],
}

NAME_TO_KIND = {
    "handoff.md": "handoff",
    "current-phase.md": "current-phase",
    "next-thread-prompt.md": "next-thread",
    "PROJECT_INTEL.md": "project-intel",
    "PROJECT_DEV_PLAN.md": "project-dev-plan",
    "PROJECT_PRD.md": "project-prd",
    "PROJECT_DB_DESIGN.md": "project-db-design",
}


def decode_text(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace"), "utf-8-replace"


def count_cjk(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def parse_input(raw: str) -> tuple[Path, str | None]:
    if "::" not in raw:
        return Path(raw), None
    path_part, kind_part = raw.rsplit("::", 1)
    kind = kind_part.strip() or None
    return Path(path_part), kind


def resolve_kind(path: Path, kind: str | None) -> str | None:
    if kind is not None:
        return kind
    return NAME_TO_KIND.get(path.name)


def classify(path: Path, kind: str | None = None) -> dict:
    text, encoding = decode_text(path)
    stripped = text.strip()
    question_count = text.count("?")
    replacement_count = text.count("\ufffd")
    cjk_count = count_cjk(text)
    line_count = len(text.splitlines())
    effective_kind = resolve_kind(path, kind)

    status = "ok"
    reasons: list[str] = []

    if not stripped:
        status = "error"
        reasons.append("empty-file")
    if cjk_count == 0 and question_count >= 20:
        status = "error"
        reasons.append("likely-real-corruption")
    if replacement_count > 0:
        status = "error"
        reasons.append("replacement-char-present")
    if line_count < 3:
        status = "error"
        reasons.append("too-short")
    if kind is not None and effective_kind not in KIND_REQUIREMENTS:
        status = "error"
        reasons.append(f"unknown-kind:{kind}")

    required = KIND_REQUIREMENTS.get(effective_kind, [])

    for item in required:
        if item not in text:
            status = "error"
            reasons.append(f"missing:{item}")

    return {
        "path": str(path),
        "kind": effective_kind,
        "encoding": encoding,
        "status": status,
        "line_count": line_count,
        "cjk_count": cjk_count,
        "question_count": question_count,
        "replacement_count": replacement_count,
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate handoff markdown files.")
    parser.add_argument("paths", nargs="+", help="Paths to handoff files")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    reports = []
    exit_code = 0
    for raw in args.paths:
        path, kind = parse_input(raw)
        if not path.exists():
            report = {"path": str(path), "kind": kind, "status": "error", "reasons": ["missing-file"]}
            exit_code = 1
        else:
            report = classify(path, kind=kind)
            if report["status"] != "ok":
                exit_code = 1
        reports.append(report)

    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    else:
        for item in reports:
            print(f"[{item['status'].upper()}] {item['path']}")
            if item.get("kind"):
                print(f"  - kind: {item['kind']}")
            for key in ("encoding", "line_count", "cjk_count", "question_count", "replacement_count"):
                if key in item:
                    print(f"  - {key}: {item[key]}")
            if item.get("reasons"):
                print(f"  - reasons: {', '.join(item['reasons'])}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
