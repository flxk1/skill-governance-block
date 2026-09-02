# Skill Governance Block — specification (v0.1, draft)

A **vendor-neutral** way for a skill to declare its own governance boundary in its
manifest, so that *what a skill does* and *what it is allowed to do* are authored
once, in one place. The declaration is read by an **orchestrator** to plan before it
dispatches the skill, and enforced by a **governance tool** at the point of action.
This document defines the declaration and its meaning; it names no orchestrator,
governance tool, agent runtime, or host — those are implementations of this contract,
listed only in a binding appendix.

The boundary is expressed as a *binding* of the **Loomground governance language**
(the `.lg` policy-graph standard: `actor`/`human`/`gate`/`master` nodes, the five
verdicts, and the nine declarations). This document borrows that vocabulary and adds
nothing to it; a block is *valid* iff it compiles to a well-formed Loomground patch.

> **Non-normative note.** Declaring a measure here does not by itself satisfy any
> legal or regulatory obligation. Conformance is a property of an implementation,
> not a finding of compliance.

---

## 1. Scope and neutrality

- **In scope:** the shape of the `governance` block, the meaning of each field as a
  Loomground declaration, the litmus that decides what may appear in it, and the
  contract a conforming **reader** (plan-time) and **enforcer** (action-time) MUST
  honor.
- **Out of scope, by construction:** *how* a runtime computes a metric, counts,
  schedules, watermarks, persists, or communicates — those are host concerns and are
  never expressible in the block (see §5). Also out of scope: the manifest format a
  host happens to use (YAML frontmatter, JSON, TOML) — the block is a data shape, not
  a syntax.
- **Neutral by design.** The normative text (§§2–7) names no product. Concrete
  bindings — a specific manifest format, a specific orchestrator's reader, a specific
  governance tool's enforcement — live in `bindings/` as one implementation each of
  this contract, never as the contract itself.

Two roles consume a block:

| role | when | obligation (§7) |
|---|---|---|
| **reader** | before the skill is dispatched | plan on the block: surface grade gaps up front, gate reserved actions, exclude prohibited, carry obligations as accept-criteria, cap budget |
| **enforcer** | at each governed action | return a Loomground verdict for the action, from the same declaration |

A reader and an enforcer that consume the same block cannot disagree, because there is
one declaration.

