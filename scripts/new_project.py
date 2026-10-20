"""Scaffold a new project in content/projects/<slug>/.

    python scripts/new_project.py "Cycloidal Drive v2"
    python scripts/new_project.py "Rocket Fin Can" --dates "Nov 2026"
    python scripts/new_project.py "Rocket Fin Can" --from "D:/somewhere/fin can photos" --build
    python scripts/new_project.py "Resume Parser" --software
    python scripts/new_project.py            # prompts for everything

--from copies every image in that folder (not subfolders) into the project's
images/ folder; the first one, or one named cover.*, becomes the cover.
New projects start as "draft" so they don't go live until you flip the status
(or pass --publish).
"""
import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "content" / "projects"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

WRITEUP = """<!-- The spec block in project.json carries the summary. This is the
     longer story for engineers who click through. Comments are stripped. -->

## Why I built it

## Design

<!-- Figures: ![alt text describing the image](images/file.jpg "Caption under it")
     They are numbered automatically (Fig. 2, Fig. 3, ...). -->

## Testing and results

## What I'd change
"""


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def ask(prompt: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    return input(f"{prompt}{hint}: ").strip() or default


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("title", nargs="?")
    ap.add_argument("--slug", help="folder / URL name (default: from title)")
    ap.add_argument("--summary", default="")
    ap.add_argument("--software", action="store_true", help="list under Software instead of Projects")
    ap.add_argument("--dates", help='shown on the site, e.g. "Spring 2025" or "Sep 2026 – Present"')
    ap.add_argument("--order", type=int, default=50, help="position in project lists (1 = first)")
    ap.add_argument("--from", dest="source", help="folder of images to copy in")
    ap.add_argument("--featured", action="store_true")
    ap.add_argument("--publish", action="store_true", help="mark as published instead of draft")
    ap.add_argument("--build", action="store_true", help="rebuild the site afterwards")
    args = ap.parse_args()

    interactive = args.title is None
    title = args.title or ask("Project title")
    if not title:
        sys.exit("A title is required.")
    summary = args.summary or (ask("One-line summary") if interactive else "")
    dates = args.dates or dt.date.today().strftime("%b %Y")

    slug = args.slug or slugify(title)
    folder = PROJECTS / slug
    if folder.exists():
        sys.exit(f"content/projects/{slug} already exists; pick another title or pass --slug.")
    (folder / "images").mkdir(parents=True)

    cover = ""
    if args.source:
        src = Path(args.source).expanduser()
        if not src.is_dir():
            print(f"warning: --from folder not found: {src}")
        else:
            images = sorted(f for f in src.iterdir() if f.suffix.lower() in IMAGE_EXTS)
            for f in images:
                shutil.copy2(f, folder / "images" / f"{slugify(f.stem)}{f.suffix.lower()}")
            named = [f for f in images if f.stem.lower() == "cover"]
            first = (named or images or [None])[0]
            if first:
                cover = f"images/{slugify(first.stem)}{first.suffix.lower()}"
            print(f"copied {len(images)} image(s)")

    meta = {
        "title": title,
        "summary": summary,
        "result": "One sentence in your own voice with a real number, shown in project lists.",
        "dates": dates,
        "order": args.order,
        "progress": "",
        "kind": "software" if args.software else "hardware",
        "status": "published" if args.publish else "draft",
        "featured": args.featured,
        "role": "",
        "spec": [
            ["Problem", ""],
            ["Constraints", ""],
            ["Method", ""],
            ["Result", ""],
            ["Tools", ""],
        ],
        "cover": cover,
        "cover_alt": "",
        "cover_caption": "",
        "cover_callouts": [],
        "links": [],
    }
    (folder / "project.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (folder / "writeup.md").write_text(WRITEUP, encoding="utf-8")

    print(f"created content/projects/{slug}/")
    print("  project.json  <- result line, spec block, cover alt/caption/callouts, links")
    print("  writeup.md    <- the project page body (Markdown)")
    print("  images/       <- drop photos/renders here; they auto-optimize on build")
    if args.build:
        sys.stdout.flush()
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py"), "--drafts"], check=False)


if __name__ == "__main__":
    main()
