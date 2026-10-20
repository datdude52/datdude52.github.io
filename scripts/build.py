"""Build the static site from /content into /site.

    python scripts/build.py            # build published projects
    python scripts/build.py --drafts   # include projects with "status": "draft"
    python scripts/build.py --pdf      # also print the resume page to PDF (needs Edge or Chrome)
    python scripts/build.py --serve    # build, then serve at http://localhost:8000

Pages: index.html, projects/, projects/<slug>/, resume/, about/, 404.html.
Everything resolves relative to this file and every link is relative, so the
output works from file://, GitHub Pages, Netlify, etc. Design rules: docs/DESIGN.md.
"""
import argparse
import datetime as dt
import functools
import hashlib
import html
import http.server
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import md  # noqa: E402

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("[build] Pillow is required for image sizing: pip install pillow")

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUT = ROOT / "site"
TEMPLATE = (ROOT / "templates" / "layout.html").read_text(encoding="utf-8")
PDF_NAME = "Andrew_Miller_Resume.pdf"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTS = {".mp4", ".webm"}
WIDTHS = (480, 960, 1600)
PROSE_SIZES = "(min-width: 820px) 720px, 100vw"
COVER_SIZES = "(min-width: 1100px) 1000px, 100vw"
FEATURE_SIZES = "(min-width: 1100px) 640px, 100vw"
ROW_SIZES = "(min-width: 640px) 200px, 100vw"
GALLERY_SIZES = "(min-width: 820px) 480px, 100vw"

NAV = [("home", "Home", "index.html"), ("projects", "Projects", "projects/index.html"),
       ("resume", "Resume", "resume/index.html"), ("about", "About", "about/index.html")]

esc = functools.partial(html.escape, quote=True)
WARNINGS = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)
    print(f"[build] warning: {msg}")


# ------------------------------------------------------------------ data ---

def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"[build] Invalid JSON in {path.relative_to(ROOT)}: {e}")


def load_projects(include_drafts: bool) -> list:
    projects = []
    for folder in sorted((CONTENT / "projects").iterdir()):
        meta_file = folder / "project.json"
        if not folder.is_dir() or folder.name.startswith(("_", ".")) or not meta_file.exists():
            continue
        p = load_json(meta_file)
        if p.get("status", "published") == "draft" and not include_drafts:
            continue
        p["slug"] = folder.name
        p["dir"] = folder
        writeup = folder / "writeup.md"
        p["body"] = writeup.read_text(encoding="utf-8") if writeup.exists() else ""
        media = folder / "images"
        files = sorted(media.iterdir()) if media.exists() else []
        videos = {f.stem for f in files if f.suffix.lower() in VIDEO_EXTS}
        p["videos"] = [f.name for f in files if f.suffix.lower() in VIDEO_EXTS]
        # A .jpg next to a video with the same name is that video's poster, not a gallery photo.
        p["images"] = [f.name for f in files if f.suffix.lower() in IMAGE_EXTS]
        p["posters"] = {f.name for f in files if f.suffix.lower() in IMAGE_EXTS and f.stem in videos}
        if not p.get("cover") and p["images"]:
            p["cover"] = "images/" + next(n for n in p["images"] if n not in p["posters"])
        if p.get("cover") and not p.get("cover_alt"):
            warn(f'{p["slug"]}: cover has no "cover_alt" text')
        projects.append(p)
    projects.sort(key=lambda p: (p.get("order", 99), p["title"]))
    return projects


# ---------------------------------------------------------------- images ---

