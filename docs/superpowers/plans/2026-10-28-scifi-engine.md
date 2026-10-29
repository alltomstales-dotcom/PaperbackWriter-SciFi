# Sci-fi Genre Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `pbw_scifi`, the sci-fi engine's checks and gates, then run it on a calibration book and a two-book series, committing as each gate passes.

**Architecture:** A separate Python package that depends on `paperbackwriter` v0.1.0 for genre-neutral tools (staging, outline batches, proofreading, export, narration) and adds only sci-fi logic: the rules list, the exposition counter, the sci-fi reader-log checker and gates, and a Gutenberg importer for calibration. The method lives in Markdown skill files; the books live in a separate private repo whose tags version every iteration.

**Tech Stack:** Python 3.10+, standard library, pytest; `paperbackwriter` (git dependency); fpdf2 via `paperbackwriter[pdf]` for export.

**Spec:** `docs/superpowers/specs/2026-10-28-scifi-engine-design.md`

## Global Constraints

- The mystery repo's code is not changed. Only a `v0.1.0` tag is added to its current commit.
- Dependency: `paperbackwriter @ git+https://github.com/alltomstales-dotcom/PaperbackWriter@v0.1.0`.
- No plot, intended solution, plans, chapters or reader logs in this public repo. Process notes only (`JOURNAL.md`, `CALIBRATION.md`).
- Every rules/exposition/gate report prints IDs, chapters and counts, never rule text or solution text.
- Checkpoints come from `paperbackwriter.outline.checkpoints(n)`: (7, 12, 17, 21, 24) for 24 chapters.
- Late-rule cutoff: `int(n_chapters * 0.75)` (18 for 24).
- Gates: clarity at checkpoint 1 (premise correct, ≥ 2/3 of rules introduced so far stated, none wrong); intended solution not ranked first at checkpoint 2; p ≤ .35 at checkpoint 3.
- Blind-read targets: overall, rules_fair, solution_earned, prose each ≥ 7; ≥ 1 wonder quote per batch; obvious no earlier than one chapter before the reveal.
- Exposition threshold: 400 words until calibrated; calibrated value = 90th-percentile run length of the reference, rounded to 50, minimum 300.
- Commit identity: `alltomstales-dotcom <327489623+alltomstales-dotcom@users.noreply.github.com>`. Push after each task.
- **Amendment (author, 2026-10-28):** "upload each version/iteration of what it writes as a versioned object". The book work goes in a **private** repo `alltomstales-dotcom/PaperbackWriter-SciFi-Books`, local `Downloads/PaperbackWriter-SciFi-Books`, with an annotated tag per iteration (Task 9). This replaces the spec's private book folder under `PPW_10212025/series/`, which sits inside a repo whose remote URL holds a token.

## Review Focus

1. A rules table written with extra spaces, bold IDs (`**R3**`) or "Ch. 5": the parser should still read it, and a row it cannot read should be an error, not a silent skip.
2. A reader route that matches no solution key: probability 0, rank last, status `absent`, and the gate treats it as hidden (pass), not as a crash.
3. A chapter whose dialogue uses straight quotes or single curly quotes: exposition runs must still break on dialogue.
4. Gutenberg text with Windows line endings and `_italics_`: the importer must produce clean `chNN.txt` files with `*italics*`.
5. A grader file missing a rule the plan introduced by the checkpoint: that rule counts as missing, not as stated.

---

### Task 1: Scaffold, pinned dependency and the reuse boundary

**Files:**
- Create: `pyproject.toml`, `pbw_scifi/__init__.py`, `tests/test_reuse.py`
- External: tag `v0.1.0` on `alltomstales-dotcom/PaperbackWriter`

**Interfaces:**
- Produces: importable package `pbw_scifi`; venv `~/venvs/pbw-scifi` with `paperbackwriter` 0.1.0 and pytest.

- [ ] **Step 1: Tag the mystery repo and push the tag**

```bash
cd /mnt/c/Users/tbmye/Downloads/PaperbackWriter-public
git tag -a v0.1.0 -m "v0.1.0: first public release" && git push origin v0.1.0
```

- [ ] **Step 2: Write `pyproject.toml` and `pbw_scifi/__init__.py`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "pbw-scifi"
version = "0.1.0"
description = "Sci-fi genre engine for PaperbackWriter."
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.10"
dependencies = ["paperbackwriter @ git+https://github.com/alltomstales-dotcom/PaperbackWriter@v0.1.0"]

[project.optional-dependencies]
pdf = ["fpdf2>=2.7"]
dev = ["pytest", "fpdf2>=2.7"]

[project.scripts]
paperbackwriter-scifi = "pbw_scifi.cli:main"

[tool.setuptools]
packages = ["pbw_scifi"]
```

```python
"""PaperbackWriter-SciFi: the sci-fi genre engine."""

