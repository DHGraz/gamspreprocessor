"tests for the bookkeeper module."

from gamspreprocessor.projectsplitter.formatguesser import guess_format


def test_guess_format(datadir):
    "Guess the format of the file from the extension."

    assert guess_format(datadir / "TEI_1.xml") == ("application/xml", "tei")
    assert guess_format(datadir / "LIDO_1.xml") == ("application/xml", "lido")
    assert guess_format(datadir / "foo.xml") == ("application/xml", "")
    assert guess_format(datadir / "foo.csv") == ("text/csv", "")
    assert guess_format(datadir / "foo.pdf") == ("application/pdf", "")
    assert guess_format(datadir / "d1/bar.pdf") == ("application/pdf", "")
    assert guess_format("img.jpeg") == ("image/jpeg", "")
    assert guess_format("img.png") == ("image/png", "")
