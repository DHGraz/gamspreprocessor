"Tests for project creation and initialization."

from click.testing import CliRunner

from gamspreprocessor.cli.main import cli


def test_init_project(tmp_path):
    "The basic test is that '--help' does not lead to an error."
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "init", str(tmp_path)])
    assert result.exit_code == 0
    assert "Please edit this file" in result.output
    assert (tmp_path / "gamsproject.toml").is_file()


def test_project_cli_help():
    """Test that 'project --help' displays help information."""
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "--help"])
    assert result.exit_code == 0
    assert "Helpers for managing GAMS projects" in result.output


def test_init_project_non_existent_dir():
    """Test init command with non-existent directory."""
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "init", "/non/existent/path"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_update_project_non_existent_file():
    """Test update command with non-existent file."""
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "update", "/non/existent/file.toml"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_init_and_update_flow(tmp_path, monkeypatch):
    """Test the complete flow: initialize a project and then update it."""
    # Initialize the project
    # create an initial configuration
    runner = CliRunner()
    init_result = runner.invoke(cli, ["project", "init", str(tmp_path)])
    assert init_result.exit_code == 0
    assert (tmp_path / "gamsproject.toml").is_file()

    # Update an up to date project
    monkeypatch.setattr(
        "gamspreprocessor.cli.project.project_api.project_configuration_needs_update",
        lambda x: False,
    )
    result = runner.invoke(cli, ["project", "update", str(tmp_path / "gamsproject.toml")])
    assert result.exit_code == 0
    assert "already up to date" in result.output

    # Update a project that needs updating
    monkeypatch.setattr(
        "gamspreprocessor.cli.project.project_api.project_configuration_needs_update",
        lambda x: True,
    )
    monkeypatch.setattr(
        "gamspreprocessor.cli.project.project_api.update_project_configuration",
        lambda x: None,
    )
    result = runner.invoke(cli, ["project", "update", str(tmp_path / "gamsproject.toml")])
    assert result.exit_code == 0
    assert "Updated" in result.output