__version__ = "0.1.0"
```

- [ ] **Step 3: Write the reuse-boundary test**

```python
"""Every function this project borrows from paperbackwriter, called once.
If an upgrade of the dependency breaks one, this fails first."""
import json


def test_borrowed_outline_functions():
    from paperbackwriter.outline import batches, checkpoints, sections
    assert checkpoints(24) == (7, 12, 17, 21, 24)
    assert batches(24)[0] == (1, 7)
    assert sections("Chapter 1: A\n\nx\n") == {1: ("Chapter 1: A", "x")}


def test_borrowed_stage_proof_and_export(tmp_path):
    from paperbackwriter.export import Book, build_epub, load_chapters
    from paperbackwriter.proof import apply_fixes
    from paperbackwriter.reads import stage
    src = tmp_path / "chapters"
    src.mkdir()
    for n in (1, 2):
        (src / f"ch{n:02d}.txt").write_text(f"Chapter {n}: T\n\nThe hull rang at dawn.\n")
    assert stage(src, tmp_path / "read", 1) == 1
    assert apply_fixes(src, [{"file": "ch02.txt", "old": "dawn", "new": "dusk"}]) == (1, [])
    out = build_epub(Book("T", "A", load_chapters(src)), tmp_path / "t.epub")
    assert out.stat().st_size > 0
```

- [ ] **Step 4: Create the venv, install, run**

```bash
python3 -m venv ~/venvs/pbw-scifi
~/venvs/pbw-scifi/bin/pip install -q -e ".[dev]"
~/venvs/pbw-scifi/bin/python -m pytest -q
```
Expected: 2 passed.

- [ ] **Step 5: Commit and push** — `git add -A && git commit -m "Scaffold: package, pinned paperbackwriter v0.1.0, reuse-boundary tests" && git push`

---

### Task 2: rules.py — the world's rules list

**Files:**
- Create: `pbw_scifi/rules.py`, `tests/test_rules.py`

**Interfaces:**
- Produces: `Rule(id: str, text: str, chapter: int)` (chapter 0 = established before this book); `parse_rules(text: str) -> dict[str, Rule]`; `solution_rules(text: str) -> list[str]`; `check_rules(plan_dir: Path, series_rules: Path | None = None, n_chapters: int = 24) -> dict` with keys `passed`, `errors`, `rules`, `solution_rules`, `cutoff`.

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

import pytest

from pbw_scifi.rules import Rule, check_rules, parse_rules, solution_rules

TABLE = """| ID | Rule | Introduced |
|---|---|---|
| R1 | The ring spins once a minute | ch 1 |
| **R2** | Air is rationed by deck | introduced: Ch. 3 |
| R3 | Nobody crosses the spine at night | chapter 20 |
"""


def test_parse_rules_reads_loose_formatting():
    rules = parse_rules(TABLE)
    assert rules["R2"] == Rule("R2", "Air is rationed by deck", 3)
    assert rules["R3"].chapter == 20


def test_series_rows_are_established_before_the_book():
    assert parse_rules("| R9 | Gravity is 0.8 g | book 1 |\n")["R9"].chapter == 0


def test_duplicate_rule_ids_are_an_error():
    with pytest.raises(ValueError, match="R1"):
        parse_rules(TABLE + "| R1 | Again | ch 2 |\n")


def test_an_unreadable_rule_row_is_an_error_not_a_skip():
    with pytest.raises(ValueError, match="R4"):
        parse_rules(TABLE + "| R4 | No chapter column |\n")


def test_solution_rules_reads_the_uses_line():
    assert solution_rules("Intended solution: x\n**Uses rules:** R1, R3 and R2\n") == ["R1", "R3", "R2"]
    with pytest.raises(ValueError):
        solution_rules("no line here")


def _plan(tmp: Path, uses: str, table: str = TABLE) -> Path:
    (tmp / "02b_rules_and_clues.md").write_text(table)
    (tmp / "01_novum_and_solutions.md").write_text(f"Uses rules: {uses}\n")
    return tmp


def test_a_solution_on_early_rules_passes(tmp_path):
    result = check_rules(_plan(tmp_path, "R1, R2"))
    assert result["passed"], result["errors"]
    assert result["cutoff"] == 18


def test_a_solution_rule_introduced_after_75_percent_fails(tmp_path):
    result = check_rules(_plan(tmp_path, "R1, R3"))
    assert result["errors"] == ["R3 is used by the solution but first appears in chapter 20 (after 18)"]


def test_an_unknown_solution_rule_fails(tmp_path):
    assert "R7 is used by the solution but is not in the rules list" in check_rules(_plan(tmp_path, "R7"))["errors"]


def test_book_two_may_add_rules_but_not_redefine_series_rules(tmp_path):
    series = tmp_path / "SERIES_RULES.md"
    series.write_text("| R1 | The ring spins once a minute | book 1 |\n| R8 | Docking needs two keys | book 1 |\n")
    plan = tmp_path / "plan"
    plan.mkdir()
    _plan(plan, "R8, R2")
    assert check_rules(plan, series)["passed"]
    (plan / "02b_rules_and_clues.md").write_text(TABLE.replace("R1 | The ring spins once a minute", "R1 | The ring is still"))
    assert "R1 redefines a series rule" in check_rules(plan, series)["errors"]


def test_errors_never_contain_rule_text(tmp_path):
    result = check_rules(_plan(tmp_path, "R3"))
    assert not any("spine" in e for e in result["errors"])
```

