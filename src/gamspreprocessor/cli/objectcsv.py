"""CLI commands for managing GAMS object CSV files."""

import logging

from pathlib import Path


import click
import gamslib.objectcsv
import gamslib.projectconfiguration

logger = logging.getLogger()


@click.group(name="csv")
def cli():
    """Helpers for managing GAMS object CSV files."""
    # intentionally left empty


@click.command(name="create")
@click.option(
    "--configfile",
    "-c",
    default=None,
    help=(
        "Path to the project TOML file. If not set, "
        "we check, if an environment variable 'GAMSCFG_PROJECT_TOML' is set. "
        "If not, we check if a '.env' file exists in the current working directory "
        "and if it contains a line 'project_toml='. If none of these options are set, "
        "we search for a 'project.toml' in this order: "
        "1) in the objects folder or a parent folder of the objects folder, "
        "2) in the current working directory. "
        "If no project TOML file is found, the command will fail."
    ),
)
@click.option(
    "--force-overwrite",
    "-f",
    is_flag=True,
    help=(
        "Overwrite existing csv files. Use with caution, "
        "because all manually changed metadata will get lost"
    ),
)
@click.option(
    "--update", "-u", is_flag=True, default=False, help="Update existing csv files."
)
@click.argument("projectroot", required=True, type=click.Path(exists=True))
def createcsv(
    projectroot: str,
    configfile: str | None,
    force_overwrite: bool = False,
    update: bool = False,
):
    """Generate csv files with metadata for object directories.

    Generates a 'object.csv' and 'datastreams.csv' file for each object directory
    in or below 'rootfolder'. This means that this command can be run against
    a single object directory or a project directory containing multiple object directories.

    This command will not overwrite existing csv files, unless the '--force-overwrite' flag
    or the `--update` flag is set.

    Using '--force-overwrite' will overwrite all existing csv files. All existing metadata
    will be lost. This is only useful if you want to start over with the metadata.

    Using the `--update` flag will merge data for some fields from the existing csv files.
    This is useful if you want to update some metadata after you have added datastreams or
    you have changed the project configuration. Updating will not touch fields
    like `description`, `tags` or `lang`. But it will replace fields which can be automatically
    derived from dublin core or the project configuration. So use with care if you have changed
    fields like `title`, `creator`, `publisher` or `rights` by hand. If no new value can be
    derived, the existing field will be kept.

    Use `packager objectcsv create --help` to see the available options.
    """
    if configfile is None:
        config_path = gamslib.projectconfiguration.utils.get_config_file_from_env()
        if config_path is None:  # env settings not found
            config_path = gamslib.projectconfiguration.utils.find_project_toml(
                Path(projectroot)
            )
    else:
        config_path = Path(configfile)

    cfg = gamslib.projectconfiguration.get_configuration(config_path)
<<<<<<< HEAD
=======

>>>>>>> 88963ca (Update: Collecting csv without creating csv files first now fails with error message)
    if update:
        csv_objects = gamslib.objectcsv.create_csv_files(
            Path(projectroot), cfg, update=True
        )
        click.echo(
            f"Updated csv files for {len(csv_objects)} objects "
            f"({sum(obj.count_datastreams() for obj in csv_objects)} content files)."
        )
    else:  # create new csv files
        csv_objects = gamslib.objectcsv.create_csv_files(
            Path(projectroot), cfg, force_overwrite
        )
        click.echo(
            f"Created csv files for {len(csv_objects)} objects "
            f"({sum(obj.count_datastreams() for obj in csv_objects)} content files)."
        )


@click.command(name="collect")
@click.option(
    "--output-dir",
    "-o",
    default=None,
    help="Path to the output directory. Default is the current working directory.",
)
@click.option("--to-csv", "-c", is_flag=True, help="Output csv files instead of xlsx.")
@click.argument("objects-dir", required=True, type=click.Path(exists=True))
def collectcsv(objects_dir: str, output_dir: str | None = None, to_csv: bool = False):
    """Collect data from all csv files in all object folders.

    Collect data from all 'object.csv' and all 'datastreams.csv' files below 'objects-dir'
    into a 'all_objects.xlsx' file.

    If the '--to-csv' flag is set, the output will not be a single xlsx file, but two csv
    files will be created: 'all_objects.csv' and 'all_datastreams.csv'.


    If no 'output-dir' is set, the new file(s) will be created in the current
    working directory.

    Use 'preprocess csv collect --help' to see the available options.
    """
    # if output_dir is not None:
    output_path = Path(output_dir) if output_dir else Path.cwd()
<<<<<<< HEAD

    try:
        obj_csv = gamslib.objectcsv.manage_csv.collect_csv_data(
            Path(objects_dir),  # all_objects_file, all_ds_file
        )
    except ValueError as e:
        click.echo(f"Cannot collect data, because of empty csv "
                  f"files: {e}. Try running csv create first!")
        raise e from e
    except FileNotFoundError as e:
        click.echo(f"Cannot collect data, because of missing csv "
                   f"file(s): {e}. Try running 'csv create' first!")
=======
    all_objects_file = output_path / 'all_objects.csv'
    all_ds_file = output_path / 'all_datastreams.csv'

    try:
        obj_csv = gamslib.objectcsv.collect_csv_data(
            Path(objects_dir), all_objects_file, all_ds_file
        )
    except gamslib.objectcsv.exception.ValidationError as e:
        click.echo(f"Validation error: {e}")
        raise e from e
    except FileNotFoundError as e:
        click.echo(f"File not found: {e}")
