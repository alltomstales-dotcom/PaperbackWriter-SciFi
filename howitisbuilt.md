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

**What the reader made of Wells.** A fresh Opus reader got the book in five batches and filled in the log at each one. Results:
- **Verification:** 290 quotes, every one found word for word.
- **Wonder:** quoted in every batch, 7 to 10 moments each time.
- **Verdict:** overall **7**, rules fair **8**, solution earned **7**, wonder **8**, prose **7**, character **6**. The ending became obvious at chapter 27 of 29.

Its complaints are specific and fair: Griffin's real aim only surfaces in chapter 24, the first murder happens off the page, and the bloodhounds and powdered glass set up for the hunt never decide anything. That last one is a fair-play note a sci-fi engine should catch, a set-up with no pay-off.

The skimming quotes landed where the counter said they would. By the last log the reader had skimmed in chapters 4, 10, 19, 22, 23 and 26, and chapter 26 holds the longest run of narration in the book (819 words). One data point, but it's the first evidence that the exposition counter measures something a reader feels.

Two caveats, both recorded in `CALIBRATION.md`:
- **The reader recognised the book.** Its guesses about the ending don't count as a hiding measurement, but its scores and its quoting do.
- **Our first pattern for "the intended solution" was too loose.** Words like *crowd* and *kill* matched several of the reader's guesses at once. Keys for our books will name the *means* of the solution, not its outcome.

So the bar for Book 1 is clear: **match a classic that's lasted 129 years**, at 7 or better on overall, rules fair, solution earned and prose.

## 2026-10-28 · Task 11 begins: Book 1's plan, and two more seams

Book 1 is planned: a series bible, a rules list (twelve rules, six of them used by the intended solution, all on the page by chapter 8 of 24), the solution curve, a resolution map, the canon, and 24 chapter skeletons. None of the plot appears here; it lives in the private books repo.

Turning the skeletons into the reader's outline exposed two seams between the parent engine and this one. Both are small, and neither would have shown up in unit tests written from the spec alone:
- **Rule IDs would have leaked to the reader.** The method doc said to tag rules inline as `(R1)`, as the mystery engine does with clues. But the parent's converter only strips IDs starting with C, M, T or H. A plan reader would have seen "(R8)" next to the event that introduces the solution's key rule, which is about as loud a spotlight as exists. Planner notes now go on a `Planner:` line that the converter drops.
- **The gate looked for the outline batches in the wrong folder.** The plan check looks in `plan/reader/digest/`, but the gate only looked in `plan/digest/`. The gate now matches the plan check, and a test pins it.

Neither problem would have been found by reading the code. Both turned up the first time the tools ran on a real plan, which is the whole argument for building the engine by writing books with it.

## 2026-10-28 · The first plan read fails, twice over

A fresh reader got Book 1's outline, chapters 1–7, and wrote down the premise, every rule it had noticed (seventeen, with 46 exact quotes) and seven possible solutions. Then a separate grader compared the reader's rules with the plan's rules list. The gate failed: **5 of 10 rules "stated"**, against a pass mark of two-thirds.

On inspection the reader understood the world well. Each of our rules packed two or three claims into one line ("the lift needs the ship overhead; three seats; three hours each way"), and the grader, told not to reward vague answers, marked a rule missing whenever one part was absent. The reader wrote the flood tide's direction almost word for word; the rule was marked missing because it didn't mention the ebb. **The failure was in how we wrote the rules, not in the book.** So the engine changed: one claim per rule, enforced by `rules` (a semicolon in a rule is now an error), and the grader prompt now says a rule is stated when its claim is captured in substance.

The read also found two real problems, and these are the ones that matter:
- **The solution was already visible at 30%.** The reader's second guess, at 20%, was the intended solution, and it quoted the line that gave it away: a joke in chapter 5 that showed a key capability too plainly. The planner's own audit had listed that line as its top risk. The plan reader confirmed it in one batch.
- **A hole in the world.** The reader proposed a way out the plan had never closed off: a perfectly sensible use of the tide. A world where the obvious smart move would work makes characters look stupid for not trying it, so the plan needs a rule that closes it, shown early and innocently.

