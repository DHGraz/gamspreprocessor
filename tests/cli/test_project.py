from click.testing import CliRunner

from gamspreprocessor.cli.main import cli


def test_init_project(tmp_path):
    "The basic test is that '--help' does not lead to an error."
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "init", str(tmp_path)])
    assert result.exit_code == 0
    assert "Please edit this file" in result.output
    assert (tmp_path / "project.toml").is_file()
