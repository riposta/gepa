def test_settings_defaults():
    from gepa.config.settings import settings
    assert settings.gepa_trigger_threshold == 50
    assert settings.programs_dir == "gepa/dspy_modules/programs"
