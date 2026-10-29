"""The world's rules list, and the fair-play check on the solution.

Rules live in a Markdown table, one per row: | R7 | rule text | ch 5 |. The third column
is the chapter where the rule first appears on the page ("ch 5", "Ch. 5", "chapter 5",
"introduced: ch 5"), or "book N" for a series rule established before this book.
Reports carry IDs and chapter numbers only, so they are safe to show the author.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

RULE_ID = re.compile(r"[Rr](\d+)([A-Za-z]?)")
LOOKS_LIKE_ID = re.compile(r"[Rr]\s*\d")
WHEN = re.compile(r"(?:introduced:\s*)?(?:ch(?:apter)?\.?\s*(\d+)|book\s*(\d+))", re.I)
USES = re.compile(r"(?mi)^\W*uses rules:?\**\s*(.+)$")
BOOK_RULES = "02b_rules_and_clues.md"
SOLUTION = "01_novum_and_solutions.md"


@dataclass(frozen=True)
class Rule:
    id: str
    text: str
    chapter: int  # 0 = established before this book


def parse_rules(text: str) -> dict[str, Rule]:
    rules: dict[str, Rule] = {}
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        first = cells[0].strip("*` ")
        m = RULE_ID.fullmatch(first)
        if not m:
            # Header, separator and clue rows are skipped; a near-miss rule ID is not.
            if LOOKS_LIKE_ID.match(first) or (not first and any(cells[1:])):
                raise ValueError(f"rule row with no clean ID (use R3 or R3a): {first or '(empty)'!r}")
            continue
        rid = f"R{m.group(1)}{m.group(2).lower()}"
        when = WHEN.fullmatch(cells[2]) if len(cells) > 2 else None
        if len(cells) < 2 or not cells[1] or not when:
            raise ValueError(f"{rid}: row needs '| {rid} | rule | ch N |' (or 'book N')")
        if rid in rules:
            raise ValueError(f"duplicate rule ID {rid}")
        rules[rid] = Rule(rid, cells[1], int(when.group(1)) if when.group(1) else 0)
    return rules


def solution_rules(text: str) -> list[str]:
    m = USES.search(text)
    ids = [f"R{n}{s.lower()}" for n, s in re.findall(r"\b[Rr](\d+)([A-Za-z]?)\b", m.group(1))] if m else []
    if not ids:
        raise ValueError("no 'Uses rules: R1, R2' line in the solution file")
    return ids


def check_rules(plan_dir: Path, series_rules: Path | None = None, n_chapters: int = 24) -> dict:
    plan_dir = Path(plan_dir)
    cutoff = int(n_chapters * 0.75)
    errors: list[str] = []
    series = parse_rules(Path(series_rules).read_text(encoding="utf-8")) if series_rules else {}
    book = parse_rules((plan_dir / BOOK_RULES).read_text(encoding="utf-8"))
    for rid, rule in book.items():
        if rid in series and series[rid].text != rule.text:
            errors.append(f"{rid} redefines a series rule")
        # A clarity grader marks a compound rule "missing" when any one part is absent.
        if ";" in rule.text:
            errors.append(f"{rid} states more than one claim (split it: one claim per rule)")
    # A series rule counts from before this book unless the book lists it: a reader new
    # to the series meets it where this book first shows it.
    known = {**series, **book}
    uses = solution_rules((plan_dir / SOLUTION).read_text(encoding="utf-8"))
    for rid in uses:
        if rid not in known:
            errors.append(f"{rid} is used by the solution but is not in the rules list")
        elif known[rid].chapter > cutoff:
            errors.append(f"{rid} is used by the solution but first appears in chapter {known[rid].chapter} (after {cutoff})")
    return {"passed": not errors, "errors": errors, "rules": len(known), "solution_rules": uses, "cutoff": cutoff}
