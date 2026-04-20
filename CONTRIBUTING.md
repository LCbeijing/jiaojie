# Contributing to jiaojie

Thanks for helping improve `jiaojie`.

## What to improve

Good contributions include:

- tighter handoff logic
- better validation heuristics
- safer encoding handling
- better cross-platform install stability
- better regression coverage
- clearer multilingual documentation

## Design principles

Please preserve these priorities:

1. keep `skill/SKILL.md` lean
2. push low-frequency details into `skill/references/`
3. prefer deterministic checks in `skill/scripts/`
4. do not bloat the default prompt surface
5. validate behavior with the regression script when possible

## Local verification

Run:

```bash
python3 skill/scripts/regression_readonly.py
python3 skill/scripts/regression_readonly.py --json
```

## Installation model

This repository is an open-source wrapper around the actual skill content located in `skill/`.

Please keep:

- repository-level files at repo root
- skill runtime files inside `skill/`

## Pull request guidance

- explain the use case
- describe the failure mode being fixed
- keep changes minimal
- include validation evidence when changing scripts
