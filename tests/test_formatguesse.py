from gamspreprocessor.formatguesser import guess_format

def test_guess_format(datadir):
    "Guess the format of the file from the extension."

    foo_xml = datadir / "projects" / "foo.xml"
    with open(foo_xml, "w", encoding="utf-8") as f:
        f.write("<foo></foo>")

    assert guess_format(datadir / "projects" / "TEI_1.xml") == "tei"
    assert guess_format(datadir / "projects" / "LIDO_1.xml") == "lido"
    assert guess_format(str(foo_xml)) == "xml"
    assert guess_format(datadir / "projects" / "foo.csv") == "csv"
    assert guess_format(datadir / "projects" / "foo.pdf") == "pdf"
    assert guess_format(datadir / "projects" / "d1/bar.pdf") == "pdf"
    assert guess_format("img.jpeg") == "image"
    assert guess_format("img.png") == "image"
