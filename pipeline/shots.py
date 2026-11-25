# import json
# import shutil
# import subprocess
# from pathlib import Path
# import imageio_ffmpeg
# from pipeline.core import run_with_cache
# from pipeline.validate import load_and_validate

# import hashlib

# def file_sha256(path: Path) -> str:
#     return hashlib.sha256(path.read_bytes()).hexdigest()

# FFMPEG_BIN = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()


# def render_motion_clip(img_path: Path, wan_clip: Path, mode: str, dur: float, out_mp4: Path) -> bytes:
#     tmp_out = out_mp4.with_suffix(".tmp.mp4")
#     frames = int(round(dur * 24))

#     if wan_clip.exists():
#         cmd = [
#             FFMPEG_BIN, "-y", "-stream_loop", "-1", "-i", str(wan_clip),
#             "-t", f"{dur:.2f}",
#             "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24,format=yuv420p",
#             "-an", "-c:v", "libx264", "-crf", "20", str(tmp_out)
#         ]
#     else:
#         if mode == "ken_burns_out":
#             zp = f"zoompan=z='max(1.15-0.0006*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps=24"
#         elif mode == "pan_right":
#             zp = f"zoompan=z='1.12':x='min(on*1.2,iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps=24"
#         else:
#             zp = f"zoompan=z='min(zoom+0.0006,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps=24"

#         cmd = [
#             FFMPEG_BIN, "-y", "-loop", "1", "-i", str(img_path),
#             "-t", f"{dur:.2f}",
#             "-vf", f"scale=1920:1080,{zp},format=yuv420p",
#             "-an", "-c:v", "libx264", "-crf", "20", str(tmp_out)
#         ]

#     subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#     data = tmp_out.read_bytes()
#     tmp_out.unlink(missing_ok=True)
#     return data


# def generate_shots(sb: dict) -> None:
#     manifest = {m["id"]: m for m in json.loads(Path("outputs/audio/manifest.json").read_text(encoding="utf-8"))}

#     for shot in sb["shots"]:
#         sid = shot["id"]
#         dur = manifest[sid]["slot_dur"]
#         img_path = Path(f"outputs/keyframes/{sid}.png")
#         wan_clip = Path(f"outputs/wan22/{sid}.mp4")
#         out_mp4 = Path(f"outputs/shots/{sid}.mp4")

#         engine = "wan-2.2-i2v" if wan_clip.exists() else f"ffmpeg-{shot['motion_mode']}"
#         params = {
#             "keyframe_mtime": img_path.stat().st_mtime,
#             "wan_present": wan_clip.exists(),
#             "motion_mode": shot["motion_mode"],
#             "motion_prompt": shot["motion_prompt"],
#             "duration_sec": dur,
#         }
#         run_with_cache(
#             stage="shots",
#             item_id=sid,
#             model=engine,
#             params=params,
#             seed=shot["seed"],
#             output_path=out_mp4,
#             cost_usd=0.0,
#             fn=lambda i=img_path, w=wan_clip, m=shot["motion_mode"], d=dur, o=out_mp4: render_motion_clip(i, w, m, d, o),
#         )
#     print("[OK] All 8 moving shot clips ready in outputs/shots/.")


# if __name__ == "__main__":
#     generate_shots(load_and_validate())

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
import imageio_ffmpeg
from pipeline.core import run_with_cache
from pipeline.validate import load_and_validate

