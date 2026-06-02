"""CLI subcommand gams3export.

Export GAMS files to object directories.
"""

from dataclasses import dataclass
import logging
from pathlib import Path

import click
from gamspreprocessor.gams3 import export_objects
from gamspreprocessor.gams3.object import ExportStatus

logger = logging.getLogger(__name__)


def _get_export_file_logger() -> logging.Logger:
    """Return a logger that writes only to gams3export.log."""
    file_logger = logging.getLogger(f"{__name__}.file")
    loglevel = click.get_current_context().params.get("loglevel", False)
    file_logger.setLevel(loglevel if loglevel else logging.INFO)
    file_logger.propagate = False

    if not file_logger.handlers:
        handler = logging.FileHandler("gams3export.log", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        file_logger.addHandler(handler)

    return file_logger

@dataclass
class ExportStats:
    "Result of exporting a GAMS 3 object."

    objects_found: int = 0
    objects_exported: int = 0
    objects_replaced: int = 0
    objects_ignored: int = 0
    errors: int = 0
    warnings: int = 0
    datastreams_exported: int = 0

    def update_stats(self, obj):
        "Update the export stats based on the status of the given Gams3Object."
        self.objects_found += 1
        if obj.status == ExportStatus.EXPORTED:
            self.objects_exported += 1
            self.datastreams_exported += len(obj.exported_files)
        elif obj.status == ExportStatus.REPLACED:
            self.objects_replaced += 1
            self.datastreams_exported += len(obj.exported_files)
        elif obj.status == ExportStatus.IGNORED:
            self.objects_ignored += 1
        elif obj.status == ExportStatus.ERROR:
            self.errors += 1
        self.warnings += len(obj.warnings)

    def print_resume(self):
        "Print a summary of the export stats to the console."
        click.echo(
            f"Exported {self.objects_exported} objects with {self.datastreams_exported} datastreams, "
            f"replaced {self.objects_replaced} objects, "
            f"ignored {self.objects_ignored} objects, "
            f"with {self.warnings} warnings and {self.errors} errors.",
            err=self.errors > 0 
        )

def log_to_file(obj):
    "Log the export result of a Gams3Object to the export log file."
    file_logger = _get_export_file_logger()
    if obj.status == ExportStatus.ERROR:
        for err in obj.errors:
            file_logger.error(
                "Error while exporting object '%s': %s", obj.pid, err
            )
    else:
        file_logger.info(
            "Exported object '%s' with status %s: %d datastreams exported, %d warnings, %d errors",
            obj.pid,
            obj.status.name,
            len(obj.exported_files),
            len(obj.warnings),
            len(obj.errors),
        )
        if obj.warnings:
            file_logger.warning(
                "Warnings for object '%s': %s", obj.pid, "; ".join(str(warn) for warn in obj.warnings)
            )

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
@click.option('--colon-replacement', default="%3A", 
              help=("String to replace ':' in PIDs when naming subdirectories. "
                    "Ignored if --strip-prefix is used. Default: '%3A'. "
                    "DO NOT USE THIS OPTION to create object folders as expected by the packager!")
)
@click.argument("pattern", nargs=1)
def gams3export( # noqa: PLR0913 # pylint: disable=too-many-positional-arguments, too-many-arguments 
    output_dir: str, replace: bool, strip_prefix: bool, base_url: str, pattern: str,
    colon_replacement: str
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
    file_logger = _get_export_file_logger()
    quiet = click.get_current_context().params.get("quiet", False)
    output_root = Path(output_dir)
    file_logger.info(
        "Starting gams3export: pattern=%s output_dir=%s replace=%s strip_prefix=%s base_url=%s",
        pattern,
        output_dir,
        replace,
        strip_prefix,
        base_url,
    )
    # will be created by export_objects if it doesn't exist,
    # But I want the user to explicitely create the directory first.
    if not output_root.is_dir():
        file_logger.error("Output directory does not exist or is not a directory: %s", output_dir)
        raise click.ClickException(
            f"Output directory '{output_dir}' does not exist or is not a directory."
        )
    stats = ExportStats()
    for g3obj in export_objects(
            pattern,
            output_root,
            overwrite=replace,
            base_url=base_url,
            strip_prefix=strip_prefix,
            colon_replacement=colon_replacement
        ):
        stats.update_stats(g3obj)
        log_to_file(g3obj)
        if g3obj.status == ExportStatus.ERROR:
            click.echo(
                f"Error while exporting object {g3obj.pid}. See log file for details", err=True
            )
        if not quiet:
            click.echo(
                f"Exported object '{g3obj.pid}' with status {g3obj.status.name}: "
                f"{len(g3obj.exported_files)} datastreams exported, "
                f"{len(g3obj.warnings)} warnings, "
                f"{len(g3obj.errors)} errors."
            )
    click.echo('-' * 40)
    stats.print_resume()
