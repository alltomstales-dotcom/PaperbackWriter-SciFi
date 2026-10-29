"""Command line: `paperbackwriter-scifi <command>` (or `python -m pbw_scifi <command>`).

Staging chapters, building outline digests, proofreading and export use the mystery
package's `paperbackwriter` command; this one adds the sci-fi checks and gates.
Exit codes: 0 pass, 1 a check failed, 2 bad input.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _print(result) -> int:
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not isinstance(result, dict) or result.get("passed", True) else 1


def cmd_rules(a):
    from .rules import check_rules
    return _print(check_rules(Path(a.plan), Path(a.series) if a.series else None, a.chapters))


def cmd_exposition(a):
    from .exposition import report
    over = report(Path(a.chapters_dir), a.threshold)
    for r in over:
        print(f"ch{r['chapter']:02d}  {r['words']:>5} words  {r['start']!r}")
    print(f"{len(over)} runs over {a.threshold} words")
    return 1 if over else 0


def cmd_calibrate_threshold(a):
    from .exposition import calibrated_threshold
    return _print(calibrated_threshold(Path(a.chapters_dir)))


def cmd_check_read(a):
    from .reads import check_log, solution_rank, wonder_count
    result = check_log(Path(a.log), a.finished)
    result["wonder"] = wonder_count(Path(a.log))
    if a.key:
        result["solution"] = solution_rank(Path(a.log), a.key)
    return _print(result)


def cmd_rank(a):
    from .reads import solution_rank
    return _print(solution_rank(Path(a.log), a.key))


def cmd_gate(a):
    from .reads import advance_plan_read
    return _print(advance_plan_read(Path(a.reference), Path(a.gate), a.checkpoint, a.chapters))


def cmd_import_reference(a):
    from .calibrate import split_gutenberg, write_chapters
    n = write_chapters(split_gutenberg(Path(a.source).read_text(encoding="utf-8")), Path(a.out))
    print(f"wrote {n} chapters to {a.out}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="paperbackwriter-scifi", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("rules", help="fair-play check: the solution uses only rules introduced by 75%%")
    s.add_argument("plan")
    s.add_argument("--series", help="SERIES_RULES.md (rules established before this book)")
    s.add_argument("--chapters", type=int, default=24)
    s.set_defaults(func=cmd_rules)

    s = sub.add_parser("exposition", help="list exposition runs over the threshold")
    s.add_argument("chapters_dir")
    s.add_argument("--threshold", type=int, default=400)
    s.set_defaults(func=cmd_exposition)

    s = sub.add_parser("calibrate-threshold", help="90th-percentile exposition run of a reference book")
    s.add_argument("chapters_dir")
    s.set_defaults(func=cmd_calibrate_threshold)

    s = sub.add_parser("check-read", help="verify a reader's checkpoint log")
    s.add_argument("log")
    s.add_argument("--key", action="append", help="regex for the intended solution (private)")
    s.add_argument("--finished", action="store_true", help="audit a completed read")
    s.set_defaults(func=cmd_check_read)

    s = sub.add_parser("rank", help="rank of the intended solution in a log")
    s.add_argument("log")
    s.add_argument("--key", action="append", required=True)
    s.set_defaults(func=cmd_rank)

    s = sub.add_parser("gate", help="score a plan-read checkpoint; release the next batch on a pass")
    s.add_argument("reference")
    s.add_argument("gate")
    s.add_argument("checkpoint", type=int)
    s.add_argument("--chapters", type=int, default=24)
    s.set_defaults(func=cmd_gate)

    s = sub.add_parser("import-reference", help="Project Gutenberg .txt -> chNN.txt files")
    s.add_argument("source")
    s.add_argument("out")
    s.set_defaults(func=cmd_import_reference)

    a = p.parse_args(argv)
    try:
        return a.func(a)
    except (ValueError, FileNotFoundError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
