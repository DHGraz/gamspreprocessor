from pathlib import Path

from gamspreprocessor.gams3 import ExportResult, export_objects


class FakeObject:
    def __init__(self, pid):
        self.pid = pid
        self.export_calls = []

    def export(self, output_dir, overwrite=False, strip_prefix=False):
        self.export_calls.append((output_dir, overwrite, strip_prefix))
        return [Path(output_dir) / f"{self.pid}.xml"]


def test_export_objects_creates_output_dir_and_yields_objects(tmp_path, monkeypatch):
    "Test that export_objects creates the output directory and yields ExportResult instances for each object."
    objects = [FakeObject("o:one"), FakeObject("o:two")]
    captured = {}

    class FakeQuery:
        def __init__(self, base_url):
            captured["base_url"] = base_url

        def find_objects(self, pattern):
            captured["pattern"] = pattern
            for obj in objects:
                yield obj

    monkeypatch.setattr("gamspreprocessor.gams3.Gams3Query", FakeQuery)

    yielded = list(
        export_objects(
            pid_pattern="o:*",
            output_dir=tmp_path / "exported",
            overwrite=True,
            base_url="https://example.com/fedora",
        )
    )

    assert (tmp_path / "exported").exists()
    assert captured == {"base_url": "https://example.com/fedora", "pattern": "o:*"}
    assert all(isinstance(item, ExportResult) for item in yielded)
    assert [item.obj for item in yielded] == objects
    assert [item.exported_files for item in yielded] == [
        [tmp_path / "exported" / "o:one.xml"],
        [tmp_path / "exported" / "o:two.xml"],
    ]
    assert [item.warnings for item in yielded] == [[], []]
    for obj in objects:
        assert obj.export_calls == [((tmp_path / "exported"), True, False)]
