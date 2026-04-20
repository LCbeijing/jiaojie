# 交接 / jiaojie

**A Codex skill for reliable handoff, resume, rebuild, and document health validation.**

`jiaojie` turns messy thread-to-thread continuation into a disciplined workflow:

- read the handoff bundle first,
- expand only when needed,
- avoid full-repo re-discovery,
- validate before declaring a document healthy or broken,
- keep main docs and handoff docs in sync.

It is designed for real multi-session development work, especially when teams or agents frequently:

- hand work from one thread to another,
- resume after interruptions,
- inherit stale or damaged handoff notes,
- need to distinguish “terminal garble” from real document corruption,
- want lower token waste and faster continuation.

---

## Why this skill exists

Most agent handoffs fail in one of four ways:

1. the next thread re-explores the whole repo,
2. outdated conclusions survive after reality changed,
3. handoff docs become bloated and unusable,
4. Windows + PowerShell + Chinese text workflows produce false corruption alarms.

`jiaojie` addresses those problems with a strict philosophy:

- **minimal but sufficient handoff**
- **progressive disclosure**
- **validate before judging**
- **status consistency across docs**

This means:

- faster resumes,
- fewer repeated tokens,
- less duplicated repo exploration,
- safer document maintenance,
- more trustworthy continuation prompts for future agents.

---

## Core idea

`jiaojie` is not “write more docs”.

It is:

- keep **stable facts** in `handoff.md`,
- keep **current batch execution state** in `current-phase.md`,
- keep **immediate startup instructions** in `next-thread-prompt.md`,
- then validate the result with scripts before handing off.

---

## Common use cases

### 1. End-of-thread handoff

When a work batch is about to end, use `jiaojie` to compress current reality into a handoff bundle for the next thread.

### 2. Resume from an existing handoff

When a new thread starts, use `jiaojie` to read the handoff bundle first, then continue directly without asking the user to repeat context.

### 3. Rebuild stale or broken handoff

When the handoff bundle is missing, outdated, contradictory, or clearly insufficient, use `jiaojie` to rebuild it from currently verifiable sources.

### 4. Validate document health

When a thread claims a main document is broken, `jiaojie` helps verify whether that is:

- real corruption,
- stale status,
- or just display/encoding noise.

### 5. Keep docs in sync after recovery

If a main document becomes healthy again, `jiaojie` ensures the handoff bundle stops telling future agents that it is still broken.

---

## What makes `jiaojie` different

- **Handoff-first continuation** instead of repo-first continuation
- **Script-backed validation** instead of guesswork
- **Progressive disclosure references** instead of one bloated skill file
- **Alias-safe validation** via `::kind` for non-standard filenames
- **Read-only regression tests** for long-term maintenance

---

## Repository layout

```text
jiaojie/
├─ README.md
├─ LICENSE
├─ CONTRIBUTING.md
├─ install.sh
└─ skill/
   ├─ SKILL.md
   ├─ agents/
   │  └─ openai.yaml
   ├─ references/
   │  ├─ mode-playbooks.md
   │  ├─ handoff-file-contracts.md
   │  ├─ validation-and-health.md
   │  ├─ windows-encoding-safety.md
   │  └─ status-sync-and-rebuild.md
   └─ scripts/
      ├─ validate_handoff.py
      ├─ audit_doc_health.py
      ├─ diagnose_encoding.py
      └─ regression_readonly.py
```

---

## Quick install

### Option A — one-line install

```bash
curl -fsSL https://raw.githubusercontent.com/LCbeijing/jiaojie/main/install.sh | bash
```

This installs the skill into:

- `$CODEX_HOME/skills/jiaojie` when `CODEX_HOME` is set
- otherwise `~/.codex/skills/jiaojie`

### Option B — manual install

Clone the repo, then copy `skill/` into your Codex skills directory as `jiaojie`.

---

## Verify the installation

Run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/jiaojie/scripts/regression_readonly.py" --json
```

Expected result:

- `"ok": true`
- all tests passed

---

## Best-fit environments

`jiaojie` is especially strong when:

- you use Codex or agentic workflows daily,
- you often continue work across threads/sessions,
- your projects rely on handoff docs,
- you want to reduce repeated repo re-analysis,
- you work in Chinese-heavy documentation environments,
- you need safer Windows text handling.

It can still be useful outside Chinese workflows, but the current prompts and phrasing are optimized for Chinese-language development handoff patterns.

---

## Example triggers

Typical user phrases that should trigger this skill:

- `收尾交接`
- `继续交接`
- `重建交接`
- `交接包`
- `jiaojie`
- `$jiaojie`

---

## Philosophy

`jiaojie` optimizes for:

- **professionalism** — structured handoff responsibility
- **completeness** — mode routing, validation, sync, rebuild
- **efficiency** — smaller prompts, fewer repeated reads
- **reliability** — validation before claims
- **maintainability** — read-only regression checks

---

## Contributing

Contributions are welcome.

If you improve:

- handoff quality,
- validation accuracy,
- installation stability,
- multilingual usability,
- or regression coverage,

please open an issue or pull request.

See [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## License

MIT — see [LICENSE](./LICENSE).
