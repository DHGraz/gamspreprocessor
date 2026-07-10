"""Test the public project API wrappers."""

from gamspreprocessor import project as project_api


def test_initialize_project_creates_project_file(tmp_path):
    """The wrapper should create the default project configuration file."""
    project_api.initialize_project(tmp_path)

    assert (tmp_path / "gamsproject.toml").is_file()


def test_project_configuration_update_wrappers(tmp_path, monkeypatch):
    """The wrappers should delegate to the underlying project config helpers."""
    project_toml = tmp_path / "gamsproject.toml"
    project_toml.touch()

    monkeypatch.setattr(
        "gamspreprocessor.project.configuration_needs_update", lambda config: True
    )
    called = {}

    def fake_update(config_file):
        called["config_file"] = config_file

    monkeypatch.setattr("gamspreprocessor.project.update_configuration", fake_update)

    assert project_api.project_configuration_needs_update(project_toml) is True
    project_api.update_project_configuration(project_toml)

    assert called["config_file"] == project_toml