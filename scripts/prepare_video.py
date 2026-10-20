"""Turn a phone video into a small web clip plus a poster frame.

    python scripts/prepare_video.py "path/to/IMG_1234.MOV" content/projects/<slug>/images/demo
    python scripts/prepare_video.py clip.mov out/demo --start 2 --length 8

Writes demo.mp4 (H.264, 720p max, no audio, about 1-3 MB) and demo.jpg (poster).
Then reference it from project.json:
    "gallery": [{"src": "images/demo.mp4", "caption": "..."}]
Needs ffmpeg; `pip install imageio-ffmpeg` bundles one.
"""
import argparse
import shutil
import subprocess
from pathlib import Path


def ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise SystemExit("ffmpeg not found: pip install imageio-ffmpeg")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("out", help="output path without extension")
    ap.add_argument("--start", type=float, default=0, help="seconds to skip")
    ap.add_argument("--length", type=float, help="seconds to keep")
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    trim = ["-ss", str(args.start)] + (["-t", str(args.length)] if args.length else [])
    # Fit inside 1280x720 whichever way the phone was held; tone-map HDR to plain SDR.
    vf = "scale='if(gt(iw,ih),min(1280,iw),-2)':'if(gt(iw,ih),-2,min(1280,ih))',format=yuv420p"
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", *trim, "-i", args.source, "-an",
                    "-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", "28",
                    "-movflags", "+faststart", str(out.with_suffix(".mp4"))], check=True)
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", "1", "-i", str(out.with_suffix(".mp4")),
                    "-frames:v", "1", "-q:v", "3", str(out.with_suffix(".jpg"))], check=True)
    mb = out.with_suffix(".mp4").stat().st_size / 1e6
    print(f"wrote {out.with_suffix('.mp4').name} ({mb:.1f} MB) and poster {out.with_suffix('.jpg').name}")


if __name__ == "__main__":
    main()
