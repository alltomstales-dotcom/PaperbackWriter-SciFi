"""Import a public-domain novel from Project Gutenberg as chNN.txt files for calibration reads."""
from __future__ import annotations

import re
from pathlib import Path

HEADING = re.compile(r"(?m)^(?:CHAPTER ([IVXLC]+)\.?|THE (EPILOGUE))\s*$")


def _title(s: str) -> str:
    small = {"a", "an", "the", "of", "in", "and", "at", "on", "to", "for", "who", "was"}
    words = s.strip().rstrip(".").lower().split()
    return " ".join(w if i and w in small else w[:1].upper() + w[1:] for i, w in enumerate(words))


def split_gutenberg(text: str) -> list[tuple[int, str, str]]:
    text = text.replace("\r\n", "\n")
    start = text.find("*** START OF")
    end = text.find("*** END OF")
    body = text[text.find("\n", start) + 1: end if end != -1 else None]
    marks = list(HEADING.finditer(body))
    out = []
    for i, m in enumerate(marks):
        chunk = body[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(body)].strip("\n")
        if m.group(2):
            title, rest = "Epilogue", chunk
        else:
            first, _, rest = chunk.partition("\n")
            title = _title(first)
        paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", rest) if p.strip()]
        prose = "\n\n".join(re.sub(r"_([^_]+)_", r"*\1*", p) for p in paras)
        out.append((i + 1, title, prose))
    return out


def write_chapters(chapters, out_dir: Path) -> int:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for n, title, prose in chapters:
        (out_dir / f"ch{n:02d}.txt").write_text(f"Chapter {n}: {title}\n\n{prose}\n", encoding="utf-8")
    return len(chapters)