class ImageSet:
    """One source image published as a capped fallback plus WebP width variants."""

    def __init__(self, src: Path, dest_dir: Path, rel_dir: str, crop: float = None):
        stem, ext = src.stem, src.suffix.lower()
        self.rel = f"{rel_dir}/{src.name}"
        dest_dir.mkdir(parents=True, exist_ok=True)
        fallback = dest_dir / src.name
        fresh = lambda p: p.exists() and p.stat().st_mtime >= src.stat().st_mtime
        with Image.open(src) as im:
            fmt = im.format
            im = ImageOps.exif_transpose(im)
            if crop:  # crop to an aspect ratio (w/h), keeping the upper-middle of the frame
                w, h = im.size
                if w / h > crop:
                    nw = round(h * crop); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
                else:
                    nh = round(w / crop); top = round((h - nh) * 0.25); im = im.crop((0, top, w, top + nh))
            scale = min(1.0, WIDTHS[-1] / im.width)
            self.w, self.h = round(im.width * scale), round(im.height * scale)
            if not fresh(fallback) or crop:
                out = im.resize((self.w, self.h), Image.LANCZOS) if scale < 1 else im
                if ext in (".jpg", ".jpeg"):
                    out.convert("RGB").save(fallback, "JPEG", quality=82, optimize=True, progressive=True)
                elif ext == ".png":
                    out.save(fallback, "PNG", optimize=True)
                else:
                    out.save(fallback, fmt)
            self.variants = []
            lossless = ext == ".png"  # plots, renders and drawings stay crisp
            for w in [w for w in WIDTHS if w < self.w] + [self.w]:
                v = dest_dir / f"{stem}-{w}.webp"
                if not fresh(v) or crop:
                    im.resize((w, round(self.h * w / self.w)), Image.LANCZOS).save(
                        v, "WEBP", lossless=lossless, quality=80 if not lossless else 90, method=6)
                self.variants.append((f"{rel_dir}/{v.name}", w))

    def img(self, alt: str, sizes: str, prefix: str = "", eager: bool = False, cls: str = "") -> str:
        srcset = ", ".join(f"{prefix}{esc(u)} {w}w" for u, w in self.variants)
        loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
        c = f' class="{cls}"' if cls else ""
        return (f'<img{c} src="{prefix}{esc(self.rel)}" srcset="{srcset}" sizes="{sizes}" '
                f'width="{self.w}" height="{self.h}" alt="{esc(alt)}" {loading} decoding="async">')


# ------------------------------------------------------------- rendering ---

def is_external(url: str) -> bool:
    return bool(re.match(r"^(https?:|mailto:|tel:)", url))


def href(url: str, root: str) -> str:
    return url if is_external(url) or url.startswith("#") else root + url


def block(url: str, label: str, root: str = "", kind: str = "", attrs: str = "") -> str:
    cls = "block" + (f" block--{kind}" if kind else "")
    return f'<a class="{cls}" href="{esc(href(url, root))}"{attrs}>{esc(label)}</a>'


def page(site: dict, *, title: str, description: str, content: str, root: str, current: str = "",
         og_type: str = "website", og_image: str = "", path: str = "", noindex: bool = False) -> str:
    base = site.get("base_url", "").rstrip("/")
    social = []
    if base and not noindex:
        social.append(f'<link rel="canonical" href="{esc(base)}/{esc(path)}">')
        social.append(f'<meta property="og:url" content="{esc(base)}/{esc(path)}">')
    if base and og_image:
        social.append(f'<meta property="og:image" content="{esc(base)}/{esc(og_image)}">')
        social.append('<meta name="twitter:card" content="summary_large_image">')
    body_font = site.get("fonts", [{}])[0].get("family", "")
    preload_file = ROOT / "assets" / "fonts" / f"{re.sub(r'[^a-z0-9]+', '-', body_font.lower())}-normal-400.woff2"
    preload = (f'<link rel="preload" href="{root}assets/fonts/{preload_file.name}" as="font" type="font/woff2" crossorigin>'
               if preload_file.exists() else "")
    nav = "".join(
        f'<li><a class="navlink" href="{root}{url}"{" aria-current=\"page\"" if key == current else ""}>{label}</a></li>'
        for key, label, url in NAV)
    values = {
        "title": esc(title), "description": esc(description), "name": esc(site["name"]),
        "root": root, "content": content, "body_class": f"page-{current}" if current else "",
        "og_type": og_type, "social": "\n  ".join(social), "preload": preload, "nav": nav,
        "robots": '<meta name="robots" content="noindex">' if noindex else "",
        "year": str(dt.date.today().year),
        "updated": dt.date.today().strftime("%B %Y"),
        # Changes whenever the stylesheet does, so browsers never keep an old copy after a deploy.
        "css_v": hashlib.sha1((ROOT / "assets" / "css" / "style.css").read_bytes()).hexdigest()[:8],
        "contact_blocks": "".join(block(l["url"], l["label"], root, "light") for l in site.get("links", []))
                          + block("resume/index.html", "Resume", root, "light"),
    }
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values.get(m.group(1), ""), TEMPLATE)


