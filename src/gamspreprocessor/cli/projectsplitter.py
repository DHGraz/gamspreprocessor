"""The subcommands for the projectsplitter module."""

import logging
from pathlib import Path

import click

from gamspreprocessor import projectsplitter as projectsplitter_api

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@click.group(name="splitproject")
def cli():
    """Helpers for creating object directories.

    These commands might be useful to convert a GAMS3/4 style project directory
    into a set of object directories like expected in GAMS5.
    """

# pylint: disable=too-many-positional-arguments
@click.command(name="split")
@click.option(
    "-o",
    "--output-dir",
    default="./objects",
    type=click.Path(exists=True),
    help=("The output folder where the object directories will be created."
          "Default: '<projectroot>/objects'."),
)
@click.option(
    "-f",
    "--object-format",
    type=click.Choice(["auto", "tei", "lido"], case_sensitive=False),
    default="auto",
    help="The type of files to split. Default is 'auto'.",
)
@click.option(
    "-l",
    "--file-list",
    type=click.Path(exists=True),
    help="A file containing a list of files (with path, if necessary) to be split.",
)
@click.option(
    "-r",
    "--replace",
    is_flag=True,
    default=False,
    help="Replace existing object directories. Think twice before using this option.",
)
@click.option(
    "--reset",
    is_flag=True,
    default=False,
    help="Reset the bookkeeper. Only use this to start all over again.",
)
@click.option(
    "--strip-prefix", is_flag=True, default=False, help="Strip the prefix (e.g. o:)"
)
@click.argument("sourcefiles", nargs=-1)
def split_project(  # noqa: PLR0913
    output_dir: str,
    object_format: str,
    reset: bool,
    replace: bool,
    file_list: str,
    strip_prefix: bool,
    sourcefiles: tuple[str, ...],
):
    """Split project files into objects directories.

    Legacy projects kept all objects in a single directory.
    This command will create a directory for each object.

    The sourcefiles arguments accecpts a list of files to be split.
    if your shell supports wildcards (most will), you can use them to
    specify the files. eg. 'somedir/*.xml' will split all xml files in
    the somedir directory.
    """
    if file_list and sourcefiles:
        raise click.ClickException(
            "You cannot use both '--file-list' and 'sourcefiles'."
        )
    if file_list:
        with open(file_list, "r", encoding="utf-8", newline="") as f:
            src_files = f.read().splitlines()
    else:
        src_files = sourcefiles
    try:
        splitter = projectsplitter_api.create_project_splitter(
            Path(output_dir),
            Path(src_files[0]).parent,
            replace=replace,
            reset=reset,
        )
        file_counter = 0
        object_counter = 0
        for sourcefile in src_files:
            try:
                copied_files = projectsplitter_api.split_project_file(
                    splitter, sourcefile, object_format, strip_prefix
                )
            except FileExistsError as exp:
                raise click.ClickException(
                    f"Object directory for {sourcefile} already exists. "
                    "Use '--replace' to overwrite the object directory or delete the directory by hand."
                ) from exp
            file_counter += len(copied_files)
            object_counter += 1
            click.echo(f"Split {sourcefile} into object directories.")
    except ValueError as exp:
        raise click.ClickException(str(exp)) from exp
    click.echo(
        f"Created {object_counter} object dirs, containing {file_counter} files."
    )


@click.command(name="showunhandled")
@click.argument("output-dir", type=click.Path(exists=True))
def showunhandled(output_dir: str = "./objects"):
    """List all files which have not been added to an object directory.

    'output-dir' is the root directory of the object directories, this is the value you used
    as option '-o' ('--output-dir') for the split command. If not set, the default is './objects'.

    This command lists all files from the project directory, which have not been
    processed by a split command yet.
    """
    try:
        unhandled_files = projectsplitter_api.list_unhandled_files(Path(output_dir))
    except FileNotFoundError as exp:
        raise click.ClickException(str(exp)) from exp
    if len(unhandled_files) == 0:
        click.echo("No unhandled files found.")
    elif len(unhandled_files) == 1:
        click.echo(f"Found 1 unhandled file: {unhandled_files[0]}")
    else:
        # python < 3.12 does not support backslashes in f-strings
        files_str = "\n\t".join(str(f) for f in unhandled_files)
        click.echo(f"Found {len(unhandled_files)} unhandled files:\n{files_str}")


cli.add_command(split_project)
cli.add_command(showunhandled)
