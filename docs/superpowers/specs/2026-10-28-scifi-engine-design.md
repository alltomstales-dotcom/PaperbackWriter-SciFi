# PaperbackWriter-SciFi: design

Date: 2026-10-28. Status: design approved in conversation; this written spec awaits review.

## 1. Goal

A genre engine for **near-future, idea-driven science fiction set in one closed setting** (a station, a colony or a ship), built as a separate project from the PaperbackWriter mystery engine. It is validated by writing a **two-book series**: Book 1 builds and tunes the engine, and Book 2 runs it frozen.

The mystery engine tests one reader belief, "who did it", at staged checkpoints, gates on it, and verifies every claim mechanically. This engine does the same for sci-fi's equivalent: **how the central problem will be solved, and whether the solution plays fair with the world's rules.**

### What the author said (2026-10-28)
- Distinct code projects per genre; leave the mystery engine alone.
- Romance and sci-fi first; **sci-fi first**.
- Subgenre: near-future, idea-driven, one closed setting (accepted recommendation).
- "Write a pair of books for each genre to iterate and validate the pipeline."
- The pair is **Book 1 and Book 2 of a series**.
- Make the repo public; commit and push while building and iterating, so the history records the process and its evolution.

### Assumed (from earlier series, not restated by the author)
- About 24 chapters and 50,000 words per book.
- The author reads cold: messages and public files carry stages and numbers, never plot.
- The model split used for Glass Island: the strongest model plans; Sonnet 5.5 drafts and does the fix pass; fresh agents read and proofread.

### Non-goals
- No change to `alltomstales-dotcom/PaperbackWriter` code. The only touch is a `v0.1.0` tag on its current commit, so this project can pin it.
- No romance engine here. It gets its own repo and spec later.
- No book text, plans or reader logs in the public repo.

## 2. Architecture

```
PaperbackWriter (mystery, untouched, tag v0.1.0)
        ▲ pip dependency, pinned
        │  reused: outline.checkpoints/batches/sections/build_digest/planner_to_reader,
        │          reads.stage, proof.apply_fixes, export.*, narrate.*
PaperbackWriter-SciFi (this repo, public, MIT)
  pbw_scifi/                    genre code
  .claude/skills/writing-scifi-novels/   the method
  templates/                    series bible, rules list, process, status
  CALIBRATION.md  JOURNAL.md    public, spoiler-free record of how the engine changed
Private book folders (never in this repo)
  …/PPW_10212025/series/<series-slug>/  bible, plans, chapters, blind reads, releases
```

### Repository layout

```
README.md  LICENSE  pyproject.toml  .gitignore
CALIBRATION.md   gate and threshold changes, dated, with the evidence for each
JOURNAL.md       dated process notes: stage reached, scores, what changed and why. No plot
docs/superpowers/specs/  docs/superpowers/plans/
.claude/skills/writing-scifi-novels/  SKILL.md intake.md plan-files.md writer-brief.md blind-read.md
templates/  SERIES_BIBLE.md  RULES.md  PROCESS.md  STATUS.md  AGENTS.md
pbw_scifi/  __init__.py  __main__.py  cli.py  rules.py  exposition.py  reads.py  calibrate.py
tests/
```

## 3. Components

Each module has one job and is tested on its own.