def figure(media, *, alt: str, caption: str, num: int, sizes: str, prefix: str = "",
           callouts=None, eager: bool = False, cls: str = "fig") -> str:
    overlay = key = ""
    if callouts:
        lines, marks = [], []
        for i, c in enumerate(callouts, 1):
            (px, py), (lx, ly) = c["at"], c["label_at"]
            side = "left" if lx < px else "right"
            lines.append(f'<line x1="{px}" y1="{py}" x2="{lx}" y2="{ly}" vector-effect="non-scaling-stroke"/>')
            marks.append(f'<span class="callout__dot" style="left:{px}%;top:{py}%">{i}</span>'
                         f'<span class="callout__label callout__label--{side}" style="left:{lx}%;top:{ly}%">{esc(c["label"])}</span>')
        overlay = (f'<svg class="callout__lines" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'
                   f'{"".join(lines)}</svg><span aria-hidden="true">{"".join(marks)}</span>')
        key = '<ol class="callout__key">' + "".join(f"<li>{esc(c['label'])}</li>" for c in callouts) + "</ol>"
        cls += " fig--annotated"
    cap = (f'<figcaption><span class="fig__num">Fig. {num}</span> {md.inline(caption)}{key}</figcaption>'
           if caption or key else "")
    if isinstance(media, dict):  # video
        body = (f'<video class="fig__video" controls preload="none" playsinline poster="{prefix}{esc(media["poster"])}"'
                f' width="{media["w"]}" height="{media["h"]}" aria-label="{esc(alt)}">'
                f'<source src="{prefix}{esc(media["src"])}" type="video/mp4"></video>')
        return f'<figure class="{cls}"><div class="fig__media">{body}</div>{cap}</figure>'
    return (f'<figure class="{cls}"><a class="fig__media" href="{prefix}{esc(media.rel)}">'
            f'{media.img(alt, sizes, prefix, eager)}{overlay}</a>{cap}</figure>')


def project_row(p: dict, images: dict, root: str) -> str:
    url = f'{root}projects/{p["slug"]}/index.html'
    cover = images.get((p["slug"], p.get("cover")))
    thumb = (f'<div class="row__thumb" aria-hidden="true">{cover.img("", ROW_SIZES, f"{root}projects/{p["slug"]}/")}</div>'
             if cover else "")
    status = ""
    if p.get("status") == "draft":
        status = '<span class="tag tag--draft">Draft</span>'
    elif p.get("progress"):
        status = f'<span class="tag">{esc(p["progress"])}</span>'
    return f"""
        <li class="row{" row--text" if not cover else ""}">
          {thumb}
          <div class="row__text">
            <p class="row__dates">{esc(p.get("dates", ""))} {status}</p>
            <h3><a class="row__link" href="{url}">{esc(p["title"])}</a></h3>
            <p>{esc(p.get("result") or p.get("summary", ""))}</p>
          </div>
        </li>"""


def project_list(projects: list, images: dict, root: str, heading_level: str = "h2") -> str:
    out = []
    for kind, heading in (("hardware", "Engineering projects"), ("software", "Software")):
        rows = [project_row(p, images, root) for p in projects if p.get("kind", "hardware") == kind]
        if rows:
            out.append(f'<section class="group"><{heading_level}>{heading}</{heading_level}>'
                       f'<ol class="rows">{"".join(rows)}</ol></section>')
    return "\n".join(out)


