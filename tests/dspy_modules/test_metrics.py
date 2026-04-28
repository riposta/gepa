from unittest.mock import MagicMock


def test_metryka_dokladna_wycena():
    gold = MagicMock()
    gold.rzeczywiste_godziny = 100

    pred = MagicMock()
    pred.szacunek_godzin = 105
    pred.uzasadnienie = "Projekt wymaga 5 sprintów: backend 60h, frontend 30h, testy 15h."
    pred.pewnosc = 0.7

    from gepa.dspy_modules.metrics import metryka_wyceny
    score = metryka_wyceny(gold, pred)
    assert 0.8 < score <= 1.0


def test_metryka_zla_wycena():
    gold = MagicMock()
    gold.rzeczywiste_godziny = 100

    pred = MagicMock()
    pred.szacunek_godzin = 200  # 100% błąd
    pred.uzasadnienie = "Ok."   # za krótkie
    pred.pewnosc = 0.99         # przesadna pewność

    from gepa.dspy_modules.metrics import metryka_wyceny
    score = metryka_wyceny(gold, pred)
    assert score < 0.5


def test_metryka_zwraca_float():
    gold = MagicMock()
    gold.rzeczywiste_godziny = 200

    pred = MagicMock()
    pred.szacunek_godzin = 180
    pred.uzasadnienie = "Standardowy projekt webowy."
    pred.pewnosc = 0.6

    from gepa.dspy_modules.metrics import metryka_wyceny
    score = metryka_wyceny(gold, pred)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_feedback_tekstowy():
    gold = MagicMock()
    gold.rzeczywiste_godziny = 100

    pred = MagicMock()
    pred.szacunek_godzin = 150
    pred.uzasadnienie = "Projekt webowy."
    pred.pewnosc = 0.5

    from gepa.dspy_modules.metrics import metryka_wyceny_z_feedbackiem
    score, feedback = metryka_wyceny_z_feedbackiem(gold, pred)
    assert isinstance(score, float)
    assert isinstance(feedback, str)
    assert len(feedback) > 0
