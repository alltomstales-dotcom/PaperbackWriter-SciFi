"""Every function this project borrows from paperbackwriter, called once.
If an upgrade of the dependency breaks one, this fails first."""


def test_borrowed_outline_functions():
    from paperbackwriter.outline import batches, checkpoints, sections
    assert checkpoints(24) == (7, 12, 17, 21, 24)
    assert batches(24)[0] == (1, 7)
    assert sections("Chapter 1: A\n\nx\n") == {1: ("Chapter 1: A", "x")}


def test_borrowed_stage_proof_and_export(tmp_path):
    from paperbackwriter.export import Book, build_epub, load_chapters
    from paperbackwriter.proof import apply_fixes
    from paperbackwriter.reads import stage
    src = tmp_path / "chapters"
    src.mkdir()
    for n in (1, 2):
        (src / f"ch{n:02d}.txt").write_text(f"Chapter {n}: T\n\nThe hull rang at dawn.\n")
    assert stage(src, tmp_path / "read", 1) == 1
    assert apply_fixes(src, [{"file": "ch02.txt", "old": "dawn", "new": "dusk"}]) == (1, [])
    out = build_epub(Book("T", "A", load_chapters(src)), tmp_path / "t.epub")
    assert out.stat().st_size > 0
