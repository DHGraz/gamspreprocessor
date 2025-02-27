import os
import pytest
from gamspreprocessor.projectsplitter.genericobjectsource import GenericObjectSource

def test_pid_with_colon(tmp_path):
    """If strip_prefix is True, the o: should be removed."""
    # we cannot have colons in filenames on Windows because Windows treats 
    # the colon as a drive letter separator. 
    # We skip this test on windows, because the next test (escaped colon)
    # should follow the same logic
    if os.name == "nt":  # pragma: no cover
        pytest.skip("This test is not relevant on Windows.")  
    test_file = tmp_path / "o:foo.xml"
    src = GenericObjectSource(test_file, strip_prefix=True, strip_extension=True)
    assert src.source_file == test_file
    assert src.strip_prefix
    assert src.strip_extension
    assert src.referenced_files == []
    # Not changed yet
    assert src.pid == "o:foo"
    # rewrite_pid sets the new pid
    new_pid = src.rewrite_pid()
    assert new_pid == "foo"
    assert src.pid == "foo"
    


def test_pid_with_colon_escaped(tmp_path):
    "Like test_pid_with_colon, but with a percent-escaped colon."
    src = GenericObjectSource(tmp_path / "o%3Afoo.xml", strip_prefix=True, strip_extension=True)
    assert src.source_file == tmp_path / "o%3Afoo.xml"
    assert src.strip_prefix
    assert src.strip_extension
    assert src.referenced_files == []
    with pytest.warns(UserWarning):
        assert src.safe_pid == "foo"


def test_pid_with_colon_keep_prefix(tmp_path):
    """If strip_prefix is False, the o: should not be be removed.
    
    But: The colon should be escaped and a warning should be issued.
    """
    # we cannot have colons in filenames on Windows because Windows treats 
    # the colon as a drive letter separator. 
    # We skip this test on windows, because the next test (escaped colon)
    # should follow the same logic
    if os.name == "nt":  # pragma: no cover
        pytest.skip("This test is not relevant on Windows.")  
    test_file = tmp_path / "o:foo.pdf"
    src = GenericObjectSource(test_file, strip_prefix=False, strip_extension=True)
    assert src.source_file == test_file
    assert src.strip_prefix is False
    assert src.strip_extension
    assert src.referenced_files == []
    with pytest.warns(UserWarning):
        assert src.pid == "o:foo"
        assert src.safe_pid == "o%3Afoo"
        

def test_pid_with_escaped_colon_keep_prefix(tmp_path):
    """If strip_prefix is False, the o%3A should not be kept."""
    test_file = tmp_path / "o%3Afoo.pdf"
    src = GenericObjectSource(test_file, strip_prefix=False, strip_extension=True)
    assert src.source_file == test_file
    assert src.strip_prefix is False
    assert src.strip_extension
    assert src.referenced_files == []
    with pytest.warns(UserWarning):
        assert src.safe_pid == "o%3Afoo"


def test_pid_with_keep_extension(tmp_path):
    """If strip_extension is False, the extension should be kept."""
    src = GenericObjectSource(tmp_path / "foo.xml", strip_prefix=True, strip_extension=False)
    assert src.source_file == tmp_path / "foo.xml"
    assert src.strip_prefix
    assert src.strip_extension is False
    assert src.referenced_files == []
    assert src.pid == "foo.xml"


def test_save(tmp_path):
    """Test the save method."""
    src_file = tmp_path / "foo.xml"
    src_file.touch()
    src = GenericObjectSource(src_file, strip_prefix=True, strip_extension=False)
    
    obj_dir = tmp_path / "object1"
    obj_dir.mkdir()
    retval = src.save(obj_dir)
    assert (obj_dir / "foo.xml").exists()
    assert retval == [obj_dir / "foo.xml"]


def test_str(tmp_path):
    """Test the __str__ method."""
    src = GenericObjectSource(tmp_path / "foo.xml", strip_prefix=True, strip_extension=False) 
    assert str(src) == f"GenericObjectSource({tmp_path / 'foo.xml'})"

def test_repr(tmp_path):
    """Test the __repr__ method."""
    src = GenericObjectSource(tmp_path / "foo.xml", strip_prefix=True, strip_extension=False) 
    print('-'*80)
    print(repr(src))
    print('-'*80)
    assert repr(src) == f"GenericObjectSource({tmp_path / 'foo.xml'}, strip_prefix=True, strip_extension=False)"
    