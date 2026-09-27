# Example: `finalise-change`

A worked block → compiled `.lg` → validated. The skill completes/verifies/stages a
change in a repository, coordinates peers before any commit, and never pushes.

## The block (manifest frontmatter)

```yaml
governance:
  grade: L2
  actions:
    - { kind: read,                  risk: low }
    - { kind: edit,                  risk: medium }
    - { kind: run-tests,             risk: medium }
    - { kind: run-gates,             risk: medium }
    - { kind: worktree-irreversible, risk: high, grade: L3 }   # clean-checkout verify
    - { kind: commit,                risk: high, grade: L3 }
    - { kind: push,                  risk: critical }
  reserved:
    - { kind: commit,  by: { all: [owner, peer] } }            # quorum: owner + a peer
    - { kind: publish, by: owner }
  prohibited: [ push, key-ops ]
  obligations: [ gates-green, clean-checkout-verified, evidence-cascade-current, attribution, no-co-authored-by ]
  redress:
    - { kind: commit, by: owner, overturn: true, within: 7d }
```

## Compiled patch — `finalise-change.lg`

See the file beside this one, produced by the canonical compiler at
`../reference/compile_block_to_lg.py` (SPEC §4) from the block above, byte for byte
(`tests/test_compile_reproduces_lg.py` proves this). Roles `owner`/`peer` compile to
declared humans; each of the block's 7 `actions[]` entries becomes its own source gate
egressing straight to `master` (no intermediate `release` gate — see SPEC §4(2)); the
per-action grades on `worktree-irreversible` and `commit` (`L3`) each carry their
`grade` line. Each of the 5 `obligations[]` entries is attached to every one of the 7
action gates (SPEC §4(3)) — not to `master` directly, since `master`'s class is not
`gate`.

## Validation result

Through the Loomground reference evaluator (parse + `check`, no `L.Reject`):
**`WELL-FORMED`**. Verdict for every one of the 7 action gates:

| action | gate risk | grade required | verdict | master |
|---|---|---|---|---|
| `read` | low | (block floor L2) | `auto` | act |
| `edit` | medium | (block floor L2) | `auto` | act |
| `run-tests` | medium | (block floor L2) | `auto` | act |
| `run-gates` | medium | (block floor L2) | `auto` | act |
| `worktree-irreversible` | high | L3 (L2 < required L3) | `human` | withhold |
| `commit` | high | L3 → also `reserved commit by owner and peer` | `reserved` | withhold |
| `push` | critical | (block floor L2) → `prohibit push` | `prohibited` | withhold |

SPEC §7 names three conformance checks the evaluator computes directly from the
compiled patch, and this table demonstrates each: (a) a below-grade action yields
`human` (`worktree-irreversible`), (b) a reserved action yields `reserved` (`commit`,
quorum), (c) a prohibited action yields `prohibited` (`push`, severed). The `auto` rows
are the baseline where none of these applies. `publish` is reserved to `owner` but is
not itself a declared `actions[]` entry (it has no source gate to evaluate a token
against), so check (b) is demonstrated by `commit`. The `human` row is the
boundary in action: a below-grade actor is withheld to a human, by declaration alone —
the same verdict an enforcer returns at the point of action. `key-ops` (prohibited,
alongside `push`) is likewise not itself a declared action; SPEC §7(d) — an unattached
obligation withholds release — is a **host** test (the evaluator does not track
obligation-attachment state; see SPEC.md §7) and is not part of this evaluator-verdict
table.