- [ ] **Step 2: Run to watch them fail** — `~/venvs/pbw-scifi/bin/python -m pytest tests/test_rules.py -q` → ImportError.

- [ ] **Step 3: Implement `pbw_scifi/rules.py`**

```python
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

ROW = re.compile(r"^\|\s*\**(R\d+)\**\s*\|(.*)$", re.M)
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
    for m in ROW.finditer(text):
        rid = m.group(1)
        cells = [c.strip() for c in m.group(2).split("|")]
        when = WHEN.fullmatch(cells[1]) if len(cells) > 1 else None
        if not cells[0] or not when:
            raise ValueError(f"{rid}: row needs '| {rid} | rule | ch N |' (or 'book N')")
        if rid in rules:
            raise ValueError(f"duplicate rule ID {rid}")
        rules[rid] = Rule(rid, cells[0], int(when.group(1)) if when.group(1) else 0)
    return rules


def solution_rules(text: str) -> list[str]:
    m = USES.search(text)
    ids = re.findall(r"R\d+", m.group(1)) if m else []
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
    known = {**book, **series}  # a series rule is established before this book
    uses = solution_rules((plan_dir / SOLUTION).read_text(encoding="utf-8"))
    for rid in uses:
        if rid not in known:
            errors.append(f"{rid} is used by the solution but is not in the rules list")
        elif known[rid].chapter > cutoff:
            errors.append(f"{rid} is used by the solution but first appears in chapter {known[rid].chapter} (after {cutoff})")
    return {"passed": not errors, "errors": errors, "rules": len(known), "solution_rules": uses, "cutoff": cutoff}
```

- [ ] **Step 4: Run** — expected: all `test_rules.py` tests pass.

- [ ] **Step 5: Commit and push** — `git commit -m "rules: rules list parser and fair-play check on the solution"`

---

### Task 3: exposition.py — info-dump counter

**Files:**
- Create: `pbw_scifi/exposition.py`, `tests/test_exposition.py`

**Interfaces:**
- Produces: `Run(words: int, start: str)`; `runs(text: str) -> list[Run]`; `report(chapters_dir: Path, threshold: int) -> list[dict]` (keys `chapter`, `words`, `start`); `calibrated_threshold(chapters_dir: Path) -> dict` (keys `threshold`, `p90`, `runs`, `max`).

- [ ] **Step 1: Write the failing tests**

```python
from pbw_scifi.exposition import Run, calibrated_threshold, report, runs

TEXT = "Chapter 1: Spin\n\nThe ring turned. " + "word " * 100 + "\n\nMore of the same. " + "word " * 50 + \
       "\n\n“Air,” she said.\n\nAfter that. " + "word " * 10 + "\n\n* * *\n\nNew scene.\n"


def test_runs_break_on_dialogue_and_scene_breaks_and_skip_the_heading():
    assert [r.words for r in runs(TEXT)] == [157, 12, 2]
    assert runs(TEXT)[0].start.startswith("The ring turned.")


def test_straight_and_single_quotes_count_as_dialogue():
    assert [r.words for r in runs("a b\n\n\"Hi,\" he said.\n\nc d\n\n‘Yes,’ she said.\n\ne\n")] == [2, 2, 1]


def test_report_lists_only_runs_over_the_threshold(tmp_path):
    (tmp_path / "ch01.txt").write_text(TEXT)
    assert report(tmp_path, 150) == [{"chapter": 1, "words": 157, "start": runs(TEXT)[0].start}]
    assert report(tmp_path, 400) == []


def test_calibrated_threshold_is_the_rounded_90th_percentile_with_a_floor(tmp_path):
    body = "\n\n“x,” y.\n\n".join("w " * n for n in range(100, 1100, 100))  # runs 100..1000
    (tmp_path / "ch01.txt").write_text("Chapter 1: A\n\n" + body + "\n")
    result = calibrated_threshold(tmp_path)
    assert result["p90"] == 900 and result["threshold"] == 900
    (tmp_path / "ch01.txt").write_text("Chapter 1: A\n\nw w w\n")
    assert calibrated_threshold(tmp_path)["threshold"] == 300
```

