import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

STAGES = [
    ("Validate storyboard", [sys.executable, "-m", "pipeline.validate"]),
    ("Narration & manifest", [sys.executable, "-m", "pipeline.narration"]),
    ("Keyframes", [sys.executable, "-m", "pipeline.keyframes"]),
    ("Motion shots", [sys.executable, "-m", "pipeline.shots"]),
    ("Music score", [sys.executable, "-m", "pipeline.music"]),
    ("Final assembly (16:9 & 9:16)", [sys.executable, "-m", "pipeline.assemble"]),
]


def main() -> int:
    for label, cmd in STAGES:
        print(f"\n=== [{label}] Running: {' '.join(cmd)} ===")
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            print(f"[ERROR] Stage failed: {label} (exit code {result.returncode})")
            return result.returncode
    print("\n[DONE] End-to-end pipeline completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())