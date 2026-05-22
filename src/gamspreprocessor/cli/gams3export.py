"""CLI subcommand gams3export.

Export GAMS files to object directories.
"""

import logging
from pathlib import Path
from gamspreprocessor.gams3 import export_objects
import click

logger = logging.getLogger(__name__)


@click.command(name="gams3export")
@click.option(
    "-o",
    "--output-dir",
    default="./objects",
    type=click.Path(),
    help="The output folder where the object directories will be created. Default: './objects'.",
)
@click.option(
    "-r",
    "--replace",
    is_flag=True,
    help="Replace existing object directories during export.",
)
@click.option(
    "--strip-prefix", is_flag=True, default=False, help="Strip the prefix (e.g. o:)"
)
@click.option(
    "--base-url",
    default="https://gams.uni-graz.at/archive",
    help="Base URL of the GAMS 3 repository. Default: 'https://gams.uni-graz.at/archive'",
)
@click.argument("pattern", nargs=1)
def gams3export(
    output_dir: str, replace: bool, strip_prefix: bool, base_url: str, pattern: str
):
    """Export one or more objects from a GAMS 3 repository to local directories.

    pattern is a string containing a object PID or a pattern with wildcard, e.g. "o:foo*".
    Use quotes around the pattern to prevent shell expansion if wildcards are used.
    All objects matching the pattern will be exported.

    This subcommand can be used to export all objects matching a given PID pattern
    from a GAMS 3 repository to local directories. Each object will be stored in a
    separate subdirectory named after its PID (with ":" replaced by "%3A"). Use the
    --strip-prefix option to remove the "o:" prefix from the PID when naming the
    subdirectories.
    """
    quiet = click.get_current_context().params.get("quiet", False)
    output_root = Path(output_dir)
    # will be created by export_objects if it doesn't exist,
    # But I want the user to explicitely create the directory first.
    # TODO: does this make sense? Maybe just create it if it doesn't exist?
    if not output_root.is_dir():
        raise click.ClickException(
            f"Output directory '{output_dir}' does not exist or is not a directory."
        )
    warn_counter = 0
    ds_counter = 0
    obj_counter = 0
    for obj_counter, result in enumerate(
        export_objects(
            pattern,
            output_root,
            overwrite=replace,
            base_url=base_url,
            strip_prefix=strip_prefix,
        ),
        start=1,
    ):
        if result.warnings:
            for warn in result.warnings:
                logger.warning(
                    "Warning while exporting object '%s': %s", result.obj.pid, warn
                )
                click.echo(
                    f"Warning while exporting object {result.obj.pid}: {warn}", err=True
                )
                warn_counter += 1
        ds_counter += len(result.exported_files)
        if not quiet:
            click.echo(
                f"Exported object '{result.obj.pid}' with {len(result.exported_files)} datastreams."
            )
    if not quiet:
        click.echo('-' * 40)
        click.echo(
            f"Exported {ds_counter} datastreams from {obj_counter} objects "
            f"with {warn_counter} warnings."
        )
