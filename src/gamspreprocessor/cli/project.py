"""CLI commands for managing GAMS projects."""

import logging
from pathlib import Path

import click
from gamslib.projectconfiguration import create_configuration

logger = logging.getLogger()


@click.group(name="project")
def cli():
    """Helpers for managing GAMS projects.

    These commands might be useful to manage GAMS projects.
    """
    # intentionally left empty


@click.command(name="init")
@click.argument("project-root", type=click.Path(exists=True))
def init_project(project_root: str):
    """Create a project.toml in the project-root directory."""
    create_configuration(Path(project_root))
    logger.info(
        "Created %a/project.toml. Please edit this file to configure your project.",
        project_root,
    )


cli.add_command(init_project)
