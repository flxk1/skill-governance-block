"""Evaluator-backed check of `examples/finalise-change.lg` against a real Loomground
reference implementation. Runs (not skips) whenever
`SKILL_GOVERNANCE_BLOCK_LOOMGROUND_REF` names a directory holding `loomground.py` — no
reference implementation is vendored into this repo, so CI without the env var set will
skip these, but any run that sets it must see them pass, not silently skip.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_LG = REPO_ROOT / "examples" / "finalise-change.lg"

EXPECTED_VERDICTS = {
    "read": ("auto", "act"),
    "edit": ("auto", "act"),
    "run-tests": ("auto", "act"),
    "run-gates": ("auto", "act"),
    "worktree-irreversible": ("human", "withhold"),
    "commit": ("reserved", "withhold"),
    "push": ("prohibited", "withhold"),
}

RISK_BY_KIND = {
    "read": "low",
    "edit": "medium",
    "run-tests": "medium",
    "run-gates": "medium",
    "worktree-irreversible": "high",
    "commit": "high",
    "push": "critical",
}


def _load_loomground_ref():
    ref_dir = os.environ.get("SKILL_GOVERNANCE_BLOCK_LOOMGROUND_REF")
    if not ref_dir:
        return None
    lg_py = Path(ref_dir) / "loomground.py"
    if not lg_py.is_file():
        raise RuntimeError(
            f"SKILL_GOVERNANCE_BLOCK_LOOMGROUND_REF={ref_dir!r} has no loomground.py"
        )
    spec = importlib.util.spec_from_file_location("loomground_ref_sgb", lg_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["loomground_ref_sgb"] = mod
    spec.loader.exec_module(mod)
    return mod


LOOMGROUND_REF = _load_loomground_ref()

pytestmark = pytest.mark.skipif(
    LOOMGROUND_REF is None,
    reason="SKILL_GOVERNANCE_BLOCK_LOOMGROUND_REF not set to a checkout with loomground.py",
)


def test_example_patch_is_well_formed():
    L = LOOMGROUND_REF
    text = EXAMPLE_LG.read_text(encoding="utf-8")
    graph = L.check(L.parse(text))  # raises L.Reject if not well-formed
    assert graph is not None


def test_example_verdict_table_matches_spec_7_meaning():
    L = LOOMGROUND_REF
    text = EXAMPLE_LG.read_text(encoding="utf-8")
    graph = L.check(L.parse(text))
    for kind, (want_verdict, want_master) in EXPECTED_VERDICTS.items():
        tok = dict(id="t1", kind=kind, risk=RISK_BY_KIND[kind], party="deployer", provenance=[])
        res, _ = L.evaluate(graph, [dict(actor="finalise_change", source=kind, token=tok)])
        assert res[kind]["verdict"] == want_verdict, (kind, res[kind])
        assert res[kind].get("master") == want_master, (kind, res[kind])
