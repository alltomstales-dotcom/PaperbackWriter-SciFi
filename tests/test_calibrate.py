from pbw_scifi.calibrate import split_gutenberg, write_chapters

RAW = ("Header junk\r\n*** START OF THE PROJECT GUTENBERG EBOOK X ***\r\n\r\nContents\r\n I. One\r\n\r\n"
       "CHAPTER I.\r\nTHE STRANGE MAN’S ARRIVAL\r\n\r\n\r\nThe stranger came early in\r\nFebruary, _very_ cold.\r\n\r\n"
       "“Hi,” he said.\r\n\r\nCHAPTER II.\r\nMR. TEDDY HENFREY\r\n\r\nSecond chapter text.\r\n\r\n"
       "THE EPILOGUE\r\n\r\nThe end.\r\n\r\n*** END OF THE PROJECT GUTENBERG EBOOK X ***\r\nlicence\r\n")


def test_split_gutenberg_finds_chapters_and_epilogue():
    chapters = split_gutenberg(RAW)
    assert [(n, t) for n, t, _ in chapters] == [(1, "The Strange Man’s Arrival"), (2, "Mr. Teddy Henfrey"), (3, "Epilogue")]
    assert chapters[0][2] == "The stranger came early in February, *very* cold.\n\n“Hi,” he said."


def test_write_chapters_matches_the_engine_format(tmp_path):
    assert write_chapters(split_gutenberg(RAW), tmp_path) == 3
    assert (tmp_path / "ch01.txt").read_text().startswith("Chapter 1: The Strange Man’s Arrival\n\nThe stranger")