Per the stop rules, a failed plan read means redesign, not drafting. Version 2 of the plan follows.

**Plan v2.** Four changes, each answering something the v1 reader wrote down:
- **Rules:** split into 21 one-claim rules.
- **The leaking capability** now first appears in chapter 13, inside a scene that serves a different solution, instead of as a joke in chapter 5.
- **The hole** is closed by a new rule, shown when a minor character proposes the idea and the lead tests it on the instruments for a full tide.
- **A decoy** that uses the same resource the wrong way, so a reader who suspects that resource matters has somewhere plausible to put that suspicion.

All the rules the solution uses are still on the page by chapter 13 of 24. And one more seam turned up: `check-plan .` run from inside the plan folder couldn't find the writer brief one level up, because the parent engine asks a relative path for its parent. The wrapper now resolves the path first, with a test.

## 2026-10-28 · Plan v2 fails at the midpoint: don't demonstrate the cure

Plan v2 passed the first checkpoint cleanly: 12 of 16 rules understood, the intended solution nowhere in the reader's seven guesses. At the midpoint it failed. The reader's top guess, at 45%, was the intended solution, and its explanation is the most useful paragraph the engine has produced so far:

> One chapter showed the cure. The next ruled out the small tools on scale, while the one big tool that does exactly that job sat parked nearby.

The lesson is a general one for sci-fi plotting, and the mystery engine has no equivalent. **In a puzzle about *how*, demonstrating the mechanism mid-book is the same as naming the culprit.** Once a reader has seen the cure work at small scale, finding the big version is just a search, and a sharp reader runs it. Closing off the small version made things *worse*: "the robots are far too slow" reads as "so what isn't?"

Plan v3 changes the structure, not the wording:
- **The cure is never demonstrated between the first chapter and the last quarter.** The only time the mechanism is shown, it's a piece of lab history told before anything has gone wrong.
- **The cause of the disaster stays genuinely open** until the turn, with a strong wrong theory held by the person best placed to know. When the expert is wrong for good reasons, the reader's best evidence points away from the answer.
- **The late clue has an innocent reading** that supports the wrong theory.

The two failed reads cost about four minutes of reader time each, and they have already done what the mystery engine's history said they would: they caught, before a word of prose, problems that prose polishing could never have fixed.

## 2026-10-28 · Plan v3 passes, and the answer key is the weak point

Plan v3 passed every checkpoint. At the first, the reader stated 13 of 17 rules in substance. At the midpoint the intended solution sat third of the reader's guesses at 10%. At the three-quarter mark it was second at 12%, and by the last checkpoint the reader had it at 72%. The reader's verdict: rules fair 8, solution earned 7, character 7, overall 7. Those are the same numbers the calibration classic got.

The pass came with a surprise about our own tooling. **Twice the reader named the intended solution and the gate didn't notice.** The gate matches the reader's guesses against a list of key phrases, and the reader had put things in the passive voice or in different words from the key. The keyword list was written in the active voice. Had we trusted it, the midpoint numbers would have looked better than they were. Two engine changes came out of it:
- **At the hiding checkpoints a grader is now required, and its ranking is the one that counts.** A separate strong-model grader reads the reader's guesses and says where the intended solution ranks, by its essential means rather than its wording. The keyword match becomes a cross-check. Two tests pin this: the gate refuses a hiding checkpoint with no grader file, and a grader's ranking overrides a missed keyword.
- **Keys may be widened during a read, never narrowed,** and are tested against passive and hedged paraphrases before the read starts. Widening only ever makes the gate harder to pass, so it can't be used to rescue a failing book.

The reader also told us something about the genre: **on an outline, a sharp reader works out the cause of the disaster by the midpoint.** That's fine. What has to stay hidden is the *means*, meaning the specific tool and how it's used. So the plan's hiding rules are now written about the means.

## 2026-10-28 · Post-read polish (plan v3.1), before any prose

