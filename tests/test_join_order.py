"""SPEC §3: the verdict join order is `prohibited > reserved > refused > human > auto`,
strictest-wins, and this is the only order stated anywhere in the repo. If a doc drifts
to a different order (e.g. swapping `reserved`/`refused`), this test must fail.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_ORDER = ["prohibited", "reserved", "refused", "human", "auto"]

# Any file that states the five verdicts in join-order form, e.g.
# "`prohibited` ... > `reserved` ... > `refused` ... > `human` ... > `auto`".
JOIN_ORDER_RE = re.compile(
    r"`prohibited`.*?>\s*`reserved`.*?>\s*`refused`.*?>\s*`human`.*?>\s*`auto`",
    re.S,
)

# The five verdict tokens appearing in *some* order, each `>`-joined, used to catch a
# drifted order the canonical regex above would not match. `.` (not `[^`]`) so a token's
# parenthetical may wrap onto the next line, but bounded so it cannot skip past the next
# backtick-quoted verdict token.
ANY_JOIN_RE = re.compile(
    r"`(prohibited|reserved|refused|human|auto)`(?:(?!`).)*?>\s*"
    r"`(prohibited|reserved|refused|human|auto)`(?:(?!`).)*?>\s*"
    r"`(prohibited|reserved|refused|human|auto)`(?:(?!`).)*?>\s*"
    r"`(prohibited|reserved|refused|human|auto)`(?:(?!`).)*?>\s*"
    r"`(prohibited|reserved|refused|human|auto)`",
    re.S,
)

TEXT_GLOBS = ["*.md", "**/*.md", "*.txt", "**/*.txt"]


def _all_text_files():
    seen = set()
    for pattern in TEXT_GLOBS:
        for p in REPO_ROOT.glob(pattern):
            if p.is_file() and ".git" not in p.parts and p not in seen:
                seen.add(p)
                yield p


def test_spec_states_the_canonical_join_order():
    spec_text = (REPO_ROOT / "spec" / "SPEC.md").read_text(encoding="utf-8")
    assert JOIN_ORDER_RE.search(spec_text), (
        "spec/SPEC.md does not state the join order "
        "prohibited > reserved > refused > human > auto"
    )


def test_no_file_states_a_different_join_order():
    offenders = []
    for path in _all_text_files():
        text = path.read_text(encoding="utf-8")
        for m in ANY_JOIN_RE.finditer(text):
            order = list(m.groups())
            if order != CANONICAL_ORDER:
                offenders.append((path, order))
    assert not offenders, f"non-canonical join order found: {offenders}"
