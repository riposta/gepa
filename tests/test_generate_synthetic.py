import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_generate_creates_n_examples():
    mock_result = MagicMock()
    mock_result.opis_projektu = "Aplikacja mobilna iOS"
    mock_result.rzeczywiste_godziny = 320
    mock_result.typ_projektu = "nowy"
    mock_result.technologie = '["Swift", "Firebase"]'
    mock_result.uzasadnienie = "Typowy projekt mobilny."

    mock_predictor = MagicMock(return_value=mock_result)

    with patch("gepa.data.generate_synthetic.dspy.Predict", return_value=mock_predictor), \
         tempfile.TemporaryDirectory() as tmpdir:
        from gepa.data.generate_synthetic import generate
        count = generate(n=3, output_dir=tmpdir)
        assert count == 3
        files = list(Path(tmpdir).glob("*.json"))
        assert len(files) == 3
        data = json.loads(files[0].read_text())
        assert "opis_projektu" in data
        assert "rzeczywiste_godziny" in data
