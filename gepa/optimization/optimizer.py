import json
from pathlib import Path
import dspy
from dspy.teleprompt import MIPROv2
from gepa.dspy_modules.metrics import metryka_wyceny
from gepa.optimization.trainset import load_trainset, count_examples
from gepa.config.settings import settings


class OptimizerRunner:
    def __init__(
        self,
        programs_dir: str | None = None,
        trigger_threshold: int | None = None,
    ) -> None:
        self.programs_dir = Path(programs_dir or settings.programs_dir)
        self.trigger_threshold = trigger_threshold or settings.gepa_trigger_threshold
        self.programs_dir.mkdir(parents=True, exist_ok=True)

    def get_latest_program(self) -> Path | None:
        files = sorted(self.programs_dir.glob("v*.json"))
        return files[-1] if files else None

    def next_version(self) -> str:
        latest = self.get_latest_program()
        if latest is None:
            return "v2"
        num = int(latest.stem.split("_")[0].lstrip("v"))
        return f"v{num + 1}"

    def should_trigger(self, training_dir: str) -> bool:
        return count_examples(training_dir) >= self.trigger_threshold

    def run(
        self,
        student: dspy.Module,
        training_dir: str,
        val_split: float = 0.2,
    ) -> Path:
        examples = load_trainset(training_dir)
        split = max(1, int(len(examples) * (1 - val_split)))
        trainset = examples[:split]
        valset = examples[split:] or examples[:5]

        # MIPROv2 z auto='light' — mała liczba iteracji, dobry baseline
        # INTERFEJS GEPA-READY: gdy GEPA wejdzie do DSPy, podmień MIPROv2 na GEPA
        # i zamień metric= na tuple (score, feedback) z metryka_wyceny_z_feedbackiem
        optimizer = MIPROv2(
            metric=metryka_wyceny,
            auto="light",
            num_threads=1,
            verbose=True,
        )
        optimized = optimizer.compile(
            student,
            trainset=trainset,
            valset=valset,
            requires_permission_to_run=False,
        )

        version = self.next_version()
        output_path = self.programs_dir / f"{version}_miprov2.json"
        optimized.save(str(output_path))

        from gepa.monitoring.mlflow_tracker import OptimizationTracker
        tracker = OptimizationTracker()
        tracker.log_run(
            optimizer_name="MIPROv2",
            num_examples=len(examples),
            val_score=0.0,
            program_path=str(output_path),
        )
        return output_path
