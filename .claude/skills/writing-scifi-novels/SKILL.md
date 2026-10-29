---
name: writing-scifi-novels
description: Use when planning, drafting, blind-reading, fixing, proofreading or releasing a near-future, idea-driven science-fiction novel or series with PaperbackWriter-SciFi — the staged route where the solution to the central problem stays hidden until late and then plays fair with the world's rules.
---

# Writing Sci-Fi Novels

## Overview

The sci-fi engine is the mystery engine's method with a different hidden thing. A mystery hides **who**; this hides **how the central problem gets solved**, and then proves the solution used only rules the reader was given.

**Core principle:** the hiding and the fairness are designed in the plan and measured by a reader who has never seen it. Prose passes cannot add either.

Tools: `paperbackwriter-scifi` (this repo) and `paperbackwriter` (the mystery package, for staging, digests, proofreading and export).

## Where files go (the private books repo)

```
series/<series-slug>/BUILD_BRIEF.md  SERIES_BIBLE.md  SERIES_RULES.md  PROCESS.md  STATUS.md
series/<series-slug>/bookN/plan/                 plan files, reader/, reader/digest/, reference + gate JSON
series/<series-slug>/bookN/WRITER_BRIEF.md
series/<series-slug>/bookN/chapters/chNN.txt
series/<series-slug>/bookN/blind_read/<date>/    staged text, log_chNN.json, grade_chNN.json, verdict.json
series/<series-slug>/bookN/release/
calibration/<book>/chapters/  calibration/<book>/read/
```

Commit every artefact change and tag each iteration: `b1-plan-vN`, `b1-planread-vN-pass|fail`, `b1-draft-N`, `b1-read-N`, `b1-fix-1`, `b1-proof`, `b1-final-read`, `b1-release`. Tag messages carry scores, never plot.

## Stages

| # | Stage | Who | Output | Gate |
|---|---|---|---|---|
| 0 | Intake | You and the author | `BUILD_BRIEF.md` | Author confirms or leaves rows marked assumed. See `intake.md` |
| 1 | Series bible and rules | You | `SERIES_BIBLE.md`, `SERIES_RULES.md` | No solution in either |
| 2 | Book plan | You, one file per turn | `plan/` | `paperbackwriter-scifi rules`; `paperbackwriter check-plan` (structure). See `plan-files.md` |
| 3 | Plan read | Fresh reader + fresh grader | `blind_read/<date>-plan/` | `paperbackwriter-scifi gate` at every checkpoint |
| 4 | Draft | Sonnet 5.5, five chapters per agent, in order | `chapters/` | Each agent's self-check. See `writer-brief.md` |
| 5 | Blind read | Fresh reader, staged | `blind_read/<date>/` | Targets below |
| 6 | One fix pass | Sonnet 5.5, from an order list | changed chapters | Read again |
| 7 | Proofread | Fresh agent | `proof_fixes.json` | `paperbackwriter proof` |
| 8 | Final read and release | Fresh reader, then the build | `release/` | Read the exact text that ships; `paperbackwriter export` |

## Rules that outrank the stages

1. **Sanderson's first law.** The solution uses only rules the reader has been given, and no rule it needs first appears after 75%.
2. **Four live solutions.** At least three have real support on the page, so the reader has something to weigh.
3. **The intended solution looks like background.** Its pieces appear early doing something else: a tool, a habit, a fact used for another purpose. It is never argued for before 75%.
4. **Show the novum before explaining it.** A concrete image or consequence first. The mechanism comes later, in dialogue or action, never as a lecture.
5. **No exposition run over the calibrated threshold** (see `CALIBRATION.md`), **and no narration pointers** (`pointers` lists them; run it on every drafted batch before committing).
6. **Wonder on the page.** At least one moment of awe or scale in every reader batch.
7. **Real science is sourced.** Any real fact a plot point leans on has a source in the bible's fact table, or is replaced with an invented one.
8. **The lead acts.** A consequential decision of their own by the quarter mark, and a wrong solution argued aloud and acted on.
9. **Series canon.** Book 2 may add rules and never contradicts Book 1's. `SERIES_RULES.md` is the canon.

## Gates

| Gate | When | Pass |
|---|---|---|
| Clarity | Plan read, checkpoint 1 | Grader: premise correct; ≥ 2/3 of rules introduced so far stated; none wrong |
| Hidden | Plan read, checkpoint 2 | Intended solution not ranked first |
| Hidden | Plan read, checkpoint 3 | Intended solution at .35 or less |
| Rules | Before drafting, before release | `paperbackwriter-scifi rules` reports nothing |
| Blind read | End | overall, rules_fair, solution_earned, prose ≥ 7; ≥ 1 wonder quote per batch; obvious no earlier than one chapter before the reveal |
| Exposition | Before release | No run over the threshold |

## Stop rules

- Plan read fails: redesign the solutions, not the wording. Do not draft.
- First blind read with rules_fair or solution_earned under 5: back to the plan.
- One fix pass, then stop.
- Any edit after a blind read: read again before release.

## Who does what

| Job | Model |
|---|---|
| Bible, rules, plan, audit | The strongest reasoning model available |
| Drafting, fix pass | Sonnet 5.5 |
| Reader, grader, proofreader | A fresh agent on a strong model, never one that has seen the plan |
| Counting (quotes, rules, exposition, ranks) | Python, never a model |

Agents die at their output limit with nothing saved. One chapter per file write, one plan file per turn.

## Common mistakes (carried from the mystery engine, plus sci-fi's own)

| Mistake | What it causes |
|---|---|
| Explaining the novum in chapter 1 | The reader skims; the clarity gate passes but wonder fails |
| Introducing the key rule in the climax | Rules check fails; "deus ex machina" in the verdict |
| Making the intended solution's piece louder to fix fairness | The reader solves it at 50% |
| One solution with all the support | The reader ranks it first at 30% and never moves |
| Editing a line to hide one tell | The edit creates another two chapters earlier |
| Trusting an in-house score | Self-ratings ran about three points high in the parent engine |
