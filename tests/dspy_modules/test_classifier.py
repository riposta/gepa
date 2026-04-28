def test_normalize_type_known():
    from gepa.dspy_modules.classifier import normalize_type
    assert normalize_type("legacy") == "legacy"
    assert normalize_type("LEGACY system") == "legacy"
    assert normalize_type("ai") == "ai"
    assert normalize_type("machine learning") == "nowy"  # fallback


def test_normalize_type_unknown_returns_nowy():
    from gepa.dspy_modules.classifier import normalize_type
    assert normalize_type("randomxyz") == "nowy"


def test_typy_projektow_list():
    from gepa.dspy_modules.classifier import TYPY_PROJEKTOW
    assert set(TYPY_PROJEKTOW) == {"legacy", "nowy", "ai", "migracja"}


def test_create_classifier_returns_chainofthought():
    import dspy
    from gepa.dspy_modules.classifier import create_classifier
    clf = create_classifier()
    assert isinstance(clf, dspy.ChainOfThought)
