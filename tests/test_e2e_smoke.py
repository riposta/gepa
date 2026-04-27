from unittest.mock import patch, MagicMock


def test_full_pipeline_imports():
    from gepa.config.settings import settings
    from gepa.dspy_modules.signatures import WycenaIT
    from gepa.dspy_modules.estimator import create_estimator
    from gepa.memory.schemas import ProjektIT, Klient, WzorzecRyzyka
    from gepa.graph.state import EstimationState
    from gepa.optimization.trainset import load_trainset, count_examples
    from gepa.data.migrate_ace_poc import migrate
    from gepa.data.generate_synthetic import generate
    assert True


def test_api_app_creates():
    with patch("gepa.graph.workflow.create_graph") as mock:
        mock.return_value = MagicMock()
        from gepa.api import app
        assert app is not None
        assert app.title == "GEPA Estimation API"
