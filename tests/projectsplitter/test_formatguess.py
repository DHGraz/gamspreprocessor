"tests for the bookkeeper module."

from gamspreprocessor.projectsplitter.formatguesser import guess_format


def test_guess_format(datadir):
    "Guess the format of the file from the extension."

    assert guess_format(datadir / "TEI_1.xml") == ("application/tei+xml", "TEI")
    assert guess_format(datadir / "LIDO_1.xml") == ("application/xml", "LIDO")
    assert guess_format(datadir / "foo.xml") == ("application/xml", "")
    assert guess_format(datadir / "foo.csv") == ("text/csv", "")
    assert guess_format(datadir / "foo.pdf") == ("application/pdf", "")
    assert guess_format(datadir / "image01.jpg") == ("image/jpeg", "")
    assert guess_format(datadir / "foo.png") == ("image/png", "")
    assert guess_format(datadir / "foo.unknown") == ("application/octet-stream", "")


