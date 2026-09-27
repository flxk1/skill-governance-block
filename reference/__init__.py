"""reference — the canonical compiler for this spec (SPEC.md §4).

This package is the canonical reference implementation of "block -> .lg patch" for
skill-governance-block. It is a straight port of governance-layer's fixed
`compile_block_to_lg.py` (the L1 fix that removed the always-refused `release` gate),
minus governance-layer's own build/CLI/skill-registry machinery, which is out of this
spec's scope.

Canonical-compiler decision (recorded here and in README.md / SPEC.md): this copy, at
`reference/compile_block_to_lg.py`, is canonical for the spec. governance-layer is not
made to import it (that would mean editing governance-layer, which is out of this task's
territory); instead governance-layer keeps its own copy, and `tests/` in this repo proves
byte-for-byte parity between what this repo's compiler emits and the committed
`examples/finalise-change.lg`. If governance-layer's copy and this one ever diverge, this
repo's copy governs the spec's meaning.
"""
