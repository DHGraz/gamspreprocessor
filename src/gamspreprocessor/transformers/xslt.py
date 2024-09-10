import logging
from pathlib import Path
from saxonche import PySaxonProcessor

logger = logging.getLogger(__name__)

def transform(xml_file: Path, xslt_file: Path, output_file: Path|None = None):
    """Apply a xslt on an xml file using Saxon."""
    with PySaxonProcessor() as processor:
        xslt = processor.new_xslt30_processor(xslt_file)
        result = xslt.transform_file(xml_file)
        if output_file:
            with open(output_file, "w") as f:
                f.write(result)
        else:
            print(result)


def get_saxon_version():
    """Show the version of the Saxon processor."""
    with PySaxonProcessor() as processor:
        version = processor.version
    return version
