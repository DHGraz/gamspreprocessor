"Tests for project creation and initialization."

from click.testing import CliRunner

from gamspreprocessor.cli.main import cli


def test_init_project(tmp_path):
    "The basic test is that '--help' does not lead to an error."
    runner = CliRunner()
    result = runner.invoke(cli, ["project", "init", str(tmp_path)])
    assert result.exit_code == 0
    assert "Please edit this file" in result.output
    assert (tmp_path / "project.toml").is_file()

    def test_update_project_needed(tmp_path, mocker): # pragma: no cover
        "Test for updating a project that needs updating."
        # Create project.toml in tmp_path
        project_toml = tmp_path / "project.toml"
        project_toml.touch()

        # Mock configuration_needs_update to return True
        mocker.patch(
            "gamspreprocessor.cli.project.configuration_needs_update", return_value=True
        )
        # Mock update_configuration
        mock_update = mocker.patch("gamspreprocessor.cli.project.update_configuration")
        # Mock Path.cwd to return tmp_path
        mocker.patch("gamspreprocessor.cli.project.Path.cwd", return_value=tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["project", "update", str(project_toml)])

        assert result.exit_code == 0
        assert "Updated" in result.output
        assert "Please edit this file" in result.output
        mock_update.assert_called_once_with(tmp_path)


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
    assert (tmp_path / "project.toml").is_file()

    # Update an up to date project
    monkeypatch.setattr(
        "gamspreprocessor.cli.project.configuration_needs_update", lambda x: False
    )
    result = runner.invoke(cli, ["project", "update", str(tmp_path / "project.toml")])
    assert result.exit_code == 0
    assert "already up to date" in result.output

    # Update a project that needs updating
    monkeypatch.setattr(
        "gamspreprocessor.cli.project.configuration_needs_update", lambda x: True
    )
    result = runner.invoke(cli, ["project", "update", str(tmp_path / "project.toml")])
    assert result.exit_code == 0
    assert "Updated" in result.output
