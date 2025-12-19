"""CLI subcommand validate.

Validate the created object dir.
"""

import logging
import warnings
from pathlib import Path

import click
from gamslib.objectdir import (
    ObjectDirectoryValidationError,
    find_object_folders,
    validate_object_dir,
)

logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.option(
    "-c",
    "--continue-on-error",
    is_flag=True,
    help="Continue validating other object directories even if one fails.",
)
@click.argument("start-dir", nargs=1)
def validate(start_dir: str, continue_on_error: bool):
    """Validate object folder(s).

    This subcommand can be used to validate a single object directory or a folder containing
    multiple object directories. The validation
    checks for the presence of required files and the correctness of their formats.
    """
    quiet = click.get_current_context().params.get("quiet", False)
    start_path = Path(start_dir)
    if not start_path.is_dir():
        raise click.ClickException(f"Start directory {start_dir} is not a directory.")
    success_counter = 0
    failed_dirs = {}
    warnings.filterwarnings("ignore", category=UserWarning)
    for obj_dir in find_object_folders(start_path):
        try:
            validate_object_dir(obj_dir)
            if not quiet:
                click.echo(
                    ".",
                    nl=False,
                )
            success_counter += 1
        except ObjectDirectoryValidationError as e:
            if not quiet:
                click.echo("F", nl=False)
            failed_dirs[obj_dir.relative_to(start_path)] = str(e)
            if not continue_on_error:
                break
    if not quiet:
        click.echo()  # New line after progress indicators
    if failed_dirs:
        total_dirs = success_counter + len(failed_dirs)
        with open("validation_errors.log", "w", encoding="utf-8") as log_file:
            for obj_dir, error_msg in failed_dirs.items():
                log_file.write(f"{obj_dir}: {error_msg}\n")
        raise click.ClickException(
            f"{len(failed_dirs)}/{total_dirs} object directories failed validation. See "
            "validation_errors.log for details."
        )
    if not quiet:
        click.echo(
            f"Validation completed. All {success_counter} object directories are valid."
        )
