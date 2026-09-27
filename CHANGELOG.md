# Changelog

## Unreleased

- Layout: `SPEC.md` moved to `spec/SPEC.md`; bare `LICENSE` replaced by `LICENSES/Apache-2.0.txt` + `NOTICE` + `REUSE.toml`; added `CHANGELOG.md` and a CI workflow that validates the schema against the examples.
- Fix: SPEC §3 join order corrected to `prohibited > reserved > refused > human > auto` (was stated with `reserved`/`refused` swapped).
- SPEC §4: obligation placement wording now matches the compiler's actual placement (attached to every action source gate, never to `master`), and SPEC §7(d) ("unattached obligation withholds release") is now stated explicitly as a **host** test, not a claim about the Loomground evaluator.
- Added `reference/compile_block_to_lg.py` — the canonical reference compiler for SPEC §4 (ported from `governance-layer`'s fixed compiler); added `pyproject.toml` and `tests/` (byte-parity, join-order, evaluator-backed verdict checks).
- Regenerated `examples/finalise-change.lg` with the canonical compiler to match `examples/finalise-change.md`'s block exactly: 7 action gates (was 3, via an intermediate `work`/`verify`/`release` shape that predates the L1 fix), per-action grades, `reserve publish`, the single spelling `key-ops` (was inconsistently `key_ops` in the `.lg`), and consistent `owner`/`peer` role names (was `owner_role`/`peer_role`).