Beyond these two live roles, a block also **derives** a static fleet-governance record —
an append-only registry row and a one-page brief for anything that acts without per-step
approval — because `grade`, `prohibited`, `reserved`, and `budget` are exactly the fields
such a record needs, and a worst-case ("3am") analysis is then a *reading* of the
`prohibited`/`reserved`/`grade` lines rather than a hopeful assurance. This derivation is
non-normative (an operator's fleet convention, not part of the contract); see
`examples/registration.md`.

---

## 2. The `governance` block

A skill's manifest MAY carry a `governance` mapping. All fields are OPTIONAL; a skill
with no block is governed only by the host's ambient policy. Field types:

```
governance:
  grade:        <grade-id>                 # floor autonomy grade to run unattended
  actions:      [ <action> ]               # the action-classes this skill performs
  reserved:     [ <reservation> ]          # actions referred to a human
  prohibited:   [ <kind> ]                 # actions this skill must never take
  obligations:  [ <obligation-id> ]        # must be attached before release
  redress:      [ <redress> ]              # a released action is contestable
  budget:       { <resource>: <number> }   # a ceiling on the run
  on-boundary:  <string>                   # OPTIONAL implementation hint (non-normative)
```

- **`grade`** — a `<grade-id>` (e.g. `L2`) from an ordered autonomy ladder. The floor
  the skill requires to run without a human in the loop. The ladder itself is
  **policy** (§5), not fixed here.
- **`actions[]`** — one entry per action-class the skill performs:
  `{ kind: <kind>, risk: low|medium|high|critical, grade?: <grade-id> }`. `kind` is a
  declared category (not a free computed value). `grade` overrides the block floor for
  that action-class only (e.g. an irreversible action requiring a higher grade).
- **`reserved[]`** — `{ kind: <kind>, by: <target> }`. `target` is a `<role>`, a
  conjunction `{ all: [<role>, <role>] }`, or a quorum `{ quorum: <m>, of: [<role>…] }`
  — a quorum requires **distinct parties** (separation of duty).
- **`prohibited[]`** — `<kind>` values the skill must never take; enforcement severs
  them and this overrides any grant.
- **`obligations[]`** — `<obligation-id>` values that MUST be *attached* before the
  action is released. Declaring the obligation is in scope; *attaching* its evidence
  is a host concern (§5).
- **`redress[]`** — `{ kind: <kind>, by: <role>, overturn?: <bool>, within?: <duration> }`.
  Marks a released action as contestable.
- **`budget`** — a mapping of resource → ceiling (e.g. `{ usd: 5, iters: 40 }`). The
  resources and their accounting are **host** (§5); the block only states the ceiling.

A guard on any field may range only over `kind`, `risk`, `party`, and declared `tags`
— never over an identifier, a provenance value, a grade, or any computed quantity.

---

## 3. Mapping to the Loomground governance language

Each field projects to exactly one Loomground declaration. This is the whole meaning
of the block — there is no behavior here that is not a Loomground declaration.

| block field | Loomground declaration |
|---|---|
| `grade`, `actions[].grade` | `grade <Lk>` — required on the action's source gate |
| `actions[].kind` / `.risk` | the gate the action flows through: `gate … risk <r>` + guard categories |
| `reserved[]` | `reserve <kind> by <target>` (`<m> of {roles}` / `role and role` = quorum) |
| `prohibited[]` | `prohibit <kind>` (severed; overrides grants) |
| `obligations[]` | `obligation <id> on <gate>` |
| `redress[]` | `redress <kind> by <role> [overturn] [within <duration>]` |

The verdicts that result are Loomground's, joined strictest-wins: `prohibited` (severed)
> `refused` (no grant) > `reserved` (referred to a human) > `human` (grade withheld) >
`auto`. A release point acts only when the effective verdict is `auto` **and** every
declared obligation is attached.

---

## 4. Compilation

A block compiles to a Loomground `.lg` patch:

1. one `actor` for the skill, granted the block `grade`;
2. one source `gate` per `actions[]` entry, carrying its `risk` and (if any) required
   `grade`, granted to the actor, each egressing to the single `master`;
3. `reserve` / `prohibit` / `obligation` / `redress` lines from the matching fields;
4. `human` roles for every role named in `reserved`/`redress`.

The compilation is mechanical and total: every field above has exactly one target line,
and no field introduces a node or cord that is not one of the above.

---

## 5. The litmus — what may appear in a block

For each requirement a skill wants to encode:

- **language** — a standard/regulation *names* it as a declaration (reserve to a human,
  prohibit a practice, require a quorum, attach a disclosure obligation, make an action
  contestable, require an autonomy grade). → it belongs in the block.
- **policy** — a deployment *chooses a value* (which kinds are reserved, the grade
  ladder, the risk thresholds, the budget numbers). → the block may carry the *choice*,
  but the *scale/threshold definitions* are the deployment's, not fixed by this spec.
- **host** — a runtime *does* it: compute or count, compare to a threshold, measure
  elapsed time, watermark, persist, inspect a payload, *attach* an obligation's
  evidence, account a budget, or communicate. → **not expressible**; it is the host's
  job. The block *declares* the obligation; the host *attaches* it.

If a requirement needs a computed value, it is a host concern and MUST NOT be forced
into a guard.

---

## 6. Validation

A block is **valid** iff its compiled `.lg` patch is **well-formed** under the
Loomground standard — it passes the standard's parse and apply stages and its structure
matches the standard's schemas. Implementations SHOULD validate by compiling the block
and running it through the standard's own checker (a reference validator ships with the
governance language). A block whose compiled patch is rejected is invalid, whatever its
surface shape.

Machine schema for the block's *shape* (a pre-check before compilation) is
`schema/governance-block.schema.json`. Passing the JSON Schema is necessary but not
sufficient; the compile-and-validate step is authoritative.

---

## 7. Consumer contract (conformance)

An implementation is block-conforming for a role iff:

**Reader (plan-time)** — before dispatching a skill, it:
1. computes `need = max(grade, actions[].grade)` and, if `need` exceeds the granted
   autonomy grade, **surfaces the gap and does not silently dispatch** into it;
2. routes every `reserved` action to its human `target` (a `hold`), never auto;
3. excludes every `prohibited` kind from the plan, withholding the capability where
   the host allows (so it cannot be proposed, not merely refused);
4. carries every `obligations` entry as an accept-criterion the release must meet;
5. caps the run at `budget`.

**Enforcer (action-time)** — for each governed action it returns a Loomground verdict
computed from the compiled patch, with `unavailable`/unknown flooring to the
weaker-safer path (never a false `auto`), and it declares its honest enforcement tier
to the caller.

A conforming implementation MUST carry a load-bearing test proving that (a) a
below-grade action yields `human`, (b) a reserved action yields `reserved`, (c) a
prohibited action yields `prohibited`, and (d) an unattached obligation withholds
release — the four verdicts that give the block its meaning.

---

## 8. Versioning

This spec is `v0.1` (draft). The block's field set is additive: a reader MUST ignore
unknown `governance` fields (forward-compatibility), and MUST NOT treat an absent block
as permission. The Loomground language version a block targets is the standard's, not
this document's.
