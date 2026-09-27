"""Minimal stamp helper, ported from governance-layer's `stamp.py` (the two functions
`compile_block_to_lg.py` actually uses). Not the full toolchain-brief module — this
repo has no build/CLI/report surface to stamp; it exists only so the ported compiler
below is a faithful, runnable copy of governance-layer's fixed compiler.
"""
from __future__ import annotations

import hashlib

TOOL = "skill-governance-block-reference"
VERSION = "0.1.0"


def sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def lg_stamp_comment(input_sha256: str) -> str:
    """Stamp comment for a compiled `.lg` (`#` line comment)."""
    return f"# stamped: tool={TOOL} version={VERSION} input_sha256={input_sha256}"
