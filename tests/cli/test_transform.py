"Tests for the 'transform' group."

from click.testing import CliRunner

from gamspreprocessor.cli.transform import cli


def test_transform():
    "The basic test is that '--help' does not lead to an error."
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "transforming" in result.output


def test_saxon_version():
    "Test getting the Saxon version."
    runner = CliRunner()
    result = runner.invoke(cli, ["saxon-version"])
    assert result.exit_code == 0
    assert result.output.startswith("SaxonC-HE")


def test_transform_xslt_single_file(datadir):
    "Test transforming an XML file with a XSLT file."
    runner = CliRunner()
    xml_file = datadir / "o1" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"
    output_file = datadir / "o1" / "DC.xml"
    result = runner.invoke(
        cli, ["xslt", "-x", str(xslt_file), "-o", "DC.xml", str(xml_file)]
    )
    assert result.exit_code == 0
    assert output_file.exists()


def test_transform_xslt_multiple_files(datadir):
    "Test transforming multiple XML file with a XSLT file."
    runner = CliRunner()
    xml1_file = datadir / "o1" / "TEI.xml"
    xml2_file = datadir / "o2" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"
    output1_file = datadir / "o1" / "DC.xml"
    output2_file = datadir / "o1" / "DC.xml"
    result = runner.invoke(
        cli,
        ["xslt", "-x", str(xslt_file), "-o", "DC.xml", str(xml1_file), str(xml2_file)],
    )
    assert result.exit_code == 0
    assert output1_file.exists()
    assert output2_file.exists()


def test_transform_xslt_file_list(datadir):
    "Test transforming multiple XML file from a list of files."
    runner = CliRunner()
    xml1_file = datadir / "o1" / "TEI.xml"
    xml2_file = datadir / "o2" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"
    output1_file = datadir / "o1" / "DC.xml"
    output2_file = datadir / "o1" / "DC.xml"
    file_list = datadir / "file_list.txt"
    file_list.write_text(f"{xml1_file}\n{xml2_file}")
    result = runner.invoke(
        cli, ["xslt", "-x", str(xslt_file), "-o", "DC.xml", "-l", str(file_list)]
    )
    assert result.exit_code == 0
    assert output1_file.exists()
    assert output2_file.exists()


def test_transform_xslt_file_list_and_files(datadir):
    "Using -l and files is not allowed."
    runner = CliRunner()
    xml1_file = datadir / "o1" / "TEI.xml"
    xml2_file = datadir / "o2" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"

    file_list = datadir / "file_list.txt"
    file_list.write_text(f"{xml1_file}")
    result = runner.invoke(
        cli,
        [
            "xslt",
            "-x",
            str(xslt_file),
            "-o",
            "DC.xml",
            "-l",
            str(file_list),
            str(xml2_file),
        ],
    )
    assert result.exit_code != 0
    assert "'--file-list' and 'xmlfiles' are mutually exclusive." in result.output


def test_transform_xslt_invalid_xslt(datadir):
    "Test transforming an XML file with an invalid XSLT file."
    runner = CliRunner()
    xml_file = datadir / "o1" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"

    # break the xslt file
    xslt = xslt_file.read_text()
    xslt = xslt.replace("xsl:template", "xsl:templatee")
    xslt_file.write_text(xslt)

    result = runner.invoke(
        cli, ["xslt", "-x", str(xslt_file), "-o", "DC.xml", str(xml_file)]
    )
    assert result.exit_code != 0
    assert "Error transforming" in result.output


def test_transform_xslt_invalid_xml(datadir):
    "Test transforming an invalid XML file with a XSLT file."
    runner = CliRunner()
    xml_file = datadir / "o1" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"

    # break the xml file
    xml = xml_file.read_text()
    xml = xml.replace("<title>", "<titlee>")
    xml_file.write_text(xml)

    result = runner.invoke(
        cli, ["xslt", "-x", str(xslt_file), "-o", "DC.xml", str(xml_file)]
    )
    assert result.exit_code != 0
    assert "Error transforming" in result.output
