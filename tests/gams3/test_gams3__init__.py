from pathlib import Path

from gamspreprocessor.gams3 import export_objects


class FakeObject:
    def __init__(self, pid):
        self.pid = pid
        self.export_calls = []
        self.warnings = []
        self.errors = []

    def export(
        self,
        output_dir,
        overwrite=False,
        strip_prefix=False,
        colon_replacement="%3A",
    ):
        self.export_calls.append(
            (output_dir, overwrite, strip_prefix, colon_replacement)
        )
        return [Path(output_dir) / f"{self.pid}.xml"]


def test_export_objects_creates_output_dir_and_yields_objects(tmp_path, monkeypatch):
    "Test that export_objects creates the output directory and yields each object."
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
            colon_replacement="_",
        )
    )

    assert (tmp_path / "exported").exists()
    assert captured == {"base_url": "https://example.com/fedora", "pattern": "o:*"}
    assert yielded == objects
    for obj in objects:
        assert obj.export_calls == [((tmp_path / "exported"), True, False, "_")]
