"""Public API for working with GAMS object CSV files.

These helpers mirror the CSV-related CLI commands, but are callable directly from Python.
"""

from pathlib import Path

import gamslib.objectcsv.create_csv
import gamslib.objectcsv.manage_csv
import gamslib.objectcsv.xlsx
import gamslib.projectconfiguration
from gamslib.objectcsv.objectcollection import (
    ALL_DATASTREAMS_CSV,
    ALL_OBJECTS_CSV,
    ALL_OBJECTS_XLSX,
)
from gamslib.projectconfiguration.utils import find_project_toml, get_config_file_from_env


def resolve_project_toml(
    projectroot: Path | str, configfile: Path | str | None = None
) -> Path:
    """Resolve the project TOML file used by the CSV workflow."""
    if configfile is None:
        config_path = get_config_file_from_env()
        if config_path is None:
            config_path = find_project_toml(Path(projectroot))
    else:
        config_path = Path(configfile)
    return config_path


def create_csv_files(
    projectroot: Path | str,
    configfile: Path | str | None = None,
    force_overwrite: bool = False,
    update: bool = False,
    use_subjects_as_tags: bool = False,
) -> list:
    """Generate object and datastream CSV files for a project tree."""
    cfg = gamslib.projectconfiguration.get_configuration(
        resolve_project_toml(projectroot, configfile)
    )
    return gamslib.objectcsv.create_csv.create_csv_files(
        Path(projectroot),
        cfg,
        force_overwrite=force_overwrite,
        update=update,
        use_subjects_as_tags=use_subjects_as_tags,
    )


def collect_csv_data(
    objects_dir: Path | str,
    output_dir: Path | str | None = None,
    to_csv: bool = False,
) -> Path | tuple[Path, Path]:
    """Collect per-object CSV files into a combined XLSX or CSV export."""
    output_path = Path(output_dir) if output_dir else Path.cwd()
    obj_csv = gamslib.objectcsv.manage_csv.collect_csv_data(Path(objects_dir))
    if to_csv:
        all_objects_file = output_path / ALL_OBJECTS_CSV
        all_ds_file = output_path / ALL_DATASTREAMS_CSV
        obj_csv.save_to_csv(all_objects_file, all_ds_file)
        return all_objects_file, all_ds_file
    xlsx_file = output_path / ALL_OBJECTS_XLSX
    obj_csv.save_to_xlsx(xlsx_file)
    return xlsx_file


def update_csv_files(
    projectroot: Path | str,
    input_dir: Path | str | None = None,
    from_csv: bool = False,
) -> tuple[int, int]:
    """Update per-object CSV files from a combined XLSX or CSV export."""
    input_path = Path(input_dir) if input_dir is not None else Path.cwd()

    if from_csv:
        obj_csv_file = input_path / ALL_OBJECTS_CSV
        ds_csv_file = input_path / ALL_DATASTREAMS_CSV
        if not obj_csv_file.exists() or not ds_csv_file.exists():
            raise FileNotFoundError(
                f"Cannot find {obj_csv_file.name} or {ds_csv_file.name} in {input_path}. "
                "Please run 'collect' first to create these files."
            )
        return gamslib.objectcsv.manage_csv.split_from_csv(
            Path(projectroot), obj_csv_file, ds_csv_file
        )

    xlsx_file = input_path / ALL_OBJECTS_XLSX
    if not xlsx_file.exists():
        raise FileNotFoundError(
            f"Cannot find {xlsx_file.name} in {input_path}. "
            "Please run 'collect' first to create this file."
        )
    return gamslib.objectcsv.manage_csv.split_from_xlsx(Path(projectroot), xlsx_file)


def csv_to_xlsx(
    objects_csv_file: Path | str,
    datastreams_csv_file: Path | str,
    outputfile: Path | str = "all_objects.xlsx",
) -> Path:
    """Convert combined CSV files into one XLSX file."""
    objects_csv_path = Path(objects_csv_file)
    datastreams_csv_path = Path(datastreams_csv_file)

    if outputfile == "all_objects.xlsx":
        outputfile_path = objects_csv_path.parent / "all_objects.xlsx"
    else:
        outputfile_path = Path(outputfile)
    return gamslib.objectcsv.xlsx.csv_to_xlsx(
        objects_csv_path, datastreams_csv_path, outputfile_path
    )


def xlsx_to_csv(
    xlsx_file: Path | str,
    object_csv_file: Path | str = "all_object.csv",
    ds_csv_file: Path | str = "all_datastreams.csv",
) -> tuple[Path, Path]:
    """Convert one XLSX file into the combined CSV files."""
    xlsx_file_path = Path(xlsx_file)
    if object_csv_file == "all_object.csv":
        object_csv_path = xlsx_file_path.parent / "all_objects.csv"
    else:
        object_csv_path = Path(object_csv_file)
    if ds_csv_file == "all_datastreams.csv":
        ds_csv_path = xlsx_file_path.parent / "all_datastreams.csv"
    else:
        ds_csv_path = Path(ds_csv_file)
    return gamslib.objectcsv.xlsx.xlsx_to_csv(xlsx_file_path, object_csv_path, ds_csv_path)


__all__ = [
    "collect_csv_data",
    "create_csv_files",
    "csv_to_xlsx",
    "resolve_project_toml",
    "update_csv_files",
    "xlsx_to_csv",
]