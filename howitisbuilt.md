# How it is built

A running account of how this engine is being built: what was done, what was found, and why things changed. Newest entries at the bottom. It records process only; nothing here reveals a book's plot or solution.

The other logs:
- [`JOURNAL.md`](JOURNAL.md): one line per stage, with scores.
- [`CALIBRATION.md`](CALIBRATION.md): every gate and threshold change, with the evidence for it.
- The git history: every step as a commit.

---

## 2026-10-28 · Where this came from

[PaperbackWriter](https://github.com/alltomstales-dotcom/PaperbackWriter) writes fair-play mysteries with AI agents. Its one big idea: **a mystery fails when the reader guesses early, so test for that directly.** A fresh agent reads the book a few chapters at a time and writes down, with exact quotes, whom it suspects and how strongly. The book only moves forward if the real culprit stays out of the reader's top two until late. That route took its books from blind-read scores of 2–3 to 7–8.

The author asked for the same machinery in other genres, as **separate projects**, leaving the mystery engine untouched. Sci-fi first, then romance. Each engine is validated by writing a pair of books.

## 2026-10-28 · Finding sci-fi's version of "who did it"

Stripped of the murder, the mystery engine does three things:
1. It tracks **one reader belief** at checkpoints.
2. It **gates** on that belief: hidden until late, fair at the end.
3. It **verifies everything mechanically**: quotes by string search, answers hash-locked before the read.

Parts 2 and 3 carry over. Part 1 has to be found for each genre. For idea-driven sci-fi it is: **how will the central problem be solved, and does the solution play fair with the world's rules?** That gives a direct mapping:

| Mystery | Sci-fi |
|---|---|
| Six suspects | Four or more plausible solutions |
| Clue map | Rules list, each rule with the chapter it first appears in |
| Fair play | No rule the solution needs may first appear after 75% (Sanderson's first law) |
| Culprit probability curve | Solution probability curve |
| Physical proof | The solution follows from rules already given |

Sci-fi adds two failures mysteries rarely have:
- **Info-dumps:** these are countable, so Python measures runs of exposition.
- **A missing sense of wonder:** the reader quotes moments of awe, and every batch needs at least one.

**Choices made with the author:**
- Near-future SF in one closed setting (a station, colony or ship), closest to the closed circle that works for mysteries.
- The pair of books is Book 1 and Book 2 of a series.
- Architecture: a separate repo that installs the mystery package, pinned to a version, and reuses only its genre-neutral tools (staging, outline batches, proofreading, export, narration).

## 2026-10-28 · Spec and plan

- **Spec:** [`docs/superpowers/specs/2026-10-28-scifi-engine-design.md`](docs/superpowers/specs/2026-10-28-scifi-engine-design.md).
- **Plan (12 tasks):** [`docs/superpowers/plans/2026-10-28-scifi-engine.md`](docs/superpowers/plans/2026-10-28-scifi-engine.md).
- **Calibration book:** H. G. Wells, *The Invisible Man* (1897). It is public domain, and the reader's scores on it anchor what a "7" means. Its prose also sets the exposition threshold, so the threshold isn't a guess.
- **Validation design:** Book 1 builds and tunes the engine. The engine is then frozen as `engine-v1`, and Book 2 runs on it unchanged. If Book 2 passes every gate with no code changes, the pipeline is predictable.

**A finding while planning:** the spec originally kept book drafts in a private folder inside an older repo. That repo's git remote URL embeds an access token, so it is the wrong place for anything to be pushed from. Instead, the author asked for every iteration of the books to be uploaded as a versioned object. Book work now goes in a separate **private** repo, with an annotated git tag per iteration (`b1-plan-v1`, `b1-planread-v1-fail`, `b1-draft-1`, …). The tag messages carry the scores.

**A finding about the calibration text:** the Gutenberg file has Windows line endings and `_underscore_` italics. It has 28 chapters headed `CHAPTER I.` with the title on the next line, plus a separate `THE EPILOGUE`. The contents list also has lines like `I. The strange Man's Arrival`, and one chapter's prose has a line starting `I. And out came…`, so chapter detection can only trust the `CHAPTER` headings. The importer was designed around this before any code was written.

## 2026-10-28 · Task 1: scaffold and the reuse boundary

- The mystery repo got one tag, `v0.1.0`, and no code change. This repo installs `paperbackwriter @ git+…@v0.1.0`, so the mystery engine can keep evolving without breaking this one.
- `tests/test_reuse.py` calls every borrowed function once. These tests passed on the first run, which is expected, since they test code that already exists. Their job is to fail loudly if a later upgrade of the dependency changes something this engine relies on.

## 2026-10-28 · Task 2: the rules list

`pbw_scifi/rules.py` reads the world's rules from a Markdown table (`| R7 | rule | ch 5 |`) and checks the solution against them. The checks:
- every rule the solution uses (`Uses rules: R2, R5`) exists;
- none of them first appears after chapter 18 of 24;
- Book 2 never redefines one of Book 1's rules.

**Design point:** the checker's messages carry rule IDs and chapter numbers, never the rule text. It can run in front of an author who reads the book cold without spoiling anything, and a test enforces that.

**Robustness:** the author's tables won't be tidy, so the parser accepts `**R2**`, `Ch. 3`, `chapter 20` and `introduced: ch 5`. A row it can't read is an error, not a silent skip, because a silently dropped rule would make the fair-play check pass when it shouldn't. Tests: 10, written first, watched fail, then passed.

## 2026-10-28 · Task 3: the exposition counter

`pbw_scifi/exposition.py` measures **exposition runs**: stretches of paragraphs with no dialogue and no scene break. Long runs are where readers skim, and sci-fi is prone to them because the world has to be explained.

**What counts as dialogue:** any straight or curly double quote, or an opening single curly quote (`‘`). The closing single quote `’` is also an apostrophe ("man’s"), so on its own it doesn't count.

**The threshold is calibrated, not guessed:** it's the 90th-percentile run length of a reference novel, rounded to 50 words, with a floor of 300.

**First real measurement:** run against a finished 55,600-word mystery from the parent engine (one that scored 7–8 with blind readers), the counter found:
- 268 runs, with a 90th percentile of only **225 words**;
- 4 runs over 400 words, the longest 543.

A well-reviewed book in this pipeline's house style rarely goes a page without someone speaking. That's useful context for whatever *The Invisible Man* produces: a Victorian novel will likely run longer, so the floor of 300 may be what actually applies.

## 2026-10-28 · Task 4: reading the reader

`pbw_scifi/reads.py` checks a sci-fi reader's checkpoint log. Unlike the mystery log (one list of suspects), it has several parts:
- the premise and rules in the reader's own words;
- a probability for each way the central problem might be solved;
- quoted moments of wonder, skimming and confusion.

The rule carried over unchanged: **every quote anywhere in the log must be found word for word in the chapter it cites.** One invented quote voids the log. In the parent engine's history this check passed 164 of 164 real quotes, so readers do quote accurately; the check exists so we never have to assume it.

**Finding the intended solution among the reader's guesses.** A mystery reader names a person, so matching is easy. A sci-fi reader describes a *method* in their own words ("they vent the spine to stop the spin"). The plan therefore keeps a private list of patterns that identify the intended solution, written before the read. Three outcomes:
- **one route matches:** its rank and probability are recorded;
- **no route matches:** the reader hasn't thought of it, which counts as hidden;
- **several routes match:** the patterns are too loose, so a separate grader agent picks one, and the choice is saved next to the log.

## 2026-10-28 · Task 5: the plan-read gate

The gate is the mystery engine's, with sci-fi pass rules. Before any prose is written, a fresh reader gets the chapter outline in five batches, and the next batch is released **only if the current checkpoint passes**:

| Checkpoint (24 chapters) | Passes when |
|---|---|
| 7 (about 30%) | **Clarity.** A separate grader agent compares the reader's premise and rules with the rules the plan has introduced so far. The premise must be right, at least two-thirds of the rules stated, and none stated wrongly. |
| 12 (50%) | The intended solution is **not the reader's first choice** |
| 17 (70%) | The intended solution's probability is **.35 or less** |
| 21, 24 | Recorded, not gated |

**The early checkpoint changed meaning.** In the mystery engine, every early checkpoint asks "is the answer hidden?" In sci-fi, hiding too well at 30% is its own failure: a reader who doesn't yet understand the world can't weigh solutions, so a low score would mean confusion, not misdirection. The first checkpoint therefore tests **understanding**, and hiding is tested from 50% on.

**Answers can't move after the fact.** As in the parent engine, the plan's intended solution and the SHA-256 hashes of the plan and digest files are written to a private reference file before the read starts. If a plan file changes mid-read, the gate refuses to score, so a plan can't be quietly adjusted to pass a read it already failed.

**A grader omission counts against the book.** If the grader's verdict leaves out a rule, that rule counts as *missing*, not stated, so a lazy grade can't pass the clarity gate.

## 2026-10-28 · Task 6: importing the calibration book

`pbw_scifi/calibrate.py` turns a Project Gutenberg text into the engine's own chapter format (`chNN.txt`, first line `Chapter N: Title`). That way the same reader, quote checker and exposition counter run on a classic exactly as they will on our books.

On *The Invisible Man* it produced **29 chapters** (28 plus the epilogue), **48,162 words**, close to our planned book length. Titles came out cleanly ("Mr. Teddy Henfrey’s First Impressions"), `_italics_` became `*italics*`, and hard-wrapped lines were joined into paragraphs. With 29 chapters, the reader's checkpoints fall at chapters 9, 14, 20, 26 and 29.

## 2026-10-28 · Task 7: one command

`pbw_scifi/cli.py` puts the pieces behind one command, `paperbackwriter-scifi`, with seven subcommands. Each prints JSON and exits 0 on a pass, 1 on a failed check and 2 on bad input (a missing file, a malformed rules table). The three exit codes matter for the books repo: a script can stop the pipeline on a 1 without confusing it with a typo.

The command does **not** re-implement anything the parent package already does. Staging chapters for a reader, building outline digests, proofreading and EPUB/PDF export stay in `paperbackwriter`, pinned at the v0.1.0 tag. That's the deal we made at the start: the mystery engine is left alone, and the sci-fi engine depends on a frozen release of it rather than a fork of its code.

## 2026-10-28 · Task 8: writing the method down

The code checks the book; the method tells the agents how to write one that passes. It lives in `.claude/skills/writing-scifi-novels/`, five Markdown files that any agent can read:
- `SKILL.md`: the stages, nine rules that outrank them, the gates and stop rules;
- `intake.md`: what to ask the author and what to assume;
- `plan-files.md`: the seven plan files, including the rules table the checker parses;
- `writer-brief.md`: the template for drafting agents, the fix pass and the proofread;
- `blind-read.md`: the reader prompt, the two grader prompts and the targets.

Writing it down surfaced three changes from the mystery method:
- **"The culprit is never caught lying" became "the solution is never argued for before 75%".** In a mystery the strongest tell was a caught lie. In sci-fi the equivalent is a character who says the right idea aloud early and gets talked out of it: the reader remembers.
- **Rules appear in action, not in lectures.** The rules table records where a rule first appears *on the page*, shown happening. A rule explained in a paragraph of narration is both an exposition run and a spotlight on the solution.
- **Wonder is planned, not hoped for.** Every chapter skeleton has a "Wonder" line. If a reader batch comes back with no wonder quoted, the fix goes into the skeleton, not the prose.

The series templates add one file the mystery series didn't need: `SERIES_RULES.md`, the canon rules of the world. Book 2 can add rules but the checker rejects any that redefine one, which is how a sequel is held to the first book's physics.

## 2026-10-28 · Task 9: a home for every version of the books

Tom asked that every iteration of what the engine writes be uploaded as a versioned object. The books contain spoilers and the engine repo is public, so they can't share a repo. The books live in a **private** GitHub repo, `PaperbackWriter-SciFi-Books`, under one rule: one commit per change and an **annotated git tag per iteration**: `b1-plan-v1`, `b1-planread-v1-fail`, `b1-plan-v2`, `b1-draft-1`, `b1-read-1` and so on. Each tag message carries the scores. Any two versions can be compared with `git diff`, and the release tags get the EPUB and PDF attached.

We considered writing an archiving module and decided against it: git tags already are versioned objects, and a convention written in a README costs nothing to maintain.

## 2026-10-28 · Task 10: calibrating on a classic

Before writing a word of our own, we ran the whole toolchain on H. G. Wells's *The Invisible Man* (1897). Two questions: how long does a real novel let narration run without dialogue, and what does our reader score a book everyone agrees is good?

**Exposition.** The 90th-percentile run of narration without dialogue is **225 words**. That's exactly the same as Glass Island Book 1 from the mystery pipeline. Rounded, it falls under the 300-word floor in the spec, so **the threshold is now 300 words** (from a 400 placeholder). Only three of Wells's runs pass 400 words, and all three are in chapters 26–27, where the manhunt is told in summary rather than in scene. Those are also the pages a modern reader is most likely to skim, which the reader's "skimmed" quotes will confirm or refute.

**Calibration found its first engine bug before Book 1 started.** Laying out Book 1's plan folder, we ran the parent engine's `check-plan` on it and it could never pass: it requires the mystery's file names (`01_solution_and_suspects.md`, `02b_clues.md`). Rather than rename our files to a mystery's vocabulary, or touch the frozen parent, `paperbackwriter-scifi check-plan` now wraps the parent check and swaps in the sci-fi names. Its outline-coverage and digest checks run unchanged. This is the pattern we want for the whole project: reuse the parent's tested logic and change only what the genre changes.
