#!/usr/bin/env python3
"""Build a print-ready catalogue from a JSON content file.

    python3 build_catalogue.py --config catalogue.json --outdir out/

Produces:
    out/catalogue.html          the rendered document
    out/catalogue.pdf           print-ready A4
    out/preview/page-01.png     one image per page, for looking at the work

The previews exist because a catalogue is a visual object. Reading the HTML
tells you the markup is valid; it does not tell you the title collides with the
photo. Render, look, fix — that loop is the job.

Content lives in the JSON; layout lives in the page archetypes below and in
assets/catalogue.css. Adding a product should never mean writing HTML.
"""

from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Chromium locations, most specific first. The pre-installed Playwright build is
# the usual one in this environment; the rest cover a normal desktop.
CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "chromium",
    "chromium-browser",
    "google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

DEFAULT_BRAND = {
    "ink": "#1F3864",
    "accent": "#C9A24E",
    "wash": "#F2F2F2",
    "tint": "#D6E4F0",
    "font": "'Calibri', 'Carlito', 'Liberation Sans', 'DejaVu Sans', sans-serif",
}


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def esc_lines(value) -> str:
    """Escaped, but honouring deliberate line breaks. Where a headline breaks is
    a design decision — "Cold Storage / Solutions" reads differently from a line
    the browser happens to wrap."""
    return esc(value).replace("\n", "<br>")


