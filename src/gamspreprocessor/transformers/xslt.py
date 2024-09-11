"""Module to apply xslt on xml files using Saxon."""

import logging
from pathlib import Path

from saxonche import PySaxonApiError, PySaxonProcessor

from .exceptions import TransformationError

logger = logging.getLogger(__name__)


def transform(xml_file: Path, xslt_file: Path, output_file: Path):
    """Apply a xslt on an xml file using Saxon."""

    with PySaxonProcessor() as processor:
        xslt_proc = processor.new_xslt30_processor()
        try:
            executable = xslt_proc.compile_stylesheet(stylesheet_file=str(xslt_file))
        except PySaxonApiError as exp:
            logger.error("Error compiling the stylesheet: %s", exp)
            raise TransformationError("Error compiling the stylesheet") from exp
        try:
            executable.transform_to_file(
                source_file=str(xml_file), output_file=str(output_file)
            )
        except PySaxonApiError as exp:
            logger.error("Error transforming the file: %s", exp)
            raise TransformationError("Error transforming the file") from exp


def get_saxon_version():
    """Show the version of the Saxon processor."""
    with PySaxonProcessor() as processor:
        version = processor.version
    return version