def render_home(site: dict, projects: list, images: dict, about_img=None) -> str:
    intro = "".join(f"<p>{md.inline(p)}</p>" for p in site["home"]["intro"])
    # Degree, availability, location and work authorization: what a recruiter screens for first.
    facts = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in site["home"].get("facts", []))
    photo = (f'<div class="hero__photo">{about_img.img(site["about"].get("photo_alt", ""), "(min-width: 900px) 320px, 0px", "about/", True)}</div>'
             if about_img else "")
    hero = f"""
    <section class="hero">
      <div class="wrap hero__grid">
        <div>
        <h1>{esc(site["name"])}</h1>
        <div class="hero__intro">{intro}</div>
        {f'<dl class="facts">{facts}</dl>' if facts else ""}
        <div class="blocks">
          {block("projects/index.html", "View projects", "", "light")}
          {block("resume/index.html", "Resume", "", "outline-light")}
          {block("about/index.html", "About me", "", "outline-light")}
        </div>
        </div>
        {photo}
      </div>
    </section>"""
    feat = next((p for p in projects if p.get("status") != "draft"), None)
    featured = ""
    if feat:
        img = images.get((feat["slug"], feat.get("feature_image") or feat.get("cover")))
        url = f'projects/{feat["slug"]}/index.html'
        pic = (f'<a class="feature__media" href="{url}" tabindex="-1" aria-hidden="true">'
               f'{img.img("", FEATURE_SIZES, f"projects/{feat["slug"]}/")}</a>') if img else ""
        featured = f"""
    <section class="wrap feature">
      <h2>Featured project</h2>
      <div class="feature__panel">
        {pic}
        <div class="feature__text">
          <p class="row__dates">{esc(feat.get("dates", ""))}</p>
          <h3><a href="{url}">{esc(feat["title"])}</a></h3>
          <p>{esc(feat.get("summary", ""))}</p>
          <p>{esc(feat.get("result", ""))}</p>
          <div class="blocks">{block(url, "Read the project", "", "primary")}</div>
        </div>
      </div>
    </section>"""
    rest = [p for p in projects if p is not feat]
    listing = f'<div class="wrap listing">{project_list(rest, images, "", "h2")}</div>'

    # Each skill points at the projects that show it, so the claim and the evidence sit together.
    titles = {p["slug"]: p["title"] for p in projects if p.get("status") != "draft"}
    skill_rows = []
    for s in site["home"].get("skills", []):
        shown = [slug for slug in s.get("projects", []) if slug in titles]
        links = "".join(f'<li><a href="projects/{slug}/index.html">{esc(titles[slug])}</a></li>' for slug in shown)
        links = f'<ul class="skills__links">{links}</ul>' if links else ""
        skill_rows.append(f'<div><dt>{esc(s["skill"])}</dt><dd><p>{esc(s["detail"])}</p>{links}</dd></div>')
    skills = (f'<section class="wrap skills"><h2>Skills and where to see them</h2>'
              f'<dl class="spec skills__list">{"".join(skill_rows)}</dl></section>') if skill_rows else ""

    og = "assets/img/og.jpg" if (CONTENT / "images" / "og.jpg").exists() else ""
    return page(site, title=f'{site["name"]} | Mechanical Engineering', description=site.get("description", ""),
                content=hero + featured + listing + skills, root="", current="home", og_image=og)


def render_projects_page(site: dict, projects: list, images: dict) -> str:
    content = f"""
    <header class="page-head"><div class="wrap">
      <h1>Projects</h1>
      <p>Coursework, team, and personal projects, with the testing and results behind each one.</p>
    </div></header>
    <div class="wrap listing">{project_list(projects, images, "../", "h2")}</div>"""
    return page(site, title=f'Projects | {site["name"]}', description="Engineering projects by Andrew J. Miller.",
                content=content, root="../", current="projects", path="projects/")


