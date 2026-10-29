"""Pre-push spoiler scan: fail if a private term list matches any tracked file.

The term list lives outside this public repo (one case-insensitive regex per
line). Reports give file, line and pattern number only, never the matched text.
"""
import re
from pathlib import Path


def load_terms(path: Path) -> list[str]:
    if not path.is_file():
        raise ValueError(f"spoiler terms file not found: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.lstrip().startswith("#")]


def scan(files: list[Path], patterns: list[str], root: Path) -> list[dict]:
    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
    hits = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for i, rx in enumerate(compiled, 1):
                if rx.search(line):
                    hits.append({"file": str(f.relative_to(root)), "line": n, "pattern": i})
    return hits
