import copy
import csv
from pathlib import Path
from click.testing import CliRunner
import pytest
from gamspreprocessor.cli.main import cli

def read_csv_file(file):
    """Return the contents of a csv file as a list of dicts.
    
    Helper function for modify_csv_files."
    """
    with open(file, "r") as f:
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
    with open(file, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def modify_csv_files(object_dir) -> tuple[list[dict]]:
    """Make changes to obj1/objects.csv and obj1/datastreams.csv
    What is changed:
    - obj1/object.csv: the first row is modified by changing title to 'Changed title'
    - obj1/datastreams.csv: 
      - remove data for SOURCE.xml
      - Change title for DC.xml to 'Changed title'    
    """

    # Replace title in obj1/object.csv
    obj_csvdata = read_csv_file(object_dir / "object.csv")
    obj_csvdata[0]['title'] = 'Changed title'
    write_csv_file(object_dir / "object.csv", obj_csvdata)
    
    ds_csvdata = read_csv_file(object_dir / "datastreams.csv")
    # remove SOURCE.xml from datastreams.csv and change title of DC.xml
    new_data = []
    for row in ds_csvdata:
        if row['dsid'] == 'SOURCE.xml':
            continue
        if row['dsid'] == 'DC.xml':
            row['title'] = 'Changed title'
        new_data.append(row)

    write_csv_file(object_dir / "datastreams.csv" , new_data)    
    return obj_csvdata, new_data




def test_create_csv(datadir):
    "Test the csv create command."
    runner = CliRunner()
    #cfgfile = str(datadir / "objects" / "project.toml")
    result = runner.invoke(cli, ["csv", "create", str(datadir / "objects")])
    assert result.exit_code == 0
    assert "Created csv files for 2 objects (3 content files)" in result.output
    assert (datadir / "objects" / "obj1" / "object.csv").exists()
    assert (datadir / "objects" / "obj1" / "datastreams.csv").exists()
    assert (datadir / "objects" / "obj2" / "object.csv").exists()
    assert (datadir / "objects" / "obj2" / "datastreams.csv").exists()




def test_create_csv_with_update_flag(datadir, monkeypatch):
    "Test the csv collect command."
    runner = CliRunner()

    # create the initial csv files
    objects_dir = datadir / "objects"
    result = runner.invoke(cli, ["csv", "create", str(objects_dir)])
    assert result.exit_code == 0

    # Now modify the initial csv files in obj1. But read the original data first, so we have the original values
    modified_objects_dir = objects_dir / "obj1"
    initial_obj_csvdata = read_csv_file(modified_objects_dir / "object.csv")
    initial_ds_csvdata = read_csv_file_to_dict(modified_objects_dir / "datastreams.csv", 'dsid')
    modified_obj_csvdata, modified_ds_csvdata = modify_csv_files(modified_objects_dir)

    # make sure the modify_csv_files function worked
    assert read_csv_file(modified_objects_dir / "object.csv") == modified_obj_csvdata
    assert read_csv_file(modified_objects_dir / "datastreams.csv") == modified_ds_csvdata

    # Now run the create command again with the --update flag. 
    result = runner.invoke(
        cli, ["csv", "create", "--update", str(objects_dir)]
    )
    assert result.exit_code == 0
    assert "Updated csv files for 2 objects (3 content files)" in result.output

    final_obj_csvdata = read_csv_file(modified_objects_dir / "object.csv")
    assert len(final_obj_csvdata) == 1
    assert final_obj_csvdata[0]['title'] == initial_obj_csvdata[0]['title']

    final_ds_csvdata = read_csv_file_to_dict(modified_objects_dir / "datastreams.csv", 'dsid')
    assert 'DC.xml' in final_ds_csvdata
    assert 'SOURCE.xml' in final_ds_csvdata
    
    assert final_ds_csvdata['SOURCE.xml']['title'] == initial_ds_csvdata['SOURCE.xml']['title']
    assert final_ds_csvdata['DC.xml']['title'] == initial_ds_csvdata['DC.xml']['title']  


def test_collect_csv(datadir, monkeypatch):
    "Test the csv collect command."
    monkeypatch.chdir(datadir)
    runner = CliRunner()
    result = runner.invoke(cli, ["csv", "collect", str(datadir / "objects")])
    assert result.exit_code == 0
    assert (datadir / "all_objects.xlsx").exists()
    assert "Created xlsx file" in result.output

    # and now with option --to-csv
    result = runner.invoke(
        cli, ["csv", "collect", str(datadir / "objects"), "--to-csv"]
    )
    assert result.exit_code == 0
    assert "Created csv files" in result.output
    assert (datadir / "all_objects.csv").exists()
    assert (datadir / "all_datastreams.csv").exists()




def test_update_csv(datadir):
    "Test the csv update command."
    xlsx_file_dir = datadir / "xlsx"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["csv", "update", "--input-dir", xlsx_file_dir, str(datadir / "objects")]
    )
    assert result.exit_code == 0
    assert "Updated 1 object records and 3 datatstream records" in result.output

    # and now from csv files
    csv_file_dir = datadir / "csv"
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
    "Test the csv csv2xlsx command."
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
    "Test the csv xlsx2csv command."
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
            "--object-csv",
            str(obj_csv),
            "--ds-csv",
            str(ds_csv),
        ],
    )
    assert result.exit_code == 0
    assert "Converted xlsx file to" in result.output
    assert obj_csv.exists()
    assert ds_csv.exists()
