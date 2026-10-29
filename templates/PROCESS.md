# How these books are written

A hand-off document for any agent (Claude, Codex or a person) picking up <Series Name>. It has no spoilers. Current progress is in `STATUS.md`, next to this file.

## The one rule about the author

If the author reads each book cold, **never put the intended solution, the rule it turns on or a twist in a message to them, in `STATUS.md`, in this file, in the bible, in `SERIES_RULES.md` or in the build brief.** Solutions live only in `bookN/plan/` and `bookN/blind_read/`. Report results as numbers and stages.

## What we are building

<Number> near-future science-fiction novels, about <24> chapters and <50,000> words each, set in <the closed setting>. The lead is <who>. Each book's central problem is solved, late, by rules the reader was given. Full answers are in `BUILD_BRIEF.md`. Series canon is in `SERIES_BIBLE.md` and `SERIES_RULES.md`.

## Where things are

```
series/<slug>/
  PROCESS.md, STATUS.md, AGENTS.md   this hand-off
  BUILD_BRIEF.md                     what the author asked for, and what was assumed
  SERIES_BIBLE.md, SERIES_RULES.md   setting, science, cast, voice, world rules. No spoilers
  bookN/plan/                        SPOILERS. Plan files, reader/ outlines, reader/digest/ batches
  bookN/WRITER_BRIEF.md              SPOILERS. Instructions for drafting agents
  bookN/chapters/chNN.txt            the book
  bookN/invented.md                  small details writers made up, one line each
  bookN/blind_read/<date>/           SPOILERS. Reader logs, grades, verdicts
  bookN/release/                     final files
```

The method is in `.claude/skills/writing-scifi-novels/` of the PaperbackWriter-SciFi repository (`SKILL.md`, `intake.md`, `plan-files.md`, `writer-brief.md`, `blind-read.md`).

## The route, one book at a time

| # | Stage | Who | Output | Gate |
|---|---|---|---|---|
| 1 | Plan | The strongest reasoning model available | plan files, `canon.md`, `audit.md` | `paperbackwriter-scifi rules` clean; each file under 2,000 words |
| 2 | Plan read | A fresh reader and a fresh grader | `blind_read/<date>-plan/` | Clarity at checkpoint 1; intended solution not first at 2; ≤ .35 at 3 (`paperbackwriter-scifi gate`) |
| 3 | Draft | A drafting model, five chapters per agent, in order | `chapters/` | Each agent reads all earlier chapters and obeys canon |
| 4 | Blind read | A fresh agent, chapters released in stages | `blind_read/<date>/` | Overall, rules fair, solution earned, prose 7; wonder in every batch |
| 5 | One fix pass | A drafting agent, from a list of exact orders | changed chapters | One pass only, then read again |
| 6 | Proofread | A fresh agent, hard errors only | `proof_fixes.json` | Exact-string edits (`paperbackwriter proof`) |
| 7 | Final read and release | A fresh agent, then the build | `release/` | No exposition run over the threshold; the score describes the final text |

## Stop rules

- Plan read fails: redesign the solutions. Do not draft.
- Rules fair or solution earned under 5 on the first blind read: back to the plan.
- After one fix pass, stop fixing.
- Any edit after a blind read: read again before release.

## Practical limits

- An agent that writes several chapters or plan files in one reply runs out of output and saves nothing. One chapter per file write.
- Keep every working file in the books repo, committed and tagged. Scratch folders get deleted.

## Keeping the log

Add a dated line to `STATUS.md` at each stage change and each read. Scores and stages only.
