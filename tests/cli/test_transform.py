"Tests for the 'transform' group."

from click.testing import CliRunner

from gamspreprocessor.cli.transform import cli

# pylint: disable=duplicate-code

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


def test_transform_xslt(datadir):
    "Test transforming an XML file with a XSLT file."
    runner = CliRunner()
    xml_file = datadir / "o1" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"
    output_file = datadir / "o1" / "DC.xml"
    result = runner.invoke(
        cli, ["xslt", "-x", str(xslt_file), str(xml_file), str(output_file)]
    )
    assert result.exit_code == 0
    assert output_file.exists()

def test_transform_xslt_invalid_xslt(datadir, tmp_path):
    "Test transforming an XML file with an invalid XSLT file."
    runner = CliRunner()
    xml_file = datadir / "o1" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"
    output_file = tmp_path / "DC.xml"

    # break the xslt file
    xslt = xslt_file.read_text()
    xslt = xslt.replace("xsl:template", "xsl:templatee")
    xslt_file.write_text(xslt)

    result = runner.invoke(
        cli, ["xslt", "-x", str(xslt_file), str(xml_file), str(output_file)]
    )
    assert result.exit_code != 0
    assert "Error transforming" in result.output


def test_transform_xslt_invalid_xml(datadir):
    "Test transforming an invalid XML file with a XSLT file."
    runner = CliRunner()
    xml_file = datadir / "o1" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"
    output_file = datadir / "o1" / "DC.xml"

    # break the xml file
    xml = xml_file.read_text()
    xml = xml.replace("<title>", "<titlee>")
    xml_file.write_text(xml)

    result = runner.invoke(
        cli, ["xslt", "-x", str(xslt_file), str(xml_file), str(output_file)]
    )
    assert result.exit_code != 0
    assert "Error transforming" in result.output
