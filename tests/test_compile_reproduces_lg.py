"""Compiling `examples/finalise-change.md`'s `governance:` block with the canonical
reference compiler (`reference/compile_block_to_lg.py`, SPEC §4) must reproduce the
committed `examples/finalise-change.lg` byte for byte. If this test fails, either the
compiler drifted from SPEC §4 or the committed `.lg` was hand-edited out of sync with
the block it was compiled from.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from reference.compile_block_to_lg import compile_block

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_MD = REPO_ROOT / "examples" / "finalise-change.md"
EXAMPLE_LG = REPO_ROOT / "examples" / "finalise-change.lg"


def _extract_block(md_text: str) -> dict:
    start = md_text.find("```yaml\n")
    assert start != -1, "no ```yaml fenced block found in finalise-change.md"
    start += len("```yaml\n")
    end = md_text.find("```", start)
    assert end != -1, "unterminated ```yaml fenced block in finalise-change.md"
    doc = yaml.safe_load(md_text[start:end])
    return doc["governance"]


def test_compiled_block_matches_committed_lg_byte_for_byte():
    md_text = EXAMPLE_MD.read_text(encoding="utf-8")
    block = _extract_block(md_text)
    compiled = compile_block("finalise-change", block)
    committed = EXAMPLE_LG.read_text(encoding="utf-8")
    assert compiled == committed


def test_example_block_has_seven_action_gates_and_reserve_publish():
    md_text = EXAMPLE_MD.read_text(encoding="utf-8")
    block = _extract_block(md_text)
    assert len(block["actions"]) == 7
    kinds = [a["kind"] for a in block["actions"]]
    assert kinds == ["read", "edit", "run-tests", "run-gates",
                      "worktree-irreversible", "commit", "push"]
    graded = {a["kind"]: a.get("grade") for a in block["actions"] if a.get("grade")}
    assert graded == {"worktree-irreversible": "L3", "commit": "L3"}
    reserved_kinds = {r["kind"] for r in block["reserved"]}
    assert "publish" in reserved_kinds
    committed = EXAMPLE_LG.read_text(encoding="utf-8")
    assert "reserve publish by owner" in committed
    assert committed.count("gate ") == 7  # exactly one source gate per action


def test_example_uses_one_consistent_key_ops_spelling():
    md_text = EXAMPLE_MD.read_text(encoding="utf-8")
    committed = EXAMPLE_LG.read_text(encoding="utf-8")
    assert "key_ops" not in md_text and "key_ops" not in committed
    assert "key-ops" in md_text
    assert "prohibit key-ops" in committed


def test_example_owner_roles_consistent():
    committed = EXAMPLE_LG.read_text(encoding="utf-8")
    # a single spelling for the owner role throughout the compiled patch, matching the
    # block's `by: owner` / `by: { all: [owner, peer] }` (not "owner_role").
    assert "human owner role owner" in committed
    assert "owner_role" not in committed
    assert "reserve commit by owner and peer" in committed
    assert "reserve publish by owner" in committed
    assert "redress commit by owner overturn within 7d" in committed
