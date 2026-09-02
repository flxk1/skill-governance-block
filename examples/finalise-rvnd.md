# Example: `finalise-rvnd`

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

## Compiled patch — `finalise-rvnd.lg`

See the file beside this one. Roles `owner`/`peer` compile to declared humans; each
`actions[]` entry becomes a source gate egressing to `master`; `worktree-irreversible`
and `commit` carry the required `grade L3`.

## Validation result

Through the Loomground reference validator: **`WELL-FORMED`** (parse + apply). Verdicts
driven through the engine — the four that give the block its meaning:

| action token | gate | verdict | release |
|---|---|---|---|
| `edit @ medium` (actor granted L2) | work | `auto` | act |
| `worktree-irreversible @ high` (L2 < required L3) | verify | `human` | withhold |
| `commit @ high` | release | `reserved` (quorum) | withhold |
| `push @ high` | — | `prohibited` (severed) | withhold |

The `human` row is the boundary in action: a below-grade actor is withheld to a human,
by declaration alone — the same verdict an enforcer returns at the point of action.
