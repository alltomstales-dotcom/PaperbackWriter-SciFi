# Blind read (stages 3, 5 and 8) and the grader

The acceptance test. A reader who does not know the solution and cannot read ahead writes down, at fixed points, what they understand of the world and how they think the central problem will be solved, with exact quotes.

## Set-up

- **A fresh agent** on a strong model that has never seen the plan, the bible's book sections or an earlier draft.
- **Staged release.** `paperbackwriter stage bookN/chapters bookN/blind_read/<date> <checkpoint>` for prose, or the gate's batch release for a plan read. Later text never exists in the folder early.
- **Checkpoints:** `paperbackwriter.outline.checkpoints(n)`: 7, 12, 17, 21, 24 for 24 chapters.
- **Verify every log:** `paperbackwriter-scifi check-read <log> --key <regex>` (keys stay private).

## Reader prompt

```
You are a demanding science-fiction reader and editor. You are reading a novel you have
never seen, in batches. You do NOT know how it ends, and the later chapters do not exist
yet on disk, so do not look for them.

The text is in <outdir> (chNN.txt files, or batchN.md outline batches). The first line of
each chapter is its title as a reader sees it. Read everything released so far, in full.

At each checkpoint write <outdir>/log_chNN.json (NN = last chapter read):
{
  "after_chapter": N,
  "premise": "the story's central what-if, in one or two sentences",
  "rules": [{"rule": "a rule of this world as you understand it",
             "evidence": [{"chapter": n, "quote": "exact words from the text"}]}],
  "solutions": [{"route": "how you think the central problem will be solved",
                 "p_solution": 0.0-1.0,
                 "evidence": [{"chapter": n, "quote": "..."}]}],
  "wonder": [{"chapter": n, "quote": "a moment of awe or scale that worked on you"}],
  "skimmed": [{"chapter": n, "quote": "where you started skimming", "why": "..."}],
  "confusion": [{"chapter": n, "quote": "...", "question": "what you could not follow"}],
  "how_confident": "guess | lean | fairly sure | certain",
  "what_gave_it_away": "the specific moments, quoted, or 'nothing yet'",
  "craft_problems": [{"chapter": n, "quote": "...", "problem": "..."}]
}
List at least three solutions if you can think of them; p_solution across them sums to 1.
Every quote must be copied exactly from the text. It will be verified by string search,
and an invented quote voids the log. Leave a list empty rather than invent an entry.
Judge honestly: if the solution is obvious, say so and say when you knew.
Then STOP and reply with a two-line summary. The next batch will be released.

After the final chapter also write <outdir>/verdict.json:
{"rules_fair": 1-10, "solution_earned": 1-10, "wonder": 1-10, "prose": 1-10,
 "character": 1-10, "overall": 1-10,
 "when_solution_became_obvious": chapter or null,
 "rule_appeared_too_late": [{"chapter": n, "quote": "..."}],
 "fair_play_notes": "did the ending use only rules you were given?",
 "top_5_fixes": ["...concrete, with chapter numbers..."]}
```

For a **plan read**, the reader gets outline batches instead of chapters; drop `wonder`, `skimmed` and `craft_problems` (an outline has no prose) and keep the rest.

## Grader prompts (a separate fresh agent, never the reader)

**Clarity, checkpoint 1.** Give the grader the rules introduced by the checkpoint (IDs and text, from `02b_rules_and_clues.md`), the novum paragraph from `01`, and the reader's `premise` and `rules`:

```
Here is what a story has established so far: its premise and a numbered list of rules.
Here is a reader's own account of the premise and the rules. For each numbered rule, say
whether the reader's account states it (in any words), misses it, or states it wrongly.
Say whether the reader's premise is correct. Do not reward vague statements.
Write <outdir>/grade_chNN.json:
{"premise_correct": true|false,
 "rules": [{"id": "R1", "verdict": "stated|missing|wrong", "note": "..."}]}
```

**Ambiguous rank.** When `gate` reports that the solution keys matched several routes, give the grader the intended solution (one paragraph) and the reader's `solutions` list:

```
Which of these routes, if any, is the same solution as the one described? Answer with its
index, or null if none is. Write <outdir>/rank_chNN.json: {"route_index": n or null, "why": "..."}
```

## Targets

| Measure | Target |
|---|---|
| Plan read checkpoint 1 | Clarity passes |
| Plan read checkpoint 2 | Intended solution not first |
| Plan read checkpoint 3 | Intended solution ≤ .35 |
| Blind read verdict | overall, rules_fair, solution_earned, prose ≥ 7 |
| Wonder | ≥ 1 quote in every batch's log |
| Became obvious | No earlier than one chapter before the turn |
| Exposition | No run over the calibrated threshold |

Calibration anchors (what a 7 means for this reader) are in `CALIBRATION.md`.

## Reading the result

- "What gave it away" is the finding; the scores only say which stage to go back to.
- Clarity fails: the novum is explained too late or not at all; show it in action earlier.
- Solution first at 50%: one solution has all the support, or the intended one was spotlit. Back to file 01.
- rules_fair low: a rule arrived late or was stated only in the climax. Plant it earlier, in action, with an innocent use.
- Wonder empty in a batch: the plan has no moment of scale there. Add one to the skeleton, not to the prose.
- Skimmed quotes cluster: an exposition run. Cut it or turn it into a scene.

Record each read: date, text read, scores, the checkpoint ranks, and what gave it away (scores only in public files).
