"""Tiny Markdown -> HTML converter (no dependencies).

Covers what a project write-up needs: headings, paragraphs, bold/italic,
inline code, code fences, links, images (with captions), ordered/unordered
lists, blockquotes, horizontal rules and pipe tables.

If the `markdown` package is installed it is used instead, with the
`tables` and `fenced_code` extensions.
"""
import html
import re

try:  # Prefer the real library when it's available.
    import markdown as _markdown  # type: ignore
except ImportError:  # pragma: no cover
    _markdown = None


def render(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()  # TODO notes stay private
    if not text:
        return ""
    if _markdown is not None:
        return _markdown.markdown(text, extensions=["tables", "fenced_code"])
    return _Renderer(text).run()


# ---------------------------------------------------------------- inline ---

_INLINE_CODE = re.compile(r"`([^`]+)`")
_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])")


def inline(text: str) -> str:
    # Pull inline code out first so its contents are never formatted.
    codes = []

    def stash(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = _INLINE_CODE.sub(stash, text)
    text = html.escape(text, quote=False)
    text = _IMAGE.sub(lambda m: _img(m.group(1), m.group(2)), text)
    text = _LINK.sub(lambda m: _link(m.group(1), m.group(2)), text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITALIC.sub(r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def _img(alt, src):
    return f'<img src="{src}" alt="{alt}" loading="lazy" decoding="async">'


def _link(label, href):
    external = href.startswith(("http://", "https://"))
    extra = ' target="_blank" rel="noopener"' if external else ""
    return f'<a href="{href}"{extra}>{label}</a>'


# ----------------------------------------------------------------- blocks ---

class _Renderer:
    def __init__(self, text):
        self.lines = text.replace("\r\n", "\n").split("\n")
        self.i = 0
        self.out = []

    def run(self):
        while self.i < len(self.lines):
            line = self.lines[self.i]
            s = line.strip()
            if not s:
                self.i += 1
            elif s.startswith("```"):
                self.fence()
            elif re.match(r"#{1,6}\s", s):
                level = len(s) - len(s.lstrip("#"))
                body = s[level:].strip()
                slug = re.sub(r"[^a-z0-9]+", "-", body.lower()).strip("-")
                self.out.append(f'<h{level} id="{slug}">{inline(body)}</h{level}>')
                self.i += 1
            elif re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", s):
                self.out.append("<hr>")
                self.i += 1
            elif s.startswith(">"):
                self.quote()
            elif s.startswith("|") and self._is_table():
                self.table()
            elif re.match(r"([-*+]|\d+\.)\s", s):
                self.list()
            elif _IMAGE.fullmatch(s):
                self.figure(s)
            else:
                self.paragraph()
        return "\n".join(self.out)

    def fence(self):
        lang = self.lines[self.i].strip()[3:].strip()
        self.i += 1
        body = []
        while self.i < len(self.lines) and not self.lines[self.i].strip().startswith("```"):
            body.append(self.lines[self.i])
            self.i += 1
        self.i += 1
        cls = f' class="language-{lang}"' if lang else ""
        self.out.append(f"<pre><code{cls}>{html.escape(chr(10).join(body))}</code></pre>")

    def quote(self):
        body = []
        while self.i < len(self.lines) and self.lines[self.i].strip().startswith(">"):
            body.append(self.lines[self.i].strip()[1:].lstrip())
            self.i += 1
        self.out.append(f"<blockquote>{_Renderer(chr(10).join(body)).run()}</blockquote>")

    def _is_table(self):
        nxt = self.lines[self.i + 1].strip() if self.i + 1 < len(self.lines) else ""
        return bool(re.fullmatch(r"\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?", nxt))

    def table(self):
        def cells(row):
            return [c.strip() for c in row.strip().strip("|").split("|")]

        head = cells(self.lines[self.i])
        self.i += 2
        rows = []
        while self.i < len(self.lines) and self.lines[self.i].strip().startswith("|"):
            rows.append(cells(self.lines[self.i]))
            self.i += 1
        th = "".join(f"<th>{inline(c)}</th>" for c in head)
        tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
        self.out.append(
            f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>'
        )

    def list(self):
        ordered = bool(re.match(r"\d+\.", self.lines[self.i].strip()))
        tag = "ol" if ordered else "ul"
        items = []
        while self.i < len(self.lines):
            s = self.lines[self.i].strip()
            m = re.match(r"([-*+]|\d+\.)\s+(.*)", s)
            if m:
                items.append(m.group(2))
            elif s and items and self.lines[self.i].startswith((" ", "\t")):
                items[-1] += " " + s  # wrapped continuation line
            else:
                break
            self.i += 1
        lis = "".join(f"<li>{inline(it)}</li>" for it in items)
        self.out.append(f"<{tag}>{lis}</{tag}>")

    def figure(self, s):
        m = _IMAGE.fullmatch(s)
        alt, src, caption = m.group(1), m.group(2), m.group(3) or m.group(1)
        cap = f"<figcaption>{inline(caption)}</figcaption>" if caption else ""
        self.out.append(f"<figure>{_img(html.escape(alt), src)}{cap}</figure>")
        self.i += 1

    def paragraph(self):
        body = []
        while self.i < len(self.lines):
            s = self.lines[self.i].strip()
            if not s or s.startswith(("```", "#", ">", "|")) or re.match(r"([-*+]|\d+\.)\s", s):
                break
            body.append(s)
            self.i += 1
        self.out.append(f"<p>{inline(' '.join(body))}</p>")
