"""Pointers: narration that tells the reader which detail matters.

Blind readers keyed on these in Book 1's first draft: "nobody had ears for it",
"the right answer to a question she had not quite asked", "It was not hers yet".
A wink by negation ("nobody noticed") points as hard as "she would remember this".
Dialogue is skipped: a character may say these things; the narrator may not.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .exposition import _chapter_files

PATTERNS = [
    r"(?:nobody|no one|no-one)\b[^.!?]{0,40}?\b(?:had ears for|listened to|noticed|heard|paid attention to) (?:it|that|this)",
    r"\b(?:registered|heard|saw|noticed) it without (?:hearing|seeing|noticing|registering) it",
    r"\bthe right (?:answer|question|thing)\b",
    r"\bnot (?:hers|his|theirs|mine) yet\b",
    r"\b(?:would|was to|were to) (?:remember|recall|think of) (?:it|that|this)\b[^.!?]{0,30}",
    r"\b(?:did not|didn't) know it yet\b",
    r"\bat the back of (?:her|his|their) mind\b",
    r"\bfiled (?:it|that|this) away\b",
    r"\bsomething about (?:it|that|this) (?:nagged|bothered|tugged)",
]
_RX = re.compile("|".join(f"(?:{p})" for p in PATTERNS), re.IGNORECASE)
_QUOTED = re.compile(r"“[^”]*”|\"[^\"]*\"")
_SENTENCE = re.compile(r"[^.!?]*[.!?]+[”’]?|[^.!?]+$")


@dataclass(frozen=True)
class Hit:
    phrase: str
    sentence: str


def find_pointers(text: str) -> list[Hit]:
    hits: list[Hit] = []
    for paragraph in (p.strip() for p in text.split("\n\n")):
        narration = _QUOTED.sub(" ", paragraph)
        for sentence in (s.strip() for s in _SENTENCE.findall(narration)):
            m = _RX.search(sentence)
            if m:
                hits.append(Hit(m.group(0).strip(), sentence))
    return hits


def report(chapters_dir: Path) -> list[dict]:
    return [{"chapter": n, "phrase": h.phrase, "sentence": h.sentence}
            for n, text in _chapter_files(chapters_dir) for h in find_pointers(text)]
