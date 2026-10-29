# Writer brief (stage 4), fix pass (stage 6) and proofread (stage 7)

Save as `series/<slug>/bookN/WRITER_BRIEF.md`. Fill every `<...>`. Draft in order, five chapters per Sonnet 5.5 agent, one agent at a time. Each agent reads all earlier chapters.

## Template

```markdown
# Writer brief: <title>
B=<absolute path to series/<slug>/bookN>

You are drafting a near-future science-fiction novel set entirely in <the closed setting>.
<Person and tense>, with <lead> as the viewpoint character. Tone: <tone from the bible>.

Read first, in full:
- <absolute path>/SERIES_BIBLE.md and SERIES_RULES.md
- $B/plan/canon.md, 01, 02a, 02b, 03, 04 to 07
- $B/plan/audit.md (its fixes override the earlier files)

Then read every chapter already in $B/chapters/ in full. Canon wins any conflict.

Your chapters: <N to M>. Output: $B/chapters/chNN.txt.
- First line "Chapter N: Title", a blank line, then plain prose. No markdown.
- "* * *" alone on a line for a real scene break only.
- Curly quotes.
- <1,900 to 2,200> words. One chapter per Write call. Keep your thinking short.

## Rules
- **Obey canon exactly:** names, numbers, times, distances, technology limits, document wording. Log invented colour in $B/invented.md, one line each ("chN: detail"). Invent nothing that touches the central problem or its solution.
- **Rules appear in action.** Each rule the skeleton lists for your chapter appears in scene: something done, seen or suffered. Never a lecture. If a character must explain, it is short, in dialogue, under pressure, and someone pushes back.
- **No exposition run over <threshold> words.** A run is consecutive paragraphs with no dialogue. Break long ones with a line of speech, an interruption or a cut.
- **Wonder.** The skeleton's moment of scale or awe gets room: concrete, sensory, specific numbers from canon.
- **New events.** Every chapter has a discovery, reversal, danger or decision. No recap paragraphs.
- **Craft.** Specific detail; dialogue with subtext and distinct voices; varied sentence length; varied endings.
- **Avoid:** rule-of-three lists, "something shifted", "a beat", held breaths, "the hum of" anything more than once in the book.

## Hiding rules (read twice)
1. **The intended solution's pieces are background.** Until chapter <X> they appear only as the skeleton places them, doing something else, mid-paragraph, inside a louder scene. No lingering, no "she would remember this later".
2. **Every wrong solution gets real weight.** Characters argue for them sincerely, for reasons on the page.
3. **The lead's wrong turn is argued aloud and acted on,** for good reasons. Never obtuse.
4. **No chapter title names a clue or a rule.**
5. **Never stack.** Before chapter <Y>, no two pieces of the intended solution within three chapters.
6. **Self-check before each save:** "If a sharp reader stopped here, which solution would they rank first, and is it what 02a_curve says?" If the intended one would be first before chapter <X>, cut what put it there.

After your last chapter run wc -w on your files. Reply in under 100 words with any canon conflict or gap you worked around.
```

## Fix pass (stage 6, once)

- Build an **order list** from the blind read: one line per change, with chapter, the exact sentence, and the replacement or instruction.
- Orders fix contradictions, move a rule's first appearance earlier (in action, innocently), cut exposition runs, and add missing wonder. They never make a clue to the intended solution louder.
- After any change to a rule or a number, search the whole book for lines that now contradict it.
- Reject a rewritten chapter that loses a named character or a number from canon, or changes length by more than 80 words without an order saying so.

## Proofread (stage 7)

A fresh agent reads every line and reports **hard errors only**: contradictions of fact, number, time, place, name and order of events, each with the quote, the problem and an exact replacement. It builds its own timeline first. It writes `bookN/proof_fixes.json` (`[{"file": "ch05.txt", "old": "...", "new": "..."}]`); apply with `paperbackwriter proof bookN/proof_fixes.json --dry`, then without `--dry`.
