"""CLI subcommand for transforming a single file.

The 'multitransform' might be a useful alternative to the 'transform' command.
"""
import logging
from pathlib import Path
import click

from gamspreprocessor.transformers.xslt import transform, get_saxon_version
from gamspreprocessor.transformers.exceptions import TransformationError

logger = logging.getLogger(__name__)


@click.group(name="transform")
def cli():
    """Helpers for transforming GAMS files.

    These commands might be useful to transform GAMS files into other formats.
    """


@click.command(name="xslt")
@click.option("--xslt-file", "-x", type=click.Path(exists=True),
              help="Path to the XSLT file to be applied.")
@click.argument("xml-file", type=click.Path(exists=True))
@click.argument("output-file", type=click.Path())
def transform_xslt(xslt_file: str, xml_file: str, output_file: str):
    "Apply a xslt on a single xml file."
    try:
        transform(Path(xml_file), Path(xslt_file), Path(output_file))
    except TransformationError as exp:
        logger.error("Error transforming %s: %s", xml_file, exp)
        raise click.ClickException(f"Error transforming {xml_file}: {exp}") from exp


@click.command(name="xslt-processor")
def xslt_processor():
    """Show the version of the XSLT processor."""
    click.echo(f"{get_saxon_version()}")


cli.add_command(xslt_processor)
cli.add_command(transform_xslt)
