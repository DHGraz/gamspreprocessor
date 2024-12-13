"Tests for the 'transform' group."

from click.testing import CliRunner
import pytest

from gamspreprocessor.cli.multitransform import cli


def test_multitransform():
    "The basic test is that '--help' does not lead to an error."
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "at once" in result.output


def test_saxon_version():
    "Test getting the Saxon version."
    runner = CliRunner()
    result = runner.invoke(cli, ["saxon-version"])
    assert result.exit_code == 0
    assert result.output.startswith("SaxonC-HE")


def test_transform_xslt_single_file(datadir):
    "Test multitransform xslt file with a xml file."
    runner = CliRunner()
    xslt_file = datadir / "tei2dc.xsl"
    xml_file = datadir / "objects" / "o1" / "TEI.xml"
    output_file = datadir / "objects" / "o1" / "DC.xml"

    result = runner.invoke(
        cli, ["xslt", "-x", str(xslt_file), "-o", "DC.xml", "-p", "TEI.xml",  str(xml_file.parent)]
    )
    assert result.exit_code == 0
    assert output_file.exists()


def test_transform_xslt_multiple_files(datadir):
    "Test transforming multiple XML files with a XSLT file."
    
    objects_dir = datadir / "objects"
    xslt_file = datadir / "tei2dc.xsl"
    output1_file = datadir / "objects" / "o1" / "DC.xml"
    output2_file = datadir / "objects" / "o2" / "DC.xml"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["xslt", "-x", str(xslt_file), "-r", "-o", "DC.xml", "-p", "TEI.x*", str(objects_dir)]
    )
    assert result.exit_code == 0
    assert output1_file.exists()
    assert output2_file.exists()


def test_transform_xslt_multiple_file_ambigous_pattern(datadir):
    "If the pattern matches multiple files in a single directiry, an error should be raised."
    objects_dir = datadir / "objects"
    xslt_file = datadir / "tei2dc.xsl"
    (objects_dir / "o1" / "TEI_1.xml").write_text("<TEI></TEI>")
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["xslt", "-x", str(xslt_file), "-r", "-o", "DC.xml", "-p", "TEI*.xml", str(objects_dir)]
    )
    assert result.exit_code != 0
    assert "Ambiguous" in result.output
    

def test_transform_xslt_file_list(datadir):
    "Test transforming multiple XML file from a list of files."
    
    # create the file_list file
    tei_files = [
        datadir / "objects" / "o1" / "TEI.xml",
        datadir / "objects" / "o2" / "TEI.xml"
    ]
    file_list_file = datadir / "file_list.txt"
    with file_list_file.open("w", encoding="utf-8", newline="") as file_list:
        for teilfile in tei_files:
            file_list.write(f"{teilfile.absolute()}\n")
        
    xslt_file = datadir / "tei2dc.xsl"
    output1_file = datadir / "objects" / "o1" / "DC.xml"
    output2_file = datadir / "objects" / "o2" / "DC.xml"
    
    runner = CliRunner()
    result = runner.invoke(
        cli, ["xslt", "-x", str(xslt_file), "-o", "DC.xml", "-l", str(file_list_file)]
    )
    assert result.exit_code == 0
    assert output1_file.exists()
    assert output2_file.exists()


def test_transform_xslt_file_list_and_start_dir(datadir):
    "Using -l and start_dir should raise a warning."
    xslt_file = datadir / "tei2dc.xsl"
    file_list = datadir / "file_list.txt"
    file_list.touch()
    objects_dir = datadir / "objects"   

    runner = CliRunner()
    with pytest.warns(UserWarning, match="Ignoring start-dir argument"):
        result = runner.invoke(
            cli, ["xslt", "-x", str(xslt_file), "-p", "TEI.xml", "-o", "DC.xml", 
                "-l", str(file_list), str(objects_dir),
            ],
        )
    assert result.exit_code == 0


def test_transform_xslt_no_file_list_and_no_start_dir(datadir):
    "Using neither -l nor start_dir should raise an error."
    xslt_file = datadir / "tei2dc.xsl"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["xslt", "-x", str(xslt_file), "-o", "DC.xml", "-p", "TEI.xml"]
    )
    assert result.exit_code != 0
    assert "You must provide" in result.output

def test_transform_xslt_no_xslt_file(datadir):
    "Using neither -l nor start_dir should raise an error."
    runner = CliRunner()
    result = runner.invoke(
        cli, ["xslt", "-o", "DC.xml", "-p", "TEI.xml", str(datadir)]
    )
    assert result.exit_code != 0
    assert "Missing option" in result.output

def test_transform_xslt_no_pattern(datadir):
    "Missing --pattern should raise an error."
    xslt_file = datadir / "tei2dc.xsl"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["xslt", "-x", str(xslt_file), "-o", "DC.xml", str(datadir)]
    )
    assert result.exit_code != 0
    assert "You must provide" in result.output    

def test_transform_xslt_no_output_file(datadir):
    "Using neither -l nor start_dir should raise an error."
    xslt_file = datadir / "tei2dc.xsl"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["xslt", "-x", str(xslt_file), "-p", "TEI.xml", str(datadir)]
    )
    assert result.exit_code != 0
    assert "Missing option" in result.output    

def test_transform_xslt_multiple_start_dirs(datadir):
    "start_dir must be a single value."

    # objects_dir = datadir / "objects"
    # #xml1_file = datadir / "o1" / "TEI.xml"
    # # xml2_file = datadir / "o2" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"
    # output1_file = datadir / "objects" / "o1" / "DC.xml"
    # output2_file = datadir / "objects" / "o2" / "DC.xml"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["xslt", "-x", str(xslt_file), "-o", "DC.xml", "-p", "TEI.xml", "foo", "bar"]   
    )
    assert result.exit_code != 0
    assert "single start-dir" in result.output

def test_transform_xslt_invalid_xslt(datadir, tmp_path):
    "Test transforming an XML file with an invalid XSLT file."
    
    xslt_file = datadir / "tei2dc.xsl"
    objects_dir = datadir / "objects"

    # break the xslt file
    xslt = xslt_file.read_text()
    xslt = xslt.replace("xsl:template", "xsl:templatee")
    xslt_file.write_text(xslt)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["xslt", "-x", str(xslt_file), "-r", "-o", "DC.xml", "-p", "TEI*.xml", str(objects_dir)]
    )
    assert result.exit_code != 0
    assert "Error transforming" in result.output