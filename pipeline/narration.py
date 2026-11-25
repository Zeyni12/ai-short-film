import argparse
import asyncio
import json
import shutil
import subprocess
import wave
from pathlib import Path
import edge_tts
import imageio_ffmpeg
from pipeline.core import run_with_cache
from pipeline.validate import load_and_validate

FFMPEG_BIN = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()


def edge_tts_amharic_wav(text: str, voice: str = "am-ET-AmehaNeural") -> bytes:
    tmp_mp3 = Path("outputs/audio/_tmp_edge.mp3")
    tmp_wav = Path("outputs/audio/_tmp_edge.wav")
    tmp_mp3.parent.mkdir(parents=True, exist_ok=True)

    async def _synth():
        communicate = edge_tts.Communicate(text, voice=voice, rate="-6%")
        await communicate.save(str(tmp_mp3))

    asyncio.run(_synth())
    subprocess.run(
        [
            FFMPEG_BIN, "-y", "-i", str(tmp_mp3),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ar", "24000", "-ac", "1", str(tmp_wav)
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    data = tmp_wav.read_bytes()
    tmp_mp3.unlink(missing_ok=True)
    tmp_wav.unlink(missing_ok=True)
    return data


def generate_narration(sb: dict) -> list[dict]:
    lang = sb["meta"]["language"]
    amharic_voice = "am-ET-AmehaNeural"
    manifest = []

    for shot in sb["shots"]:
        sid = shot["id"]
        out_wav = Path(f"outputs/audio/{sid}.wav")
        params = {"text": shot["narration"], "voice": amharic_voice, "language": lang}

        run_with_cache(
            stage="narration",
            item_id=sid,
            model="edge-tts-am-ET-AmehaNeural",
            params=params,
            seed=shot["seed"],
            output_path=out_wav,
            cost_usd=0.0,
            fn=lambda t=shot["narration"]: edge_tts_amharic_wav(t, amharic_voice),
        )

        with wave.open(str(out_wav), "rb") as wf:
            audio_dur = wf.getnframes() / float(wf.getframerate())

        effective_dur = max(float(shot["duration_sec"]), round(audio_dur + 0.8, 2))
        manifest.append({
            "id": sid,
            "wav": str(out_wav),
            "audio_dur": round(audio_dur, 2),
            "slot_dur": effective_dur,
            "subtitle_en": shot["subtitle_en"]
        })

    Path("outputs/audio/manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def build_radio_cut(manifest: list[dict]) -> None:
    concat_txt = Path("outputs/audio/radio_concat.txt")
    lines = []
    for item in manifest:
        padded = Path(f"outputs/audio/{item['id']}_padded.wav")
        subprocess.run([
            FFMPEG_BIN, "-y", "-i", item["wav"],
            "-af", f"apad=whole_dur={item['slot_dur']}",
            "-ar", "44100", "-ac", "2", str(padded)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        lines.append(f"file '{padded.resolve().as_posix()}'")
    concat_txt.write_text("\n".join(lines), encoding="utf-8")

    merged_voice = Path("outputs/audio/radio_voice.wav")
    subprocess.run([FFMPEG_BIN, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(merged_voice)], check=True)

    radio_mp4 = Path("outputs/radio_cut.mp4")
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-f", "lavfi", "-i", "color=c=black:s=1280x720:r=24",
        "-i", str(merged_voice),
        "-f", "lavfi", "-i", "anoisesrc=color=pink:amplitude=0.008",
        "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first:weights=1 0.15:normalize=0[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(radio_mp4)
    ], check=True)
    print(f"[OK] Phase 1 Radio Cut ready with loud Amharic voice: {radio_mp4}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--radio-cut", action="store_true")
    args = parser.parse_args()
    sb = load_and_validate()
    manifest = generate_narration(sb)
    if args.radio_cut:
        build_radio_cut(manifest)