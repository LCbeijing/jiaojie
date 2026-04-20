# Windows / PowerShell / 中文文档安全写法

何时读：在 Windows + PowerShell 环境下需要读写中文 handoff / 主文档时。

## 写入方式优先级

1. **首选 `apply_patch`**
   - 适合：改现有 Markdown、替换段落、补标题、局部修文
   - 原因：最不依赖终端代码页
2. **次选 `Path(...).write_text(..., encoding='utf-8')`**
   - 适合：内容来自本地模板、已有文件、短字符串或程序内构造
3. **最低优先级：PowerShell 直接拼正文写文件**
   - 除非内容极短且显式指定 UTF-8，否则尽量不用

## 高风险动作

- 在 `shell_command` 里用长篇 here-string / heredoc 直接承载中文正文
- 用 `python -` 从 stdin / 管道接大段中文正文再落盘
- 依赖终端当前代码页中转中文
- 先把中文写进 shell 变量，再多次拼接写回文件
- 把 `Get-Content` / 终端显示结果直接当成“文件完好”的唯一证据

## 相对安全的做法

- `Get-Content` 可用于粗看内容；**不能单独作为完好依据**
- 需要确认完好时，用 Python 显式 `utf-8` / `utf-8-sig` 回读
- 必须批量重写时，优先让正文来自文件或程序内字符串，而不是 shell 管道

## 写完后的最小闭环

1. 显式 `utf-8` 读回文件
2. 跑 `validate_handoff.py`
3. 如果只是终端显示异常，再跑 `diagnose_encoding.py`

## 一句话原则

终端看起来乱，不等于文件真的坏；先验证字节和显式解码结果，再做结论。