A passing read still comes with a list of weaknesses. This one's were:
- the decisive tool's key setting arrived from nowhere at the turn;
- the strong wrong theory had only authority behind it, not evidence;
- an obvious small-scale alternative was never closed;
- the turn depended on a lucky accident;
- a few characters were introduced and dropped;
- the oxygen arithmetic said different things in different chapters.

We fixed them as v3.1:
- planted two small facts early, each inside the loudest event of its chapter;
- gave the wrong theory real, true evidence that is only part of the story;
- showed the small alternative failing, *after* the last hiding checkpoint so it can't show the cure early;
- added a second, independent clue ahead of the lucky one;
- tied off the loose characters;
- wrote one oxygen ledger into the canon file.

**The v3 read describes v3, not v3.1.** We're not re-reading the outline for polish of this kind. The two new early facts are the risk, and the blind read of the prose will measure them. Any score is valid only for the text it read, and this log says which text that was.

## 2026-10-28 · Drafting Book 1: what the planner caught between agents

Five Sonnet 5.5 agents drafted the 24 chapters in order. Each one read the brief, the plan and every earlier chapter, then wrote five chapters, one file per call. The result was 49,200 words in about 50 minutes of agent time. Between agents the planner (Opus, holding the plan) read the new chapters for four kinds of problem. Each kind was fixed in the text, and then in the brief so the next agent wouldn't repeat it:

- **Winks.** A writer added "she registered it without hearing it" after a planted line. That sentence tells the reader to remember the line. It was cut, and the brief now bans winks.
- **Demonstrating images.** A writer described the key machine in a simile that made it look like it already did the job. A simile can show the cure as clearly as a scene can. It was cut, and the brief now asks for planted pieces to be described flatly.
- **Early pointers at the cause.** A minor character asked to test exactly the material that holds the answer, nine chapters early. Her request now points at her own project. The material stays in the chapter the plan gives it.
- **Fair-play holes the writers found themselves.** Each agent was asked to list canon conflicts it worked around. Two of those lists exposed real holes in the plan: a distance that couldn't fit the map, and a piece of equipment that first appeared in the climax. Under fair play, a piece of hardware that first appears in the climax is a cheat. The fix was to put it on the page the hero reads at the turn, along with her arithmetic.

The writers' conflict lists turned out to be the most useful output of drafting after the chapters themselves: **the people executing a plan are its best reviewers.** The exposition check (`exposition --threshold 300`) found eight runs over the limit across the book. Every one was broken with a line of speech from someone already in the scene.

Draft 1 is tagged. The reader who has seen nothing now reads it in five stages.

## 2026-10-28 · Prose read 1: good scores, and the answer visible from chapter 8

A fresh Opus reader read draft 1 in five stages. Every quote it used was checked against the text: 342 of 342 were exact. Its verdict:
- rules fair 8, solution earned 7, wonder 8, prose 7, character 7;
- overall 7, the same as the calibration classic.

Every score target passed. Hiding failed. The intended solution was the reader's first guess at chapter 7 (38%), at the midpoint (40%) and at the three-quarter mark (55%). The reader said the solution was obvious by chapter 8, ten chapters before the hero works it out.

The reader's "what gave it away" field named the causes exactly, and all of them were ours:
- **The post-read polish leaked.** The two early facts we added in plan v3.1, after the outline read had passed, were the first things the reader quoted. Our own audit had flagged them as the risk and left the prose read to measure them. It did. Without them, the v3 outline had held the solution at 10% at the midpoint.
- **The skeleton leaked into the prose.** One of those plants carried a simile in the planner's own skeleton. The writer copied it faithfully, and the reader quoted it.
- **The narrator pointed.** Four lines told the reader a detail mattered, for example "nobody had ears for it" and "It was not hers yet". One was written by the planner while fixing an earlier wink.

The reader also caught a real science error that four rounds of planning had missed. The electrolysis chemistry was wrong: the second plate makes hydrogen, not oxygen. And as in the outline read, it found loose ends the writers had reported but not resolved.