FFMPEG_BIN = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_multi_frame_sequence(frames_list: list[Path], dur: float, out_mp4: Path) -> bytes:
    """Crossfade across multiple action frames (e.g., shot_04_a.png, shot_04_b.png, shot_04_c.png) over `dur` seconds."""
    tmp_out = out_mp4.with_suffix(".tmp.mp4")
    n = len(frames_list)
    seg_dur = dur / n
    fade_dur = min(0.6, seg_dur * 0.25)

    inputs: list[str] = []
    for f in frames_list:
        inputs.extend(["-loop", "1", "-t", f"{seg_dur:.2f}", "-i", str(f)])

    filter_parts: list[str] = []
    for idx in range(n):
        filter_parts.append(
            f"[{idx}:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1,fps=24,format=yuv420p[v{idx}]"
        )

    curr_label = "v0"
    offset = max(0.1, seg_dur - fade_dur)
    for idx in range(1, n):
        next_label = f"xf{idx}"
        filter_parts.append(
            f"[{curr_label}][v{idx}]xfade=transition=fade:duration={fade_dur:.2f}:offset={offset:.2f}[{next_label}]"
        )
        curr_label = next_label
        offset += max(0.1, seg_dur - fade_dur)

    cmd = (
        [FFMPEG_BIN, "-y"]
        + inputs
        + [
            "-filter_complex", ";".join(filter_parts),
            "-map", f"[{curr_label}]",
            "-t", f"{dur:.2f}",
            "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
            str(tmp_out),
        ]
    )
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    data = tmp_out.read_bytes()
    tmp_out.unlink(missing_ok=True)
    return data


def render_motion_clip(img_path: Path, wan_clip: Path, mode: str, dur: float, out_mp4: Path) -> bytes:
    tmp_out = out_mp4.with_suffix(".tmp.mp4")
    frames = int(round(dur * 24))

    if wan_clip.exists():
        cmd = [
            FFMPEG_BIN, "-y", "-stream_loop", "-1", "-i", str(wan_clip),
            "-t", f"{dur:.2f}",
            "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24,format=yuv420p",
            "-an", "-c:v", "libx264", "-crf", "20", str(tmp_out)
        ]
    else:
        multi_frames = sorted(img_path.parent.glob(f"{img_path.stem}_*.png"))
        if multi_frames:
            return render_multi_frame_sequence(multi_frames, dur, out_mp4)

        if mode == "ken_burns_out":
            zp = f"zoompan=z='max(1.15-0.0006*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps=24"
        elif mode == "pan_right":
            zp = f"zoompan=z='1.12':x='min(on*1.2,iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps=24"
        else:
            zp = f"zoompan=z='min(zoom+0.0006,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps=24"

        cmd = [
            FFMPEG_BIN, "-y", "-loop", "1", "-i", str(img_path),
            "-t", f"{dur:.2f}",
            "-vf", f"scale=1920:1080,{zp},format=yuv420p",
            "-an", "-c:v", "libx264", "-crf", "20", str(tmp_out)
        ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    data = tmp_out.read_bytes()
    tmp_out.unlink(missing_ok=True)
    return data


def generate_shots(sb: dict) -> None:
    manifest = {m["id"]: m for m in json.loads(Path("outputs/audio/manifest.json").read_text(encoding="utf-8"))}

    for shot in sb["shots"]:
        sid = shot["id"]
        dur = manifest[sid]["slot_dur"]
        img_path = Path(f"outputs/keyframes/{sid}.png")
        wan_clip = Path(f"outputs/wan22/{sid}.mp4")
        out_mp4 = Path(f"outputs/shots/{sid}.mp4")
        multi_frames = sorted(img_path.parent.glob(f"{sid}_*.png"))

        engine = (
            "wan-2.2-i2v" if wan_clip.exists()
            else "ffmpeg-multi-frame" if multi_frames
            else f"ffmpeg-{shot['motion_mode']}"
        )
        params = {
            "keyframe_sha256": file_sha256(img_path),
            "multi_frame_sha256": [file_sha256(f) for f in multi_frames],
            "wan_present": wan_clip.exists(),
            "motion_mode": shot["motion_mode"],
            "motion_prompt": shot["motion_prompt"],
            "duration_sec": dur,
        }
        run_with_cache(
            stage="shots",
            item_id=sid,
            model=engine,
            params=params,
            seed=shot["seed"],
            output_path=out_mp4,
            cost_usd=0.0,
            fn=lambda i=img_path, w=wan_clip, m=shot["motion_mode"], d=dur, o=out_mp4: render_motion_clip(i, w, m, d, o),
        )
    print("[OK] All 8 moving shot clips ready in outputs/shots/.")


if __name__ == "__main__":
    generate_shots(load_and_validate())