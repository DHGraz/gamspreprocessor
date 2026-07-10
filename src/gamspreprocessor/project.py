"""Public API for managing GAMS project configuration files.

This module exposes the project-related helpers that are used by the CLI, so they
can also be called directly from Python code.
"""

from pathlib import Path

from gamslib.projectconfiguration.utils import (
    configuration_needs_update,
    initialize_project_dir,
    update_configuration,
)


def initialize_project(project_root: Path | str) -> None:
    """Create a basic project structure and project configuration file."""
    initialize_project_dir(Path(project_root))


def project_configuration_needs_update(config_file: Path | str) -> bool:
    """Return True if the project configuration should be migrated."""
    return configuration_needs_update(Path(config_file))


def update_project_configuration(config_file: Path | str) -> None:
    """Update a project configuration file to the current schema."""
    update_configuration(Path(config_file))


__all__ = [
    "initialize_project",
    "project_configuration_needs_update",
    "update_project_configuration",
]