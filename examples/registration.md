# Example: governance block ⇒ agent-registry row + brief

Closing the loop. A boundaried skill's `governance` block is not only read at plan time
(orchestrator) and enforced at action time (governance tool) — it also **derives the
skill's fleet-governance record**: the append-only registry row and the one-page brief an
operator keeps for anything that can act without per-step approval. The row/brief format
below is the `agent-governance-registry` convention (autonomy-grades pattern); any fleet
registry is one consumer of the same block.

> This is a **derivation example**, not a live-fleet registration. `finalise-rvnd` here is
> the spec's worked example, not a deployed agent — so it is shown as the record an
> operator *would* append when they actually deploy it, not inserted into a live
> `agent-registry.md`.

## The row (derived from the block)

```
| id            | name          | purpose                                                                 | grade | owner        | kill-switch                                                   | last-reviewed |
| finalise-rvnd | Finalise RVND | complete/verify/stage a change to clean-checkout-green; coordinate peers before commit; never push | L2    | Felix (flxk1) | floor the grant (unset RVND_AUTONOMY_GRADE) ⇒ consequential acts hold; PreToolUse `deny` below required grade | (not deployed) |
```

Field derivation — every column comes from the block, nothing invented:

| row column | from the block |
|---|---|
| `grade` | `grade: L2` (the floor; per-action L3 raises specific acts) |
| `purpose` | the skill's own description |
| `kill-switch` | the enforcer's grade gate: drop the granted grade → below-required acts floor to `human` (`prohibited`/`reserved` already sever/withhold regardless) |
| the brief's caps | `budget: { usd: 6, iters: 60 }` |

## The one-page brief

```markdown
# Finalise RVND

**ID:** finalise-rvnd
**Owner:** Felix (flxk1)
**Autonomy grade:** L2 — drafts/edits/tests unattended; consequential acts held to a human
**Last reviewed:** (not deployed)

## Purpose
Bring a change in a repository to a clean-checkout-green state (edit, run the test/lint/gate
suite, regenerate any evidence), coordinate peers before committing, stage locally. It never
publishes and never pushes.

## Scope
**In scope:** read, edit, run tests/gates, stage, and — held to a human — commit.
**Out of scope (and why):** push (prohibited — nothing leaves the machine autonomously);
key operations (prohibited); publishing (reserved to the owner).

## Trigger
Manual (a person asks it to finalise a change). No cron, no file watch.

## Inputs
Read-write within the target repository's working tree; read-only elsewhere.

## Outputs
Local commits on a branch and staged changes. **No** push, **no** publish, **no** external call.

## Failure modes
1. *Over-broad edit* — edits outside the intended change. Symptom: unexpected diff. Blast
   radius: local working tree only. Notices: the pre-commit diff review + peer coordination.
2. *Repeated commits* — loops committing. Symptom: many local commits. Blast radius: local
   branch only (no push). Notices: `git log` / the iters budget cap (60).
3. *Grade over-grant* — run at a grade above L2, bypassing the human hold on commit. Symptom:
   auto-commit without peer clearance. Blast radius: local commits; still no push (prohibited).
   Notices: the audit chain + the missing peer-clearance record.

### Worst-case at 3am
Running amok at 3am, the **block bounds the blast radius by construction**: `push` and
`key-ops` are `prohibited` (severed — nothing reaches any remote or key material), `commit`
and `publish` are `reserved` (withheld to a human/quorum), and the irreversible
clean-checkout verify requires grade **L3** (a granted-L2 actor is floored to `human`). The
worst it can do unattended is churn **local** commits on a branch in one repo — recoverable,
never published, never pushed. The 3am answer is acceptable *because* the boundary is
declared, not because the skill is trusted.

## Kill switch
Drop the granted autonomy grade (unset `RVND_AUTONOMY_GRADE`, or set it below L2): every
consequential action then floors to `human` at the PreToolUse enforcer. `prohibited` and
`reserved` acts are severed/withheld regardless of grade. **Tested:** not yet exercised —
must be exercised before this skill is registered above L0 in a live fleet.

## Budget caps
`max_cost_usd: 6`, `max_iterations: 60`. (From `budget` in the block.)

## Audit trail
The governance tool's signed chain (per-action verdict) + the run's own log.

## Promotion criteria
L2 → L3 (per autonomy-grades): ≥4 clean cycles at L2 with <20% rework, a tested notification
path, an exercised revocation, two kill switches in different layers, a per-day spend ceiling.
Only then could the L3-gated irreversible verify run unattended.

## Review cadence
90-day. Next review: (set at deployment).
```

## Why this is the loop closed

The same declaration produces three artifacts — a **plan** (orchestrator), an **enforced
verdict** (governance tool), and this **fleet record** (registry). The 3am paragraph is not a
hopeful assurance; it is a reading of the `prohibited` / `reserved` / `grade` lines. Change the
block and all three change together.
