"""CLI commands for managing GAMS projects."""

import logging
from pathlib import Path

import click

from gamspreprocessor import project as project_api

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
    """Create a basic project structure and project.toml."""
    project_api.initialize_project(Path(project_root))
    click.echo(
        f"Created {project_root}/project.toml. "
        "Please edit this file to configure your project."
    )


@click.command(name="update")
@click.argument("config-file", type=click.Path(exists=True))
def update_project(config_file: str):
    """Update the project.toml file in the current directory.
    
    Run this if the configuration file schema has changed. You can run it as
    often as you like, it will not overwrite any of your settings.
    It will only add new settings or remove deprecated ones.
    """
    if project_api.project_configuration_needs_update(Path(config_file)):
        project_api.update_project_configuration(Path(config_file))
        click.echo(
            f"Updated {config_file}."
            "Please edit this file to finish configuring your project."
        )
    else:
        click.echo(f"{config_file} is already up to date. No changes were made.")


cli.add_command(init_project)
cli.add_command(update_project)
