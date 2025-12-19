"""The main module of the preprocess cli application.

As we expect a bigger number of subcommands in later stages, we decided to
keep each subcommand in its own module in the cli package.
"""

import logging

import click

from .. import utils, VERSION, APP_NAME
from . import objectcsv
from . import project
from . import projectsplitter
from . import transform
from . import multitransform
from . import validate


@click.group()
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help=("Enable verbose logging. Cannot be used togesther with the --quiet flag."),
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    default=False,
    help=("Disable logging. Cannot be used togester with the '--verbose' flag."),
)
@click.option(
    "--logfile", help="Path to the log file. If not set, no logfile will be created."
)
@click.option(
    "--filelog-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="INFO",
    help="Log level for the log file. Default is INFO.",
)
@click.version_option(version=VERSION, prog_name=APP_NAME)
def cli(verbose: bool, quiet: bool, logfile: str, filelog_level: str):
    """preprocessor is the GAMS tool to preprocess and prepare GAMS objects before ingest.

    Each object is expected to be in a separate directory.

    Run preprocess --help to see the available commands.
    """
    if quiet and verbose:
        raise click.UsageError("Cannot use --quiet and --verbose together.")
    if quiet:
        loglevel = logging.ERROR
    elif verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    filelog_level_int = logging.getLevelNamesMapping()[filelog_level.upper()]
    utils.configure_logging(loglevel, logfile, filelog_level_int)


cli.add_command(objectcsv.cli)
cli.add_command(project.cli)
cli.add_command(projectsplitter.cli)
cli.add_command(transform.cli)
cli.add_command(multitransform.cli)
cli.add_command(validate.validate)
