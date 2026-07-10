"""Test the public projectsplitter API wrappers."""

import json
from pathlib import Path
from shutil import copytree

import pytest

from gamspreprocessor import projectsplitter as projectsplitter_api
from gamspreprocessor.projectsplitter.bookkeeper import BookKeeper


FIXTURE_PROJECTS = (
    Path(__file__).resolve().parent / "projectsplitter" / "data" / "projects"
)


def copy_project_fixture(tmp_path: Path) -> Path:
    """Copy the checked-in project fixture tree into a temporary directory."""
    project_dir = tmp_path / "projects"
    copytree(FIXTURE_PROJECTS, project_dir)
    return project_dir


def test_create_project_splitter_and_split_file(tmp_path):
    """The wrapper should create and use a splitter for a single source file."""
    project_dir = copy_project_fixture(tmp_path)
    output_dir = tmp_path / "objects"

    splitter = projectsplitter_api.create_project_splitter(output_dir, project_dir)
    copied_files = projectsplitter_api.split_project_file(
        splitter, project_dir / "foo.pdf"
    )

    assert len(copied_files) == 1
    assert copied_files[0].is_file()


def test_list_unhandled_files(tmp_path):
    """The wrapper should return unhandled files from the bookkeeper."""
    project_dir = copy_project_fixture(tmp_path)
    objects_dir = tmp_path / "objects"
    objects_dir.mkdir()

    bookkeeper = {
        (project_dir / "image01.jpeg").resolve().as_posix(): [],
        (project_dir / "image02.jpeg").resolve().as_posix(): ["foo"],
        (project_dir / "TEI_1.xml").resolve().as_posix(): ["bar"],
    }
    (objects_dir / BookKeeper.FILENAME).write_text(json.dumps(bookkeeper))

    unhandled_files = projectsplitter_api.list_unhandled_files(objects_dir)

    assert len(unhandled_files) == 1
    assert unhandled_files[0].name == "image01.jpeg"


def test_list_unhandled_files_missing_bookkeeper(tmp_path):
    """The wrapper should fail when the bookkeeping file does not exist."""
    with pytest.raises(FileNotFoundError, match="No bookkeeper file found"):
        projectsplitter_api.list_unhandled_files(tmp_path / "objects")