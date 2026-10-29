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