Three engine changes followed:
- **`pointers`**, a check that flags narration telling the reader which detail matters. It finds 0 such lines in *The Invisible Man*.
- **A stop rule** for a book that scores well but shows its answer early: move each leaking plant so that it first appears as the working tool of a *wrong* solution.
- **Two rules for planners:** add no new solution pieces after a plan read without reading that batch again, and write skeletons flatly.

The plan became v3.2. The two leaking facts now first appear inside the decoys: one as a word in a joke about a rival plan, the other as the means of committing a different, failing rescue. All 24 chapters then went through one fix pass from a single order list, with four Sonnet agents working in parallel. A fresh reader will read the result from the start.

## 2026-10-28 · Prose read 2: the fix pass slowed the leak; the structure decided

The one fix pass followed plan v3.2. Four Sonnet agents worked in parallel from a single order list. The fixes:
- moved the leaking plants into the decoys;
- corrected the chemistry;
- closed every continuity gap the reader had named;
- gave the climax a real setback.

The `pointers` and exposition checks both came back clean.

A fresh reader then read the result from the start. The hiding numbers moved in the right direction:

| Checkpoint | Read 1 | Read 2 |
|---|---|---|
| ch 7 | 1st, 38% | 2nd, 20% |
| ch 12 | 1st, 40% | 1st, 35% |
| ch 17 | 1st, 55% | 1st, 45% |

It wasn't enough. Read 2's verdict: rules fair 8, solution earned 7, wonder 7, prose 7, character 6, overall 6. That is one point below read 1's overall. Read 1 and read 2 are different readers on different texts, so a one-point swing is within the noise we'd expect. What the two agree on matters more.

**Both readers got the cause by chapter 3 or 4,** from different clues each time. And once you know the cause, this plot made the cure the next thought. That's a property of the plot's structure, and no sentence-level fix could remove it. The engine now says so in the plan rules: **the cause and the cure must not share an object.** If they do, a decoy cure using a different tool of equal power has to be argued, acted on, and fail late.

Read 2 found one more signal we'd introduced while fixing read 1. Giving the geochemist a reason she was kept off the samples made the reader suspicious. A blocked test or a too-neat lab result reads as the author hiding something, so blocked evidence now has its own rule.

Under the stop rules, that was Book 1's one fix pass. Book 1 now goes to proofreading (hard errors only), a final read of the exact text being released, and export. Its scores will be what they are. Book 2 will be written on the frozen engine with these rules in it, and its hiding numbers are the real test of whether the engine has learned anything.

## 2026-10-29 · Book 1 released, and the engine frozen

The proofread was done by an Opus agent and limited to hard errors. It found 79, every one an exact-string fix that the parent engine's `proof` command applies only where the old text occurs exactly once:
- 40 calendar dates turned into "Day N";
- 22 contradictions between chapters;
- 7 arithmetic slips;
- 5 typos;
- 5 places where the last chapters broke the book's own biology.

Under the engine's own rule, any edit after a read needs another read before release. So a third fresh reader read the exact text being released. Its verdict: rules fair 8, solution earned 8, wonder 7, prose 8, character 7, **overall 7**. Every score target passed. Hiding failed for the third time (obvious by chapter 8).

Three readers read three versions. Taken together, they say something useful about the engine:
- **Scores are stable at about 7 and track the calibration classic.** Overall went 7, 6, 7, and rules fair was 8 every time. The grading is consistent enough to steer by.
- **Hiding is decided at the plan, and our plan had a structural flaw no prose could fix.** The cause and the cure overlapped. Every reader found the cause by chapter 3–8, and the cure followed. The fix pass slowed this down: chapter 7 went from first at 38% to second at 20%. It could not stop it.
- **The tools caught what they were built for.** Every reader quote was verified, 900 or so across three reads, with no invented quotes surviving the check. The pointer and exposition checks held through every edit. The gates refused the hiding checkpoints exactly when they should have.

