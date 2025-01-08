from click.testing import CliRunner
from gamspreprocessor.cli.main import cli


def test_create_csv(datadir):
    "Test the csv create command."
    runner = CliRunner()
    #cfgfile = str(datadir / "objects" / "project.toml")
    result = runner.invoke(cli, ["csv", "create", str(datadir / "objects")])
    assert result.exit_code == 0
    assert "Created csv files for 2 objects (3 content files)" in result.output


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
