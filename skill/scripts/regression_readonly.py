#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VALIDATE = ROOT / "validate_handoff.py"
AUDIT = ROOT / "audit_doc_health.py"


def run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_standard_repo(base: Path) -> Path:
    repo = base / "repo-standard"
    write(
        repo / "docs" / "codex" / "handoff.md",
        """# 项目交接总账
## 1. 项目目标
- 维护交接稳定性
## 2. 基线定义
- 基线：`app/main.py`
## 3. 已完成核心成果
- 已建立 handoff 三件套
## 4. 固定约束与冻结规则
- 统一 UTF-8
## 5. 已知风险与遗留问题
- 暂无
## 6. 下一阶段建议
- 继续功能开发
## 7. 可信来源 / 验证依据
- 当前文件已校验
## 8. 最后更新时间
- 2026-04-04
""",
    )
    write(
        repo / "docs" / "codex" / "current-phase.md",
        """# 当前阶段进展
## 1. 当前阶段目标
- 保持交接可续做
## 2. 本批已完成事项
- 完成三件套
## 3. 最近改动文件 / 模块
- `docs/codex/*`
## 4. 当前验证结果
- handoff 三件套通过结构校验
## 5. 当前阻塞 / 风险
- 暂无
## 6. 下一步最优先动作
- 继续开发
## 7. 最后更新时间
- 2026-04-04
""",
    )
    write(
        repo / "docs" / "codex" / "next-thread-prompt.md",
        """你在仓库 `repo-standard` 中继续工作。

先读取以下文件：
- `docs/codex/handoff.md`
- `docs/codex/current-phase.md`

当前阶段目标：
- 保持交接可续做

不要重新全仓摸底；先按交接继续。

直接开始：
1. 阅读主文档
2. 继续开发

关键限制：
- 保持状态一致
""",
    )
    write(
        repo / "PROJECT_INTEL.md",
        """# 项目摸底 / 评估梳理
## 1. 项目目标与业务背景
- 示例仓库
## 2. 基线判断与权威来源
- 当前主文档可读
""",
    )
    return repo


def build_alias_repo(base: Path) -> Path:
    repo = base / "repo-alias"
    write(
        repo / "docs" / "codex" / "delivery.md",
        """# 项目交接总账
## 1. 项目目标
- 验证 kind 路由
## 2. 基线定义
- 基线 A
## 3. 已完成核心成果
- 已完成
## 4. 固定约束与冻结规则
- UTF-8
## 5. 已知风险与遗留问题
- 暂无
## 6. 下一阶段建议
- 继续
## 7. 可信来源 / 验证依据
- 当前校验
## 8. 最后更新时间
- 2026-04-04
""",
    )
    write(
        repo / "docs" / "codex" / "phase-board.md",
        """# 当前阶段进展
## 1. 当前阶段目标
- 验证 alias
## 2. 本批已完成事项
- 已建立别名文件
## 3. 最近改动文件 / 模块
- `docs/codex/*`
## 4. 当前验证结果
- 通过
## 5. 当前阻塞 / 风险
- 暂无
## 6. 下一步最优先动作
- 继续
## 7. 最后更新时间
- 2026-04-04
""",
    )
    write(
        repo / "docs" / "codex" / "resume-thread.md",
        """你在仓库 `repo-alias` 中继续工作。

先读取以下文件：
- `docs/codex/delivery.md`
- `docs/codex/phase-board.md`

当前阶段目标：
- 验证 next-thread alias

不要重新全仓摸底；先按交接继续。

直接开始：
1. 继续

关键限制：
- 使用 alias 校验
""",
    )
    return repo


def test_validate_standard(base: Path) -> tuple[bool, str]:
    repo = build_standard_repo(base)
    result = run_cmd(
        [
            sys.executable,
            str(VALIDATE),
            str(repo / "docs" / "codex" / "handoff.md"),
            str(repo / "docs" / "codex" / "current-phase.md"),
            str(repo / "docs" / "codex" / "next-thread-prompt.md"),
            f"{repo / 'PROJECT_INTEL.md'}::project-intel",
        ]
    )
    ok = result.returncode == 0 and result.stdout.count("[OK]") == 4
    return ok, result.stdout + result.stderr


