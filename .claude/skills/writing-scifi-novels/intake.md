# Intake: "what are we building"

Stage 0. The output is `series/<slug>/BUILD_BRIEF.md`.

1. Fill every row you can from what the author has said and from earlier books.
2. Ask only the **must ask** rows still empty: one round, four questions at most, each with a recommended answer first.
3. Give every other row a default marked "assumed". Silence on an assumed row is not agreement.

| # | Row | Ask it like this | Must ask? | Default |
|---|---|---|---|---|
| 1 | Format | "One book or a series? How many?" | Yes | Two-book series |
| 2 | Novum | "What's the one 'what if'?" | Yes | Offer three, each a single changed fact about the near future |
| 3 | Setting | "Where is everyone shut in together? A station, a colony, a ship, a sealed town?" | Yes | Offer three, each with a real-world analogue |
| 4 | When | "How far ahead? Ten years, fifty, a hundred?" | No | 30–60 years ahead |
| 5 | Lead | "Who solves it, what is their job, and why do people listen to them?" | Yes | A practical trade (engineer, medic, pilot, inspector) |
| 6 | Stakes | "What fails if they fail, and how long do they have?" | No | Lives inside the setting, a clock of days |
| 7 | Science | "Hard (real physics, sourced) or soft (one invented thing, the rest real)?" | No | One invented thing, the rest real and sourced |
| 8 | Tone and content | "How dark, how funny, any romance or faith on the page?" | No | Grounded, wry, real danger, clean |
| 9 | Length | "How long?" | No | 24 chapters, about 50,000 words |
| 10 | Shelf | "Who's the reader, and which categories?" | No | Three, narrowest true one first |
| 11 | Series shape | "Same lead in both books? What carries over?" | No | Same lead and setting; a new central problem each book; rules carry over |
| 12 | Spoilers | "Do you want to know the solution, or read it cold?" | Yes, before stage 2 | Read it cold |
| 13 | Done means | "What blind-read scores count as finished?" | No | overall, rules fair, solution earned, prose all 7+ |

## The series bible (stage 1)

Sections, in order (template: `templates/SERIES_BIBLE.md`):
0. How to use it: canon, no solutions, real people never speak.
1. The promise: what every book delivers.
2. The setting: layout, who lives there, how it is cut off, what it runs on.
3. The novum and its consequences: what changed in the world and three things that follow from it.
4. Technology and science: what exists, what does not, and the limits that matter. Banned list (no faster-than-light, no mind-reading, etc., as fits).
5. Recurring cast: no shared first names, surnames or first initials. The lead's trade, wound, rule, limits and voice.
6. Voice, tone, content, length.
7. Series signatures: three set pieces that recur, never the same way twice.
8. Series arc: threads across the books.
9. The books: premise, calendar, the central problem as the public sees it.
10. Fact table: each real fact with its source or "invented".

Rules that hold across books go in `SERIES_RULES.md` (template: `templates/SERIES_RULES.md`), as `| R1 | rule | book 1 |`.