So the engine is frozen as `engine-v1`. Book 1's lessons are now rules in the plan files: the cause and the cure must not share an object, blocked evidence reads as a signal, and no solution pieces are added after a plan read. Book 2 will be planned and written on `engine-v1` without changing a line of engine code. If Book 2's hiding passes, the lessons worked. If it fails, we'll know the method needs more than rules.

Book 1 is at the private books repo's `b1-release`, with EPUB, PDF and RTF attached.

## 2026-10-29 · Book 2 planned on the frozen engine

Book 2 is the validation run: `engine-v1`, no code changes, no method changes. The only things that moved are the three plan rules Book 1 paid for, and this is the first plan written under them.

**Choosing the problem by the rules, not by taste.** The first question for Book 2's plan was not "what's a good story?" but "what problem has a cause and a cure with nothing in common?" Book 1's cause and cure overlapped, and three readers walked from one to the other. So Book 2's plan (in the private books repo, spoilers) picks a cause that the reader is *meant* to work out early, because Book 1 showed readers get the cause by chapter 3 to 8 anyway. Its cure has no connection to that cause, and the wrong solutions are argued for and acted on with real weight.

**Writing the hiding into the plan as checkable lines.** Every piece of the intended solution has a chapter, a louder event and an innocent reading in the clue map. The pieces sit at least three chapters apart before the two-thirds mark, and each one is either a number in a routine report, a joke, or the working tool of a wrong solution. The plan also bans one whole class of image before the turn, the one that would demonstrate the cure. That is Book 1's "no demonstrating images" lesson turned into a plan-level ban, not a sentence-level fix.

**Checks before anyone reads it.** `rules` passes: 27 rules, every rule the solution uses on the page by chapter 17 of 24. `check-plan` passes once the writer brief exists. The answer key for the plan read was tested against six paraphrases of the intended solution and six near-misses before the read started. The grader stays authoritative at the hiding checkpoints, as Book 1 taught.

Tag `b2-plan-v1`. The staged plan read is running.

## 2026-10-29 · Book 2's plan read: one fail, one pass

**The first read failed, and the leak was mine.** At the chapter-12 checkpoint the reader ranked the intended solution first, at 25%. It got there by joining two lines: a number in a routine report in chapter 2, and a passing grumble in chapter 8. Neither line had a job in its scene. A planted fact with no job reads as a plant. Book 1 had already learned to make each piece the working tool of a wrong solution, but I had done that for only three of the five pieces. Worse, the chapter 2 skeleton had a narrator wink in it ("nobody looks up…"), written by me, the planner, in the plan itself. The engine's `pointers` check runs on prose, not on skeletons. Lesson: read skeletons with the same eye.

A second finding is about the method. My prompt for that read added a phrase inviting the reader to hunt for hidden pieces, which the frozen template doesn't have. It's ledgered as a deviation, and every later read uses the template word for word.

**The fix redesigned the plants, not the sentences.** That is the stop rule. The two leaking facts moved to after the last hiding checkpoint, and each went inside a wrong solution's scene. The problem, the solutions and the turn stayed the same.

**The second read passed every gate:**
- clarity 14/17 at chapter 7;
- intended solution absent at chapter 12;
- 30% at chapter 17, tied first (the gate is at most 35%);
- 60% at chapter 21;
- verdict: rules fair 8, earned 8, character 7, overall 8.

That is the first plan in this project to hide its solution past the checkpoints. It did it on the same frozen engine that failed Book 1's hiding three times. What changed was only the plan rules Book 1 paid for.

**The price was fairness, and we chose to pay it knowingly.** The read's top complaint: one rule the solution needs is stated just one chapter before the turn. That is fair, but thin. Moving it earlier would put a piece of the solution before the last hiding checkpoint, which needs a re-read. Before the read, the audit set the rule: redesign only if rules-fair falls below 7. It scored 8, so the fact stays where it is, and the drafting notes ask for it to be made clear and concrete.

