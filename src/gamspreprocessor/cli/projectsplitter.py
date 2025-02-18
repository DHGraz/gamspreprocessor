"""The subcommands for the projectsplitter module."""

import logging
from pathlib import Path
from typing import Tuple

import click

from ..projectsplitter.bookkeeper import BookKeeper
from ..projectsplitter.splitter import ProjectSplitter

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@click.group(name="splitproject")
def cli():
    """Helpers for creating object directories.

    These commands might be useful to convert a GAMS3/4 style project directory
    into a set of object directories like expected in GAMS5.
    """


@click.command(name="split")
@click.option(
    "-o",
    "--output-dir",
    default="./objects",
    type=click.Path(exists=True),
    help="The output folder where the object directories will be created. Default: '<projectroot>/objects'.",
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
def split_project( # noqa: PLR0913
    output_dir: str,
    object_format: str,
    reset: bool,
    replace: bool,
    file_list: str,
    strip_prefix: bool,
    sourcefiles: Tuple[str],
):
    """Split project files into objects directories.

    Legacy projects kept all objects in a single directory.
    This command will create a directory for each object.

    The sourcefiles arguments accecpts a list of files to be split.
    if your shell supports wildcards (most will), you can use them to
    specify the files. eg. 'somedir/*.xml' will split all xml files in
    the somedir directory.
    """
    file_counter = 0
    object_counter = 0
    if file_list and sourcefiles:
        raise click.ClickException(
            "You cannot use both '--file-list' and 'sourcefiles'."
        )
    if file_list:
        with open(file_list, "r", encoding="utf-8", newline="") as f:
            src_files = f.read().splitlines()
    else:
        src_files = sourcefiles
    if len(src_files) == 0:
        raise click.ClickException("No processable source files found.")
    splitter = ProjectSplitter(Path(output_dir), Path(src_files[0]).parent, replace)
    if reset:
        splitter.reset()
    # it's enough to update once per run
    splitter.update_bookkeeper()
    for sourcefile in src_files:
        try:
            copied_files = splitter.split(Path(sourcefile), object_format, strip_prefix)
            file_counter += len(copied_files)
            object_counter += 1
            click.echo(f"Split {sourcefile} into object directories.")
        except FileExistsError:
            raise click.ClickException(
                f"Object directory for {sourcefile} already exists. "
                "Use '--replace' to overwrite the object directory or delete the directory by hand."
            )
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
    objects_dir = Path(output_dir)
    if not (objects_dir / BookKeeper.FILENAME).exists():
        raise click.ClickException("No bookkeeper file found. Did you run split?")
    bookkeeper = BookKeeper(objects_dir / BookKeeper.FILENAME)
    unhandled_files = bookkeeper.get_unhandled()
    if len(unhandled_files) == 0:
        click.echo("No unhandled files found.")
    elif len(unhandled_files) == 1:
        click.echo(f"Found 1 unhandled file: {unhandled_files[0]}")
    else:
        # python < 3.12 does not support backslashes in f-strings
        files_str = "\n\t".join(str(f) for f in unhandled_files)
        click.echo(f"Found {len(unhandled_files)} unhandled files:\n" f"{files_str}")


cli.add_command(split_project)
cli.add_command(showunhandled)
