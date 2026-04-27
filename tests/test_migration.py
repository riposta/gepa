import json
import tempfile
from pathlib import Path


def test_migrate_converts_ace_poc_format():
    ace_example = {
        "project_spec": "Portal klientów dla banku",
        "actual_costs": {"total_md": 45, "breakdown": {"backend": 20, "frontend": 15, "testing": 10}},
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src"
        dst = Path(tmpdir) / "dst"
        src.mkdir()
        dst.mkdir()
        (src / "bank_portal.json").write_text(json.dumps(ace_example))

        from gepa.data.migrate_ace_poc import migrate
        result = migrate(str(src), str(dst))

        files = list(dst.glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text())
        assert "opis_projektu" in data
        assert "rzeczywiste_godziny" in data
        assert data["rzeczywiste_godziny"] == 45 * 8
        assert result == 1