class Builder:
    def __init__(self, config: dict, base_dir: Path):
        self.config = config
        self.base = base_dir
        self.brand = {**DEFAULT_BRAND, **config.get("brand", {})}
        self.doc_title = config.get("title", "Catalogue")
        self.missing_images: list[str] = []
        self.folio_pages: list[int] = []   # indices that carry a page number

    # ---------------------------------------------------------------- images

    def image(self, src: str | None, css_class: str = "", alt: str = "") -> str:
        """An <img> if the file exists, a labelled placeholder if it does not.

        Never returns empty — a silent gap is the one failure mode that reaches
        the client, because nobody notices what isn't there."""
        if not src:
            return f'<div class="missing">NO IMAGE<br>{esc(alt or "specify a source")}</div>'
        path = (self.base / src).resolve() if not src.startswith(("http://", "https://", "data:")) else None
        if path is not None and not path.exists():
            self.missing_images.append(src)
            return f'<div class="missing">MISSING<br>{esc(src)}</div>'
        url = path.as_uri() if path is not None else src
        cls = f' class="{css_class}"' if css_class else ""
        return f'<img{cls} src="{esc(url)}" alt="{esc(alt)}">'

    def bg_image(self, src: str | None, css_class: str, alt: str = "") -> str:
        """Full-bleed image for a cover, feature or section band.

        Distinguishes two different things that both look like "no picture".
        A path that was given and does not resolve is a fault, and shows as a
        placeholder so it gets fixed. No path at all is a decision — a plain
        brand field is a legitimate cover, and often the right one for a
        document where a stock photograph would be worse than none."""
        if not src:
            return ""
        if (self.base / src).exists() or src.startswith(("http", "data:")):
            return self.image(src, css_class, alt)
        self.missing_images.append(src)
        return (
            f'<div class="{css_class}" style="display:flex">'
            f'<div class="missing">MISSING: {esc(src)}</div></div>'
        )

    # ----------------------------------------------------------------- pages

    def folio(self, page: dict, number: int | None) -> str:
        if number is None:
            return ""
        left = esc(page.get("folio", self.config.get("folio", self.doc_title)))
        return (
            f'<div class="folio"><span>{left}</span>'
            f'<span class="folio__num">{number:02d}</span></div>'
        )

    def cover(self, p: dict) -> str:
        mark = p.get("mark", "")
        if "|" in mark:
            head, tail = mark.split("|", 1)
            mark_html = f"{esc(head)}<span>{esc(tail)}</span>"
        else:
            mark_html = esc(mark)
        return f"""
      {self.bg_image(p.get("image"), "cover__image", "cover")}
      <div class="cover__scrim"></div>
      <div class="cover__body">
        <div class="cover__mark">{mark_html}</div>
        <div class="cover__stack">
          <div class="rule"></div>
          <h1 class="cover__title">{esc_lines(p.get("title", ""))}</h1>
          <p class="cover__sub">{esc_lines(p.get("subtitle", ""))}</p>
        </div>
        <div class="cover__foot">{esc(p.get("footer", ""))}</div>
      </div>"""

    def contents(self, p: dict, entries: list[dict]) -> str:
        items = p.get("items") or entries
        rows = []
        numeral = 0
        for item in items:
            is_sub = item.get("level", 0) > 0
            if is_sub:
                num_html = '<span class="toc__num"></span>'
            else:
                numeral += 1
                num_html = f'<span class="toc__num">{numeral:02d}</span>'
            sub = f' <span class="toc__sub">{esc(item["subtitle"])}</span>' if item.get("subtitle") else ""
            page_no = item.get("page")
            rows.append(
                f'<li class="{"toc--sub" if is_sub else ""}">{num_html}'
                f'<span class="toc__label">{esc(item.get("label", item.get("title", "")))}</span>{sub}'
                f'<span class="toc__dots"></span>'
                f'<span class="toc__page">{esc(page_no) if page_no else ""}</span></li>'
            )
        return f"""
      <div class="well">
        <div class="eyebrow">{esc(p.get("eyebrow", "Contents"))}</div>
        <h1>{esc(p.get("title", "What's inside"))}</h1>
        <div class="rule"></div>
        <ul class="toc">{"".join(rows)}</ul>
      </div>"""

    def section(self, p: dict) -> str:
        img = f'{self.image(p["image"], "section__image", p.get("title", ""))}' if p.get("image") else ""
        return f"""
      {img}
      <div class="well">
        <div class="section__numeral">{esc(p.get("number", ""))}</div>
        <h1 class="section__title">{esc_lines(p.get("title", ""))}</h1>
        <div class="rule"></div>
        <p class="section__sub">{esc(p.get("subtitle", ""))}</p>
      </div>"""

    def feature(self, p: dict) -> str:
        bullets = "".join(f"<li>{esc(b)}</li>" for b in p.get("bullets", []))
        bullets_html = f'<h3>{esc(p.get("bullets_title", "Highlights"))}</h3><ul class="bullets">{bullets}</ul>' if bullets else ""
        specs = "".join(
            f'<tr><td>{esc(s.get("label"))}</td><td>{esc(s.get("value"))}</td></tr>'
            for s in p.get("specs", [])
        )
        specs_html = f'<h3>{esc(p.get("specs_title", "Specification"))}</h3><table class="specs">{specs}</table>' if specs else ""
        footnote = f'<p class="caption">{esc(p["footnote"])}</p>' if p.get("footnote") else ""
        height = p.get("image_height", "118mm")
        return f"""
      <div style="position:absolute;top:0;left:0;right:0;height:{height};overflow:hidden">
        {self.bg_image(p.get("image"), "feature__image", p.get("title", ""))}
      </div>
      <div class="feature__body" style="top:{height}">
        <div class="eyebrow">{esc(p.get("eyebrow", ""))}</div>
        <h1>{esc(p.get("title", ""))}</h1>
        <div class="feature__cols">
          <div class="feature__main">
            <p class="lead">{esc(p.get("lead", ""))}</p>
            {bullets_html}
          </div>
          <div class="feature__side">{specs_html}{footnote}</div>
        </div>
      </div>"""

    def grid(self, p: dict) -> str:
        cols = int(p.get("columns", 2))
        cells = []
        for item in p.get("items", []):
            tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in item.get("tags", []))
            cells.append(f"""
          <div class="item">
            <div class="item__frame">{self.image(item.get("image"), "", item.get("name", ""))}</div>
            <div class="item__name">{esc(item.get("name", ""))}</div>
            <div class="item__line">{esc(item.get("line", ""))}</div>
            <div class="tags">{tags}</div>
          </div>""")
        intro = f'<p class="lead">{esc(p["intro"])}</p>' if p.get("intro") else ""
        return f"""
      <div class="well">
        <div class="eyebrow">{esc(p.get("eyebrow", ""))}</div>
        <h1>{esc(p.get("title", ""))}</h1>
        <div class="rule"></div>
        {intro}
        <div class="grid grid--{cols}">{"".join(cells)}</div>
      </div>"""

    def spec(self, p: dict) -> str:
        table = p.get("table", {})
        head = "".join(f"<th>{esc(h)}</th>" for h in table.get("headers", []))
        # Rows named in `highlight` (0-based) render in the alert colours. A
        # table whose exclusions look exactly like its inclusions has not
        # communicated the exclusion, however clearly the words are chosen.
        flagged = set(p.get("highlight", []))
        body = "".join(
            f'<tr class="{"row--flag" if i in flagged else ""}">'
            + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>"
            for i, row in enumerate(table.get("rows", []))
        )
        intro = f'<p class="lead">{esc(p["intro"])}</p>' if p.get("intro") else ""
        note = f'<p class="caption">{esc(p["note"])}</p>' if p.get("note") else ""
        # Signature lines for a handover or acceptance document, where the
        # point is not only that the terms were stated but that they were
        # received.
        signoff = ""
        if p.get("signoff"):
            cols = "".join(
                f'<div class="sign__col"><div class="sign__rule"></div>'
                f'<div class="sign__label">{esc(c)}</div></div>'
                for c in p["signoff"]
            )
            signoff = f'<div class="sign">{cols}</div>'
        return f"""
      <div class="well">
        <div class="eyebrow">{esc(p.get("eyebrow", ""))}</div>
        <h1>{esc(p.get("title", ""))}</h1>
        <div class="rule"></div>
        {intro}
        <table class="table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>
        {note}
        {signoff}
      </div>"""

    def gallery(self, p: dict) -> str:
        cols = int(p.get("columns", 2))
        figs = []
        for im in p.get("images", []):
            cap = f'<figcaption class="caption">{esc(im["caption"])}</figcaption>' if im.get("caption") else ""
            figs.append(
                f'<figure><div class="frame">{self.image(im.get("src"), "", im.get("caption", ""))}</div>{cap}</figure>'
            )
        return f"""
      <div class="well">
        <div class="eyebrow">{esc(p.get("eyebrow", ""))}</div>
        <h1>{esc(p.get("title", ""))}</h1>
        <div class="rule"></div>
        <div class="gallery gallery--{cols}">{"".join(figs)}</div>
      </div>"""

    def text(self, p: dict) -> str:
        img = self.image(p["image"], "text__image", p.get("title", "")) if p.get("image") else ""
        panel = f'<div class="panel"><p>{esc(p["panel"])}</p></div>' if p.get("panel") else ""
        body = "".join(f"<p>{esc(par)}</p>" for par in p.get("body", []))
        cls = "prose--2" if int(p.get("columns", 1)) == 2 else ""
        return f"""
      <div class="well">
        <div class="eyebrow">{esc(p.get("eyebrow", ""))}</div>
        <h1>{esc(p.get("title", ""))}</h1>
        <div class="rule"></div>
        {img}{panel}
        <div class="{cls} grow">{body}</div>
      </div>"""

    def back(self, p: dict) -> str:
        lines = "".join(f"<div>{line}</div>" for line in p.get("contact", []))
        return f"""
      <div class="back">
        <div>
          <div class="rule"></div>
          <h1 class="back__headline">{esc_lines(p.get("headline", ""))}</h1>
        </div>
        <div class="back__contact">{lines}</div>
        <div class="back__note">{esc(p.get("note", ""))}</div>
      </div>"""

    # ------------------------------------------------------------- assembly

    def render(self) -> str:
        pages = self.config.get("pages", [])

        # Page numbers: cover and back cover are unnumbered by convention, so the
        # printed folio matches what a reader would count.
        numbers: list[int | None] = []
        counter = 0
        for p in pages:
            if p.get("type") in ("cover", "back") or p.get("folio") is False:
                numbers.append(None)
            else:
                counter += 1
                numbers.append(counter)

        # Auto contents: every section opener becomes an entry with its folio.
        entries = [
            {
                "label": p.get("title", ""),
                "subtitle": p.get("subtitle", "") if p.get("type") == "section" else "",
                "page": n,
                "level": 0 if p.get("type") == "section" else 1,
            }
            for p, n in zip(pages, numbers)
            if p.get("type") == "section" or p.get("toc")
        ]

        rendered = []
        for p, n in zip(pages, numbers):
            kind = p.get("type", "text")
            dark = p.get("dark", kind in ("cover", "section", "back"))
            classes = "page" + (" page--dark" if dark else "")
            if p.get("class"):
                classes += " " + p["class"]

            if kind == "cover":
                inner = self.cover(p)
            elif kind == "contents":
                inner = self.contents(p, entries)
            elif kind == "section":
                inner = self.section(p)
            elif kind == "feature":
                inner = self.feature(p)
            elif kind == "grid":
                inner = self.grid(p)
            elif kind == "spec":
                inner = self.spec(p)
            elif kind == "gallery":
                inner = self.gallery(p)
            elif kind == "back":
                inner = self.back(p)
            elif kind == "html":
                inner = p.get("html", "")
            else:
                inner = self.text(p)

            rendered.append(f'<section class="{classes}">{inner}{self.folio(p, n)}</section>')

        css = (Path(__file__).resolve().parent.parent / "assets" / "catalogue.css").read_text()
        tokens = "\n".join(f"      --{k}: {v};" for k, v in self.brand.items())

        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(self.doc_title)}</title>
