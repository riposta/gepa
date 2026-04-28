from unittest.mock import patch, MagicMock, call


def test_tracker_creates_instance():
    with patch("mlflow.set_tracking_uri"), patch("mlflow.set_experiment"):
        from gepa.monitoring.mlflow_tracker import OptimizationTracker
        tracker = OptimizationTracker(experiment_name="test")
        assert tracker is not None
        assert tracker.experiment_name == "test"


def test_log_run_calls_mlflow_params_and_metrics():
    with patch("mlflow.set_tracking_uri"), \
         patch("mlflow.set_experiment"), \
         patch("mlflow.start_run") as mock_run, \
         patch("mlflow.log_params") as mock_params, \
         patch("mlflow.log_metrics") as mock_metrics, \
         patch("mlflow.log_artifact") as mock_artifact:

        ctx = MagicMock()
        mock_run.return_value.__enter__ = MagicMock(return_value=ctx)
        mock_run.return_value.__exit__ = MagicMock(return_value=False)

        from gepa.monitoring.mlflow_tracker import OptimizationTracker
        tracker = OptimizationTracker(experiment_name="test")
        tracker.log_run(
            optimizer_name="MIPROv2",
            num_examples=60,
            val_score=0.78,
            program_path="/tmp/v2_miprov2.json",
        )

        mock_params.assert_called_once_with({
            "optimizer": "MIPROv2",
            "num_examples": 60,
        })
        mock_metrics.assert_called_once_with({"val_score": 0.78})
        mock_artifact.assert_called_once_with("/tmp/v2_miprov2.json")
