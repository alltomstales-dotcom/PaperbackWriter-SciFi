"""Sci-fi blind reads: verify reader logs, rank the intended solution, and gate a plan read.

The reader writes log_chNN.json at each checkpoint: the premise, the rules as they
understand them, probabilities across ways the central problem might be solved, and
quoted moments of wonder, skimming and confusion. Every quote is checked by exact
string search; an invented quote voids the log.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

from paperbackwriter.outline import checkpoints, sections

from .rules import parse_rules

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



def clarity(grade_path: Path, rule_ids: list[str]) -> dict:
    """Score a grader's verdict on the reader's premise and rules. A rule the grader left out is missing."""
    grade = _load(grade_path)
    verdicts = {r["id"]: r["verdict"] for r in grade.get("rules", [])}
    stated = [r for r in rule_ids if verdicts.get(r) == "stated"]
    wrong = [r for r in rule_ids if verdicts.get(r) == "wrong"]
    missing = [r for r in rule_ids if r not in stated and r not in wrong]
    passed = bool(grade.get("premise_correct")) and not wrong and len(stated) * 3 >= len(rule_ids) * 2
    return {"passed": passed, "premise_correct": bool(grade.get("premise_correct")),
            "stated": stated, "missing": missing, "wrong": wrong}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def advance_plan_read(reference: Path, gate_path: Path, checkpoint: int, n_chapters: int = 24) -> dict:
    """Score one plan-read checkpoint; release the next digest batch only on a pass.

    Checkpoint 1: clarity (needs grade_chNN.json from a grader agent).
    Checkpoint 2: the intended solution is not ranked first.
    Checkpoint 3: the intended solution is at .35 or less.
    Later checkpoints record the numbers and always pass.
    """
    reference, gate_path = Path(reference), Path(gate_path)
    points = checkpoints(n_chapters)
    if checkpoint not in points:
        raise ValueError(f"checkpoint must be one of {points}")
    ref = _load(reference)
    candidate = (reference.parent / ref["candidate_directory"]).resolve()
    folder = (reference.parent / ref["reader_folder"]).resolve()
    for name, h in ref["plan_sha256"].items():
        if _sha(candidate / name) != h:
            raise ValueError(f"plan file changed since the reference was written: {name}")
    for name, h in ref["digest_sha256"].items():
        if _sha(candidate / "digest" / name) != h or ((folder / name).exists() and _sha(folder / name) != h):
            raise ValueError(f"digest batch changed since the reference was written: {name}")
    log_path = folder / f"log_ch{checkpoint:02d}.json"
    checked = check_log(log_path)
    if not checked["passed"]:
        raise ValueError(f"log failed verification: {checked['errors']}")
    index = points.index(checkpoint)
    rank = solution_rank(log_path, ref["solution_keys"])
    if rank["status"] == "ambiguous":
        resolved = folder / f"rank_ch{checkpoint:02d}.json"
        if not resolved.exists():
            raise ValueError(f"solution keys match routes {rank['matches']}; a grader must write {resolved.name}")
        chosen = _load(resolved)["route_index"]
        solutions = _load(log_path)["solutions"]
        p = solutions[chosen]["p_solution"] if chosen is not None else 0.0
        rank = {"status": "resolved", "p": p, "matches": [chosen] if chosen is not None else [],
                "rank": 1 + sum(s["p_solution"] > p for s in solutions) if chosen is not None else len(solutions) + 1}
    record = {"checkpoint": checkpoint, "rank": rank["rank"], "probability": rank["p"],
              "match": rank["status"], "exact_quotes": checked["evidence_count"]}
    if index == 0:
        grade = folder / f"grade_ch{checkpoint:02d}.json"
        if not grade.exists():
            raise ValueError(f"clarity gate needs {grade.name} from a grader agent")
        rules = parse_rules((candidate / "02b_rules_and_clues.md").read_text(encoding="utf-8"))
        due = [r.id for r in rules.values() if 0 < r.chapter <= checkpoint]
        record["clarity"] = clarity(grade, due)
        passed = record["clarity"]["passed"]
    elif index == 1:
        passed = rank["rank"] > 1
    elif index == 2:
        passed = rank["p"] <= 0.35
    else:
        passed = True
    record["passed"] = passed
    gate = _load(gate_path)
    if len(gate["checkpoints"]) != index:
        raise ValueError("checkpoints must be scored in order")
    gate["checkpoints"].append(record)
    gate["gate_passed"] = len(gate["checkpoints"]) >= 3 and all(r["passed"] for r in gate["checkpoints"][:3])
    if not passed:
        gate["stage"] = f"FAILED_AT_{checkpoint}"
    elif checkpoint < points[-1]:
        name = f"batch{index + 2}.md"
        if (folder / name).exists():
            raise ValueError("next batch was already released")
        shutil.copy2(candidate / "digest" / name, folder / name)
        record["released_through"] = points[index + 1]
        gate["stage"] = "EARLY_GATE_PASSED" if gate["gate_passed"] else "RUNNING"
    else:
        gate["stage"] = "READ_COMPLETE"
    gate_path.write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
    return record
