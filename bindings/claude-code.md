# Binding: Claude Code + ctrl + RVND

**Non-normative.** One concrete implementation of the vendor-neutral spec (`../SPEC.md`)
on a specific stack. Nothing here is part of the contract; it shows how the two roles —
**reader** and **enforcer** — are realized here. Another host, orchestrator, or
governance tool is a different binding of the same block.

| spec role | realized by | where |
|---|---|---|
| manifest carrying the block | a skill's `SKILL.md` YAML frontmatter | any skill |
| **reader** (plan-time) | the `orchestrate` skill's governance pre-flight | ctrl-engineering `skills/orchestrate/SKILL.md` |
| **enforcer** (action-time) | the PreToolUse hook returning a verdict | RVND `rvnd-hook-scoped` |
| compiler + validator | the `loomground` skill's bundled engine | loomground-governance `validate.py` |
| the four seams the fields feed | Toolset / Dispatch / Accept / Hook | ctrl-engineering `GOVERNANCE-SEAMS.md` |

## Manifest form

The block sits in the skill's YAML frontmatter beside `name`/`description`:

```yaml
---
name: <skill>
description: <…>
governance:
  grade: L2
  actions:
    - { kind: worktree-irreversible, risk: high, grade: L3 }
  reserved:
    - { kind: commit, by: { all: [owner, peer] } }
  prohibited: [ push ]
  obligations: [ gates-green, attribution ]
  redress:
    - { kind: commit, by: owner, overturn: true, within: 7d }
---
```

## Reader → the four seams

The orchestrate pre-flight maps each field to the seam it pre-populates (per
`GOVERNANCE-SEAMS.md`), before dispatch:

- `prohibited` → **Toolset** seam: withhold the raw capability at hire.
- `grade` (+ per-action) → **Dispatch** seam: below-grade → `hold`, surfaced up front.
- `obligations` → **Accept** seam: conditions the verify gate must see attached.
- `reserved` → **Hook** seam: route to a human.

The reader's plan-time grade check is the same `hold` the Dispatch seam enforces
per-leg — surfaced earlier so a grade gap is a pre-flight message, not a mid-run wall.

## Enforcer → verdicts

The compiled `.lg` is enforced at the PreToolUse hook: it returns the Loomground verdict
for each governed tool call. On this stack the hook is `enforced` inside a registered
workspace and `advisory-observed` elsewhere — the honest tier is declared to the caller.

## Validation on this stack

Compile the block to `<skill>.lg` and run the loomground skill's validator:

```
python3 <loomground-skill>/validate.py <skill>.lg      # -> WELL-FORMED | REJECTED (parse|apply)
```

A worked, validated example is in `../examples/` (`finalise-rvnd.lg` →
`WELL-FORMED`, with the four meaning-giving verdicts confirmed by the engine).
