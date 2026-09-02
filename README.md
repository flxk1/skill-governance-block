# skill-governance-block

A **vendor-neutral** spec: a skill declares its own governance boundary in its manifest,
so *what a skill does* and *what it may do* are authored once. An **orchestrator** reads
the block to plan before dispatch; a **governance tool** enforces it at the point of
action. The declaration is a frontmatter *binding* of the **Loomground governance
language**, and a block is valid iff it compiles to a well-formed Loomground patch.

The spec names no product. Orchestrators, governance tools, agent runtimes, and hosts
are *implementations* of this contract — collected in `bindings/`, one each, never the
contract itself.

## Contents

- **`SPEC.md`** — the normative, vendor-neutral spec: the `governance` block, its
  mapping to Loomground declarations, the litmus (language / policy / host), the
  compilation, validation, and the reader/enforcer conformance contract.
- **`schema/governance-block.schema.json`** — machine schema for the block's *shape*
  (a pre-check; the authoritative check is compile-and-validate against the Loomground
  standard).
- **`examples/`** — `finalise-rvnd`: a block, its compiled `.lg`, and the validated
  result (`WELL-FORMED`, four verdicts confirmed); plus `registration.md`, deriving the
  fleet-registry row + one-page brief from the same block (the loop closed — one
  declaration ⇒ plan + enforced verdict + fleet record).
- **`bindings/claude-code.md`** — one concrete, non-normative binding (a skill's YAML
  frontmatter → a specific orchestrator's plan-time reader → a specific governance
  tool's action-time hook).

## Status

`v0.1`, draft.

## License

Apache-2.0 (see [LICENSE](LICENSE)). Copyright 2026 flxk1.

## Validate a block

1. Shape check: validate the `governance` mapping against
   `schema/governance-block.schema.json`.
2. Authoritative check: compile the block to a Loomground `.lg` patch and run it through
   the governance language's reference validator — the block is valid iff the patch is
   `WELL-FORMED`.
