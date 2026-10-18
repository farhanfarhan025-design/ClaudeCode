#!/usr/bin/env python3
"""Paint a yellow highlight over chosen lines of a rendered house-format PDF.

    python3 highlight.py in.pdf out.pdf "WARRANTY" ["second phrase" ...]

Each phrase is matched on the page, and every text line it falls in is filled.
The fill is painted UNDER the text as page content, not added as an annotation:
an annotation can be hidden, stripped or dropped when a client prints or
forwards the file, and a highlight that disappears on the copy the client reads
is worse than none. Keep the unhighlighted PDF as well; the highlighted one is
the copy that leaves the office.
"""
import sys
import pymupdf

YELLOW = (1, 0.91, 0.20)


def highlight(src, dst, phrases):
    d = pymupdf.open(src)
    painted = 0
    for page in d:
        bands = []
        for phrase in phrases:
            for hit in page.search_for(phrase):
                # Take the whole line the phrase sits in, not just the words matched.
                for block in page.get_text("dict")["blocks"]:
                    for line in block.get("lines", []):
                        b = line["bbox"]
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
    out, n = highlight(sys.argv[1], sys.argv[2], sys.argv[3:])
    print("highlighted %d line(s) -> %s" % (n, out))
