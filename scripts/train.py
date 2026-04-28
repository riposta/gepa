"""Run MIPROv2 optimization on training data and save the optimized program."""
import argparse
import sys
from pathlib import Path

import dspy

sys.path.insert(0, str(Path(__file__).parent.parent))

from gepa.config.settings import settings
from gepa.dspy_modules.estimator import create_estimator
from gepa.optimization.optimizer import OptimizerRunner
from gepa.optimization.trainset import count_examples


def main() -> None:
    parser = argparse.ArgumentParser(description="Train GEPA estimator with MIPROv2")
    parser.add_argument(
        "--training-dir",
        default="gepa/data/training",
        help="Directory with training JSON files (default: gepa/data/training)",
    )
    parser.add_argument(
        "--val-split",
        type=float,
        default=0.2,
        help="Fraction of data used for validation (default: 0.2)",
    )
    args = parser.parse_args()

    lm = dspy.LM(
        model=settings.llm_model,
        api_base=settings.llm_api_base or None,
        api_key=settings.llm_api_key.get_secret_value() or None,
    )
    dspy.configure(lm=lm)

    n = count_examples(args.training_dir)
    if n == 0:
        print(f"No training examples found in {args.training_dir}")
        sys.exit(1)

    print(f"Training examples: {n}")
    print(f"Model: {settings.llm_model}")
    print(f"Validation split: {args.val_split:.0%}")
    print()

    runner = OptimizerRunner()
    student = create_estimator()
    path = runner.run(student, args.training_dir, val_split=args.val_split)

    print(f"\nDone. Program saved to: {path}")
    print("Load it into the running API with: POST /model/reload")


if __name__ == "__main__":
    main()