def render_resume_page(site: dict, resume: dict, project_slugs: set, has_pdf: bool) -> str:
    def entry(e):
        l1, l2 = e.get("line1", ["", ""]), e.get("line2")
        name = esc(l1[0])
        if e.get("project") in project_slugs:
            name = f'<a href="../projects/{e["project"]}/index.html">{name}</a>'
        ctx = f'<span class="cv-context"> | {esc(e["context"])}</span>' if e.get("context") else ""
        parts = [f'<p class="cv-line1"><span><strong>{name}</strong>{ctx}</span><span>{esc(l1[1])}</span></p>']
        if l2:
            parts.append(f'<p class="cv-line2"><span>{esc(l2[0])}</span><span>{esc(l2[1])}</span></p>')
        parts += [f'<p class="cv-detail"><strong>{esc(k)}:</strong> {esc(v)}</p>' for k, v in e.get("details", [])]
        if e.get("bullets"):
            parts.append("<ul>" + "".join(f"<li>{esc(b)}</li>" for b in e["bullets"]) + "</ul>")
        return f'<div class="cv-entry">{"".join(parts)}</div>'

    sections = []
    for s in resume["sections"]:
        body = "".join(entry(e) for e in s.get("entries", []))
        body += "".join(f'<p class="cv-detail">{f"<strong>{esc(k)}:</strong> " if k else ""}{esc(v)}</p>'
                        for k, v in s.get("details", []))
        sections.append(f'<section><h2 class="cv-heading">{esc(s["heading"])}</h2>{body}</section>')
    contact = " | ".join(esc(c) for c in resume["contact"])
    actions = [block(PDF_NAME, "Download PDF", "", "primary", " download")] if has_pdf else []
    actions.append('<button class="block" type="button" onclick="window.print()">Print</button>')
    actions.append(block("mailto:" + site["email"], "Email me", "", ""))
    content = f"""
    <header class="page-head"><div class="wrap">
      <h1>Resume</h1>
      <div class="blocks">{"".join(actions)}</div>
    </div></header>
    <div class="wrap sheet-wrap">
      <article class="sheet" aria-label="Resume">
        <p class="cv-name">{esc(resume["name"])}</p>
        <p class="cv-contact">{contact}</p>
        {"".join(sections)}
      </article>
    </div>"""
    return page(site, title=f'Resume | {site["name"]}', description=f'Resume of {site["name"]}.',
                content=content, root="../", current="resume", path="resume/")


def render_about_page(site: dict, about_img) -> str:
    a = site["about"]
    photo = (f'<figure class="about__photo">{about_img.img(a.get("photo_alt", ""), "(min-width: 820px) 360px, 100vw", "", True)}</figure>'
             if about_img else "")
    paras = "".join(f"<p>{md.inline(p)}</p>" for p in a["paragraphs"])
    contact = "".join(block(l["url"], l["label"], "../", "primary" if i == 0 else "") for i, l in enumerate(site["links"]))
    content = f"""
    <header class="page-head"><div class="wrap"><h1>About me</h1></div></header>
    <div class="wrap about">
      {photo}
      <div class="about__text prose">
        {paras}
        <h2>Get in touch</h2>
        <p>The best way to reach me is by email at <a href="mailto:{esc(site["email"])}">{esc(site["email"])}</a>.</p>
        <div class="blocks">{contact}</div>
      </div>
    </div>"""
    return page(site, title=f'About | {site["name"]}', description=f'About {site["name"]}.', content=content,
                root="../", current="about", path="about/")