def test_validate_alias(base: Path) -> tuple[bool, str]:
    repo = build_alias_repo(base)
    result = run_cmd(
        [
            sys.executable,
            str(VALIDATE),
            f"{repo / 'docs' / 'codex' / 'delivery.md'}::handoff",
            f"{repo / 'docs' / 'codex' / 'phase-board.md'}::current-phase",
            f"{repo / 'docs' / 'codex' / 'resume-thread.md'}::next-thread",
        ]
    )
    ok = result.returncode == 0 and result.stdout.count("[OK]") == 3
    return ok, result.stdout + result.stderr


def test_audit_detects_stale(base: Path) -> tuple[bool, str]:
    repo = build_standard_repo(base / "stale")
    write(
        repo / "docs" / "codex" / "handoff.md",
        (repo / "docs" / "codex" / "handoff.md").read_text(encoding="utf-8")
        + "- `PROJECT_INTEL.md` 已损坏，不要作为首要可信来源。\n",
    )
    result = run_cmd(
        [
            sys.executable,
            str(AUDIT),
            "--main-docs",
            f"{repo / 'PROJECT_INTEL.md'}::project-intel",
            "--handoff-docs",
            str(repo / "docs" / "codex" / "handoff.md"),
            str(repo / "docs" / "codex" / "current-phase.md"),
            str(repo / "docs" / "codex" / "next-thread-prompt.md"),
        ]
    )
    ok = result.returncode != 0 and "Stale status findings:" in result.stdout
    return ok, result.stdout + result.stderr


def test_audit_allows_expired(base: Path) -> tuple[bool, str]:
    repo = build_standard_repo(base / "expired")
    write(
        repo / "docs" / "codex" / "handoff.md",
        (repo / "docs" / "codex" / "handoff.md").read_text(encoding="utf-8")
        + "- `PROJECT_INTEL.md` 旧结论已过期；当前文件已通过校验，可作为可信来源。\n",
    )
    result = run_cmd(
        [
            sys.executable,
            str(AUDIT),
            "--main-docs",
            f"{repo / 'PROJECT_INTEL.md'}::project-intel",
            "--handoff-docs",
            str(repo / "docs" / "codex" / "handoff.md"),
            str(repo / "docs" / "codex" / "current-phase.md"),
            str(repo / "docs" / "codex" / "next-thread-prompt.md"),
        ]
    )
    ok = result.returncode == 0 and "No stale damage/rebuild descriptions found" in result.stdout
    return ok, result.stdout + result.stderr


def emit_json(
    *,
    tests: list[dict[str, object]],
    temp_dir: Path,
    keep_temp: bool,
    failed: bool,
) -> None:
    payload = {
        "ok": not failed,
        "script": str(Path(__file__).resolve()),
        "counts": {
            "total": len(tests),
            "passed": sum(1 for item in tests if item["passed"]),
            "failed": sum(1 for item in tests if not item["passed"]),
        },
        "tests": tests,
        "temp_dir": str(temp_dir) if (keep_temp or failed) else None,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only regression tests for jiaojie skill scripts.")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary fixtures for debugging")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON summary")
    args = parser.parse_args()

    temp_dir = Path(tempfile.mkdtemp(prefix="jiaojie-regression-"))
    tests = [
        ("validate_standard", test_validate_standard),
        ("validate_alias", test_validate_alias),
        ("audit_detects_stale", test_audit_detects_stale),
        ("audit_allows_expired", test_audit_allows_expired),
    ]

    results: list[dict[str, object]] = []
    failed_outputs: list[tuple[str, str]] = []
    try:
        for name, fn in tests:
            ok, output = fn(temp_dir)
            results.append(
                {
                    "name": name,
                    "passed": ok,
                    **({"output": output} if not ok else {}),
                }
            )
            if not args.json:
                print(f"[{'PASS' if ok else 'FAIL'}] {name}")
            if not ok:
                failed_outputs.append((name, output))

        if failed_outputs:
            if args.json:
                emit_json(tests=results, temp_dir=temp_dir, keep_temp=args.keep_temp, failed=True)
            else:
                print("\n--- failure details ---")
                for name, output in failed_outputs:
                    print(f"\n## {name}\n{output}")
                print(f"\nTemporary fixtures: {temp_dir}")
            return 1

        if args.json:
            emit_json(tests=results, temp_dir=temp_dir, keep_temp=args.keep_temp, failed=False)
        else:
            print("\nAll read-only regression tests passed.")
            if args.keep_temp:
                print(f"Temporary fixtures kept at: {temp_dir}")
        return 0
    finally:
        if not args.keep_temp and not failed_outputs:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
