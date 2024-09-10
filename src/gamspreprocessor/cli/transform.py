import logging
from pathlib import Path
import click

from gamspreprocessor.transformers.xslt import transform, show_saxon_version

logger = logging.getLogger(__name__)


@click.group(name="transform")
def cli():
    """Helpers for transforming GAMS files.

    These commands might be useful to transform GAMS files into other formats.
    """

@click.command(name="xslt")
@click.option("--xslt-file", "-x", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output-file",
    help=("The output file name. This file will be created in the same folder "
        "as the input file.")
)
@click.option(
    "-l",
    "--file-list",
    type=click.Path(exists=True),
    help="A file containing a list of files (with path, if necessary) to be transformed.",
)
@click.argument("xmlfiles", type=click.Path(exists=True), nargs=-1)
def transform_xslt(output_file:str, xslt_file:str, file_list:str, xmlfiles:list[str]):
    "Apply a xslt on an xml file."
    if xmlfiles and file_list:
        raise ValueError("'--file-list' and 'xmlfiles' are mutually exclusive.")
    if file_list:
        xmlfiles = Path(file_list).read_text().splitlines()
    for xmlfile in xmlfiles:
        output_file_path = Path(xmlfile).parent / output_file
        transform(Path(xmlfile), Path(xslt_file), output_file_path)  



@click.command(name="saxon-version")
def saxon_version():
    """Show the version of the Saxon processor."""
    logger.info("%s", show_saxon_version())
