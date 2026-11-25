import json
import shutil
import subprocess
from pathlib import Path
import imageio_ffmpeg
from pipeline.core import log_run
from pipeline.validate import load_and_validate

FFMPEG_BIN = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()


def format_srt_time(seconds: float) -> str:
    ms = int(round((seconds - int(seconds)) * 1000))
    total_s = int(seconds)
    h = total_s // 3600
    m = (total_s % 3600) // 60
    s = total_s % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(manifest: list[dict], srt_path: Path) -> float:
    cursor = 0.0
    blocks = []
    for idx, item in enumerate(manifest, start=1):
        start = cursor + 0.15
        end = cursor + item["slot_dur"] - 0.15
        blocks.append(f"{idx}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{item['subtitle_en']}\n")
        cursor += item["slot_dur"]
    srt_path.write_text("\n".join(blocks), encoding="utf-8")
    return cursor


def assemble_film(sb: dict) -> None:
    manifest = json.loads(Path("outputs/audio/manifest.json").read_text(encoding="utf-8"))
    srt_path = Path("outputs/subtitles_en.srt")
    total_story_dur = write_srt(manifest, srt_path)

    # 1. Concatenate shot clips + 4s AI disclosure end card
    v_list = Path("outputs/video_concat.txt")
    v_lines = [f"file '{Path('outputs/shots/' + m['id'] + '.mp4').resolve().as_posix()}'" for m in manifest]

    end_card_mp4 = Path("outputs/end_card.mp4")
    end_text = sb["meta"]["end_card_text"].replace(":", "\\:").replace("'", "")
    subprocess.run([
        FFMPEG_BIN, "-y", "-f", "lavfi", "-i", "color=c=0x111111:s=1280x720:r=24:d=4",
        "-vf", f"drawtext=text='{end_text}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(end_card_mp4)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    v_lines.append(f"file '{end_card_mp4.resolve().as_posix()}'")
    v_list.write_text("\n".join(v_lines), encoding="utf-8")

    raw_video = Path("outputs/raw_video.mp4")
    subprocess.run([FFMPEG_BIN, "-y", "-f", "concat", "-safe", "0", "-i", str(v_list), "-c", "copy", str(raw_video)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Concatenate voice track + 4s silence for end card
    a_list = Path("outputs/audio_concat.txt")
    a_lines = [f"file '{Path('outputs/audio/' + m['id'] + '_padded.wav').resolve().as_posix()}'" for m in manifest]
    end_sil = Path("outputs/audio/end_silence.wav")
    subprocess.run([FFMPEG_BIN, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo:d=4", str(end_sil)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    a_lines.append(f"file '{end_sil.resolve().as_posix()}'")
    a_list.write_text("\n".join(a_lines), encoding="utf-8")

    full_voice = Path("outputs/full_voice.wav")
    subprocess.run([FFMPEG_BIN, "-y", "-f", "concat", "-safe", "0", "-i", str(a_list), "-c", "copy", str(full_voice)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Mix score + sidechain duck under narration + normalize loudness (-14 LUFS)
    score_wav = Path("outputs/music/selected_score.wav")
    final_audio = Path("outputs/final_mix.wav")
    total_dur = total_story_dur + 4.0
    subprocess.run([
        FFMPEG_BIN, "-y",
        "-stream_loop", "-1", "-i", str(score_wav),
        "-i", str(full_voice),
        "-t", f"{total_dur:.2f}",
        "-filter_complex",
        "[0:a]volume=0.35[bg];[1:a]asplit=2[v1][v2];"
        "[bg][v1]sidechaincompress=threshold=0.02:ratio=6:attack=50:release=400[ducked];"
        "[ducked][v2]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
        "-map", "[out]", str(final_audio)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 4. Export 16:9 Horizontal with burned English subtitles
    srt_escaped = srt_path.resolve().as_posix().replace(":", "\\:")
    out_16x9 = Path("outputs/final_16x9.mp4")
    subprocess.run([
        FFMPEG_BIN, "-y", "-i", str(raw_video), "-i", str(final_audio),
        "-vf", f"subtitles='{srt_escaped}':force_style='FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,MarginV=28'",
        "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(out_16x9)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5. Export 9:16 Vertical (blurred background fill + centered 16:9 frame + subtitles)
    out_9x16 = Path("outputs/final_9x16.mp4")
    subprocess.run([
        FFMPEG_BIN, "-y", "-i", str(raw_video), "-i", str(final_audio),
        "-filter_complex",
        f"[0:v]split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bgb];"
        f"[fg]scale=1080:-2[fgc];[bgb][fgc]overlay=(W-w)/2:(H-h)/2,"
        f"subtitles='{srt_escaped}':force_style='FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,MarginV=120'[vout]",
        "-map", "[vout]", "-map", "1:a",
        "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(out_9x16)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    log_run({"stage": "assemble", "item_id": "final_exports", "model": "ffmpeg-libx264", "params": {"ratios": ["16:9", "9:16"]}, "seed": 0, "latency_ms": 0, "cost_usd": 0.0, "cache_hit": False})
    print(f"[OK] Final exports ready:\n  - Horizontal (16:9): {out_16x9}\n  - Vertical   (9:16): {out_9x16}")


if __name__ == "__main__":
    assemble_film(load_and_validate())