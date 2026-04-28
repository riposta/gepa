def test_configure_langfuse_returns_none_without_keys():
    from gepa.monitoring.langfuse_config import configure_langfuse
    result = configure_langfuse(public_key="", secret_key="")
    assert result is None


def test_configure_langfuse_returns_none_with_partial_keys():
    from gepa.monitoring.langfuse_config import configure_langfuse
    result = configure_langfuse(public_key="pk-test", secret_key="")
    assert result is None


def test_configure_langfuse_does_not_raise_on_import_error():
    import sys
    # Symuluj brak langfuse
    langfuse_modules = [k for k in sys.modules if "langfuse" in k]
    saved = {k: sys.modules.pop(k) for k in langfuse_modules}
    try:
        import importlib
        import gepa.monitoring.langfuse_config as lfc
        importlib.reload(lfc)
        result = lfc.configure_langfuse(public_key="", secret_key="")
        assert result is None
    finally:
        sys.modules.update(saved)
