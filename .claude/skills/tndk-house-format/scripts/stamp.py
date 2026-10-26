#!/usr/bin/env python3
"""Overlay the company seal and Farhan's signature onto a rendered house-format PDF.

    python3 stamp.py in.pdf out.pdf [anchor_text]

The block is placed on the last page, in the clear space to the left of the
signature panel — the way it lands on the hand-stamped originals. It anchors on
the signatory name, so nothing printed is obscured. Keep the unsigned PDF too.
"""
import os
import sys
import fitz

SEAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "seal_sign.png")
WIDTH = 190.0          # points
ASPECT = 559 / 900     # seal_sign.png


def stamp(src, dst, anchor="Ronaldo"):
    d = fitz.open(src)
    page = d[-1]
    hits = page.search_for(anchor)
    if not hits:
        raise SystemExit("anchor %r not found on the last page" % anchor)
    r = hits[0]
    h = WIDTH * ASPECT
    # Sit the block in the clear space to the left of the signature panel, the way
    # it lands on the hand-stamped originals: nothing printed is obscured.
    x0 = r.x0 - 45 - WIDTH
    y0 = r.y0 - 2
    page.insert_image(fitz.Rect(x0, y0, x0 + WIDTH, y0 + h), filename=SEAL, overlay=True)
    d.save(dst, garbage=4, deflate=True)
    return dst


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    anchor = sys.argv[3] if len(sys.argv) > 3 else "Ronaldo"
    print("stamped ->", stamp(src, dst, anchor))