<style>
{css}
:root {{
{tokens}
}}
{self.config.get("extra_css", "")}
</style>
</head>
<body>
{"".join(rendered)}
</body>
</html>"""


# ------------------------------------------------------------------ chromium


def find_chrome() -> str | None:
    for candidate in CHROME_CANDIDATES:
        if candidate.startswith("/") and Path(candidate).exists():
            return candidate
        found = shutil.which(candidate)
        if found:
            return found
    return None


def run_chrome(chrome: str, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", *args],
        capture_output=True, text=True,
    )


# A4 at 96 dpi, the CSS reference resolution Chromium renders mm against.
A4_PX = (794, 1123)


def viewport_offset(chrome: str, work_dir: Path) -> tuple[int, int]:
    """How much bigger --window-size must be than the viewport you actually want.

    Headless Chromium counts window furniture in --window-size, so asking for
    1123 gives a viewport of about 1036 and the bottom of every page is cropped.
    The gap varies by version, so measure it instead of hardcoding it."""
    probe = work_dir / "_probe.html"
    probe.write_text(
        "<html><body><script>document.title=innerWidth+'x'+innerHeight;</script></body></html>"
    )
    result = run_chrome(chrome, [
        "--window-size=800,1000", "--virtual-time-budget=800", "--dump-dom", probe.as_uri(),
    ])
    probe.unlink(missing_ok=True)
    import re as _re
    found = _re.search(r"<title>(\d+)x(\d+)</title>", result.stdout or "")
    if not found:
        return (0, 87)  # observed default; better than cropping if the probe fails
    return (800 - int(found.group(1)), 1000 - int(found.group(2)))


def crop_png_height(path: Path, keep_rows: int) -> None:
    """Trim a PNG to its first `keep_rows` scanlines, in place.

    Chromium's screenshot canvas is the window size while the viewport is ~87px
    shorter, so every capture carries a white strip along the bottom. On a dark
    page that strip reads as a design defect and sends you hunting for a bug
    that isn't there. Cropping is safe without a decoder library: PNG row
    filters only ever reference the row above, so dropping trailing rows leaves
    the remaining ones intact."""
    import struct
    import zlib

    raw = path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        return

    pos, chunks, idat = 8, [], bytearray()
    while pos < len(raw):
        (length,) = struct.unpack(">I", raw[pos:pos + 4])
        kind = raw[pos + 4:pos + 8]
        data = raw[pos + 8:pos + 8 + length]
        if kind == b"IDAT":
            idat += data
        else:
            chunks.append((kind, data))
        pos += 12 + length

    header = next((d for k, d in chunks if k == b"IHDR"), None)
    if header is None:
        return
    width, height, depth, colour = struct.unpack(">IIBB", header[:10])
    if depth != 8 or height <= keep_rows:
        return

    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(colour)
    if channels is None:
        return

    stride = width * channels + 1
    pixels = zlib.decompress(bytes(idat))[: stride * keep_rows]

    out = bytearray(b"\x89PNG\r\n\x1a\n")

    def put(kind: bytes, data: bytes) -> None:
        out.extend(struct.pack(">I", len(data)) + kind + data
                   + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))

    for kind, data in chunks:
        if kind == b"IHDR":
            put(kind, struct.pack(">II", width, keep_rows) + header[8:])
            put(b"IDAT", zlib.compress(pixels, 6))
        elif kind != b"IEND":
            put(kind, data)
    put(b"IEND", b"")
    path.write_bytes(bytes(out))


def render_pdf(chrome: str, html_path: Path, pdf_path: Path) -> bool:
    return run_chrome(chrome, [
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        html_path.as_uri(),
    ]).returncode == 0


def render_previews(chrome: str, html_path: Path, out_dir: Path, page_count: int, scale: int) -> list[Path]:
    """One PNG per page, by hiding the others. Slower than a PDF rasteriser but
    depends on nothing beyond the browser already being here."""
    out_dir.mkdir(parents=True, exist_ok=True)
    off_w, off_h = viewport_offset(chrome, html_path.parent)
    win_w = A4_PX[0] * scale + off_w
    win_h = A4_PX[1] * scale + off_h

    source = html_path.read_text()
    shots: list[Path] = []
    for i in range(page_count):
        isolate = (
            f"<style>.page{{display:none!important}}"
            f".page:nth-of-type({i + 1}){{display:block!important}}</style>"
        )
        temp = html_path.with_name(f"_preview_{i:02d}.html")
        temp.write_text(source.replace("</head>", isolate + "</head>"))
        shot = out_dir / f"page-{i + 1:02d}.png"
        run_chrome(chrome, [
            f"--window-size={win_w},{win_h}",
            f"--force-device-scale-factor={scale}",
            f"--screenshot={shot}",
            temp.as_uri(),
        ])
        temp.unlink(missing_ok=True)
        if shot.exists():
            crop_png_height(shot, A4_PX[1] * scale)
            shots.append(shot)
    return shots


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a print-ready catalogue from JSON.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--no-preview", action="store_true", help="skip the page PNGs")
    parser.add_argument("--scale", type=int, default=1, help="preview scale factor (2 = retina)")
    args = parser.parse_args()

    if not args.config.exists():
        print(f"config not found: {args.config}", file=sys.stderr)
        return 1

    config = json.loads(args.config.read_text())
    builder = Builder(config, args.config.resolve().parent)

    # Absolute throughout: Chromium is handed file:// URIs, which relative paths
    # cannot express.
    args.outdir = args.outdir.resolve()
    args.outdir.mkdir(parents=True, exist_ok=True)
    html_path = args.outdir / "catalogue.html"
    html_path.write_text(builder.render())

    page_count = len(config.get("pages", []))
    print(f"{page_count} pages → {html_path}")

    if builder.missing_images:
        print("\n  Missing images (rendered as pink placeholders — fix before delivering):")
        for src in dict.fromkeys(builder.missing_images):
            print(f"    - {src}")
        print()

    chrome = find_chrome()
    if not chrome:
        print("No Chromium found — HTML written, but no PDF. Open it in a browser and "
              "print to PDF at A4 with margins set to none.", file=sys.stderr)
        return 0

    pdf_path = args.outdir / "catalogue.pdf"
    if render_pdf(chrome, html_path, pdf_path):
        print(f"PDF  → {pdf_path}")
    else:
        print("PDF render failed", file=sys.stderr)

    if not args.no_preview:
        shots = render_previews(chrome, html_path, args.outdir / "preview", page_count, args.scale)
        print(f"PNG  → {args.outdir / 'preview'} ({len(shots)} pages)")
        print("\nLook at every page before you deliver it. That is the point of the previews.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
