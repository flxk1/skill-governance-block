"""compile_block_to_lg — the canonical reference compiler: a `governance` block (SPEC §2)
to a Loomground `.lg` patch (SPEC §4).

Ported from governance-layer's `src/governance_layer/compile_block_to_lg.py` (commit
26ec18d, `dbdc014 Fix L1: compile to skill-governance-block spec/SPEC.md §4 exactly (no
release gate)`), with `compile_root`/`main` dropped — those walk a `skills/*/SKILL.md`
tree that is governance-layer's concern, not this spec's. `compile_block` below is
otherwise unchanged logic: same field mapping, same line order, same obligation
placement.

SPEC §4, exactly, and nothing else:
  1. one `actor`, granted the block `grade`;
  2. one source `gate` per `actions[]` entry, carrying its `risk` and (if any) `grade`, granted to
     the actor, each with a `cord` straight to the single `master` (no intermediate gate);
  3. `reserve`/`prohibit`/`obligation`/`redress` lines from the matching fields;
  4. a `human` role for every role named in `reserved`/`redress`.
No other node or cord is emitted — in particular there is no `release` gate. An earlier version
of this compiler routed every action gate through an intermediate `gate release risk low` with no
`grant`, so `release` was always `refused` (no actor is ever granted an ungated gate) and no action
could ever reach `master act`.

Obligation placement (SPEC §3/§4(3)/§7(d)): SPEC §3 gives `obligation <id> on <gate>`, and §7(d)
requires a HOST test that an unattached obligation withholds release (see SPEC.md §7 — this is a
property of a host's release gate, never of the Loomground evaluator's verdict computation). The
reference language's own well-formedness check (`loomground.check`, "obligation on undeclared gate
<X>") requires every `obligation ... on X` to name a node whose class is `gate`; `master`'s class
is `master`, not `gate`, so `obligation <id> on master` does not parse under the reference
implementation — one line per obligation directly on `master` is not available. Each declared
obligation is instead attached to *every* action source gate for the role (one
`obligation <id> on <kind>` line per action). This is well-formed, and because every action gate
egresses straight to `master`, it still gates every path to `master`.

L0: this module only formats text; it never applies a patch. Every `.lg` MAY carry a
tool+version+input_sha256 stamp comment (see `stamp.py`), same convention as governance-layer.
"""
from __future__ import annotations

from .stamp import lg_stamp_comment


def _actor(name: str) -> str:
    return name.replace("-", "_")


def _party_names(by) -> set:
    if isinstance(by, str):
        return {by}
    if isinstance(by, dict):
        if "all" in by:
            return set(by["all"])
        if "of" in by:
            return set(by["of"])
    return set()


def _by_syntax(by) -> str:
    if isinstance(by, str):
        return by
    if "all" in by:
        return " and ".join(by["all"])
    if "of" in by:
        return f"{by['quorum']} of {{ {', '.join(by['of'])} }}"
    return "owner"


def compile_block(name: str, block: dict, input_sha256: str = "") -> str:
    actor = _actor(name)
    parties = set()
    for r in block.get("reserved", []) or []:
        parties |= _party_names(r["by"])
    for r in block.get("redress", []) or []:
        parties |= _party_names(r["by"])

    L = [f"# {name}.lg — compiled from the governance block (SPEC §4). Generated; do not edit by hand."]
    if input_sha256:
        L.append(lg_stamp_comment(input_sha256))
    for p in sorted(parties):
        L.append(f"human {p} role {p}")
    L.append(f"actor {actor} grade {block['grade']}")
    L.append("")
    # SPEC §4(2): one source gate per action, granted to the actor, egressing straight to master.
    for a in block["actions"]:
        g = f" grade {a['grade']}" if a.get("grade") else ""
        L.append(f"gate {a['kind']} risk {a['risk']}{g} grant {actor}")
    L.append("")
    for a in block["actions"]:
        L.append(f"cord {actor} -> {a['kind']}")
    for a in block["actions"]:
        L.append(f"cord {a['kind']} -> master")
    L.append("")
    for k in block.get("prohibited", []) or []:
        L.append(f"prohibit {k}")
    for r in block.get("reserved", []) or []:
        L.append(f"reserve {r['kind']} by {_by_syntax(r['by'])}")
    # SPEC §4(3): the reference language rejects `obligation ... on master` (master is not a
    # `gate`), so each obligation is attached to every action source gate instead (see module
    # docstring). One `obligation <id> on <kind>` line per (obligation, action) pair.
    for o in block.get("obligations", []) or []:
        for a in block["actions"]:
            L.append(f"obligation {o} on {a['kind']}")
    for r in block.get("redress", []) or []:
        s = f"redress {r['kind']} by {r['by'] if isinstance(r['by'], str) else _by_syntax(r['by'])}"
        if r.get("overturn"):
            s += " overturn"
        if r.get("within"):
            s += f" within {r['within']}"
        L.append(s)
    return "\n".join(L) + "\n"
