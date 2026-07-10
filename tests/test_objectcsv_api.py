"""Test the public objectcsv API wrappers."""

from pathlib import Path
from shutil import copytree

from gamspreprocessor import objectcsv as objectcsv_api


FIXTURE_OBJECTS = Path(__file__).resolve().parent / "cli" / "test_objectcsv" / "objects"


def copy_object_fixture(tmp_path: Path) -> Path:
    """Copy the checked-in object fixture tree into a temporary directory."""
    objects_dir = tmp_path / "objects"
    copytree(FIXTURE_OBJECTS, objects_dir)
    return objects_dir


def test_create_csv_files_api(tmp_path):
    """The public wrapper should create the per-object csv files."""
    objects_dir = copy_object_fixture(tmp_path)
    csv_objects = objectcsv_api.create_csv_files(
        objects_dir, configfile=objects_dir / "gamsproject.toml"
    )

    assert len(csv_objects) == 2
    assert (objects_dir / "obj1" / "object.csv").exists()
    assert (objects_dir / "obj1" / "datastreams.csv").exists()
    assert (objects_dir / "obj2" / "object.csv").exists()
    assert (objects_dir / "obj2" / "datastreams.csv").exists()


def test_collect_and_convert_api(tmp_path):
    """The public wrapper should collect to csv and xlsx outputs."""
    objects_dir = copy_object_fixture(tmp_path)
    objectcsv_api.create_csv_files(
        objects_dir, configfile=objects_dir / "gamsproject.toml"
    )

    xlsx_file = objectcsv_api.collect_csv_data(
        objects_dir, output_dir=tmp_path
    )
    assert xlsx_file == tmp_path / "all_objects.xlsx"
    assert xlsx_file.exists()

    object_csv_file, ds_csv_file = objectcsv_api.collect_csv_data(
        objects_dir, output_dir=tmp_path, to_csv=True
    )
    assert object_csv_file == tmp_path / "all_objects.csv"
    assert ds_csv_file == tmp_path / "all_datastreams.csv"
    assert object_csv_file.exists()
    assert ds_csv_file.exists()


def test_update_csv_files_accepts_path_input_dir(tmp_path):
    """The public update wrapper should accept Path input directories."""
    objects_dir = copy_object_fixture(tmp_path)
    objectcsv_api.create_csv_files(
        objects_dir, configfile=objects_dir / "gamsproject.toml"
    )
    objectcsv_api.collect_csv_data(objects_dir, output_dir=tmp_path)

    num_of_obj, num_of_ds = objectcsv_api.update_csv_files(
        objects_dir, input_dir=tmp_path
    )

    assert num_of_obj == 2
    assert num_of_ds == 3