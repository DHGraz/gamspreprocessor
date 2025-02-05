"""CLI commands for managing GAMS object CSV files."""

import logging
from pathlib import Path
import tempfile

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
@click.argument("projectroot", required=True, type=click.Path(exists=True))
def createcsv(projectroot: str, configfile: str | None, force_overwrite: bool = False):
    """Generate csv files with metadata for object directories.

    Generates a 'object.csv' and 'datastreams.csv' file for each object directory
    in or below 'rootfolder'. This means that this command can be run against
    a single object directory or a project directory containing multiple object directories.

    Use `packager objectcsv create --help` to see the available options.
    """
    if configfile is None:
        config_path = gamslib.projectconfiguration.utils.get_config_file_from_env()
        if config_path is None: # env settings not found
            config_path = gamslib.projectconfiguration.utils.find_project_toml(Path(projectroot))
        
    cfg = gamslib.projectconfiguration.get_configuration(config_path)
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
@click.argument("projectroot", required=True, type=click.Path(exists=True))
def collectcsv(projectroot: str, output_dir: str | None = None, to_csv: bool = False):
    """Collect data from all csv files in all object folders.

    Collect data from all 'object.csv' and all 'datastreams.csv' files below 'rootfolder'
    into a 'all_objects.xlsx' file.
    If the '--to-csv' flag is set, the output will be be no xlsx file, but two csv
    files will be created: 'all_objects.csv' and 'all_datastreams.csv'.

    If no 'output-dir' is set, the new file(s) will be created in the current
    working directory.

    Use 'packager csv collect --help' to see the available options.
    """
    # if output_dir is not None:
    output_path = Path(output_dir) if output_dir else Path.cwd()
    all_objects_file = output_path / "all_objects.csv"
    all_ds_file = output_path / "all_datastreams.csv"

    obj_csv = gamslib.objectcsv.collect_csv_data(
        Path(projectroot), all_objects_file, all_ds_file
    )
    # ToDo: add folder {obj_csv.object_dir.name} to avoid problems with linter/tests
    if to_csv:
        click.echo(f"Created csv files {all_objects_file} and {all_ds_file} for data in folder {obj_csv.object_dir.name}.")
    else:
        xlsx_file = output_path / "all_objects.xlsx"
        gamslib.objectcsv.csv_to_xlsx(all_objects_file, all_ds_file, xlsx_file)
        all_objects_file.unlink()
        all_ds_file.unlink()
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

    Use 'packager csv update --help' to see the available options.
    """
    input_path = Path(input_dir) if isinstance(input_dir, str) else Path.cwd()

    if from_csv:
        num_of_obj, num_of_ds = gamslib.objectcsv.update_csv_files(
            Path(projectroot), input_path
        )

    else:
        # convert xlsx to csv files before update
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            xlsx_file = input_path / "all_objects.xlsx"
            obj_file = tmp_path / "all_objects.csv"
            ds_file = tmp_path / "all_datastreams.csv"
            gamslib.objectcsv.xlsx_to_csv(xlsx_file, obj_file, ds_file)
            num_of_obj, num_of_ds = gamslib.objectcsv.update_csv_files(
                Path(projectroot), tmp_path
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

    Use 'packager csv csv2xlsx --help' to see the available options.
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

    Use 'packager csv xlsx2csv --help' to see the available options.
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
