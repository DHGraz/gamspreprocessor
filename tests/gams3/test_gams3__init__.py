from gamspreprocessor.gams3 import export_objects


class FakeObject:
    def __init__(self, pid):
        self.pid = pid
        self.export_calls = []

    def export(self, output_dir, overwrite=False):
        self.export_calls.append((output_dir, overwrite))


def test_export_objects_creates_output_dir_and_yields_objects(tmp_path, monkeypatch):
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
    assert yielded == objects
    for obj in objects:
        assert obj.export_calls == [((tmp_path / "exported"), True)]
