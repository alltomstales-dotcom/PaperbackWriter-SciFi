"""Sci-fi blind reads: verify reader logs, rank the intended solution, and gate a plan read.

The reader writes log_chNN.json at each checkpoint: the premise, the rules as they
understand them, probabilities across ways the central problem might be solved, and
quoted moments of wonder, skimming and confusion. Every quote is checked by exact
string search; an invented quote voids the log.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from paperbackwriter.outline import sections

CHAPTER_FILE = re.compile(r"ch(\d+)\.txt")


def _staged_text(folder: Path) -> dict[int, str]:
    chapters: dict[int, str] = {}
    for p in sorted(folder.glob("ch*.txt")):
        m = CHAPTER_FILE.fullmatch(p.name)
        if m:
            chapters[int(m.group(1))] = p.read_text(encoding="utf-8")
    for p in sorted(folder.glob("batch*.md")):
        for n, (heading, body) in sections(p.read_text(encoding="utf-8")).items():
            chapters[n] = heading + "\n" + body
    return chapters


def _quotes(value):
    if isinstance(value, dict):
        if "quote" in value:
            yield value
        for item in value.values():
            yield from _quotes(item)
    elif isinstance(value, list):
        for item in value:
            yield from _quotes(item)


def _load(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def check_log(path: Path, finished: bool = False) -> dict:
    path = Path(path)
    data = _load(path)
    checkpoint = int(data["after_chapter"])
    chapters = _staged_text(path.parent)
    if finished:
        chapters = {n: t for n, t in chapters.items() if n <= checkpoint}
    errors = []
    if set(chapters) != set(range(1, checkpoint + 1)):
        errors.append("Staged chapters must be exactly chapters 1 through the checkpoint")
    ps = [s.get("p_solution") for s in data.get("solutions", [])]
    if not ps or not all(isinstance(p, (int, float)) and 0 <= p <= 1 for p in ps):
        errors.append("Every solution needs a p_solution between 0 and 1")
    elif abs(sum(ps) - 1) > 1e-6:
        errors.append("Solution probabilities do not sum to one")
    evidence = list(_quotes(data))
    for i, item in enumerate(evidence, 1):
        if not item.get("quote") or item["quote"] not in chapters.get(item.get("chapter"), ""):
            errors.append(f"Evidence {i}: quotation absent from cited chapter")
    return {"log": str(path), "checkpoint": checkpoint, "evidence_count": len(evidence),
            "passed": not errors, "errors": errors}


def solution_rank(log_path: Path, keys: list[str]) -> dict:
    """Find the intended solution among the reader's routes by the plan's private regex keys."""
    solutions = _load(log_path).get("solutions", [])
    matches = [i for i, s in enumerate(solutions) if any(re.search(k, s["route"], re.I) for k in keys)]
    if len(matches) > 1:
        return {"status": "ambiguous", "rank": None, "p": None, "matches": matches}
    p = solutions[matches[0]]["p_solution"] if matches else 0.0
    rank = 1 + sum(s["p_solution"] > p for s in solutions) if matches else len(solutions) + 1
    return {"status": "matched" if matches else "absent", "rank": rank, "p": p, "matches": matches}


def wonder_count(log_path: Path) -> int:
    return len(_load(log_path).get("wonder", []))
