# skill-governance-block
Vendor-neutral skill-manifest binding of the Loomground governance language: a skill declares its governance boundary once, in its manifest.

## Problem
A skill's limits live in prose; the orchestrator and the enforcer read different things. One manifest block both read: grade, actions, reserved, prohibited, obligations.

## Read
- [`spec/SPEC.md`](spec/SPEC.md) — the contract, v0.1 draft.
- [`examples/finalise-change.md`](examples/finalise-change.md) — a block, its compiled `.lg`, its validation.
- [`docs/rationale.md`](docs/rationale.md) — design rationale.
- [`reference/compile_block_to_lg.py`](reference/compile_block_to_lg.py) — the **canonical** reference compiler for SPEC §4 (see "Canonical compiler" below).

## Usage
1. Shape check: validate the `governance` mapping against `schema/governance-block.schema.json`.
2. Authoritative check: compile the block with `reference/compile_block_to_lg.py` to a Loomground `.lg` patch and run a Loomground reference validator; valid iff `WELL-FORMED`.

## Example
```
in : examples/finalise-change.md `governance:` block → reference/compile_block_to_lg.py → examples/finalise-change.lg → Loomground reference evaluator
out: examples/finalise-change.lg reproduced byte-for-byte (tests/test_compile_reproduces_lg.py)
     WELL-FORMED (7 action gates; auto/human/reserved/prohibited each demonstrated — see examples/finalise-change.md's verdict table)
```

## Canonical compiler

`reference/compile_block_to_lg.py` in this repo is the **canonical** implementation of
SPEC §4 ("block → `.lg` patch") for this spec. It is a straight port of
`governance-layer`'s fixed compiler (the L1 fix that removed the always-refused
`release` gate). `governance-layer` is not made to import this repo's package — that
would require editing `governance-layer`, which is a separate project outside this
repo's territory; instead `governance-layer` keeps its own copy, and this repo's
`tests/test_compile_reproduces_lg.py` proves byte-for-byte parity between this
compiler's output and the committed `examples/finalise-change.lg`. No test in this
repo compares against `governance-layer`'s copy, so divergence between the two copies is
not detected here; if they ever diverge, this repo's `reference/` copy governs the
spec's meaning.

## Contracts
| item | definition |
|---|---|
| manifest field | `governance` mapping; fields `grade`, `actions`, `reserved`, `prohibited`, `obligations`, `redress`, `budget`, `on-boundary`; all optional (SPEC §2) |
| target language | Loomground `.lg` policy graph: nine declarations, five verdicts (SPEC §3) |
| reader, plan-time | plans on the block: grade gaps, reserved gated, prohibited excluded, obligations as accept-criteria, budget capped (SPEC §7) |
| enforcer, action-time | one Loomground verdict per governed action, from the same block (SPEC §7) |
| validity | the block compiles to a `WELL-FORMED` patch (SPEC §6) |
| schema | `schema/governance-block.schema.json`, JSON Schema 2020-12, shape pre-check |

## Family
Vendor-neutral skill-manifest binding; external contract; host bindings explicitly non-normative. Consumes [`loomground-governance`](https://github.com/flxk1/loomground-governance): language, schemas, reference validator. Consumed by orchestrators (reader) and governance tools (enforcer). `bindings/claude-code.md` documents one Claude Code binding with generic reader and enforcer ports.

## Status
Spec v0.1, draft · 1 schema · 1 worked example · 1 binding · 1 canonical reference compiler (`reference/`) · CI validates the schema against `examples/` and `bindings/`.

## How this is made

The code and documentation are written with Loomground agents. The maintainer reads and corrects all of it.

## License
Apache-2.0 — [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt), `NOTICE`, `REUSE.toml`.
