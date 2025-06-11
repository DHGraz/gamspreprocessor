"""CLI subcommand 'multitransform'.

Multitransform is similiar to tranform, but can be used to transform more than one file.
"""

import logging
from pathlib import Path
import warnings
import click

from gamspreprocessor.transformers.xslt import transform, get_saxon_version
from gamspreprocessor.transformers.exceptions import TransformationError
from gamspreprocessor import utils

logger = logging.getLogger(__name__)


@click.group(name="multitransform")
def cli():
    """Helpers for transforming multiple files at once.

    These commands might be useful to transform GAMS files into other formats.
    """

# pylint: disable=too-many-arguments, too-many-positional-arguments
@click.command(name="xslt")
@click.option("--xslt-file", "-x", type=click.Path(exists=True), required=True)
@click.option(
    "-o",
    "--output-filename",
    required=True,
    help=(
        "The output file name. This file will be created in the same folder "
        "as the input file. This means, the output file name is the same for "
        "all transformations (but in different directories). "
    ),
)
@click.option(
    "--pattern",
    "-p",
    default="",
    help=(
        "A pattern (*,?,!) to identify the files to be transformed. Cannot be used "
        "together with --file-list"
    ),
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help=(
        "Apply pattern set as argument also on subdirectories. "
        "Can only be used together with --pattern."
    ),
)
@click.option(
    "-e",
    "--exclude",
    multiple=True,
    help=(
        "A file name (e.g. 'DC.xml') which should be excluded from "
        "the transformation. `--exclude` can be used multiple times " 
        "to specify a list of file names. " 
        "Attention: The values are file names, not filename patterns! "
        "Example: multitransform xslt -p '*.xml' -e DC.xml -e DC2.xml will transform all "
        "'.xml'-Files but 'DC.xml' and DC2.xml'"
    ))
@click.option(
    "-l",
    "--file-list",
    type=click.Path(exists=True),
    help="A file containing a list of files (with path, if necessary) to be transformed.",
)
@click.argument("start-dir", nargs=-1)
def transform_xslt( # noqa: PLR0913
    xslt_file: str,
    start_dir: list[str],
    output_filename: str,
    file_list: str = "",
    pattern: str = "",
    exclude: list[str]|None = None,
    recursive: bool = False,
):
    """Apply a xslt on multiple xml files (in different directories)."""
    # check input
    if file_list and start_dir:
        warnings.warn("Ignoring start-dir argument, because file-list is set.")
    if not start_dir and not file_list:
        raise click.ClickException("You must provide a start-dir directory or a file-list.")
    if not file_list:
        if len(start_dir) > 1:
            raise click.ClickException("You must provide a single start-dir directory")
        if not pattern:
            raise click.ClickException("You must provide a pattern.")

    # collect files to be transformed
    xmlfiles: list[Path] = []
    if file_list:
        xmlfiles = [Path(file) for file in Path(file_list).read_text(encoding="utf-8").splitlines()]
    elif recursive:
        xmlfiles = list(Path(start_dir[0]).rglob(pattern))
    else:
        xmlfiles = list(Path(start_dir[0]).glob(pattern))
    
    # exclude DC.xml files if not explicitly requested
    if exclude is not None:
        xmlfiles = [x for x in xmlfiles if x.name not in exclude]

    # As we have a fixed output file name, we need to make sure that the pattern only
    # matches one file per directory
    suspicious_dirs = utils.find_multiple_files_per_dir(xmlfiles)
    if suspicious_dirs:
        first_problematic_dir = str(suspicious_dirs[0][0])
        problem_files  = ", ".join([x.name for x in suspicious_dirs[0][1]])
        raise click.ClickException(
            f"Ambiguous pattern '{pattern}' matches more than one file in at least one directory. "
            f"{first_problematic_dir}: {problem_files}."
            "Please refine your pattern."
        )

    # here we go
    for xmlfile in xmlfiles:
        output_file_path = xmlfile.parent / output_filename
        try:
            transform(xmlfile, Path(xslt_file), output_file_path)
        except TransformationError as exp:
            logger.error("Error transforming %s: %s", xmlfile, exp)
            raise click.ClickException(f"Error transforming {xmlfile}: {exp}") from exp


@click.command(name="saxon-version")
def saxon_version():
    """Show the version of the Saxon processor."""
    click.echo(f"{get_saxon_version()}")


cli.add_command(saxon_version)
cli.add_command(transform_xslt)