def render_project(site: dict, p: dict, images: dict, videos: dict, prev_p, next_p) -> str:
    slug = p["slug"]
    spec = [row for row in p.get("spec", []) if row[1].strip()]
    if p.get("role") and not any(k in ("Role", "My role") for k, _ in spec):
        spec.insert(0, ["Role", p["role"]])
    spec_html = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in spec)
    status = f'<span class="tag">{esc(p["progress"])}</span>' if p.get("progress") else ""
    links = "".join(block(l["url"], l["label"], "", "primary" if i == 0 else "") for i, l in enumerate(p.get("links", [])))

    num = 0
    cover_html = ""
    cover = images.get((slug, p.get("cover")))
    if cover:
        num += 1
        cover_html = figure(cover, alt=p.get("cover_alt", ""), caption=p.get("cover_caption", ""), num=num,
                            sizes=COVER_SIZES, callouts=p.get("cover_callouts"), eager=True, cls="fig fig--cover")

    body = md.render(p["body"])

    def body_fig(m):
        nonlocal num
        src, alt, caption = m.group(1), html.unescape(m.group(2)), m.group(3) or ""
        img = images.get((slug, src))
        if not img:
            warn(f"{slug}: writeup references missing image {src}")
            return m.group(0)
        num += 1
        return figure(img, alt=alt, caption=html.unescape(re.sub(r"<[^>]+>", "", caption)), num=num, sizes=PROSE_SIZES)

    body = re.sub(r'<figure><img src="([^"]+)" alt="([^"]*)"[^>]*>(?:<figcaption>(.*?)</figcaption>)?</figure>',
                  body_fig, body)
    # Optional "lessons" in project.json: what went wrong and what I would change. Shown only when written.
    lessons = p.get("lessons") or []
    if isinstance(lessons, str):
        lessons = [lessons]
    if lessons:
        body += "<h2>What I learned</h2>" + "".join(f"<p>{md.inline(x)}</p>" for x in lessons)

    used = {p.get("cover")} | set(re.findall(r'href="(images/[^"]+)"', body))
    items = p.get("gallery") or [{"src": f"images/{n}"} for n in p["images"] + p["videos"] if n not in p["posters"]]
    gallery = []
    for g in items:
        if g["src"] in used:
            continue
        media = images.get((slug, g["src"])) or videos.get((slug, g["src"]))
        if not media:
            warn(f'{slug}: gallery item {g["src"]} not found')
            continue
        if not g.get("alt") and not g.get("caption"):
            warn(f'{slug}: gallery item {g["src"]} has no alt or caption')
        num += 1
        gallery.append(figure(media, alt=g.get("alt", ""), caption=g.get("caption", ""), num=num, sizes=GALLERY_SIZES))

    def pager(q, label):
        return (f'<a class="pager__link" href="../{q["slug"]}/index.html"><small>{label}</small>{esc(q["title"])}</a>'
                if q else "<span></span>")

    content = f"""
    <article class="project">
      <header class="page-head"><div class="wrap">
        <p class="crumbs"><a href="../index.html">Projects</a></p>
        <h1>{esc(p["title"])}</h1>
        <p class="project__dek">{esc(p.get("summary", ""))}</p>
        <p class="project__meta">{esc(p.get("dates", ""))} {status}</p>
        {f'<div class="blocks">{links}</div>' if links else ""}
      </div></header>
      <div class="wrap project__body">
        {f'<dl class="spec">{spec_html}</dl>' if spec_html else ""}
        {cover_html}
        <div class="prose">{body or "<p>The full write-up for this project is in progress.</p>"}</div>
        {f'<section class="gallery-wrap"><h2>More photos and figures</h2><div class="gallery">{"".join(gallery)}</div></section>' if gallery else ""}
        <nav class="pager" aria-label="More projects">{pager(prev_p, "Previous project")}{pager(next_p, "Next project")}</nav>
      </div>
    </article>"""
    og = f'projects/{slug}/{p["cover"]}' if cover else ""
    return page(site, title=f'{p["title"]} | {site["name"]}', description=p.get("summary", ""), content=content,
                root="../../", current="projects", og_type="article", og_image=og, path=f"projects/{slug}/")


# ------------------------------------------------------------------- pdf ---

def browser() -> str:
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidates + [shutil.which(n) or "" for n in ("msedge", "google-chrome", "chromium", "chrome")]:
        if c and Path(c).exists():
            return c
    return ""


def print_resume_pdf() -> None:
    exe = browser()
    if not exe:
        warn("no Edge/Chrome found; skipped PDF (the existing PDF in content/resume is used)")
        return
    target = CONTENT / "resume" / PDF_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    page_url = (OUT / "resume" / "index.html").resolve().as_uri()
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={target}", page_url], check=False, capture_output=True, timeout=120)
    if target.exists():
        shutil.copy2(target, OUT / "resume" / PDF_NAME)
        print(f"[build] printed resume -> content/resume/{PDF_NAME}")
    else:
        warn("PDF printing failed")


# ------------------------------------------------------------------ main ---

