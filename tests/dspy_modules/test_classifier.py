def test_normalize_type_known():
    from gepa.dspy_modules.classifier import normalize_type
    assert normalize_type("legacy") == "legacy"
    assert normalize_type("LEGACY system") == "legacy"
    assert normalize_type("ai") == "ai"
    assert normalize_type("machine learning") == "new"  # fallback


def test_normalize_type_unknown_returns_new():
    from gepa.dspy_modules.classifier import normalize_type
    assert normalize_type("randomxyz") == "new"


def test_project_types_list():
    from gepa.dspy_modules.classifier import PROJECT_TYPES
    assert set(PROJECT_TYPES) == {"legacy", "new", "ai", "migration"}


def test_create_classifier_returns_chainofthought():
    import dspy
    from gepa.dspy_modules.classifier import create_classifier
    clf = create_classifier()
    assert isinstance(clf, dspy.ChainOfThought)
