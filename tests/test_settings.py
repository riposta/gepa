from pathlib import Path


def test_settings_defaults():
    from gepa.config.settings import settings
    assert settings.gepa_trigger_threshold == 50
    assert settings.programs_dir == Path("gepa/dspy_modules/programs")


def test_secret_fields_are_masked():
    from gepa.config.settings import settings
    assert "SecretStr" in repr(settings.llm_api_key) or settings.llm_api_key.get_secret_value() == ""