def build(include_drafts: bool = False, make_pdf: bool = False) -> None:
    WARNINGS.clear()
    site = load_json(CONTENT / "site.json")
    resume = load_json(CONTENT / "resume.json")
    projects = load_projects(include_drafts)
    slugs = {p["slug"] for p in projects}

    for stale in OUT.glob("projects/*/"):
        if stale.is_dir() and stale.name not in slugs:
            shutil.rmtree(stale, ignore_errors=True)  # OneDrive can briefly lock files
    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True)

    og_src = CONTENT / "images" / "og.jpg"
    if og_src.exists():
        ImageSet(og_src, OUT / "assets" / "img", "assets/img")
    about_src = CONTENT / site["about"].get("photo", "")
    about_img = ImageSet(about_src, OUT / "about" / "img", "img", crop=0.8) if about_src.is_file() else None

    images, videos = {}, {}
    for p in projects:
        dest = OUT / "projects" / p["slug"] / "images"
        dest.mkdir(parents=True, exist_ok=True)
        for n in p["images"]:
            images[(p["slug"], f"images/{n}")] = ImageSet(p["dir"] / "images" / n, dest, "images")
        for n in p["videos"]:
            shutil.copy2(p["dir"] / "images" / n, dest / n)
            poster = next((x for x in p["images"] if Path(x).stem == Path(n).stem), None)
            if not poster:
                warn(f'{p["slug"]}: video {n} has no poster image (run scripts/prepare_video.py)')
                continue
            ps = images[(p["slug"], f"images/{poster}")]
            videos[(p["slug"], f"images/{n}")] = {"src": f"images/{n}", "poster": ps.rel, "w": ps.w, "h": ps.h}
        if p.get("cover") and (p["slug"], p["cover"]) not in images:
            warn(f'{p["slug"]}: cover "{p["cover"]}" not found')

    for i, p in enumerate(projects):
        prev_p = projects[i - 1] if i > 0 else None
        next_p = projects[i + 1] if i + 1 < len(projects) else None
        (OUT / "projects" / p["slug"] / "index.html").write_text(
            render_project(site, p, images, videos, prev_p, next_p), encoding="utf-8")

    pdf_src = CONTENT / "resume" / PDF_NAME
    (OUT / "resume").mkdir(parents=True, exist_ok=True)
    if pdf_src.exists():
        shutil.copy2(pdf_src, OUT / "resume" / PDF_NAME)
    pages = {
        OUT / "index.html": render_home(site, projects, images, about_img),
        OUT / "projects" / "index.html": render_projects_page(site, projects, images),
        OUT / "resume" / "index.html": render_resume_page(site, resume, slugs, pdf_src.exists() or make_pdf),
        OUT / "about" / "index.html": render_about_page(site, about_img),
    }
    for path, text in pages.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    if make_pdf:
        print_resume_pdf()

    abs_root = (site.get("base_url", "").rstrip("/") or "") + "/"
    (OUT / "404.html").write_text(page(
        site, title=f'Page not found | {site["name"]}', description="", root=abs_root, noindex=True,
        content=f'<header class="page-head"><div class="wrap"><h1>Page not found</h1>'
                f'<p>That page does not exist or has moved.</p>'
                f'<div class="blocks">{block(abs_root + "index.html", "Go to the home page", "", "primary")}'
                f'{block(abs_root + "projects/index.html", "See all projects")}</div></div></header>'),
        encoding="utf-8")
    write_sitemap(site, projects)
    drafts = sum(p.get("status") == "draft" for p in projects)
    print(f"[build] {len(projects)} project(s){f' ({drafts} draft)' if drafts else ''}, "
          f"{len(WARNINGS)} warning(s) -> {OUT.relative_to(ROOT)}/index.html")


def write_sitemap(site: dict, projects: list) -> None:
    base = site.get("base_url", "").rstrip("/")
    if not base:
        return
    urls = [f"{base}/", f"{base}/projects/", f"{base}/resume/", f"{base}/about/"]
    urls += [f'{base}/projects/{p["slug"]}/' for p in projects if p.get("status") != "draft"]
    body = "".join(f"<url><loc>{esc(u)}</loc></url>" for u in urls)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>',
        encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")


def serve(port: int) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    print(f"[serve] http://localhost:{port}  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--drafts", action="store_true", help="include draft projects")
    ap.add_argument("--pdf", action="store_true", help="print the resume page to PDF")
    ap.add_argument("--serve", action="store_true", help="serve the site after building")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    build(args.drafts, args.pdf)
    if args.serve:
        serve(args.port)
