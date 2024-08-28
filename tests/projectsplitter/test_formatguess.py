"tests for the bookkeeper module."
from gamspreprocessor.projectsplitter.formatguesser import guess_format

def test_guess_format(datadir):
    "Guess the format of the file from the extension."

    assert guess_format(datadir / "TEI_1.xml") == "tei"
    assert guess_format(datadir  / "LIDO_1.xml") == "lido"
    assert guess_format(datadir / "foo.xml") == "xml"
    assert guess_format(datadir / "foo.csv") == "csv"
    assert guess_format(datadir / "foo.pdf") == "pdf"
    assert guess_format(datadir / "d1/bar.pdf") == "pdf"
    assert guess_format("img.jpeg") == "image"
    assert guess_format("img.png") == "image"
