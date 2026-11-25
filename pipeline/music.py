import shutil
import subprocess
from pathlib import Path
import imageio_ffmpeg
from pipeline.core import run_with_cache
from pipeline.validate import load_and_validate

FFMPEG_BIN = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()


def build_score(sb: dict) -> Path:
    mcfg = sb["music"]
    selected = mcfg["selected_candidate"]
    ace_wav = Path(f"outputs/music/{selected}.wav")
    out_wav = Path("outputs/music/selected_score.wav")
    dur = float(mcfg["duration_sec"])

    def _prepare():
        tmp = Path("outputs/music/_tmp_score.wav")
        if ace_wav.exists():
            subprocess.run([
                FFMPEG_BIN, "-y", "-stream_loop", "-1", "-i", str(ace_wav),
                "-t", f"{dur:.2f}", "-ar", "44100", "-ac", "2", str(tmp)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            expr = (
                "0.08*sin(2*PI*146.83*t)+0.06*sin(2*PI*220.00*t)+"
                "0.04*sin(2*PI*293.66*t)*(0.6+0.4*sin(2*PI*0.15*t))"
            )
            subprocess.run([
                FFMPEG_BIN, "-y", "-f", "lavfi",
                "-i", f"aevalsrc='{expr}':s=44100:d={dur:.2f}",
                "-af", f"afade=t=in:st=0:d=2,afade=t=out:st={max(0, dur-3):.2f}:d=3",
                "-ac", "2", str(tmp)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        data = tmp.read_bytes()
        tmp.unlink(missing_ok=True)
        return data

    model_used = "ace-step-3.5b" if ace_wav.exists() else "ffmpeg-pentatonic-pad-fallback"
    run_with_cache(
        stage="music",
        item_id=selected,
        model=model_used,
        params={"prompt": mcfg["prompt"], "bpm": mcfg["bpm"], "duration_sec": dur, "ace_file_exists": ace_wav.exists()},
        seed=4201,
        output_path=out_wav,
        cost_usd=0.0,
        fn=_prepare,
    )
    print(f"[OK] Selected score ready: {out_wav} ({model_used})")
    return out_wav


if __name__ == "__main__":
    build_score(load_and_validate())