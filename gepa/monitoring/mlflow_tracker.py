import mlflow
from gepa.config.settings import settings


class OptimizationTracker:
    def __init__(self, experiment_name: str = "gepa_optimization") -> None:
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(experiment_name)
        self.experiment_name = experiment_name

    def log_run(
        self,
        optimizer_name: str,
        num_examples: int,
        val_score: float,
        program_path: str,
    ) -> None:
        with mlflow.start_run():
            mlflow.log_params({
                "optimizer": optimizer_name,
                "num_examples": num_examples,
            })
            mlflow.log_metrics({"val_score": val_score})
            mlflow.log_artifact(program_path)
