import pytest
from unittest.mock import patch, MagicMock


def test_estimator_returns_required_fields():
    with patch("dspy.ChainOfThought") as mock_cot:
        mock_instance = MagicMock()
        mock_instance.return_value = MagicMock(
            szacunek_godzin=120,
            uzasadnienie="Projekt wymaga 3 sprintów.",
            pewnosc=0.75,
        )
        mock_cot.return_value = mock_instance

        from gepa.dspy_modules.estimator import create_estimator
        estimator = create_estimator()
        result = estimator(
            opis_projektu="REST API w Django",
            historia_klienta="Brak historii.",
            wzorce_ryzyk="Brak wzorców.",
        )

        assert hasattr(result, "szacunek_godzin")
        assert hasattr(result, "uzasadnienie")
        assert hasattr(result, "pewnosc")


def test_wycena_signature_has_correct_fields():
    from gepa.dspy_modules.signatures import WycenaIT
    import dspy
    # Sprawdź że signature ma wymagane pola wejściowe i wyjściowe
    fields = WycenaIT.model_fields if hasattr(WycenaIT, 'model_fields') else {}
    # DSPy signatures mają __annotations__
    annotations = WycenaIT.__annotations__ if hasattr(WycenaIT, '__annotations__') else {}
    assert "opis_projektu" in annotations or "opis_projektu" in str(WycenaIT)
    assert "szacunek_godzin" in annotations or "szacunek_godzin" in str(WycenaIT)
