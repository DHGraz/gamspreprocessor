"Tests for the AbstractFileReference class."
from pathlib import Path

import pytest

from gamspreprocessor.objectsource import AbstractFileReference


class MockFileReference(AbstractFileReference):
    """To test the AbstractFileReference class, we need a vanilla subclass"""
    def get_reference(self) -> str:
        return ""

    def set_reference(self, new_reference: str) -> None:
        pass

    def get_id(self) -> str:
        return ""


def test_rank_path_identical_paths():
    long_path =  Path("/some/path/to/file.txt")
    short_path = Path("/some/path/to/file.txt")
    assert AbstractFileReference._rank_path(long_path, short_path) == len(long_path.as_posix())

def test_rank_path_different_paths():
    long_path =        Path("/some/path/to/file.txt")
    short_path = Path("/some/other/path/to/file.txt")
    assert AbstractFileReference._rank_path(long_path, short_path) == len("/path/to/file.txt")

def test_rank_path_no_common_suffix():
    long_path = Path("/some/path/to/file1.txt")
    short_path = Path("/some/path/to/file2.txt")
    assert AbstractFileReference._rank_path(long_path, short_path) == len(".txt")

def test_rank_path_partial_match():
    long_path =   Path("/some/path/to/file.txt")
    short_path = Path("/other/path/to/file.txt")
    assert AbstractFileReference._rank_path(long_path, short_path) == len("/path/to/file.txt")

def test_rank_path_empty_paths():
    long_path = Path("")
    short_path = Path("")
    assert AbstractFileReference._rank_path(long_path, short_path) == 0

def test_rank_path_one_empty_path():
    long_path = Path("/some/path/to/file.txt")
    short_path = Path("")
    assert AbstractFileReference._rank_path(long_path, short_path) == 0
    

def test_testfile_reference():
    "This is only to make coverage happy"
    ref = MockFileReference()
    assert ref.get_reference() == ""
    assert ref.get_id() == ""
    ref.set_reference("new_reference")

def test_hash_with_source_file():
    ref = MockFileReference()
    ref.source_file = Path("/some/path/to/file.txt")
    expected_hash = hash(f"{ref.__class__.__name__!s} {ref.source_file.absolute()}")
    assert hash(ref) == expected_hash

def test_hash_without_source_file():
    ref = MockFileReference()
    expected_hash = hash(f"{ref.__class__.__name__!s} {id(ref)}")
    assert hash(ref) == expected_hash

def test_repr_with_source_file():
    ref = MockFileReference()
    ref.source_file = Path("/some/path/to/file.txt")
    expected_repr = f"{ref.__class__.__name__}({ref.source_file!s})"
    assert repr(ref) == expected_repr

def test_repr_without_source_file():
    ref = MockFileReference()
    expected_repr = f"{ref.__class__.__name__}(None)"
    assert repr(ref) == expected_repr

