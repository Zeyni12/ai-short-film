import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict

RUNS_LOG = Path("runs.jsonl")
CACHE_DIR = Path("outputs/.cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def compute_hash(payload: Dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def log_run(entry: Dict[str, Any]) -> None:
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    with RUNS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_with_cache(
    stage: str,
    item_id: str,
    model: str,
    params: Dict[str, Any],
    seed: int,
    output_path: Path,
    cost_usd: float,
    fn: Callable[[], bytes],
    max_retries: int = 3,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cache_key = compute_hash({"stage": stage, "item_id": item_id, "model": model, "params": params, "seed": seed})
    marker = CACHE_DIR / f"{stage}_{item_id}_{cache_key}.done"

    if marker.exists() and output_path.exists():
        log_run({
            "stage": stage, "item_id": item_id, "model": model,
            "params": params, "seed": seed, "latency_ms": 0,
            "cost_usd": 0.0, "cache_hit": True, "output": str(output_path)
        })
        return output_path

    last_err = None
    for attempt in range(1, max_retries + 1):
        t0 = time.perf_counter()
        try:
            data = fn()
            output_path.write_bytes(data)
            marker.write_text(cache_key, encoding="utf-8")
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            log_run({
                "stage": stage, "item_id": item_id, "model": model,
                "params": params, "seed": seed, "latency_ms": latency_ms,
                "cost_usd": cost_usd, "cache_hit": False, "attempt": attempt,
                "output": str(output_path)
            })
            return output_path
        except Exception as exc:
            last_err = exc
            time.sleep(2 ** attempt)

    raise RuntimeError(f"[{stage}:{item_id}] Failed after {max_retries} attempts: {last_err}")