import json
import sys
from pathlib import Path
import jsonschema


def load_and_validate() -> dict:
    schema = json.loads(Path("schema/storyboard.schema.json").read_text(encoding="utf-8"))
    storyboard = json.loads(Path("storyboard.json").read_text(encoding="utf-8"))
    jsonschema.validate(instance=storyboard, schema=schema)
    total_sec = sum(s["duration_sec"] for s in storyboard["shots"])
    if not (60 <= total_sec <= 90):
        raise ValueError(f"Total duration {total_sec}s is outside required 60-90s window.")
    print(f"[OK] Validated storyboard.json ({len(storyboard['shots'])} shots, {total_sec}s total).")
    return storyboard


if __name__ == "__main__":
    try:
        load_and_validate()
    except Exception as e:
        print(f"[ERROR] Validation failed: {e}", file=sys.stderr)
        sys.exit(1)