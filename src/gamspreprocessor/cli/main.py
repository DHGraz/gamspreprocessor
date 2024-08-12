"""The main module of the preprocess cli application.

As we expect a bigger number of subcommands in later stages, we decided to 
keep each subcommand in its own module in the cli package.
"""
import logging

import click

from .. import NAME, VERSION, utils
from . import projectsplitter

logger = logging.getLogger(NAME)
utils.configure_logging()


@click.group()
@click.option(
    "-v",
    "--verbose",
    "loglevel",
    flag_value=logging.DEBUG,
    help=(
        "Enable verbose logging. If used together with --quiet, only the "
        "last option specified is used."
    ),
)
@click.option(
    "-q",
    "--quiet",
    "loglevel",
    flag_value=logging.ERROR,
    help=(
        "Disable logging. Only Errors are shown. If used together with "
        "--verbose, only the last option specified is used."
    ),
)
@click.option(
    "--logfile", help="Path to the log file. If not set, no logfile will be created."
)
@click.version_option(version=VERSION, prog_name=NAME)
def cli(loglevel, logfile=f"{NAME}.log"):
    """preprocessor is the GAMS tool to preprocess GAMS objetcs.

    Each object is expected to be in a separate directory.

    Run packager --help to see the available commands.
    """
    if loglevel is None:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel)
    # for file logging we want at least logging.INFO
    filelog_level = logging.INFO if loglevel > logging.INFO else loglevel
    utils.configure_logging(loglevel, logfile, filelog_level)


cli.add_command(projectsplitter.split_project)
