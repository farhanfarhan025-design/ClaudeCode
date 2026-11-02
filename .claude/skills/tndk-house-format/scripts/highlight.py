#!/usr/bin/env python3
"""Paint a yellow highlight over chosen lines of a rendered house-format PDF.

    python3 highlight.py in.pdf out.pdf "WARRANTY" ["second phrase" ...]
    python3 highlight.py in.pdf out.pdf --block "3. COMPRESSOR" "4. WHAT"

Each phrase is matched on the page, and every text line it falls in is filled.
With --block, two phrases are given and everything from the line holding the
first up to (not including) the line holding the second is filled — which is how
a whole numbered note gets marked, since a note wraps over several lines and only
its first carries the heading.
The fill is painted UNDER the text as page content, not added as an annotation:
an annotation can be hidden, stripped or dropped when a client prints or
forwards the file, and a highlight that disappears on the copy the client reads
is worse than none. Keep the unhighlighted PDF as well; the highlighted one is
the copy that leaves the office.
"""
import sys
import pymupdf

YELLOW = (1, 0.91, 0.20)


def _lines(page):
    out = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(s["text"] for s in line["spans"]).strip()
            if text:
                out.append((line["bbox"], text))
    out.sort(key=lambda r: r[0][1])
    return out


def highlight(src, dst, phrases, block=False):
    d = pymupdf.open(src)
    painted = 0
    for page in d:
        bands = []
        if block:
            # Everything from the line holding the first phrase up to the line
            # holding the second: a note wraps, and only its first line is named.
            rows = _lines(page)
            start = next((i for i, (_, t) in enumerate(rows) if phrases[0] in t), None)
            if start is None:
                continue
            end = next((i for i, (_, t) in enumerate(rows)
                        if i > start and phrases[1] in t), len(rows))
            bands = [b for b, _ in rows[start:end]]
        else:
            for phrase in phrases:
                for hit in page.search_for(phrase):
                    # Take the whole line the phrase sits in, not just the words matched.
                    for b, _ in _lines(page):
                        if b[1] - 1 <= hit.y0 and hit.y1 <= b[3] + 1:
                            bands.append(b)
        if not bands:
            continue
        seen, uniq = set(), []
        for b in sorted(bands, key=lambda r: r[1]):
            key = (round(b[1], 1), round(b[3], 1))
            if key not in seen:
                seen.add(key)
                uniq.append(b)
        shape = page.new_shape()
        for b in uniq:
            shape.draw_rect(pymupdf.Rect(b[0] - 2, b[1] - 0.8, b[2] + 2, b[3] + 0.5))
        shape.finish(color=None, fill=YELLOW)
        shape.commit(overlay=False)
        painted += len(uniq)
    if not painted:
        raise SystemExit("none of %r found" % (phrases,))
    d.save(dst, garbage=4, deflate=True)
    return dst, painted


if __name__ == "__main__":
    args = sys.argv[1:]
    block = "--block" in args
    if block:
        args.remove("--block")
    out, n = highlight(args[0], args[1], args[2:], block=block)
    print("highlighted %d line(s) -> %s" % (n, out))
