"""Exposition runs: stretches of paragraphs with no dialogue and no scene break.

A long run is where readers skim. The threshold is calibrated on a reference novel
(CALIBRATION.md) rather than guessed.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

SCENE_BREAK = "* * *"
HEADING = re.compile(r"Chapter \d+: .+")
DEFAULT_THRESHOLD = 300  # calibrated on the reference novel (CALIBRATION.md, 2026-10-28)


@dataclass(frozen=True)
class Run:
    words: int
    start: str


def _is_dialogue(paragraph: str) -> bool:
    return any(q in paragraph for q in ('"', "“", "”")) or bool(re.search(r"(^|\s)‘", paragraph))


def runs(text: str) -> list[Run]:
    out: list[Run] = []
    words, start = 0, ""
    for p in (p.strip() for p in text.split("\n\n")):
        if not p or HEADING.fullmatch(p):
            continue
        if p == SCENE_BREAK or _is_dialogue(p):
            if words:
                out.append(Run(words, start))
            words, start = 0, ""
            continue
        if not words:
            start = p[:60]
        words += len(p.split())
    if words:
        out.append(Run(words, start))
    return out


def _chapter_files(chapters_dir: Path) -> list[tuple[int, str]]:
    found = []
    for path in sorted(Path(chapters_dir).glob("ch*.txt")):
        m = re.fullmatch(r"ch(\d+)\.txt", path.name)
        if m:
            found.append((int(m.group(1)), path.read_text(encoding="utf-8")))
    if not found:
        # An empty or mistyped folder must not read as a clean gate.
        raise ValueError(f"no chNN.txt files in {chapters_dir}")
    return found


def report(chapters_dir: Path, threshold: int) -> list[dict]:
    return [{"chapter": n, "words": r.words, "start": r.start}
            for n, text in _chapter_files(chapters_dir) for r in runs(text) if r.words > threshold]


def calibrated_threshold(chapters_dir: Path) -> dict:
    lengths = sorted(r.words for _, text in _chapter_files(chapters_dir) for r in runs(text))
    if not lengths:
        raise ValueError(f"no chapter text in {chapters_dir}")
    p90 = lengths[max(0, math.ceil(0.9 * len(lengths)) - 1)]  # nearest-rank
    return {"threshold": max(300, int(round(p90 / 50.0)) * 50), "p90": p90, "runs": len(lengths), "max": lengths[-1]}
