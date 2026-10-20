"""Stress-test the built site: crawl every page, follow every link, load every asset.

    python scripts/build.py && python scripts/check_site.py
    python scripts/check_site.py --no-external     # skip internet link checks
    python scripts/check_site.py --shots           # also save full-page screenshots to qa/

Checks, per page, at desktop (1280px) and phone (390px) width:
  - every internal link points at a page or file that exists (and #anchors exist)
  - every request (CSS, fonts, images, video) returns 200; no console errors
  - every <img> loaded, has alt text (or alt="" with aria-hidden context), has width/height
  - exactly one <h1>, a <title>, and a meta description
  - nothing overflows horizontally on a phone
  - external links answer (some sites, like LinkedIn, block bots; those are flagged, not failed)
Exits non-zero if anything fails. Needs: pip install playwright (uses installed Edge or Chrome).
"""
import argparse
import functools
import http.server
import socket
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
QA = ROOT / "qa"
BOT_BLOCKERS = {"www.linkedin.com", "linkedin.com"}


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def serve(port: int) -> http.server.ThreadingHTTPServer:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Quiet, directory=str(SITE)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def check_external(url: str) -> str:
    host = urlparse(url).netloc
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0 (site link check)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return f"ok {r.status}"
    except urllib.error.HTTPError as e:
        if host in BOT_BLOCKERS or e.code in (403, 429, 999):
            return f"blocked {e.code} (site refuses bots; check by hand)"
        return f"FAIL {e.code}"
    except Exception as e:  # noqa: BLE001
        return f"FAIL {type(e).__name__}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-external", action="store_true")
    ap.add_argument("--shots", action="store_true")
    args = ap.parse_args()
    if not (SITE / "index.html").exists():
        print("site/ is empty: run python scripts/build.py first")
        return 1

    port = free_port()
    srv = serve(port)
    base = f"http://127.0.0.1:{port}/"
    failures, notes, external = [], [], set()
    seen, queue = set(), ["index.html", "404.html"]

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge")
        except Exception:
            browser = p.chromium.launch(channel="chrome")
        for width, label in ((1280, "desktop"), (390, "phone")):
            ctx = browser.new_context(viewport={"width": width, "height": 900})
            page = ctx.new_page()
            bad_requests, console = [], []
            page.on("response", lambda r: bad_requests.append(f"{r.status} {r.url}") if r.status >= 400 else None)
            page.on("requestfailed", lambda r: bad_requests.append(f"failed {r.url}"))
            page.on("console", lambda m: console.append(m.text) if m.type == "error" else None)
            todo = list(queue) if label == "desktop" else sorted(seen)
            visited = set()
            while todo:
                rel = todo.pop(0)
                if rel in visited:
                    continue
                visited.add(rel)
                bad_requests.clear(); console.clear()
                page.goto(base + rel, wait_until="load")
                for y in range(0, page.evaluate("document.body.scrollHeight") + 900, 600):  # trigger lazy images
                    page.evaluate(f"window.scrollTo(0, {y})"); page.wait_for_timeout(120)
                page.wait_for_load_state("networkidle")
                info = page.evaluate("""() => ({
                  title: document.title,
                  desc: document.querySelector('meta[name=description]')?.content ?? null,
                  h1: document.querySelectorAll('h1').length,
                  overflow: document.documentElement.scrollWidth - window.innerWidth,
                  links: [...document.querySelectorAll('a[href]')].map(a => ({href: a.getAttribute('href'), text: a.textContent.trim().slice(0, 40)})),
                  imgs: [...document.querySelectorAll('img')].map(i => ({src: i.currentSrc || i.src, alt: i.getAttribute('alt'),
                         ok: (i.complete && i.naturalWidth > 0) || !i.checkVisibility(), dims: i.hasAttribute('width') && i.hasAttribute('height'),
                         hidden: !!i.closest('[aria-hidden=true]')})),
                  ids: [...document.querySelectorAll('[id]')].map(e => e.id),
                })""")
                where = f"[{label}] {rel}"
                if not info["title"]:
                    failures.append(f"{where}: missing <title>")
                if rel != "404.html" and not info["desc"]:
                    failures.append(f"{where}: missing meta description")
                if info["h1"] != 1:
                    failures.append(f"{where}: {info['h1']} <h1> elements (want 1)")
                if info["overflow"] > 1:
                    failures.append(f"{where}: page is {info['overflow']}px wider than the screen")
                for img in info["imgs"]:
                    if not img["ok"]:
                        failures.append(f"{where}: image did not load {img['src']}")
                    if img["alt"] is None:
                        failures.append(f"{where}: image missing alt {img['src']}")
                    elif img["alt"] == "" and not img["hidden"]:
                        notes.append(f"{where}: decorative (empty alt) image {img['src']}")
                    if not img["dims"]:
                        failures.append(f"{where}: image without width/height {img['src']}")
                for b in bad_requests:
                    failures.append(f"{where}: request {b}")
                for c in console:
                    failures.append(f"{where}: console error {c}")
                if label == "desktop":
                    for link in info["links"]:
                        h = link["href"]
                        if h.startswith(("mailto:", "tel:")):
                            if h.startswith("mailto:") and "@" not in h:
                                failures.append(f"{where}: bad mailto {h}")
                            continue
                        if h.startswith(("http://", "https://")) and not h.startswith(base):
                            external.add(h)
                            continue
                        target = urlparse(urljoin(base + rel, h))
                        path = unquote(target.path).lstrip("/") or "index.html"
                        file = SITE / path
                        if file.is_dir():
                            file = file / "index.html"; path = path.rstrip("/") + "/index.html"
                        if not file.exists():
                            failures.append(f"{where}: broken link '{link['text']}' -> {h}")
                            continue
                        if target.fragment and path == rel and target.fragment not in info["ids"]:
                            failures.append(f"{where}: missing anchor #{target.fragment}")
                        if path.endswith(".html") and path not in seen:
                            seen.add(path); todo.append(path)
                    seen.add(rel)
                if args.shots:
                    QA.mkdir(exist_ok=True)
                    page.screenshot(path=str(QA / f"{label}--{rel.replace('/', '_')}.png"), full_page=True)
            ctx.close()
        browser.close()
    srv.shutdown()

    print(f"Pages checked: {len(seen)} (each at desktop and phone width)")
    if not args.no_external:
        print(f"External links: {len(external)}")
        for url in sorted(external):
            result = check_external(url)
            print(f"  {result:<12} {url}")
            if result.startswith("FAIL"):
                failures.append(f"external link {url}: {result}")
    for n in notes:
        print(f"note: {n}")
    if failures:
        print(f"\n{len(failures)} problem(s):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
