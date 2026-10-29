"""Structure check for a sci-fi plan folder.

Wraps the mystery engine's check_plan (outline coverage, digest batches, writer
brief, the 2,000-word cap) and swaps its fixed file names for the sci-fi ones.
"""
from __future__ import annotations

from pathlib import Path

from paperbackwriter import plan as mystery

FIXED = ("01_novum_and_solutions.md", "02a_curve.md", "02b_rules_and_clues.md",
         "03_resolution_map.md", "canon.md", "audit.md")
_MYSTERY_ONLY = sorted(set(mystery.FIXED) - set(FIXED))


def check_plan(root: Path, n_chapters: int = 24) -> dict:
    root = Path(root)
    result = mystery.check_plan(root, n_chapters)
    drop = {f"Missing {name}" for name in _MYSTERY_ONLY}
    errors = [e for e in result["errors"] if e not in drop]
    for name in FIXED:
        path = root / name
        if name in mystery.FIXED:
            continue  # already checked by the mystery engine
        if not path.is_file():
            errors.append(f"Missing {name}")
            continue
        words = len(path.read_text(encoding="utf-8").split())
        result["word_counts"][name] = words
        if not 0 < words < mystery.WORD_CAP:
            errors.append(f"{name} must contain fewer than 2,000 words")
    result["errors"] = errors
    result["passed"] = not errors
    return result
