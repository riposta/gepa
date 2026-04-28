"""Migrate training data from ace-poc format to GEPA format."""
import argparse
import json
import uuid
from pathlib import Path


def migrate(source_dir: str, dest_dir: str) -> int:
    src = Path(source_dir)
    dst = Path(dest_dir)
    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in src.glob("*.json"):
        try:
            raw = json.loads(f.read_text())
        except Exception:
            continue
        costs = raw.get("actual_costs", {})
        total_md = costs.get("total_md", 0)
        entry = {
            "project_description": raw.get("project_spec", raw.get("project_description", "")),
            "actual_hours": int(total_md * 8),
            "project_type": raw.get("project_type", "new"),
            "client_history": raw.get("client_history", ""),
            "risk_patterns": raw.get("risk_patterns", ""),
            "pm_comment": raw.get("pm_comment", ""),
            "source": "ace_poc",
            "original_file": f.name,
        }
        out = dst / f"ace_{uuid.uuid4().hex[:8]}.json"
        out.write_text(json.dumps(entry, ensure_ascii=False, indent=2))
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate ace-poc training data to GEPA format")
    parser.add_argument("--source", required=True, help="Source directory with ace-poc JSON files")
    parser.add_argument("--dest", default="gepa/data/training", help="Destination directory")
    args = parser.parse_args()
    n = migrate(args.source, args.dest)
    print(f"Migrated {n} files to {args.dest}")


if __name__ == "__main__":
    main()
