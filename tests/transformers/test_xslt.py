"Unit tests for the transformer.xslt module."

import pytest

from gamspreprocessor.transformers.exceptions import TransformationError
from gamspreprocessor.transformers.xslt import get_saxon_version, transform


def test_get_saxon_version():
    "Test the get_saxon_version function."
    version = get_saxon_version()
    assert version.startswith("SaxonC-HE")


def test_transform(datadir):
    "Test transforming an XML file with a XSLT file."
    xml_file = datadir / "o1" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"
    output_file = datadir / "o1" / "DC.xml"
    transform(xml_file, xslt_file, output_file)
    assert output_file.exists()


def test_transform_invalid_xslt(datadir):
    "Test transforming an XML file with an invalid XSLT file."
    xml_file = datadir / "o1" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"
    output_file = datadir / "o1" / "DC.xml"

    # break the xslt file
    xslt = xslt_file.read_text()
    xslt = xslt.replace("xsl:template", "xsl:templatee")
    xslt_file.write_text(xslt)

    with pytest.raises(TransformationError) as exp:
        transform(xml_file, xslt_file, output_file)
    assert "Error compiling" in exp.value.args[0]


def test_transform_invalid_xml(datadir):
    "Test transforming an invalid XML file with a XSLT file."
    xml_file = datadir / "o1" / "TEI.xml"
    xslt_file = datadir / "tei2dc.xsl"
    output_file = datadir / "o1" / "DC.xml"

    # break the xml file
    xml = xml_file.read_text()
    xml = xml.replace("<title>", "<titlee>")
    xml_file.write_text(xml)
    with pytest.raises(TransformationError) as exp:
        transform(xml_file, xslt_file, output_file)
    assert "Error transforming" in exp.value.args[0]
