# 校验与健康判断

何时读：需要决定该跑哪条校验链路，或解释“文档到底是坏了、旧结论过期了，还是只是终端显示异常”时。

目录：
- 场景到命令
- `validate_handoff.py`
- 主文档校验
- `audit_doc_health.py`
- `diagnose_encoding.py`
- 宣称“已损坏”前至少做的事

## 场景到命令

- **只改了 handoff 三件套**：跑 `validate_handoff.py` 检查结构、编码与明显损坏迹象。
- **既动了 handoff，也动了主文档**：先跑 `validate_handoff.py` 检查 handoff 与主文档，再按需跑一致性审计。
- **本轮改变了主文档健康结论**：额外跑 `audit_doc_health.py`，确认 handoff 没继续传播陈旧“已损坏 / 需重建”结论。
- **怀疑只是终端显示乱码**：最后才跑 `diagnose_encoding.py`；它用于诊断编码链路，不替代结构校验。

如果校验失败，不要向用户宣称交接已完成；应先修复或重建。

## `validate_handoff.py`

标准文件名：

```powershell
python "C:\Users\LC.DESKTOP-SENLCL9\.codex\skills\jiaojie\scripts\validate_handoff.py" `
  "<repo>\docs\codex\handoff.md" `
  "<repo>\docs\codex\current-phase.md" `
  "<repo>\docs\codex\next-thread-prompt.md"
```

非标准文件名时，用 `::kind` 显式指定：

```powershell
python "C:\Users\LC.DESKTOP-SENLCL9\.codex\skills\jiaojie\scripts\validate_handoff.py" `
  "<repo>\docs\codex\delivery.md::handoff" `
  "<repo>\docs\codex\phase-board.md::current-phase" `
  "<repo>\docs\codex\resume-thread.md::next-thread"
```

支持的 kind：
- `handoff`
- `current-phase`
- `next-thread`
- `project-intel`
- `project-dev-plan`
- `project-prd`
- `project-db-design`

常见错误含义：
- `missing-file`：文件缺失，需创建或重建
- `missing:...`：结构不完整，先补齐必要段落
- `replacement-char-present`：存在替换字符，优先怀疑真损坏
- `likely-real-corruption`：内容高度异常，优先按真损坏处理
- `unknown-kind:...`：显式类型写错，先修命令

## 主文档校验

```powershell
python "C:\Users\LC.DESKTOP-SENLCL9\.codex\skills\jiaojie\scripts\validate_handoff.py" `
  "<repo>\PROJECT_INTEL.md" `
  "<repo>\PROJECT_DEV_PLAN.md" `
  "<repo>\PROJECT_PRD.md" `
  "<repo>\PROJECT_DB_DESIGN.md"
```

如果文件名不同，也可用 `::kind`：

```powershell
"<repo>\docs\intel.md::project-intel"
```

## `audit_doc_health.py`

当本轮涉及主文档修复、重建或健康状态判断时执行：

```powershell
python "C:\Users\LC.DESKTOP-SENLCL9\.codex\skills\jiaojie\scripts\audit_doc_health.py" `
  --main-docs `
  "<repo>\PROJECT_INTEL.md" `
  "<repo>\PROJECT_DEV_PLAN.md" `
  "<repo>\PROJECT_PRD.md" `
  "<repo>\PROJECT_DB_DESIGN.md" `
  --handoff-docs `
  "<repo>\docs\codex\handoff.md" `
  "<repo>\docs\codex\current-phase.md" `
  "<repo>\docs\codex\next-thread-prompt.md"
```

它抓的是：主文档已健康但 handoff 仍写“已损坏 / 需重建”，或 handoff 仍要求“先重建主文档”而当前事实已变。  
如果写的是“旧结论已过期 / 当前已通过校验”，不应视为问题。

## `diagnose_encoding.py`

仅在怀疑“终端显示乱码”可能误导判断时执行：

```powershell
python "C:\Users\LC.DESKTOP-SENLCL9\.codex\skills\jiaojie\scripts\diagnose_encoding.py"
```

用途：查看 Python / 终端当前编码链路，并验证 UTF-8 回写与回读是否正常。不要把它当成“文档结构已通过”的替代品。

## 宣称“已损坏”前至少做的事

1. 跑 `validate_handoff.py`
2. 用 Python 显式按 `utf-8` / `utf-8-sig` 读一次文件
3. 区分“终端显示乱码”与“写入层真损坏”
4. 如果旧线程说坏了、但当前校验通过，应优先判定为“旧状态过期”