- [ ] **Step 2: Run to watch them fail.**

- [ ] **Step 3: Implement `pbw_scifi/exposition.py`**

```python
"""Exposition runs: stretches of paragraphs with no dialogue and no scene break.

A long run is where readers skim. The threshold is calibrated on a reference novel
(CALIBRATION.md) rather than guessed.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

QUOTES = ('"', "“", "”", "‘", "’ ")
SCENE_BREAK = "* * *"
HEADING = re.compile(r"Chapter \d+: .+")


@dataclass(frozen=True)
class Run:
    words: int
    start: str


def _is_dialogue(paragraph: str) -> bool:
    return any(q in paragraph for q in ('"', "“", "”")) or bool(re.search(r"(^|\s)‘", paragraph))


def runs(text: str) -> list[Run]:
    out: list[Run] = []
    words, start = 0, ""
    for p in (p.strip() for p in text.split("\n\n")):
        if not p or HEADING.fullmatch(p):
            continue
        if p == SCENE_BREAK or _is_dialogue(p):
            if words:
                out.append(Run(words, start))
            words, start = 0, ""
            continue
        if not words:
            start = p[:60]
        words += len(p.split())
    if words:
        out.append(Run(words, start))
    return out


def _chapter_files(chapters_dir: Path):
    for path in sorted(Path(chapters_dir).glob("ch*.txt")):
        m = re.fullmatch(r"ch(\d+)\.txt", path.name)
        if m:
            yield int(m.group(1)), path.read_text(encoding="utf-8")


def report(chapters_dir: Path, threshold: int) -> list[dict]:
    return [{"chapter": n, "words": r.words, "start": r.start}
            for n, text in _chapter_files(chapters_dir) for r in runs(text) if r.words > threshold]


def calibrated_threshold(chapters_dir: Path) -> dict:
    lengths = sorted(r.words for _, text in _chapter_files(chapters_dir) for r in runs(text))
    if not lengths:
        raise ValueError(f"no chapter text in {chapters_dir}")
    p90 = lengths[max(0, math.ceil(0.9 * len(lengths)) - 1)]  # nearest-rank
    return {"threshold": max(300, int(round(p90 / 50.0)) * 50), "p90": p90, "runs": len(lengths), "max": lengths[-1]}
```

(`QUOTES` is unused; delete it during implementation.)

- [ ] **Step 4: Run** — expected pass.
- [ ] **Step 5: Commit and push** — `git commit -m "exposition: run counter, report and calibrated threshold"`

---

### Task 4: reads.py — sci-fi reader logs and solution rank

**Files:**
- Create: `pbw_scifi/reads.py`, `tests/test_reads.py`

**Interfaces:**
- Consumes: `paperbackwriter.outline.sections`.
- Produces: `check_log(path: Path, finished: bool = False) -> dict` (keys `log`, `checkpoint`, `evidence_count`, `passed`, `errors`); `solution_rank(log_path: Path, keys: list[str]) -> dict` (keys `status` in {"matched","absent","ambiguous"}, `rank: int | None`, `p: float | None`, `matches: list[int]`); `wonder_count(log_path: Path) -> int`.

- [ ] **Step 1: Write the failing tests**

```python
import json
from pathlib import Path

from pbw_scifi.reads import check_log, solution_rank, wonder_count


def _folder(tmp: Path, upto: int) -> Path:
    for n in range(1, upto + 1):
        (tmp / f"ch{n:02d}.txt").write_text(f"Chapter {n}: T\n\nThe ring spun in chapter {n}.\n")
    return tmp


def _log(folder: Path, after: int, **fields) -> Path:
    data = {"after_chapter": after, "premise": "p", "rules": [], "solutions": [], "wonder": [], "skimmed": []}
    data.update(fields)
    path = folder / f"log_ch{after:02d}.json"
    path.write_text(json.dumps(data))
    return path


SOL = [{"route": "They vent the spine to stop the spin", "p_solution": 0.6},
       {"route": "The captain overrides the reactor", "p_solution": 0.4}]


def test_quotes_anywhere_in_the_log_are_verified(tmp_path):
    f = _folder(tmp_path, 3)
    good = _log(f, 3, solutions=SOL, wonder=[{"chapter": 2, "quote": "The ring spun in chapter 2"}],
                rules=[{"rule": "spin", "evidence": [{"chapter": 1, "quote": "ring spun"}]}])
    assert check_log(good)["passed"] and check_log(good)["evidence_count"] == 2
    bad = _log(f, 3, solutions=SOL, skimmed=[{"chapter": 3, "quote": "the ring stopped", "why": "x"}])
    assert not check_log(bad)["passed"]


def test_solution_probabilities_must_sum_to_one(tmp_path):
    log = _log(_folder(tmp_path, 3), 3, solutions=[{"route": "a", "p_solution": 0.5}])
    assert "Solution probabilities do not sum to one" in check_log(log)["errors"]


def test_staged_folder_must_stop_at_the_checkpoint_unless_finished(tmp_path):
    log = _log(_folder(tmp_path, 4), 3, solutions=SOL)
    assert not check_log(log)["passed"]
    assert check_log(log, finished=True)["passed"]


def test_solution_rank_matched_absent_and_ambiguous(tmp_path):
    log = _log(_folder(tmp_path, 3), 3, solutions=SOL)
    assert solution_rank(log, [r"vent\w*.*spine"]) == {"status": "matched", "rank": 1, "p": 0.6, "matches": [0]}
    assert solution_rank(log, [r"radio"]) == {"status": "absent", "rank": 3, "p": 0.0, "matches": []}
    amb = solution_rank(log, [r"the"])
    assert amb["status"] == "ambiguous" and amb["rank"] is None and amb["matches"] == [0, 1]


def test_wonder_count(tmp_path):
    log = _log(_folder(tmp_path, 3), 3, solutions=SOL, wonder=[{"chapter": 1, "quote": "ring spun"}])
    assert wonder_count(log) == 1
```