**The read also caught arithmetic I got wrong.** The air ledger ran out half a day before the date the characters speak. The reader saw the three spoken projections disagree, and it couldn't derive a deadline from them. Re-running the ledger showed why: I had given the cabin air too small a share. The fix is one continuous clock, with every spoken projection listed by chapter for the writers. It also caught a chemistry slip: the white mineral crust forms at the cathode, not the anode. All of these fixes go into a drafting-notes file outside the hashed plan, so the plan that passed is exactly the plan that was read.

Tags `b2-planread-v1-fail`, `b2-plan-v2`, `b2-planread-v2-pass`. Drafting starts next: five Sonnet agents in order, same as Book 1.

## 2026-10-29 · Book 2 drafted, and the hiding held in prose

Five Sonnet agents drafted the book in order, each from the same brief with only the chapter range changed. Between agents, the planner checked the batch:
- the two tools (`pointers`, `exposition`), which came back empty every time;
- a word scan for the images the plan bans before the turn;
- a read of every planted line.

I trimmed four lines by hand. Each one did the same thing: it gave a planted piece a little more light than the skeleton did. One was a comic aside that made a planted fact vivid. Another was a phrase that echoed the ending. The writers follow the hiding rules well, but they still decorate. The planner's job between agents is to take the decoration off the planted lines.

**The prose read passed every target, hiding included.** That is the first time in this project:

| Checkpoint | Result |
|---|---|
| ch 7 | clarity 16/17; intended solution absent |
| ch 12 | absent (rank grader null) |
| ch 17 | absent (rank grader null), reader's front: resupply .30 |
| ch 21 | first at .45, after the turn |
| verdict | rules fair 8, earned 8, wonder 7, prose 8, character 7, overall 8; obvious at ch 19, the turn itself |

Book 1, on the same frozen engine, was obvious by chapter 8 in all three reads. The difference is all in the plan. Book 2's cause and cure share no object. Every planted piece is the working tool of a wrong solution, or sits inside one's paperwork. And the two pieces that leaked in the plan read were moved past the last checkpoint before a word of prose was written. The hiding was decided at the plan, measured at the plan, and it held in prose. That is the claim this whole method makes, and Book 2 is the first evidence for it.

**What the read found instead was a stakes problem.** The reader worked out something I hadn't: run honestly, the arithmetic behind the threat made the most obvious decoy survivable, so its failure was weaker than the book claimed. The fix, in the one fix pass, is a plot change after the last hiding checkpoint that touches no piece of the solution, so the decoy fails clearly. The read also caught a geometry contradiction the ending depends on, and a handful of characters and facts that turn up only when they're needed.

The reader again asked to move that late rule earlier. Again, no: that is a solution piece placed before the last checkpoint after a read, the exact way Book 1 leaked. The score it costs is one point of rules-fair at most, and the read already gave 8.

Tags `b2-draft-1`, `b2-read-1`. The fix pass is running as four parallel Sonnet agents from one order list, as in Book 1.

## 2026-10-29 · The fix pass, a second reader, and what a calculator finds

Four Sonnet agents worked the one fix pass in parallel from a single order list. The order list did most of its work through five shared decisions (D1–D5) at the top, each fixing one fact several chapters depend on. Every agent obeyed the same five lines, so four people editing six chapters each couldn't drift apart on the facts that matter.

**A second fresh reader read the fixed text, and every target passed again:**
- rules fair 8, earned 8, wonder 8, prose 8, character 7, overall 8;
- obvious at chapter 18, one before the turn.

Hiding passed too, but closer to the line. At chapter 17 this reader ranked the intended solution first at .35, exactly the gate. Read 1 had it absent at that point, and the plan read had .30. So the honest number for this plan is about .30–.35 at the last checkpoint for a sharp reader. Read 1's "absent" was the lucky end of the range, not the norm.

Two readers on two versions also tell us how much a single read's number moves, which is worth knowing before trusting any one read.

**What the fix pass broke, and why the method expects it.** The pass added a line in chapter 1 that introduces a background fact early, as the first reader asked. The second reader immediately caught that chapters 2 and 7 still treat it as news. Every edit to plant something earlier creates a contradiction somewhere later. That is why the method allows one fix pass, then a proofread limited to exact-string fixes, then a final read of the exact text.