>>>>>>> 88963ca (Update: Collecting csv without creating csv files first now fails with error message)
        raise e from e
    if to_csv:
        all_objects_file = output_path / gamslib.objectcsv.objectcollection.ALL_OBJECTS_CSV
        all_ds_file = output_path / gamslib.objectcsv.objectcollection.ALL_DATASTREAMS_CSV
        obj_csv.save_to_csv(all_objects_file, all_ds_file)
        click.echo(
            f"Created csv files {all_objects_file} and {all_ds_file} for data "
            f"in folder {all_ds_file.parent}."
        )
    else:
        xlsx_file = output_path / "all_objects.xlsx"
        obj_csv.save_to_xlsx(xlsx_file)
        click.echo(f"Created xlsx file {xlsx_file}")


@click.command(name="update")
@click.option(
    "--input-dir",
    "-i",
    help=(
        "Path to the directory where the collected csv files are located. This is the same "
        "directory as set as '--output-dir' in the 'collect' command. Default is the "
        "projectroot folder."
    ),
)
@click.option(
    "--from-csv", "-c", is_flag=True, help="Read from csv files instead of xlsx."
)
@click.argument(
    "projectroot",
    required=True,
    type=click.Path(exists=True),
)
def updatecsv(projectroot: str, input_dir: str | None = None, from_csv: bool = False):
    """Update object and datastream csv files from the collected csv files.

    This is the counterpart to the 'collect' command.
    'update' reads data from all_objects.xlsx and updates the 'object.csv' and 'datastreams.csv'
    in each object folder.

    Use the '--from-csv' flag to read from 'all_objects.csv' and 'all_datastreams.csv' instead
    of the xlsx file.

    If 'input_dir' is not set, all files are expected to be in the current working directory.

    Use 'preprocess csv update --help' to see the available options.
    """
    input_path = Path(input_dir) if isinstance(input_dir, str) else Path.cwd()

    if from_csv:
        obj_csv_file = input_path / gamslib.objectcsv.objectcollection.ALL_OBJECTS_CSV
        ds_csv_file = input_path / gamslib.objectcsv.objectcollection.ALL_DATASTREAMS_CSV
        if not obj_csv_file.exists() or not ds_csv_file.exists():
            raise FileNotFoundError(
                f"Cannot find {obj_csv_file.name} or {ds_csv_file.name} in {input_path}. "
                "Please run 'collect' first to create these files."
            )
        num_of_obj, num_of_ds = gamslib.objectcsv.split_from_csv(
            Path(projectroot), obj_csv_file, ds_csv_file
        )

    else:
        xlsx_file = input_path / gamslib.objectcsv.objectcollection.ALL_OBJECTS_XLSX
        if not xlsx_file.exists():
            raise FileNotFoundError(
                f"Cannot find {xlsx_file.name} in {input_path}. "
                "Please run 'collect' first to create this file."
            )
        num_of_obj, num_of_ds = gamslib.objectcsv.split_from_xlsx(
            Path(projectroot), xlsx_file
        )
    click.echo(
        f"Updated {num_of_obj} object records and {num_of_ds} datatstream records."
    )


@click.command(name="csv2xlsx")
@click.option(
    "--outputfile",
    "-o",
    default="all_objects.xlsx",
    help=(
        "Path to the output xlsx file. Default is 'all_objects.xlsx' "
        "in the folder where all_object.csv was read from."
    ),
)
@click.argument("object_csv", required=True, type=click.Path(exists=True))
@click.argument("ds_csv", required=True, type=click.Path(exists=True))
def csv2xlsx(object_csv: str, ds_csv: str, outputfile: str):
    """Convert csv files to xlsx files.

    Use 'preprocess csv csv2xlsx --help' to see the available options.
    """
    object_csv_path = Path(object_csv)
    ds_csv_path = Path(ds_csv)

    if outputfile == "all_objects.xlsx":
        outputfile_path = object_csv_path.parent / "all_objects.xlsx"
    else:
        outputfile_path = Path(outputfile)
    gamslib.objectcsv.csv_to_xlsx(object_csv_path, ds_csv_path, outputfile_path)
    logger.info("Converted csv files to %s", outputfile_path)


@click.command(name="xlsx2csv")
@click.option(
    "--object-csv",
    default="all_object.csv",
    help=(
        "Path to the output object csv file. Default is 'all_objects.csv' in "
        "the directory where the xlsx lives."
    ),
)
@click.option(
    "--ds-csv",
    default="all_datastreams.csv",
    help=(
        "Path to the output datastreams csv file. Default is 'all_datastreams.csv' "
        "in the directory where the xlsx lives."
    ),
)
@click.argument("xlsx_file", required=True, type=click.Path(exists=True))
def xlsx2csv(object_csv: str, ds_csv: str, xlsx_file: str):
    """Convert a xlsx metadata file to 2 csv files.

    Use 'preprocess csv xlsx2csv --help' to see the available options.
    """
    xlsx_file_path = Path(xlsx_file)
    if object_csv == "all_object.csv":
        object_csv_path = xlsx_file_path.parent / "all_objects.csv"
    else:
        object_csv_path = Path(object_csv)
    if ds_csv == "all_datastreams.csv":
        ds_csv_path = xlsx_file_path.parent / "all_datastreams.csv"
    else:
        ds_csv_path = Path(ds_csv)
    gamslib.objectcsv.xlsx_to_csv(xlsx_file_path, object_csv_path, ds_csv_path)
    logger.info(
        "Converted xlsx file to csv files: %s and %s", object_csv_path, ds_csv_path
    )


cli.add_command(createcsv)
cli.add_command(collectcsv)
cli.add_command(updatecsv)
cli.add_command(csv2xlsx)
cli.add_command(xlsx2csv)
