import json
import os
from datetime import datetime, timezone


def write_bronze_json(rows: list[dict], dataset: str, run_id: str, bronze_dir: str) -> str:
    out_dir = os.path.join(bronze_dir, f"run_id={run_id}")
    os.makedirs(out_dir, exist_ok=True)

    path = os.path.join(out_dir, f"{dataset}_raw.json")
    payload = {
        "run_id": run_id,
        "dataset": dataset,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path