**What a reader with a calculator finds.** Both readers checked the arithmetic. The first found that the threat didn't survive an honest sum, which the fix pass solved. The second found a deeper one: a buffer quantity in the canon is several times too small for the setting's own physical dimensions, so the clock has far more slack than the story admits. That number has been in the canon since plan v1, and no check caught it. The plan read didn't (outlines don't invite the sum), the drafting agents didn't, and I didn't.

It is too deep to fix in a proofread, because the whole countdown rests on it. So the book is made consistent with itself, and the gap is recorded here. Lesson for the planner, to add before Book 3: **every number the clock depends on gets a physics check in the plan, before the plan read.** That means the volumes, the rates and the buffers, not only the arithmetic between them. A sharp sci-fi reader treats the canon as a problem set.

Tags `b2-fix-1`, `b2-read-2`. Proofread next, then a final read of the exact released text.

## 2026-10-29 · Book 2 released, and what two books say about the engine

The proofread made 37 exact-string fixes. One more fresh reader then read the exact text being released. Its scores: rules fair 8, solution earned 8, wonder 7, prose 8, character 7, overall 7. The solution was obvious at chapter 18, one chapter before the turn. Hiding passed again: the solution was absent at chapter 12 and ranked .30 at chapter 17. Every target the engine sets was met. Book 2 is released in the private books repo as `b2-release` (EPUB, PDF, RTF; 47,941 words).

**The comparison this project was built to make:**

| | Book 1 (engine built while writing) | Book 2 (engine frozen) |
|---|---|---|
| Plan reads to pass | 3 | 2 |
| Prose reads | 3 | 3 |
| Overall | 7, 6, 7 | 8, 8, 7 |
| Hidden at ch 17 | first at .45–.55 every read | absent, .35, .30 |
| Became obvious | ch 7–8 | ch 19, 18, 18 |

Same engine code, same prompts, same models in the same roles. What changed between the books is three plan rules, each bought with a Book 1 failure:
1. The cause and the cure share no object.
2. Blocked evidence reads as a signal.
3. Every planted piece has a job inside a wrong solution, or it waits until after the last checkpoint.

**Predictability is the property the brief asked for, and Book 2 shows it.** Three independent readers, each reading a different version, agreed within one point on every score. At the last hiding checkpoint they agreed within .05 once the fixes were in. The gates fired where an editor would have pushed back, and passed where an editor would have let the book through. Two books aren't proof. But the second book did what the first book's lessons said it would, on an engine that didn't change.

**What no gate caught** was a physics error in the canon numbers. One buffer quantity in the canon was physically several times too small, and only a reader with a calculator found it. That's the next rule for the plan files: physics-check every number the clock rests on before the plan read. It's the first change for the next engine version, and it goes into the romance engine's design from the start.

## 2026-10-29 · A spoiler leak in the public history, and a scan to stop the next one

A whole-branch review, run fresh on the most capable model, found the build's one critical problem. It wasn't in the code. While writing this history, the journal, the calibration notes, the skill and three tests, I had named the solution mechanisms of both books. This repo is public, and the books are meant to be read cold.

What was done:
- Every affected line was rewritten in abstract terms ("the cause and the cure share no object" instead of naming either). The test fixtures now use neutral sentences.
- New command `paperbackwriter-scifi spoilers --terms PATH`. It scans every git-tracked file against a private list of regexes kept in the private books repo, one per line, case-insensitive. It reports file, line and pattern number only, never the matched text, so the report can't leak either. A missing list is an error, not a clean pass.
- A local `pre-push` hook runs it, so a push with a hit is refused.

The first scan had one false positive: a programming word matched a solution term. The term was narrowed to the forms the books actually use.

**Lesson:** the reader's rule ("no plot in anything a reader may see") has to cover the build log as well as the book. A rule a writer has to remember fails on the twentieth commit. A scan that runs on every push doesn't. The earlier commits still hold the old wording; whether to rewrite the public history is the owner's call, not the engine's.
