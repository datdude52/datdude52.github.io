# Personal Website

Andrew J. Miller's engineering portfolio. It's a static site generated from plain JSON and Markdown files by a small Python build.

- [docs/DESIGN.md](docs/DESIGN.md) records the design and writing decisions.
- [docs/CONTENT_GAPS.md](docs/CONTENT_GAPS.md) is the to-do list: missing photos, video, and text for every page, with where each one goes.

## Quick start

```bash
pip install pillow playwright imageio-ffmpeg
python scripts/build.py --drafts --serve
```

Open http://localhost:8000. Drop `--drafts` to see only what will go live.

## Everyday tasks

| Task | Command |
|---|---|
| Build the site | `python scripts/build.py` |
| Build and print the resume PDF | `python scripts/build.py --pdf` (uses Edge or Chrome) |
| Stress-test every page, link, and asset | `python scripts/check_site.py` (add `--shots` for screenshots in `qa/`) |
| Add a project | `python scripts/new_project.py "Project Name" --from "path/to/photos"` |
| Add a video | `python scripts/prepare_video.py "IMG_1234.MOV" content/projects/<slug>/images/demo` |
| Change fonts | Edit `fonts` in `content/site.json`, then run `python scripts/fetch_fonts.py` |

## Where content lives

```
content/
  site.json          home intro, About page text and photo, contact links, fonts
  resume.json        the on-page resume (mirrors the master resume; layout per Resume_Format_Guide)
  resume/Andrew_Miller_Resume.pdf   printed from the resume page by --pdf
  images/about.jpg   About page and home page photo
  projects/<slug>/
    project.json     title, summary, result line, dates, order, spec panel, cover, callouts, gallery, links
    writeup.md       the long-form story; figures numbered automatically
    images/          photos, renders, plots, .mp4 clips (+ a .jpg poster with the same name)
```

### Project fields

```jsonc
{
  "title": "…",
  "summary": "One or two sentences under the title, in first person",
  "result": "One sentence with a real number, shown in project lists (no bold)",
  "dates": "Summer 2026 – Present",
  "order": 1,                      // list position
  "kind": "hardware",              // or "software"
  "status": "published",           // or "draft" (hidden unless --drafts)
  "progress": "Report in progress",// optional tag next to the dates
  "role": "…",
  "spec": [["Problem", "…"], ["Method", "…"], ["Testing", "…"], ["Result", "…"], ["Tools", "…"]],
  "cover": "images/cover.jpg", "cover_alt": "…", "cover_caption": "…",
  "cover_callouts": [{ "label": "…", "at": [52, 30], "label_at": [104, 22] }],
  "feature_image": "images/plot.png",   // optional; used when this is the home page's featured project
  "gallery": [{ "src": "images/x.jpg", "alt": "…", "caption": "…" },
              { "src": "images/demo.mp4", "poster": "images/demo.jpg", "alt": "…", "caption": "…" }],
  "links": [{ "label": "…", "url": "https://…" }],
  "lessons": ["What went wrong and what I would change, in my words"]  // optional; shown as "What I learned"
}
```

Callout coordinates are percentages of the image. Use `x = 104` to put the labels in the right margin. On phones, the labels turn into a numbered key.

## Keeping the resume current

1. Edit `content/resume.json`. Copy bullets from the master resume rather than rewriting them.
2. Run `python scripts/build.py --pdf`. The PDF must stay at one page. If it spills over, trim in the order your format guide gives (Interests first, then lower-priority bullets).
3. Run `python scripts/check_site.py`.

## Deploy (GitHub Pages)

1. The repo is `github.com/datdude52/datdude52.github.io`, branch `main`.
2. Go to **Settings → Pages → Source** and choose **GitHub Actions**. Each push rebuilds and publishes the site.
3. `base_url` in `content/site.json` is `https://datdude52.github.io`.

## Open items

- The ARC-001 and ARC-000 pages used to link to `github.com/datdude52/sonar-scanner`. That link returns 404 (the repo is private or missing), so it was removed. Make the repo public, then re-add the link in both `project.json` files.
- LinkedIn blocks automated link checks. The URL was verified by hand.
- See `docs/CONTENT_GAPS.md` for what to shoot and write next. Start with its short list.
- The bus-tracker doorway video (`IMG_1065.MOV`) needs your teammates' OK before it goes up.
