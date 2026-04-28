import json
from pathlib import Path


def migrate(src_dir: str, dst_dir: str) -> int:
    src = Path(src_dir)
    dst = Path(dst_dir)
    dst.mkdir(parents=True, exist_ok=True)

    count = 0
    for f in src.glob("*.json"):
        raw = json.loads(f.read_text())
        md = raw.get("actual_costs", {}).get("total_md", 0)
        converted = {
            "project_description": raw.get("project_spec", ""),
            "actual_hours": md * 8,
            "source": "ace-poc",
            "original_file": f.name,
        }
        (dst / f.name).write_text(json.dumps(converted, ensure_ascii=False, indent=2))
        count += 1

    return count


if __name__ == "__main__":
    import sys
    count = migrate(sys.argv[1], sys.argv[2])
    print(f"Migrated {count} training examples.")