### rules.py: the world's rules list
- Parses a rules table: `| R7 | rule text | introduced: ch 5 |` rows, from `02b_rules_and_clues.md` (book) and `SERIES_RULES.md` (series).
- Parses the solution's `Uses rules: R2, R5, R7` line from `01_novum_and_solutions.md`.
- `check_rules(plan_dir, series_rules, n_chapters)` reports:
  - any rule the solution uses that is not in the list;
  - any rule the solution uses whose introduction chapter is after 75% of the book (ch 18 of 24);
  - any book rule that redefines a series rule ID (Book 2 may add rules, never change Book 1's);
  - duplicate rule IDs.
- Prints no rule text, only IDs and chapters, so it is safe to run in front of the author.

### exposition.py: info-dump counter
- An **exposition run** is a stretch of consecutive paragraphs with no dialogue (no paragraph containing a quotation mark) and no scene break.
- `runs(chapter_text)` returns each run's word count and its first words. `report(chapters_dir, threshold)` lists runs over the threshold by chapter.
- The threshold starts at **400 words** and is replaced by the calibrated value (section 5). The value and its evidence go in `CALIBRATION.md`.

### reads.py: reader logs, ranking and gates
- Reuses `paperbackwriter.reads.stage` for staged release.
- **Log schema** (`log_chNN.json`), written by the reader at each checkpoint:
  ```json
  {
    "after_chapter": 12,
    "premise": "the what-if in one or two sentences",
    "rules": [{"rule": "...", "evidence": [{"chapter": 3, "quote": "exact text"}]}],
    "solutions": [{"route": "how the central problem gets solved", "p_solution": 0.0,
                   "evidence": [{"chapter": 9, "quote": "..."}]}],
    "wonder": [{"chapter": 10, "quote": "..."}],
    "skimmed": [{"chapter": 11, "quote": "...", "why": "..."}],
    "confusion": [{"chapter": 8, "quote": "...", "question": "..."}],
    "what_gave_it_away": "...",
    "craft_problems": [{"chapter": 5, "quote": "...", "problem": "..."}]
  }
  ```
- **Verdict** (`verdict.json`, after the last chapter): `rules_fair`, `solution_earned`, `wonder`, `prose`, `character`, `overall` (1–10 each), `when_solution_became_obvious` (chapter or null), `rule_appeared_too_late` (quotes), `top_5_fixes`.
- `check_log(path, finished=False)` verifies, as the mystery engine does: only chapters through the checkpoint staged (unless `finished`), probabilities in `solutions` sum to 1, and **every quote anywhere in the log is found by exact string search** in its cited chapter.
- `solution_rank(log, keys)`: the plan's private reference file lists `solution_keys`, regexes that identify the intended solution. A route matches if any key matches its text. If no route matches, the probability is 0 and the rank is last. If more than one route matches, the result is `ambiguous` and goes to a grader (below).
- `advance_plan_read(reference, gate, checkpoint)`: the hash-locked gate from the mystery engine, with sci-fi pass rules (section 4). It releases the next digest batch only on a pass.
- **Grader agent:** one narrow question, asked of a fresh agent that is not the reader: "Here are the rules the plan has introduced by chapter N, and the reader's statement of the premise and rules. For each rule: stated, missing or wrong. Is the premise correct?" The grader's JSON answer is saved next to the log. Python does the counting; the grader only judges.

### calibrate.py: reference books
- Imports a public-domain novel from Project Gutenberg into `chNN.txt` files (strips the licence header and footer, splits on chapter headings), so the same reader and tools can run on it.
- First reference: H. G. Wells, *The Invisible Man* (1897), Gutenberg #5230.

### cli.py
`paperbackwriter-scifi` with subcommands: `rules`, `exposition`, `check-read`, `rank`, `gate`, `import-reference`. Staging, digest, proofreading and export are run with the mystery package's `paperbackwriter` command.

## 4. The method

### Plan files (`bookN/plan/`, each under 2,000 words)
| File | Decides |
|---|---|
| `01_novum_and_solutions.md` | The what-if; the central problem; the intended solution with `Uses rules:`; **four or more plausible solutions**, each with real support on the page. The intended one starts as background and is never argued for before 75% |
| `02a_curve.md` | The probability a sharp reader gives each solution, per chapter |
| `02b_rules_and_clues.md` | The rules table (ID, rule, chapter introduced); a clue map per solution, each clue with an innocent reading and a louder scene to sit in |
| `03_resolution_map.md` | Sub-problems raised, doubted and resolved; one wrong solution the lead commits to and acts on; the proof chain from established rules |
| `04`–`07_chapters_*.md` | Chapter skeletons in the mystery engine's planner format (`**Ch N. Title. When. Where.**` + bullets), so `paperbackwriter reader` and `digest` work unchanged |
| `canon.md` | Names, dates, numbers, technology limits, every document's exact wording |
| `audit.md` | The planner's own read at 30, 50 and 70% |

### Rules that outrank the stages
1. **Sanderson's first law:** the solution uses only rules the reader has been given, and no rule the solution needs first appears after 75%.
2. **Four live solutions.** At least three of them have real support on the page, so the reader has something to weigh.
3. **The intended solution looks like background** until late: a tool, a habit or a fact used for something else.
4. **Show the novum before explaining it.** A concrete image or consequence comes first; the mechanism comes later, in dialogue or action, never as a lecture.
5. **No exposition run over the calibrated threshold.**
6. **Wonder on the page:** at least one moment of awe or scale in every reader batch.
7. **Real science is sourced.** Any real-world fact a plot point leans on gets a source in the bible's fact table, or is replaced with an invented one.
8. **The lead acts:** a consequential decision of their own by the quarter mark, and a wrong solution argued aloud and acted on.
9. **Series:** Book 2 may add rules and never contradicts Book 1's. The series rules list is the canon.

### Gates
| Gate | Checkpoint | Pass |
|---|---|---|
| Plan read, clarity | 7 | Grader: premise correct; at least two-thirds of the rules introduced by ch 7 stated; none wrong |
| Plan read, hidden | 12 | Intended solution **not ranked first** |
| Plan read, hidden | 17 | Intended solution at **.35 or less** |
| Rules check (Python) | before drafting and before release | `rules` reports nothing |
| Blind read | end | overall ≥ 7, rules_fair ≥ 7, solution_earned ≥ 7, prose ≥ 7; solution obvious no earlier than one chapter before the reveal; at least one wonder quote per batch |
| Exposition (Python) | before release | no run over the threshold |

### Stop rules (carried over from the mystery engine)
- Plan read fails: redesign the solutions, not the wording. Do not draft.
- A first blind read with solution_earned or rules_fair under 5: back to the plan.
- One fix pass, then stop.
- Any edit after a blind read: read again before release.

## 5. Validation protocol

1. **Calibration (before Book 1):** a full staged read of *The Invisible Man* with the sci-fi reader prompt. Record its scores. Run `exposition` on it, and set the threshold to the 90th-percentile run length of the reference, rounded to the nearest 50 words, unless that is under 300. Write the value and the evidence to `CALIBRATION.md`.
2. **Book 1:** the full route. Every change to a gate, threshold, prompt or schema is a commit with a dated line in `CALIBRATION.md` saying what changed and the evidence.
3. **Freeze:** tag `engine-v1` when Book 1 is released.
4. **Book 2:** run on `engine-v1` with no code changes. Method-doc wording fixes are allowed and logged.
5. **Validated** if Book 2 meets every gate in section 4 on `engine-v1`. If not, `JOURNAL.md` lists each miss and the change it needs; that becomes `engine-v2` before romance starts.

## 6. Privacy and the public history

- The public repo records **process**: code, method, calibration, journal entries with stages and scores. It never holds plot, culprit-equivalents (the intended solution), plans, chapters or reader logs.
- Book folders live in the private `PPW_10212025/series/<series-slug>/`. `.gitignore` here excludes `series/`, `release/` and `*.wav` as a backstop.
- Before each push: a scan for secrets, private paths and the series' character names.

## 7. Testing

- Test-first for every module, with small fixtures in `tests/`.
- The reuse boundary is tested: a test imports each function this project uses from `paperbackwriter` and runs it once, so a dependency upgrade that breaks one fails loudly.
- Before Book 1 drafting: the tools run against the calibration book end to end.

## 8. Cost

The reads cost the most. Glass Island Book 1 took nine plan versions and ten fresh readers to pass. Budget for several plan reads per book, run one at a time in the background, with scores logged in the private `STATUS.md` and the public `JOURNAL.md`.

## 9. Order of work

1. This spec, reviewed.
2. Implementation plan.
3. Code and method docs (test-first), committed as built.
4. Calibration read.
5. Series intake and bible (with the author).
6. Book 1 plan, plan read, draft, blind read, fix, proofread, final read, release; tag `engine-v1`.
7. Book 2 on the frozen engine; validation verdict in `JOURNAL.md`.
