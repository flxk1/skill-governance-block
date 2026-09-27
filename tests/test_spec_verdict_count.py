"""SPEC §7 names exactly how many conformance checks the Loomground evaluator computes
directly from the compiled patch; the unattached-obligation case is a **host** test.
No tracked file may state a different count of meaning-giving / conformance verdicts
(e.g. the retired "four meaning-giving verdicts confirmed by the engine" phrasing).

The count is derived from SPEC §7 itself, never hard-coded. Counts equal to the size of
the SPEC §3 verdict vocabulary (the full join order) are that vocabulary, not a §7
conformance count, and are allowed.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "spec" / "SPEC.md"
THIS_FILE = Path(__file__).resolve()

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
ORDINALS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
}

# Retired phrasings that assert a fourth engine-confirmed verdict. Matched
# case-insensitively with any run of whitespace (including line breaks) between words.
FORBIDDEN_PHRASES = [
    "four verdicts",
    "four meaning-giving verdicts",
    "fourth conformance verdict",
    "Four of these give the block its meaning",
]

_NUM = "|".join(list(NUMBER_WORDS) + [r"\d+"])
# "<number> [up to two qualifier words] verdicts", e.g. "four meaning-giving verdicts",
# "three evaluator-computed verdicts", "5 verdicts".
COUNT_RE = re.compile(
    rf"\b({_NUM})\b(?:\s+[A-Za-z][\w-]*){{0,2}}?\s+verdicts\b", re.I
)
# "<ordinal> [qualifier] conformance verdict", e.g. "fourth conformance verdict".
ORDINAL_RE = re.compile(
    rf"\b({'|'.join(ORDINALS)})\b(?:\s+[A-Za-z][\w-]*)?\s+conformance\s+verdicts?\b", re.I
)


def _section(text: str, number: int) -> str:
    m = re.search(rf"^## {number}\..*?(?=^## \d+\.|\Z)", text, re.S | re.M)
    assert m, f"SPEC §{number} not found"
    return m.group(0)


def _to_int(token: str) -> int:
    token = token.lower()
    return int(token) if token.isdigit() else NUMBER_WORDS[token]


def spec_evaluator_count() -> int:
    """Number of evaluator-computed checks SPEC §7 names.

    Derived twice from §7 and cross-checked: the lettered items in the "MUST carry a
    load-bearing test proving ..." sentence, and the stated number in "the <n> verdicts
    the evaluator computes".
    """
    sec = _section(SPEC.read_text(encoding="utf-8"), 7)
    m = re.search(
        r"MUST carry a load-bearing test proving(.*?)the\s+(\w+)\s+verdicts\s+the\s+"
        r"evaluator\s+computes",
        sec,
        re.S,
    )
    assert m, "SPEC §7 no longer states the evaluator-computed verdict checks"
    lettered = re.findall(r"\(([a-z])\)", m.group(1))
    stated = _to_int(m.group(2))
    assert len(lettered) == stated, (lettered, stated)
    # And the unattached-obligation case is a host test, not an evaluator verdict.
    assert re.search(r"\*\*host\*\*\s+test\s+proving\s*\n?\s*\([a-z]\)\s+an\s+unattached", sec), (
        "SPEC §7 no longer marks the unattached-obligation case as a host test"
    )
    return stated


def spec_vocabulary_count() -> int:
    """Number of verdicts in the SPEC §3 join order (the language's full vocabulary)."""
    sec = _section(SPEC.read_text(encoding="utf-8"), 3)
    m = re.search(r"joined strictest-wins:(.*?)\.\s*A release point", sec, re.S)
    assert m, "SPEC §3 join order not found"
    return len(re.findall(r"`(\w+)`", m.group(1)))


def _tracked_text_files():
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=REPO_ROOT, capture_output=True, check=True
    ).stdout.decode()
    for rel in filter(None, out.split("\0")):
        p = REPO_ROOT / rel
        if not p.is_file() or p.resolve() == THIS_FILE:
            continue
        data = p.read_bytes()
        if b"\0" in data[:8192]:
            continue  # binary
        try:
            yield rel, data.decode("utf-8")
        except UnicodeDecodeError:
            continue


def _line(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def test_spec_7_names_evaluator_count_and_host_test():
    assert spec_evaluator_count() > 0


def test_no_tracked_file_states_a_different_verdict_count():
    want = spec_evaluator_count()
    vocabulary = spec_vocabulary_count()
    offenders = []
    for rel, text in _tracked_text_files():
        for phrase in FORBIDDEN_PHRASES:
            if re.search(r"\s+".join(map(re.escape, phrase.split())), text, re.I):
                offenders.append(f"{rel}: forbidden phrase {phrase!r}")
        for m in COUNT_RE.finditer(text):
            n = _to_int(m.group(1))
            if n not in (want, vocabulary):
                offenders.append(f"{rel}:{_line(text, m.start())}: {m.group(0)!r} (SPEC §7: {want})")
        for m in ORDINAL_RE.finditer(text):
            if ORDINALS[m.group(1).lower()] > want:
                offenders.append(f"{rel}:{_line(text, m.start())}: {m.group(0)!r} (SPEC §7: {want})")
    assert not offenders, "verdict count drifts from SPEC §7:\n" + "\n".join(offenders)
