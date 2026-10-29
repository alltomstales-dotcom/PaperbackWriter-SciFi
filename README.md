# PaperbackWriter-SciFi

A genre engine for writing **near-future, idea-driven science fiction with AI agents**, tested the way [PaperbackWriter](https://github.com/alltomstales-dotcom/PaperbackWriter) tests mysteries: a fresh reader reads the book in stages and says, with exact quotes, how they think the central problem will be solved. The solution has to stay hidden until late, and then play fair with the world's rules.

A mystery hides **who**. This engine hides **how**: the central problem (air running out, a station losing its orbit, a colony cut off) is solved late, using only rules of the world the reader was shown earlier, and a reader who never saw the plan confirms both halves.

**Status:** being built in the open. [`howitisbuilt.md`](howitisbuilt.md) tells the story of the build and what each step found, [`JOURNAL.md`](JOURNAL.md) logs stages and scores, and [`CALIBRATION.md`](CALIBRATION.md) records every gate or threshold change and why. The design is in [`docs/superpowers/specs/`](docs/superpowers/specs/).

## Install

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[pdf,dev]"      # pulls PaperbackWriter v0.1.0 from GitHub
pytest -q
```

## Commands

`paperbackwriter-scifi` adds the sci-fi checks. Staging, outline digests, proofreading and export use the parent package's `paperbackwriter` command unchanged. Exit codes: 0 pass, 1 check failed, 2 bad input.

| Command | What it does |
|---|---|
| `check-plan PLAN_DIR [--chapters 24]` | Structure check of a plan folder: files present, each under 2,000 words, outline covers every chapter, digest batches match (prints no plot) |
| `rules PLAN_DIR [--series SERIES_RULES.md] [--chapters 24]` | Fair-play check: every rule the intended solution uses appears on the page by 75% |
| `exposition CHAPTERS_DIR [--threshold 400]` | Lists runs of narration with no dialogue longer than the threshold |
| `pointers CHAPTERS_DIR` | Lists narration that tells the reader which detail matters ("nobody noticed it", "the right answer", "not hers yet"); dialogue is skipped |
| `calibrate-threshold CHAPTERS_DIR` | The 90th-percentile exposition run of a reference book |
| `check-read LOG [--key REGEX ...] [--finished]` | Verifies a reader's checkpoint log: staging, probabilities, every quote found in its chapter |
| `rank LOG --key REGEX ...` | Where the intended solution sits in the reader's list |
| `gate REFERENCE GATE CHECKPOINT [--chapters 24]` | Scores a plan-read checkpoint and releases the next batch only on a pass |
| `import-reference PG.txt OUT_DIR` | A Project Gutenberg book into `chNN.txt` files, for calibration |

## The gates

| Gate | When | Pass |
|---|---|---|
| Rules | Before drafting and before release | No rule the solution uses first appears after 75% |
| Clarity | Plan read, ~30% | A grader finds the reader's premise right and ≥ 2/3 of the rules so far stated, none wrong |
| Hidden | Plan read, 50% | The intended solution is not the reader's first choice |
| Hidden | Plan read, 70% | The intended solution at .35 or less |
| Blind read | Finished book | Overall, rules fair, solution earned, prose ≥ 7; a moment of wonder quoted in every batch |
| Exposition | Before release | No run over the threshold calibrated on a classic |

## The method

The agent-facing method is plain Markdown in [`.claude/skills/writing-scifi-novels/`](.claude/skills/writing-scifi-novels/): `SKILL.md` (stages and rules), `intake.md`, `plan-files.md`, `writer-brief.md` and `blind-read.md` (reader and grader prompts). Series hand-off templates are in [`templates/`](templates/).

The books themselves, every iteration of them, live in a separate private repository with one git tag per plan, draft, read and fix, so the engine's history and the books' history can be compared step by step.

MIT licensed.
