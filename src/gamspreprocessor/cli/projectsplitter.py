"""The subcommands for the projectsplitter module."""

import logging
from pathlib import Path
from typing import Tuple

import click

from .. import NAME, utils
from ..projectsplitter.splitter import ProjectSplitter
from ..projectsplitter.bookkeeper import BookKeeper

logger = logging.getLogger(NAME)
utils.configure_logging()


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
    default=click.Path("./objects"),
    help="The output folder where the object directories will be created. Default: './objects'.",
)
@click.option(
    "-f",
    "--object-format",
    type=click.Choice(["auto", "tei", "lido"], case_sensitive=False),
    default="auto",
    help="The type of files to split. Default is 'auto'.",
)
@click.option(
    "--reset",
    is_flag=True,
    default=False,
    help="Reset the bookkeeper. Only use this to start all over again.",
)
@click.argument("sourcefiles", nargs=-1)
def split_project(output_dir: str, object_format: str, reset: bool, sourcefiles: Tuple[str]):
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
    splitter = ProjectSplitter(Path(output_dir), Path(sourcefiles[0]).parent)
    #project_dir  = sourcefiles[0].parent
    if reset:
        splitter.reset()
    # it's enough to update once per run
    splitter.update_bookkeeper()
    for sourcefile in sourcefiles:
        object_counter += 1        
        file_counter += len(splitter.split(Path(sourcefile), object_format))
    click.echo(f"Created {object_counter} object dirs, containing {file_counter} files.")


@click.command(name="foo")
@click.argument("project_root", type=click.Path(exists=True))
def find_unhandled(project_root: str):
    """List all files which have bot been added to an object dir.

    This command lists all files from the project dir, which have not been
    processed by a split command yet.
    """
    project_root = Path(project_root)
    if not (project_root / BookKeeper.FILENAME).exists():
       raise click.ClickException(
           "No bookkeeper file found. Did you run split?"
       )
    bookkeeper = BookKeeper(project_root)
    unhandled_files = bookkeeper.get_unhandled()
    click.echo("foo")
    #click.echo(f"Found {len(unhandled_files)} unhandled files:\n"
    #           f"{"\t\n".join(str(f) for f in unhandled_files)}")
    #for unhandled in unhandled_files():
    #    click.echo(unhandled)


cli.add_command(split_project)
cli.add_command(find_unhandled)