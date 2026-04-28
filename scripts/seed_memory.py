"""Seed Neo4j/Graphiti with training examples as historical episodes."""
import argparse
import asyncio
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import dspy

from gepa.config.settings import settings
from gepa.memory.graphiti_client import GraphitiClient


async def seed(training_dir: str, dry_run: bool = False) -> int:
    files = list(Path(training_dir).glob("*.json"))
    if not files:
        print(f"No training files found in {training_dir}")
        return 0

    client = GraphitiClient()
    count = 0

    for f in files:
        try:
            data = json.loads(f.read_text())
        except Exception as e:
            print(f"  SKIP {f.name}: {e}")
            continue

        project_description = data.get("project_description", "")
        actual_hours = data.get("actual_hours", 0)
        project_type = data.get("project_type", "new")
        client_history = data.get("client_history", "")
        risk_patterns = data.get("risk_patterns", "")
        pm_comment = data.get("pm_comment", "")

        if not project_description or not actual_hours:
            print(f"  SKIP {f.name}: missing project_description or actual_hours")
            continue

        content = (
            f"Project: {project_description}\n"
            f"Type: {project_type}\n"
            f"Actual hours: {actual_hours} hrs\n"
            f"Client history: {client_history}\n"
            f"Risk patterns: {risk_patterns}\n"
            f"PM comment: {pm_comment}"
        )
        episode_id = f"seed_{f.stem}_{uuid.uuid4().hex[:6]}"

        print(f"  {'[dry-run] ' if dry_run else ''}Seeding {f.name} ({project_type}, {actual_hours}h)")

        if not dry_run:
            await client.add_episode(episode_id, content)

        count += 1

    if not dry_run:
        await client.close()

    return count


async def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Neo4j with training examples")
    parser.add_argument(
        "--training-dir",
        default="gepa/data/training",
        help="Directory with training JSON files (default: gepa/data/training)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be seeded without writing to Neo4j",
    )
    args = parser.parse_args()

    lm = dspy.LM(
        model=settings.llm_model,
        api_base=settings.llm_api_base or None,
        api_key=settings.llm_api_key.get_secret_value() or None,
    )
    dspy.configure(lm=lm)

    print(f"Seeding Neo4j from {args.training_dir}...")
    if args.dry_run:
        print("(dry-run mode — no writes)\n")

    n = await seed(args.training_dir, dry_run=args.dry_run)
    print(f"\nDone. {'Would seed' if args.dry_run else 'Seeded'} {n} episodes.")


if __name__ == "__main__":
    asyncio.run(main())
