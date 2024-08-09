from typing import Tuple
import click
import logging

from .. import utils

from .. import NAME

from .. projectsplitter.splitter import Splitter

logger = logging.getLogger(NAME)
utils.configure_logging()


@click.group()
def cli():
    """Split a project directory into objects directories or find unhandled files.
    """
    pass


@click.command(name="split-project")
@click.option(
    "-o",
    "--output-dir",
    default=click.Path("./objects"),
    help="The output folder where the object directories will be created. Default: './objects'.",
)
@click.option("-f", "--format", 
              type=click.Choice(['auto', 'tei', 'lido'], case_sensitive=False),
              default = "auto",
              help="The type of files to split. Default is 'auto'.")
@click.option("--reset", is_flag=True, default=False,
              help="Reset the bookkeeper. Only use this to start all over again.")
@click.argument("sourcefiles", nargs=-1)
def split_project(output_dir:str, format:str, reset:bool, sourcefiles:Tuple[str]):
    """Split an existing project directory into objects directories.

    Legacy projects kept all objects in a single directory. 
    This command will create a directory for each object.

    The sourcefiles arguments accecpts a list of files to be split.
    if your shell supports wildcards (most will), you can use them to 
    specify the files. eg. 'somedir/*.xml' will split all xml files in 
    the somedir directory.  
    """
    splitter = Splitter(output_dir)
    if reset:
        splitter.reset()
    for sourcefile in sourcefiles:
        splitter.split(sourcefile, format)


@click.command(name="find-unhandled")
@click.option(
    "-o",
    "--output-dir",
    default=click.Path("./objects"),
    help="The output folder where the object directories will be created. Default: './objects'.",
)
@click.argument("object_root")
def find_unhandled(object_root:str):
    "List all files which have bot been added to an object dir"
    