"""
Test the csv commands in the cli module."""

import csv
from pathlib import Path

import pytest
from click.testing import CliRunner

from gamslib.objectcsv import objectdata
from gamslib.objectcsv import dsdata
from gamspreprocessor.cli.main import cli


def read_csv_file(file):
    """Return the contents of a csv file as a list of dicts.

    Helper function for modify_csv_files.
    """
    with open(file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def read_csv_file_to_dict(file, key_field):
    """Return the contents of a csv file as a dict of dicts.

    Use the value of 'key_field' as the key for the dict.
    """
    data = {}
    for row in read_csv_file(file):
        data[row[key_field]] = row
    return data


def write_csv_file(file, data):
    """Write contents of a list of dicts to a CSV file.

    Helper function for modify_csv_files.
    """
    with open(file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def modify_csv_files(object_dir) -> tuple[list[dict], list[dict]]:
    """Make changes to obj1/objects.csv and obj1/datastreams.csv
    What is changed:
    - obj1/object.csv: the first row is modified by changing title to 'Changed title'
    - obj1/datastreams.csv:
      - remove data for SOURCE.xml
      - Change title for DC.xml to 'Changed title'
    """

    # Replace title in obj1/object.csv
    obj_csvdata = read_csv_file(object_dir / "object.csv")
    obj_csvdata[0]["title"] = "Changed title"
    write_csv_file(object_dir / "object.csv", obj_csvdata)

    ds_csvdata = read_csv_file(object_dir / "datastreams.csv")
    # remove SOURCE.xml from datastreams.csv and change title of DC.xml
    new_data = []
    for row in ds_csvdata:
        if row["dsid"] == "SOURCE.xml":
            continue
        if row["dsid"] == "DC.xml":
            row["title"] = "Changed title"
        new_data.append(row)

    write_csv_file(object_dir / "datastreams.csv", new_data)
    return obj_csvdata, new_data


def test_create_csv(datadir):
    """Test the csv create command."""
    runner = CliRunner()
    # cfgfile = str(datadir / "objects" / "project.toml")
    result = runner.invoke(cli, ["csv", "create", str(datadir / "objects")])
    assert result.exit_code == 0
    assert "Created csv files for 2 objects (3 content files)" in result.output
    assert (datadir / "objects" / "obj1" / "object.csv").exists()
    assert (datadir / "objects" / "obj1" / "datastreams.csv").exists()
    assert (datadir / "objects" / "obj2" / "object.csv").exists()
    assert (datadir / "objects" / "obj2" / "datastreams.csv").exists()

    # check if all csv colums are present in object.csv
    obj_csvdata = read_csv_file(datadir / "objects" / "obj1" / "object.csv")
    for field in objectdata.ObjectData.fieldnames():
        assert field in obj_csvdata[0]
    # As we did not use the --use-subjects-as-tags option, tags should be empty
    assert obj_csvdata[0]["tags"] == ""

    # check if all csv colums are present in datastreams.csv
    ds_csvdata = read_csv_file(datadir / "objects" / "obj1" / "datastreams.csv")
    for field in dsdata.DSData.fieldnames():
        assert field in ds_csvdata[0], f"Missing field '{field}' in datastreams.csv"


def test_create_csv_with_update_flag(datadir):
    """Test the csv collect command."""
    runner = CliRunner()

    # create the initial csv files
    objects_dir = datadir / "objects"
    result = runner.invoke(cli, ["csv", "create", str(objects_dir)])
    assert result.exit_code == 0

    # Now modify the initial csv files in obj1, but keep original values
    modified_objects_dir = objects_dir / "obj1"
    initial_obj_csvdata = read_csv_file(modified_objects_dir / "object.csv")
    initial_ds_csvdata = read_csv_file_to_dict(
        modified_objects_dir / "datastreams.csv", "dsid"
    )
    modified_obj_csvdata, modified_ds_csvdata = modify_csv_files(modified_objects_dir)

    # make sure the modify_csv_files function worked
    assert read_csv_file(modified_objects_dir / "object.csv") == modified_obj_csvdata
    assert (
        read_csv_file(modified_objects_dir / "datastreams.csv") == modified_ds_csvdata
    )

    # Now run the create command again with the --update flag.
    result = runner.invoke(cli, ["csv", "create", "--update", str(objects_dir)])
    assert result.exit_code == 0
    assert "Updated csv files for 2 objects (3 content files)" in result.output

    final_obj_csvdata = read_csv_file(modified_objects_dir / "object.csv")
    assert len(final_obj_csvdata) == 1
    assert final_obj_csvdata[0]["title"] == initial_obj_csvdata[0]["title"]

    final_ds_csvdata = read_csv_file_to_dict(
        modified_objects_dir / "datastreams.csv", "dsid"
    )
    assert "DC.xml" in final_ds_csvdata
    assert "SOURCE.xml" in final_ds_csvdata

    assert (
        final_ds_csvdata["SOURCE.xml"]["title"]
        == initial_ds_csvdata["SOURCE.xml"]["title"]
    )
    assert final_ds_csvdata["DC.xml"]["title"] == initial_ds_csvdata["DC.xml"]["title"]


def test_create_csv_with_tags(datadir):
    """Test the csv create command with --use-subjects-as-tags."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["csv", "create", "--use-subjects-as-tags", str(datadir / "objects")],
    )
    assert result.exit_code == 0
    assert "Created csv files for 2 objects (3 content files)" in result.output
    obj1_csv = read_csv_file(datadir / "objects" / "obj1" / "object.csv")
    obj2_csv = read_csv_file(datadir / "objects" / "obj2" / "object.csv")

    assert "tags" in obj1_csv[0]
    assert obj1_csv[0]["tags"] == "Tag1;Tag2"

    # obj2 has no subjects, so tags should be empty
    assert "tags" in obj2_csv[0]
    assert obj2_csv[0]["tags"] == ""


def test_create_csv_with_update_flag_and_tags(datadir):
    """Test the csv create command with --update and --use-subjects-as-tags."""
    runner = CliRunner()

    # create the initial csv files without tags
    objects_dir = datadir / "objects"
    result = runner.invoke(cli, ["csv", "create", str(objects_dir)])
    assert result.exit_code == 0

    # Now run the create command again with the --update and --use-subjects-as-tags flag.
    cmd = "csv create --update --use-subjects-as-tags " + str(objects_dir)
    result = runner.invoke(cli, cmd.split())
    assert result.exit_code == 0

    obj1_csv = read_csv_file(datadir / "objects" / "obj1" / "object.csv")

    assert "tags" in obj1_csv[0]
    assert obj1_csv[0]["tags"] == "Tag1;Tag2"


def test_create_csv_with_update_flag_and_tags_does_not_overwrite_existing_tags(datadir):
    """Test the csv create command with --update and --use-subjects-as-tags.
    Make sure that existing tags are not overwritten.
    """
    runner = CliRunner()
    objects_dir = datadir / "objects"

    # create the initial csv files with tags
    result = runner.invoke(
        cli, ["csv", "create", "--use-subjects-as-tags", str(objects_dir)]
    )
    assert result.exit_code == 0
    obj1_csv = read_csv_file(objects_dir / "obj1" / "object.csv")
    assert obj1_csv[0]["tags"] == "Tag1;Tag2"

    # Change subjects in DC.xml to see if they get picked up (they should not)
    dc_xml = datadir / "objects" / "obj1" / "DC.xml"
    dc_xml_contents = dc_xml.read_text(encoding="utf-8")
    dc_xml_contents = dc_xml_contents.replace(
        "<dc:subject>Tag1</dc:subject>", "<dc:subject>NewTag1</dc:subject>"
    )
    dc_xml_contents = dc_xml_contents.replace(
        "<dc:subject>Tag2</dc:subject>", "<dc:subject>NewTag2</dc:subject>"
    )
    dc_xml.write_text(dc_xml_contents, encoding="utf-8")

    cmd = "csv create --update --use-subjects-as-tags " + str(objects_dir)
    result = runner.invoke(cli, cmd.split())
    assert result.exit_code == 0
    obj1_csv = read_csv_file(datadir / "objects" / "obj1" / "object.csv")
    # tags must be unchanged
    assert obj1_csv[0]["tags"] == "Tag1;Tag2"


def test_collect_csv(datadir, monkeypatch):
    """Test the csv collect command."""
    monkeypatch.chdir(datadir)
    runner = CliRunner()

    # First we have to generate the csv files
    result = runner.invoke(cli, ["csv", "create", str(datadir / "objects")])
    assert result.exit_code == 0
    assert (datadir / "objects" / "obj1" / "object.csv").exists()
    assert (datadir / "objects" / "obj1" / "datastreams.csv").exists()

    result = runner.invoke(cli, ["csv", "collect", str(datadir / "objects")])

    assert result.exit_code == 0

    assert (datadir / "all_objects.xlsx").exists()
    assert "Created xlsx file" in result.output

    # and now with option --to-csv
    result = runner.invoke(
        cli, ["csv", "collect", "--to-csv", str(datadir / "objects")]
    )
    assert result.exit_code == 0
    assert "Created csv files" in result.output
    assert (datadir / "all_datastreams.csv").exists()


def test_collect_csv_with_missing_csv_file(datadir):
    """Running collect on objects with missing csv files should fail."""
    runner = CliRunner()
    obj1_dir = datadir / "objects" / "obj1"

    # Create all csv files first
    result = runner.invoke(cli, ["csv", "create", str(datadir / "objects")])
    assert result.exit_code == 0

    # move object.csv out of th way
    (obj1_dir / "object.csv").rename(obj1_dir / "object.csv.bak")
    assert not (obj1_dir / "object.csv").exists()

    result = runner.invoke(cli, ["csv", "collect", str(datadir / "objects")])
    assert result.exit_code != 0

    # # Now the same for a missing datastreams.csv
    # (obj1_dir / 'object.csv.bak').rename(obj1_dir / "object.csv")
    # (obj1_dir / 'datastreams.csv').unlink()
    # assert not (obj1_dir / "datastreams.csv").exists()
    # result = runner.invoke(cli, ["csv", "collect", str(datadir / "objects")])
    # assert result.exit_code != 0


def remove_csv_data(csv_file: Path, keep_column_names: bool = True):
    """Remove the data from the csv files. Keep the column names."""
    lines = csv_file.read_text(encoding="utf-8").splitlines()
    with csv_file.open("w", encoding="utf-8", newline="") as f:
        if lines:
            if keep_column_names:
                f.write(lines[0] + "\n")
            else:
                f.write("\n")
        f.flush()


@pytest.mark.parametrize(
    "obj, csv_filename, keep_column_names",
    [
        ("obj1", "object.csv", True),
        ("obj1", "object.csv", False),
        ("obj1", "datastreams.csv", True),
        ("obj1", "datastreams.csv", False),
        ("obj2", "object.csv", True),
        ("obj2", "object.csv", False),
        ("obj2", "datastreams.csv", True),
        ("obj2", "datastreams.csv", False),
    ],
)
def test_collect_csv_with_empty_csv_file(obj, csv_filename, keep_column_names, datadir):
    """Running collect on objects with empty csv.

    Here we test it against the case where the object.csv only contains
    column names.
    """
    csv_file = datadir / "objects" / obj / csv_filename
    runner = CliRunner()

    # Prepare: Create all csv files first
    result = runner.invoke(cli, ["csv", "create", str(datadir / "objects")])
    assert result.exit_code == 0
    assert csv_file.exists()

    remove_csv_data(csv_file, keep_column_names)

    result = runner.invoke(cli, ["csv", "collect", str(datadir / "objects")])
    assert result.exit_code != 0
    assert "metadata (csv) is not set " in result.output
    assert "Try running" in result.output


def test_update_csv_from_xlsx(datadir):
    """Test the csv update command."""
    xlsx_file_dir = datadir / "xlsx"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["csv", "update", "--input-dir", xlsx_file_dir, str(datadir / "objects")]
    )
    assert result.exit_code == 0
    assert "Updated 1 object records and 3 datatstream records" in result.output


def test_update_csv_from_csv(datadir):
    """Test the csv update command with --from-csv."""

    csv_file_dir = datadir / "csv"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "csv",
            "update",
            "--from-csv",
            "--input-dir",
            csv_file_dir,
            str(datadir / "objects"),
        ],
    )
    assert result.exit_code == 0
    assert "Updated 1 object records and 3 datatstream records" in result.output


def test_csv2xlsx(datadir, tmp_path):
    """Test the csv csv2xlsx command."""
    runner = CliRunner()
    obj_csv = datadir / "csv" / "all_objects.csv"
    ds_csv = datadir / "csv" / "all_datastreams.csv"
    expected_xlsx = datadir / "csv" / "all_objects.xlsx"

    result = runner.invoke(cli, ["csv", "csv2xlsx", str(obj_csv), str(ds_csv)])
    assert result.exit_code == 0
    assert "Converted csv files to" in result.output
    assert expected_xlsx.exists()

    # now with an explicit output file
    expected_xlsx = tmp_path / "foobar.xlsx"
    result = runner.invoke(
        cli, ["csv", "csv2xlsx", str(obj_csv), str(ds_csv), "-o", str(expected_xlsx)]
    )
    assert result.exit_code == 0
    assert "Converted csv files to" in result.output
    assert expected_xlsx.exists()


def test_xlsx2csv(datadir, tmp_path):
    """Test the csv xlsx2csv command."""
    xlsx_file = datadir / "xlsx" / "all_objects.xlsx"
    runner = CliRunner()
    result = runner.invoke(cli, ["csv", "xlsx2csv", str(xlsx_file)])
    assert result.exit_code == 0
    assert "Converted xlsx file to csv files" in result.output
    assert (datadir / "xlsx" / "all_objects.csv").exists()
    assert (datadir / "xlsx" / "all_datastreams.csv").exists()

    # now with explicit output files
    obj_csv = tmp_path / "obj.csv"
    ds_csv = tmp_path / "ds.csv"
    result = runner.invoke(
        cli,
        [
            "csv",
            "xlsx2csv",
            str(xlsx_file),
            "--object-csv-file",
            str(obj_csv),
            "--ds-csv-file",
            str(ds_csv),
        ],
    )
    assert result.exit_code == 0
    assert "Converted xlsx file to" in result.output
    assert obj_csv.exists()
    assert ds_csv.exists()
