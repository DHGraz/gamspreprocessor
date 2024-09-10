from gamspreprocessor.transformers.xslt import get_saxon_version

def test_get_saxon_version():
    version = get_saxon_version()
    assert version.startswith("SaxonC-HE")