- [ ] **Step 2: Run to watch them fail.**

- [ ] **Step 3: Implement `pbw_scifi/reads.py` (log part)**

```python
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
```

- [ ] **Step 4: Run** — expected pass.
- [ ] **Step 5: Commit and push** — `git commit -m "reads: sci-fi log verification, solution rank, wonder count"`

---

### Task 5: reads.py — clarity grading and the plan-read gate

**Files:**
- Modify: `pbw_scifi/reads.py` (append)
- Create: `tests/test_gate.py`

**Interfaces:**
- Consumes: `check_log`, `solution_rank` (Task 4); `parse_rules` (Task 2); `paperbackwriter.outline.checkpoints`.
- Produces: `clarity(grade_path: Path, rule_ids: list[str]) -> dict` (keys `passed`, `stated`, `missing`, `wrong`, `premise_correct`); `advance_plan_read(reference: Path, gate_path: Path, checkpoint: int, n_chapters: int = 24) -> dict`.
- Grader file `grade_chNN.json` (written by a fresh grader agent, in the reader's folder): `{"premise_correct": true, "rules": [{"id": "R1", "verdict": "stated|missing|wrong"}]}`.
- Ambiguity file `rank_chNN.json` (grader): `{"route_index": 2}` or `{"route_index": null}`.
- Reference (private, in `plan/`, written before the read): `{"candidate_directory": ".", "reader_folder": "...", "plan_sha256": {...}, "digest_sha256": {...}, "solution_keys": ["regex", ...]}`.

- [ ] **Step 1: Write the failing tests**

```python
import hashlib
import json
from pathlib import Path

import pytest

from pbw_scifi.reads import advance_plan_read, clarity


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_clarity_counts_missing_rules_and_fails_on_a_wrong_one(tmp_path):
    g = tmp_path / "grade_ch07.json"
    g.write_text(json.dumps({"premise_correct": True, "rules": [
        {"id": "R1", "verdict": "stated"}, {"id": "R2", "verdict": "stated"}]}))
    assert clarity(g, ["R1", "R2", "R3"])["passed"]          # 2 of 3, R3 absent = missing
    assert not clarity(g, ["R1", "R2", "R3", "R4"])["passed"]  # 2 of 4
    g.write_text(json.dumps({"premise_correct": True, "rules": [
        {"id": "R1", "verdict": "stated"}, {"id": "R2", "verdict": "wrong"}]}))
    assert clarity(g, ["R1"])["passed"] is False or clarity(g, ["R1", "R2"])["passed"] is False


def _setup(tmp: Path):
    plan = tmp / "plan"
    (plan / "digest").mkdir(parents=True)
    (plan / "01_novum_and_solutions.md").write_text("Uses rules: R1\n")
    (plan / "02b_rules_and_clues.md").write_text("| R1 | Spin | ch 2 |\n| R2 | Air | ch 5 |\n| R3 | Spine | ch 15 |\n")
    for i, (lo, hi) in enumerate([(1, 7), (8, 12), (13, 17), (18, 21), (22, 24)], 1):
        (plan / "digest" / f"batch{i}.md").write_text(
            "\n\n".join(f"Chapter {n}: T\n\nThe ring spun in chapter {n}." for n in range(lo, hi + 1)) + "\n")
    read = tmp / "read"
    read.mkdir()
    (read / "batch1.md").write_bytes((plan / "digest" / "batch1.md").read_bytes())
    ref = plan / "reference.json"
    ref.write_text(json.dumps({
        "candidate_directory": ".", "reader_folder": "../read", "solution_keys": [r"vent"],
        "plan_sha256": {n: _sha(plan / n) for n in ("01_novum_and_solutions.md", "02b_rules_and_clues.md")},
        "digest_sha256": {p.name: _sha(p) for p in (plan / "digest").glob("batch*.md")}}))
    gate = plan / "gate.json"
    gate.write_text('{"checkpoints": []}')
    return plan, read, ref, gate


def _log(read: Path, after: int, solutions):
    (read / f"log_ch{after:02d}.json").write_text(json.dumps(
        {"after_chapter": after, "premise": "p", "rules": [], "solutions": solutions, "wonder": []}))


def test_checkpoint_one_is_the_clarity_gate(tmp_path):
    plan, read, ref, gate = _setup(tmp_path)
    _log(read, 7, [{"route": "vent it", "p_solution": 0.9}, {"route": "other", "p_solution": 0.1}])
    with pytest.raises(ValueError, match="grade_ch07.json"):
        advance_plan_read(ref, gate, 7)
    (read / "grade_ch07.json").write_text(json.dumps({"premise_correct": True, "rules": [
        {"id": "R1", "verdict": "stated"}, {"id": "R2", "verdict": "stated"}]}))
    record = advance_plan_read(ref, gate, 7)
    assert record["passed"] and (read / "batch2.md").exists()


def test_checkpoint_two_fails_when_the_intended_solution_ranks_first(tmp_path):
    plan, read, ref, gate = _setup(tmp_path)
    _log(read, 7, [{"route": "x", "p_solution": 1.0}])
    (read / "grade_ch07.json").write_text(json.dumps({"premise_correct": True, "rules": [
        {"id": "R1", "verdict": "stated"}, {"id": "R2", "verdict": "stated"}]}))
    advance_plan_read(ref, gate, 7)
    _log(read, 12, [{"route": "vent the spine", "p_solution": 0.5}, {"route": "x", "p_solution": 0.5 - 0.1},
                    {"route": "y", "p_solution": 0.1}])
    record = advance_plan_read(ref, gate, 12)
    assert not record["passed"] and json.loads(gate.read_text())["stage"] == "FAILED_AT_12"
    assert not (read / "batch3.md").exists()


def test_an_absent_intended_solution_counts_as_hidden(tmp_path):
    plan, read, ref, gate = _setup(tmp_path)
    _log(read, 7, [{"route": "x", "p_solution": 1.0}])
    (read / "grade_ch07.json").write_text(json.dumps({"premise_correct": True, "rules": [
        {"id": "R1", "verdict": "stated"}, {"id": "R2", "verdict": "stated"}]}))
    advance_plan_read(ref, gate, 7)
    _log(read, 12, [{"route": "x", "p_solution": 1.0}])
    assert advance_plan_read(ref, gate, 12)["passed"]


def test_a_changed_plan_file_is_refused(tmp_path):
    plan, read, ref, gate = _setup(tmp_path)
    (plan / "01_novum_and_solutions.md").write_text("Uses rules: R2\n")
    _log(read, 7, [{"route": "x", "p_solution": 1.0}])
    with pytest.raises(ValueError, match="changed"):
        advance_plan_read(ref, gate, 7)
```

- [ ] **Step 2: Run to watch them fail.**

- [ ] **Step 3: Append to `pbw_scifi/reads.py`**

```python
import hashlib
import shutil

from paperbackwriter.outline import checkpoints

from .rules import parse_rules


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
```

- [ ] **Step 4: Run** — expected pass. (Tighten the third assertion of the clarity test to the exact intended case: with R2 "wrong", `clarity(g, ["R1", "R2"])["passed"] is False`.)
- [ ] **Step 5: Commit and push** — `git commit -m "gate: clarity grading and the hash-locked sci-fi plan-read gate"`

---

### Task 6: calibrate.py — Gutenberg importer

**Files:**
- Create: `pbw_scifi/calibrate.py`, `tests/test_calibrate.py`

**Interfaces:**
- Produces: `split_gutenberg(text: str) -> list[tuple[int, str, str]]`; `write_chapters(chapters, out_dir: Path) -> int`.

- [ ] **Step 1: Write the failing tests**

```python
from pbw_scifi.calibrate import split_gutenberg, write_chapters

RAW = ("Header junk\r\n*** START OF THE PROJECT GUTENBERG EBOOK X ***\r\n\r\nContents\r\n I. One\r\n\r\n"
       "CHAPTER I.\r\nTHE STRANGE MAN’S ARRIVAL\r\n\r\n\r\nThe stranger came early in\r\nFebruary, _very_ cold.\r\n\r\n"
       "“Hi,” he said.\r\n\r\nCHAPTER II.\r\nMR. TEDDY HENFREY\r\n\r\nSecond chapter text.\r\n\r\n"
       "THE EPILOGUE\r\n\r\nThe end.\r\n\r\n*** END OF THE PROJECT GUTENBERG EBOOK X ***\r\nlicence\r\n")


def test_split_gutenberg_finds_chapters_and_epilogue():
    chapters = split_gutenberg(RAW)
    assert [(n, t) for n, t, _ in chapters] == [(1, "The Strange Man’s Arrival"), (2, "Mr. Teddy Henfrey"), (3, "Epilogue")]
    assert chapters[0][2] == "The stranger came early in February, *very* cold.\n\n“Hi,” he said."


def test_write_chapters_matches_the_engine_format(tmp_path):
    assert write_chapters(split_gutenberg(RAW), tmp_path) == 3
    assert (tmp_path / "ch01.txt").read_text().startswith("Chapter 1: The Strange Man’s Arrival\n\nThe stranger")
```

- [ ] **Step 2: Run to watch them fail.**

- [ ] **Step 3: Implement `pbw_scifi/calibrate.py`**

```python
"""Import a public-domain novel from Project Gutenberg as chNN.txt files for calibration reads."""
from __future__ import annotations

import re
from pathlib import Path

HEADING = re.compile(r"(?m)^(?:CHAPTER ([IVXLC]+)\.?|THE (EPILOGUE))\s*$")


def _title(s: str) -> str:
    small = {"a", "an", "the", "of", "in", "and", "at", "on", "to", "for", "who", "was"}
    words = s.strip().rstrip(".").lower().split()
    return " ".join(w if i and w in small else w[:1].upper() + w[1:] for i, w in enumerate(words))


def split_gutenberg(text: str) -> list[tuple[int, str, str]]:
    text = text.replace("\r\n", "\n")
    start = text.find("*** START OF")
    end = text.find("*** END OF")
    body = text[text.find("\n", start) + 1: end if end != -1 else None]
    marks = list(HEADING.finditer(body))
    out = []
    for i, m in enumerate(marks):
        chunk = body[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(body)].strip("\n")
        if m.group(2):
            title, rest = "Epilogue", chunk
        else:
            first, _, rest = chunk.partition("\n")
            title = _title(first)
        paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", rest) if p.strip()]
        prose = "\n\n".join(re.sub(r"_([^_]+)_", r"*\1*", p) for p in paras)
        out.append((i + 1, title, prose))
    return out


def write_chapters(chapters, out_dir: Path) -> int:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for n, title, prose in chapters:
        (out_dir / f"ch{n:02d}.txt").write_text(f"Chapter {n}: {title}\n\n{prose}\n", encoding="utf-8")
    return len(chapters)
```

- [ ] **Step 4: Run** — expected pass. Then run on the real file: 29 chapters (28 + Epilogue), first title "The Strange Man’s Arrival".
- [ ] **Step 5: Commit and push** — `git commit -m "calibrate: Gutenberg importer for reference reads"`

---

### Task 7: cli.py

**Files:**
- Create: `pbw_scifi/cli.py`, `pbw_scifi/__main__.py`, `tests/test_cli.py`

**Interfaces:**
- Consumes: everything above.
- Produces: `paperbackwriter-scifi {rules, exposition, calibrate-threshold, check-read, rank, gate, import-reference}`; exit 0 on pass, 1 on a failed check, 2 on bad input.

- [ ] **Step 1: Write the failing test**

```python
import json

from pbw_scifi.cli import main


def test_rules_command_exit_codes(tmp_path, capsys):
    (tmp_path / "02b_rules_and_clues.md").write_text("| R1 | Spin | ch 2 |\n| R3 | Spine | ch 20 |\n")
    (tmp_path / "01_novum_and_solutions.md").write_text("Uses rules: R1\n")
    assert main(["rules", str(tmp_path)]) == 0
    (tmp_path / "01_novum_and_solutions.md").write_text("Uses rules: R3\n")
    assert main(["rules", str(tmp_path)]) == 1
    assert "Spine" not in capsys.readouterr().out


def test_bad_input_is_exit_two(tmp_path):
    assert main(["rules", str(tmp_path / "missing")]) == 2
```

- [ ] **Step 2: Run to watch it fail.**

- [ ] **Step 3: Implement `pbw_scifi/cli.py` and `__main__.py`** — argparse subcommands mapping one-to-one to the functions above; `_print(result)` dumps JSON and returns 0 if `passed` is true or absent, 1 otherwise; `(ValueError, FileNotFoundError, KeyError)` → message on stderr, return 2. `exposition` takes `chapters_dir --threshold N` (default 400) and returns 1 if any run is listed. `import-reference` takes a Gutenberg `.txt` and an output folder.

- [ ] **Step 4: Run the whole suite** — `~/venvs/pbw-scifi/bin/python -m pytest -q` → all pass.
- [ ] **Step 5: Commit and push** — `git commit -m "cli: paperbackwriter-scifi command"`

---

### Task 8: The method — skill docs, templates, README

**Files:**
- Create: `.claude/skills/writing-scifi-novels/{SKILL.md,intake.md,plan-files.md,writer-brief.md,blind-read.md}`, `templates/{SERIES_BIBLE.md,SERIES_RULES.md,PROCESS.md,STATUS.md,AGENTS.md}`
- Modify: `README.md`

Content requirements (copy section 4 of the spec into these, adapted from the mystery skill's structure):
- `SKILL.md`: overview, file layout (books repo), stages table with the commands, the nine rules from spec §4, gates table, stop rules, who does what, common mistakes.
- `plan-files.md`: the seven plan files from spec §4, with the rules-table format (`| R7 | rule | ch 5 |`), the `Uses rules:` line, the four-solutions matrix (solution / support on the page / why a reader might believe it / why it is wrong or right / strongest chapters), and the chapter format `**Ch N. Title. When. Where.**` + bullets.
- `blind-read.md`: the sci-fi reader prompt producing the Task 4 schema and the verdict; the grader prompts for `grade_chNN.json` and `rank_chNN.json`; checkpoints; targets.
- `writer-brief.md`: the drafting template (Sonnet 5.5, five chapters per agent, canon obeyed, no exposition run over the threshold, novum shown before explained, wonder per chapter, the intended solution's pieces kept as background), the fix-pass rules and the proofread step.
- `intake.md`: the mystery intake adapted (novum, closed setting, the lead's trade, the central problem's scale, hard vs soft science, series rules).
- README: what it is, install, commands, the gates, link to `JOURNAL.md`.

- [ ] Write the files; check each skill file has no placeholder text and no plot.
- [ ] Commit and push — `git commit -m "Method: writing-scifi-novels skill, templates, README"`

---

### Task 9: Private books repo with versioned iterations

**Files:**
- Create (private repo `Downloads/PaperbackWriter-SciFi-Books`): `README.md`, `.gitignore` (`*.wav`, `__pycache__/`), `calibration/`, `series/`
- Create (public repo): `pbw_scifi/archive.py`? **No** — a shell convention is enough (YAGNI).

Convention, recorded in the books repo README and in `SKILL.md`:
- One commit per artefact change; an **annotated tag per iteration**: `cal-read-1`, `b1-bible-v1`, `b1-plan-vN`, `b1-planread-vN-pass|fail`, `b1-draft-N`, `b1-read-N`, `b1-fix-1`, `b1-proof`, `b1-final-read`, `b1-release`; then `b2-…`.
- The tag message carries the scores (no plot).
- Release tags (`bN-release`) also get a GitHub release on the private repo with the EPUB and PDF attached.

- [ ] `gh repo create alltomstales-dotcom/PaperbackWriter-SciFi-Books --private`, push, tag `init`.
- [ ] Journal line in the public repo; commit and push.

---

### Task 10: Calibration read (The Invisible Man)

- [ ] Import: `paperbackwriter-scifi import-reference pg5230.txt <books>/calibration/invisible-man/chapters` → 29 chapters.
- [ ] Threshold: `paperbackwriter-scifi calibrate-threshold <…>/chapters` → write the value and evidence to `CALIBRATION.md`.
- [ ] Staged read with a fresh Opus reader at checkpoints `checkpoints(29)` using `blind-read.md`'s prompt; `check-read` each log; verdict.
- [ ] Record the reader's scores in `CALIBRATION.md` as the anchor. Tag `cal-read-1` in the books repo. Commit and push both repos.

### Task 11: Book 1 (engine iteration)

- [ ] Intake: build brief from the agreed defaults, rows marked assumed; send the author the spoiler-free brief.
- [ ] Series bible and `SERIES_RULES.md` (tag `b1-bible-v1`).
- [ ] Plan, one file per turn; `rules` and `check-plan` (mystery command, structure only) pass; tag `b1-plan-v1`.
- [ ] Plan read with the gate; on fail, redesign the solutions, new version, tag each; on pass tag `b1-planread-vN-pass`.
- [ ] Draft with Sonnet 5.5 agents, five chapters each; tag `b1-draft-1`.
- [ ] Blind read (staged, fresh Opus); `check-read`; `exposition`; tag `b1-read-1`.
- [ ] One fix pass; proofread; final read; export; tags `b1-fix-1`, `b1-proof`, `b1-final-read`, `b1-release`.
- [ ] Every engine change: commit in the public repo with a `CALIBRATION.md` line. After release: tag `engine-v1` in the public repo.

### Task 12: Book 2 (validation on engine-v1)

- [ ] Same route on the frozen engine; no code changes; tags `b2-…`.
- [ ] Validation verdict in `JOURNAL.md`: each gate, pass or miss, and the change each miss needs.
