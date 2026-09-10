# skill-governance-block
Vendor-neutral skill-manifest binding of the Loomground governance language: a skill declares its governance boundary once, in its manifest.

## Problem
A skill's limits live in prose; the orchestrator and the enforcer read different things. One manifest block both read: grade, actions, reserved, prohibited, obligations.

## Read
- [`spec/SPEC.md`](spec/SPEC.md) — the contract, v0.1 draft.
- [`examples/finalise-rvnd.md`](examples/finalise-rvnd.md) — a block, its compiled `.lg`, its validation.
- [`docs/rationale.md`](docs/rationale.md) — design rationale.

## Usage
1. Shape check: validate the `governance` mapping against `schema/governance-block.schema.json`.
2. Authoritative check: compile the block to a Loomground `.lg` patch and run the reference validator; valid iff `WELL-FORMED`.

## Example
```
in : examples/finalise-rvnd.md `governance:` block → schema check · examples/finalise-rvnd.lg → validate.py
out: valid: examples/finalise-rvnd.md vs governance-block.schema.json
     2 governance blocks, 1 schemas, 0 errors
     WELL-FORMED
```

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
Vendor-neutral skill-manifest binding; external contract; RVND and Claude bindings explicitly non-normative. Consumes [`loomground-governance`](https://github.com/flxk1/loomground-governance): language, schemas, reference validator. Consumed by orchestrators (reader) and governance tools (enforcer). `bindings/claude-code.md`: the Claude Code + ctrl + RVND binding.

## Status
Spec v0.1, draft · 1 schema · 1 worked example · 1 binding · CI validates the schema against `examples/` and `bindings/`.

## License
Apache-2.0 — [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt), `NOTICE`, `REUSE.toml`.
