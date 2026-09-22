"""Generate CSR-001 cold storage room layout drawing (Rev B) as an A3 PDF.

Rev B changes vs Rev A:
  * Chiller and freezer evaporators moved to the right-hand wall as you
    enter each room, blowing towards the left-hand wall.
  * Freezer door (Door 2) now opens outward, i.e. swings into the chiller.
  * Door 1 swing drawn outward into the corridor to match its note.

Run:  python3 make_drawing.py   ->  CSR-001_Rev-B_Plan-Elevations.pdf
"""
import math
import os

from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "CSR-001_Rev-B_Plan-Elevations.pdf")

PW, PH = landscape(A3)          # points
BLACK = (0, 0, 0)
GREY = (0.45, 0.45, 0.45)
BLUE = (0.05, 0.35, 0.75)

# ---- building data (metres) -------------------------------------------
L_TOT, W_TOT, H = 4.75, 2.55, 2.40
L_CH = 2.75                      # chiller length (partition centreline)
T = 0.10                         # panel thickness
DOOR_W, DOOR_H = 0.90, 1.90
DOOR_Y0, DOOR_Y1 = 1.25, 2.15    # door opening measured from right-hand (bottom) wall
EVAP_CH = (0.85, 1.95)           # chiller evaporator x-extent
EVAP_FZ = (3.225, 4.225)         # freezer evaporator x-extent
EVAP_D, EVAP_HT, EVAP_TOP = 0.40, 0.40, 2.30


# ---- low level helpers -------------------------------------------------
def setc(c, rgb):
    c.setStrokeColorRGB(*rgb)
    c.setFillColorRGB(*rgb)


def text(c, x, y, s, size=8, font="Helvetica", align="c", rgb=BLACK):
    setc(c, rgb)
    c.setFont(font, size)
    {"c": c.drawCentredString, "l": c.drawString,
     "r": c.drawRightString}[align](x, y, s)


def hatch(c, rects, holes=(), spacing=1.4 * mm, lw=0.3):
    """Diagonal hatch inside `rects` minus `holes` (page-unit x,y,w,h)."""
    c.saveState()
    p = c.beginPath()
    for (x, y, w, h) in list(rects) + list(holes):
        p.rect(x, y, w, h)
    c.clipPath(p, stroke=0, fill=0, fillMode=0)   # even-odd
    xs = [r[0] for r in rects] + [r[0] + r[2] for r in rects]
    ys = [r[1] for r in rects] + [r[1] + r[3] for r in rects]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    c.setLineWidth(lw)
    setc(c, BLACK)
    d = -(y1 - y0)
    while d < (x1 - x0):
        c.line(x0 + d, y0, x0 + d + (y1 - y0), y1)
        d += spacing
    c.restoreState()


def arrow(c, x1, y1, x2, y2, head=2.2 * mm, lw=0.6, rgb=BLACK, dash=None):
    setc(c, rgb)
    c.setLineWidth(lw)
    if dash:
        c.setDash(*dash)
    c.line(x1, y1, x2, y2)
    c.setDash()
    a = math.atan2(y2 - y1, x2 - x1)
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(x2 - head * math.cos(a - 0.4), y2 - head * math.sin(a - 0.4))
    p.lineTo(x2 - head * math.cos(a + 0.4), y2 - head * math.sin(a + 0.4))
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def tick(c, x, y):
    c.setLineWidth(0.9)
    c.line(x - 1.1 * mm, y - 1.1 * mm, x + 1.1 * mm, y + 1.1 * mm)


def dim_h(c, x1, x2, y, label, ext_from=None, size=9):
    setc(c, BLACK)
    c.setLineWidth(0.35)
    c.line(x1 - 2 * mm, y, x2 + 2 * mm, y)
    if ext_from is not None:
        c.line(x1, ext_from, x1, y + 1.5 * mm)
        c.line(x2, ext_from, x2, y + 1.5 * mm)
    tick(c, x1, y)
    tick(c, x2, y)
    text(c, (x1 + x2) / 2, y + 1.4 * mm, label, size, "Helvetica-Bold")


def dim_v(c, x, y1, y2, label, ext_from=None, size=9):
    setc(c, BLACK)
    c.setLineWidth(0.35)
    c.line(x, y1 - 2 * mm, x, y2 + 2 * mm)
    if ext_from is not None:
        c.line(ext_from, y1, x + 1.5 * mm, y1)
        c.line(ext_from, y2, x + 1.5 * mm, y2)
    tick(c, x, y1)
    tick(c, x, y2)
    c.saveState()
    c.translate(x + 1.6 * mm, (y1 + y2) / 2)
    c.rotate(90)
    text(c, 0, -3.2 * mm, label, size, "Helvetica-Bold")
    c.restoreState()


def fan(c, cx, cy, r):
    c.setLineWidth(0.6)
    c.circle(cx, cy, r, stroke=1, fill=0)
    c.circle(cx, cy, r * 0.18, stroke=1, fill=0)
    for k in range(6):
        a = math.radians(k * 60 + 15)
        c.line(cx + r * 0.18 * math.cos(a), cy + r * 0.18 * math.sin(a),
               cx + r * 0.9 * math.cos(a), cy + r * 0.9 * math.sin(a))


def title(c, x, y, s1, s2):
    text(c, x, y, s1, 11, "Helvetica-Bold")
    w = c.stringWidth(s1, "Helvetica-Bold", 11)
    c.setLineWidth(0.8)
    c.line(x - w / 2, y - 1.3 * mm, x + w / 2, y - 1.3 * mm)
    text(c, x, y - 5.5 * mm, s2, 8.5)


def ground(c, x1, x2, y):
    setc(c, BLACK)
    c.setLineWidth(1.0)
    c.line(x1, y, x2, y)
    c.setLineWidth(0.35)
    k = x1
    while k < x2:
        c.line(k, y, k - 1.6 * mm, y - 1.6 * mm)
        k += 2.2 * mm


# ---- plan view --------------------------------------------------------
def plan(c):
    S = 40 * mm                      # 1 m on paper  -> 1:25 on A3
    X0, Y0 = 82 * mm, 160 * mm

    def P(x, y):
        return X0 + x * S, Y0 + y * S

    # walls: outer box minus inner rooms, openings cut afterwards
    ox, oy = P(0, 0)
    rooms = [(T, T, L_CH - T / 2 - T, W_TOT - 2 * T),
             (L_CH + T / 2, T, L_TOT - T - (L_CH + T / 2), W_TOT - 2 * T)]
    holes = [(P(x, y)[0], P(x, y)[1], w * S, h * S) for x, y, w, h in rooms]
    # door openings are holes in the wall too
    holes.append((P(0, DOOR_Y0)[0], P(0, DOOR_Y0)[1], T * S, DOOR_W * S))
    holes.append((P(L_CH - T / 2, DOOR_Y0)[0], P(0, DOOR_Y0)[1],
                  T * S, DOOR_W * S))
    hatch(c, [(ox, oy, L_TOT * S, W_TOT * S)], holes)

    setc(c, BLACK)
    c.setLineWidth(1.1)
    # outer outline (with door 1 gap)
    p = c.beginPath()
    p.moveTo(*P(0, DOOR_Y0))
    p.lineTo(*P(0, 0))
    p.lineTo(*P(L_TOT, 0))
    p.lineTo(*P(L_TOT, W_TOT))
    p.lineTo(*P(0, W_TOT))
    p.lineTo(*P(0, DOOR_Y1))
    c.drawPath(p, stroke=1, fill=0)
    # chiller inner outline (door 1 and door 2 gaps)
    x_a, x_b = T, L_CH - T / 2
    p = c.beginPath()
    p.moveTo(*P(x_a, DOOR_Y0)); p.lineTo(*P(x_a, T)); p.lineTo(*P(x_b, T))
    p.lineTo(*P(x_b, DOOR_Y0))
    p.moveTo(*P(x_b, DOOR_Y1)); p.lineTo(*P(x_b, W_TOT - T))
    p.lineTo(*P(x_a, W_TOT - T)); p.lineTo(*P(x_a, DOOR_Y1))
    c.drawPath(p, stroke=1, fill=0)
    # freezer inner outline (door 2 gap)
    x_a, x_b = L_CH + T / 2, L_TOT - T
    p = c.beginPath()
    p.moveTo(*P(x_a, DOOR_Y0)); p.lineTo(*P(x_a, T)); p.lineTo(*P(x_b, T))
    p.lineTo(*P(x_b, W_TOT - T)); p.lineTo(*P(x_a, W_TOT - T))
    p.lineTo(*P(x_a, DOOR_Y1))
    c.drawPath(p, stroke=1, fill=0)
    # jamb lines
    c.setLineWidth(1.1)
    for xj in (0, L_CH - T / 2):
        for yj in (DOOR_Y0, DOOR_Y1):
            c.line(*P(xj, yj), *P(xj + T, yj))

    # doors: hinge on the jamb nearer the left-hand wall, leaf swings
    # away from the room it serves (outward).
    def door(hx, label_pos, label):
        # hx = x of the face the door is hung on (swing goes to -x side)
        c.setLineWidth(0.9)
        lx, ly = P(hx - DOOR_W, DOOR_Y1)
        c.rect(lx, ly - 0.035 * S, DOOR_W * S, 0.035 * S, stroke=1, fill=0)
        c.setLineWidth(0.5)
        c.setDash(3, 1.5)
        cx, cy = P(hx, DOOR_Y1)
        r = DOOR_W * S
        c.arc(cx - r, cy - r, cx + r, cy + r, 180, 90)
        c.setDash()
        # hinge dot
        c.circle(cx, cy, 0.6 * mm, stroke=0, fill=1)
        tx, ty = label_pos
        for i, (s, f, sz) in enumerate(label):
            text(c, tx, ty - i * 3.6 * mm, s, sz, f, "l")

    door(0, P(-1.45, 1.05), [("DOOR 1", "Helvetica-Bold", 8.5),
                              ("900 x 1900 mm", "Helvetica", 8),
                              ("OPENS OUTWARD", "Helvetica", 8),
                              ("(INTO CORRIDOR)", "Helvetica", 8)])
    door(L_CH - T / 2, P(1.62, 1.10), [])
    for i, (s_, f_) in enumerate((("DOOR 2 (FREEZER)", "Helvetica-Bold"),
                                  ("900 x 1900 mm", "Helvetica"),
                                  ("OPENS OUTWARD", "Helvetica"),
                                  ("(INTO CHILLER)", "Helvetica"))):
        text(c, *P(2.26, 1.12 - i * 0.13), s_, 8 if i else 8.5, f_, "c")

    # evaporators on the right-hand wall (bottom of plan), blowing across
    def evap(x1, x2, name):
        y1, y2 = T, T + EVAP_D
        ax, ay = P(x1, y1)
        c.setLineWidth(1.0)
        setc(c, BLACK)
        c.setFillColorRGB(1, 1, 1)
        c.rect(ax, ay, (x2 - x1) * S, EVAP_D * S, stroke=1, fill=1)
        # coil hatch strip on the back, fans on the front
        c.setLineWidth(0.3)
        for k in range(1, int((x2 - x1) / 0.05)):
            xx = P(x1 + k * 0.05, 0)[0]
            c.line(xx, ay, xx, ay + 0.10 * S)
        c.setLineWidth(0.6)
        c.line(ax, ay + 0.10 * S, ax + (x2 - x1) * S, ay + 0.10 * S)
        n = 2
        for i in range(n):
            fx = x1 + (x2 - x1) * (i + 0.5) / n
            fcx, fcy = P(fx, y1 + 0.25)
            setc(c, BLACK)
            fan(c, fcx, fcy, 0.13 * S)
            arrow(c, *P(fx, y2 + 0.02), *P(fx, y2 + 0.55), rgb=BLUE,
                  lw=0.8, dash=(2.5, 1.5))
        setc(c, BLACK)
        text(c, *P((x1 + x2) / 2, y2 + 0.66), "AIR THROW", 7, "Helvetica",
             rgb=BLUE)
        return name

    evap(*EVAP_CH, "CH")
    evap(*EVAP_FZ, "FZ")
    # evaporator leaders (below the plan, outside the building)
    for (x1, x2), nm in ((EVAP_CH, "CHILLER EVAPORATOR"),
                         (EVAP_FZ, "FREEZER EVAPORATOR")):
        mx = (x1 + x2) / 2
        setc(c, BLACK)
        c.setLineWidth(0.45)
        tx, ty = P(mx, -0.42)
        arrow(c, tx, ty + 3 * mm, *P(mx, 0.14), head=1.8 * mm, lw=0.45)
        text(c, tx, ty, nm, 8.5, "Helvetica-Bold")
        text(c, tx, ty - 3.5 * mm, "ON RIGHT-HAND WALL AS YOU ENTER", 7)

    # room labels
    for cx, nm, dims in ((1.30, "CHILLER", "2.75 m x 2.55 m"),
                         (3.725, "FREEZER", "2.00 m x 2.55 m")):
        x, y = P(cx, 1.62)
        text(c, x, y + 5 * mm, nm, 14, "Helvetica-Bold")
        text(c, x, y, dims, 11)
        text(c, x, y - 4.8 * mm, "H = 2.40 m", 11)

    # entry arrow + corridor label
    text(c, *P(-1.35, 2.25), "NOORA", 14, "Helvetica-Bold")
    text(c, *P(-1.35, 2.06), "(ACCESS SIDE /", 9)
    text(c, *P(-1.35, 1.93), "CORRIDOR)", 9)
    arrow(c, *P(-1.70, 1.72), *P(-1.05, 1.72), head=3 * mm, lw=2.2)
    text(c, *P(-1.42, 1.53), "ENTRY", 8, "Helvetica-Bold")

    # section markers
    def sec_mark(x, y, lbl, ang):
        r = 3.2 * mm
        c.setLineWidth(0.6)
        setc(c, BLACK)
        c.setFillColorRGB(1, 1, 1)
        c.circle(x, y, r, stroke=1, fill=1)
        setc(c, BLACK)
        # pointer triangle showing view direction
        a = math.radians(ang)
        p = c.beginPath()
        p.moveTo(x + (r + 2.4 * mm) * math.cos(a), y + (r + 2.4 * mm) * math.sin(a))
        p.lineTo(x + r * math.cos(a + 0.9), y + r * math.sin(a + 0.9))
        p.lineTo(x + r * math.cos(a - 0.9), y + r * math.sin(a - 0.9))
        p.close()
        c.drawPath(p, stroke=0, fill=1)
        text(c, x, y - 1.1 * mm, lbl, 8.5, "Helvetica-Bold")

    # A-A: horizontal cut, looking at the right-hand (evaporator) wall
    ya = 0.62
    c.setLineWidth(0.4)
    setc(c, GREY)
    c.setDash([8, 2, 1.5, 2])
    c.line(*P(-0.25, ya), *P(L_TOT + 0.25, ya))
    c.setDash()
    sec_mark(*P(-0.40, ya), "A", -90)
    sec_mark(*P(L_TOT + 0.40, ya), "A", -90)
    # B-B: vertical cut in the chiller, looking towards the freezer
    xb = 0.40
    setc(c, GREY)
    c.setLineWidth(0.4)
    c.setDash([8, 2, 1.5, 2])
    c.line(*P(xb, -0.20), *P(xb, W_TOT + 0.04))
    c.setDash()
    sec_mark(*P(xb, W_TOT + 0.12), "B", 0)
    sec_mark(*P(xb, -0.30), "B", 0)

    # dimensions
    top = W_TOT * S + Y0
    dim_h(c, *[P(0, 0)[0], P(L_CH, 0)[0]], top + 11 * mm, "2.75 m", top + 1 * mm)
    dim_h(c, P(L_CH, 0)[0], P(L_TOT, 0)[0], top + 11 * mm, "2.00 m", top + 1 * mm)
    dim_h(c, P(0, 0)[0], P(L_TOT, 0)[0], top + 20 * mm, "4.75 m", top + 1 * mm)
    rx = P(L_TOT, 0)[0]
    dim_v(c, rx + 16 * mm, P(0, 0)[1], P(0, W_TOT)[1], "2.55 m", rx + 1 * mm)

    title(c, P(L_TOT / 2, 0)[0], Y0 - 22 * mm, "PLAN VIEW", "SCALE 1:25 (NTS)")


# ---- elevations / sections -------------------------------------------
E = 25 * mm                         # 1 m on paper -> 1:40 on A3
GY = 66 * mm                        # ground line


def shell(c, x0, width, cut=True, parts=(), dim_left=False):
    """Outline of a box elevation/section `width` m wide from page x0."""
    top = GY + H * E
    setc(c, BLACK)
    if cut:
        # walls, roof and floor cut: hatched bands
        bands = [(x0, GY, T * E, H * E), (x0 + (width - T) * E, GY, T * E, H * E),
                 (x0, top - T * E, width * E, T * E)]
        for px in parts:
            bands.append((x0 + (px - T / 2) * E, GY, T * E, H * E - T * E))
        for b in bands:
            hatch(c, [b], spacing=1.1 * mm, lw=0.25)
            c.setLineWidth(0.9)
            c.rect(*b, stroke=1, fill=0)
    else:
        c.setLineWidth(1.0)
        c.rect(x0, GY, width * E, H * E, stroke=1, fill=0)
        # panel joints
        c.setLineWidth(0.25)
        setc(c, GREY)
        k = 0.30
        while k < width - 0.05:
            c.line(x0 + k * E, GY, x0 + k * E, GY + H * E)
            k += 0.30
        setc(c, BLACK)
        # roof flashing
        c.setLineWidth(0.8)
        c.rect(x0 - 1.5 * mm, GY + H * E, width * E + 3 * mm, 1.5 * mm,
               stroke=1, fill=0)
    ground(c, x0 - 6 * mm, x0 + width * E + 6 * mm, GY)
    # height dimension
    if dim_left:
        dim_v(c, x0 - 14 * mm, GY, top, "2.40 m", x0 - 1 * mm, size=8.5)
    else:
        dim_v(c, x0 + width * E + 10 * mm, GY, top, "2.40 m",
              x0 + width * E + 1 * mm, size=8.5)


def door_elev(c, x_left, hinge_left, label_lines, dashed_swing=True):
    setc(c, BLACK)
    w, h = DOOR_W * E, DOOR_H * E
    c.setLineWidth(1.0)
    c.setFillColorRGB(1, 1, 1)
    c.rect(x_left, GY, w, h, stroke=1, fill=1)
    setc(c, BLACK)
    c.setLineWidth(0.5)
    c.rect(x_left + 1.2 * mm, GY, w - 2.4 * mm, h - 1.2 * mm, stroke=1, fill=0)
    # swing lines: apex on hinge side
    c.setDash(2.5, 1.5)
    hx = x_left if hinge_left else x_left + w
    fx = x_left + w if hinge_left else x_left
    c.line(fx, GY + h, hx, GY + h / 2)
    c.line(fx, GY, hx, GY + h / 2)
    c.setDash()
    # handle on the free side
    c.setLineWidth(1.2)
    hdx = fx - 2.2 * mm if hinge_left else fx + 2.2 * mm
    c.line(hdx, GY + 0.95 * E, hdx, GY + 1.20 * E)
    # hinges
    for yy in (0.25, 1.0, 1.65):
        c.rect(hx - 0.6 * mm, GY + yy * E, 1.2 * mm, 2.5 * mm, stroke=1, fill=1)
    for i, s in enumerate(label_lines):
        text(c, x_left + w + 3 * mm, GY + 1.05 * E - i * 3.4 * mm, s,
             8 if i == 0 else 7.5, "Helvetica-Bold" if i == 0 else "Helvetica", "l")


def evap_face(c, x1, x2, label):
    """Evaporator seen face-on (fans towards viewer)."""
    y2 = GY + EVAP_TOP * E
    y1 = y2 - EVAP_HT * E
    setc(c, BLACK)
    c.setLineWidth(1.0)
    c.setFillColorRGB(1, 1, 1)
    c.rect(x1, y1, x2 - x1, y2 - y1, stroke=1, fill=1)
    setc(c, BLACK)
    for i in range(2):
        fx = x1 + (x2 - x1) * (i + 0.5) / 2
        fan(c, fx, (y1 + y2) / 2, 0.15 * E)
    # drain pan / drain line
    c.setLineWidth(0.5)
    c.line(x1 + 1 * mm, y1 - 1 * mm, x2 - 1 * mm, y1 - 1 * mm)
    c.setDash(2, 1.2)
    c.line(x2 - 3 * mm, y1 - 1 * mm, x2 - 3 * mm, y1 - 7 * mm)
    c.setDash()
    text(c, (x1 + x2) / 2, y1 - 11 * mm, label, 8, "Helvetica-Bold")


def evap_side(c, x_wall, label):
    """Evaporator side profile on a wall at the right of the view, blowing left."""
    y2 = GY + EVAP_TOP * E
    y1 = y2 - EVAP_HT * E
    x1 = x_wall - EVAP_D * E
    setc(c, BLACK)
    c.setLineWidth(1.0)
    c.setFillColorRGB(1, 1, 1)
    c.rect(x1, y1, EVAP_D * E, y2 - y1, stroke=1, fill=1)
    setc(c, BLACK)
    c.setLineWidth(0.3)
    k = x_wall - 0.03 * E
    while k > x_wall - 0.13 * E:
        c.line(k, y1, k, y2)
        k -= 0.8 * mm
    # fan guard on the front face (left)
    c.setLineWidth(1.4)
    c.line(x1, y1 + 1 * mm, x1, y2 - 1 * mm)
    # bracket to wall / ceiling
    c.setLineWidth(0.8)
    c.line(x1 + 1.5 * mm, y2, x1 + 1.5 * mm, GY + (H - T) * E)
    c.line(x_wall - 1.5 * mm, y2, x_wall - 1.5 * mm, GY + (H - T) * E)
    # airflow towards left-hand wall
    for dy in (0.3, 0.7):
        yy = y1 + (y2 - y1) * dy
        arrow(c, x1 - 1 * mm, yy, x1 - 0.95 * E, yy - 0.5 * mm, rgb=BLUE,
              lw=0.8, dash=(2.5, 1.5))
    # labels outside the section on the right, with a leader
    lx = x_wall + 0.10 * E + 5 * mm
    setc(c, BLACK)
    c.setLineWidth(0.45)
    arrow(c, lx - 1 * mm, y1 - 6 * mm, x1 + EVAP_D * E * 0.6, y1 + 1 * mm,
          head=1.8 * mm, lw=0.45)
    for i, s in enumerate(label):
        text(c, lx, y1 - 7 * mm - i * 3.4 * mm, s,
             8 if i == 0 else 7, "Helvetica-Bold" if i == 0 else "Helvetica", "l")
    yy = y1 - 7 * mm - len(label) * 3.4 * mm - 2 * mm
    text(c, lx, yy, "AIR THROW TOWARDS", 7, "Helvetica-Bold", "l", rgb=BLUE)
    text(c, lx, yy - 3.4 * mm, "LEFT-HAND WALL", 7, "Helvetica-Bold", "l", rgb=BLUE)


def elevations(c):
    # 1) Left side elevation (access side) - external wall with Door 1.
    #    Viewed from the corridor: left-hand wall of the room is on the left.
    x0 = 30 * mm
    shell(c, x0, W_TOT, cut=False)
    d_left = x0 + (W_TOT - DOOR_Y1) * E
    door_elev(c, d_left, True,
              ["DOOR 1", "900 x 1900 mm", "OPENS OUTWARD", "(TO CORRIDOR)"])
    title(c, x0 + W_TOT * E / 2, 50 * mm,
          "LEFT SIDE ELEVATION (ACCESS SIDE)", "SCALE 1:40 (NTS)")

    # 2) Section A-A - the right-hand (evaporator) wall seen from inside.
    #    Looking at it from inside, the freezer end is on the left.
    x0 = 130 * mm
    shell(c, x0, L_TOT, cut=True, parts=(L_TOT - L_CH,))
    xfz = lambda m: x0 + (L_TOT - m) * E        # plan x -> this view
    evap_face(c, xfz(EVAP_FZ[1]), xfz(EVAP_FZ[0]), "FREEZER EVAPORATOR")
    evap_face(c, xfz(EVAP_CH[1]), xfz(EVAP_CH[0]), "CHILLER EVAPORATOR")
    text(c, xfz(3.725), GY + 0.85 * E, "FREEZER", 11, "Helvetica-Bold")
    text(c, xfz(1.375), GY + 0.85 * E, "CHILLER", 11, "Helvetica-Bold")
    text(c, xfz(3.725), GY + 0.55 * E, "(RIGHT-HAND WALL)", 7.5)
    text(c, xfz(1.375), GY + 0.55 * E, "(RIGHT-HAND WALL)", 7.5)
    title(c, x0 + L_TOT * E / 2, 50 * mm,
          "SECTION A-A (EVAPORATOR WALL)", "SCALE 1:40 (NTS)")

    # 3) Section B-B - standing in the chiller, looking towards the freezer.
    #    Left-hand wall on the left, right-hand (evaporator) wall on the right.
    x0 = 300 * mm
    shell(c, x0, W_TOT, cut=True, dim_left=True)
    d_left = x0 + (W_TOT - DOOR_Y1) * E
    door_elev(c, d_left, True,
              ["DOOR 2", "(FREEZER)", "900 x 1900 mm", "OPENS OUTWARD", "(INTO CHILLER)"])
    evap_side(c, x0 + (W_TOT - T) * E,
              ["CHILLER EVAPORATOR", "ON RIGHT-HAND WALL", "(FREEZER: SAME", "ARRANGEMENT)"])
    text(c, x0 + 4 * mm, GY + H * E + 3 * mm, "LEFT-HAND WALL", 7, "Helvetica-Bold", "l")
    text(c, x0 + W_TOT * E - 4 * mm, GY + H * E + 3 * mm, "RIGHT-HAND WALL", 7,
         "Helvetica-Bold", "r")
    title(c, x0 + W_TOT * E / 2, 50 * mm,
          "SECTION B-B (VIEW AS YOU ENTER)", "SCALE 1:40 (NTS)")


# ---- notes, legend, title block ---------------------------------------
def notes(c):
    x, y = 300 * mm, 283 * mm
    text(c, x, y, "NOTES:", 11, "Helvetica-Bold", "l")
    c.setLineWidth(0.8)
    c.line(x, y - 1.3 * mm, x + 16 * mm, y - 1.3 * mm)
    items = [
        ["All dimensions are in metres (m)", "unless otherwise specified."],
        ["Internal room sizes are clear", "internal dimensions."],
        ["Walls and partition are sandwich panels."],
        ["Evaporators are wall mounted on the", "RIGHT-HAND wall as you enter each",
         "room, blowing towards the LEFT-HAND", "wall (chiller and freezer)."],
        ["Door sizes: 900 x 1900 mm", "(clear opening)."],
        ["Both doors open OUTWARD. Door 2", "(freezer) swings into the chiller."],
        ["Drawing not to scale (NTS)."],
    ]
    yy = y - 7 * mm
    for i, lines in enumerate(items, 1):
        text(c, x, yy, f"{i}.", 8.5, "Helvetica", "l")
        for ln in lines:
            text(c, x + 5 * mm, yy, ln, 8.5, "Helvetica", "l")
            yy -= 3.8 * mm
        yy -= 1.2 * mm

    yy -= 3 * mm
    text(c, x, yy, "LEGEND:", 11, "Helvetica-Bold", "l")
    c.line(x, yy - 1.3 * mm, x + 17 * mm, yy - 1.3 * mm)
    yy -= 9 * mm
    rows = [("wall", "Sandwich panel wall / partition"),
            ("evap", "Evaporator (fans + coil)"),
            ("air", "Air throw direction"),
            ("door", "Door swing (outward)")]
    for kind, lbl in rows:
        bx = x
        if kind == "wall":
            hatch(c, [(bx, yy, 16 * mm, 4 * mm)], spacing=1.2 * mm)
            c.setLineWidth(0.8)
            c.rect(bx, yy, 16 * mm, 4 * mm)
        elif kind == "evap":
            c.setLineWidth(0.8)
            c.rect(bx, yy - 1 * mm, 16 * mm, 6 * mm)
            fan(c, bx + 4.5 * mm, yy + 2 * mm, 2.2 * mm)
            fan(c, bx + 11.5 * mm, yy + 2 * mm, 2.2 * mm)
        elif kind == "air":
            arrow(c, bx, yy + 2 * mm, bx + 16 * mm, yy + 2 * mm, rgb=BLUE,
                  lw=0.8, dash=(2.5, 1.5))
        else:
            setc(c, BLACK)
            c.setLineWidth(0.5)
            c.setDash(2.5, 1.5)
            c.arc(bx - 10 * mm, yy - 8 * mm, bx + 10 * mm, yy + 12 * mm, 0, 90)
            c.setDash()
            c.line(bx, yy + 2 * mm, bx + 10 * mm, yy + 2 * mm)
            c.setLineWidth(1.2)
            c.line(bx, yy + 2 * mm, bx, yy + 12 * mm)
        text(c, bx + 21 * mm, yy + 0.8 * mm, lbl, 8.5, "Helvetica", "l")
        yy -= 9 * mm

    # revision box
    yy -= 2 * mm
    text(c, x, yy, "REVISIONS:", 11, "Helvetica-Bold", "l")
    c.line(x, yy - 1.3 * mm, x + 22 * mm, yy - 1.3 * mm)
    revs = [("A", "27 APR 2025", ["First issue."]),
            ("B", "22 SEP 2026", ["Evaporators moved to right-hand",
                                   "wall; freezer door opens outward."])]
    yy -= 6 * mm
    for r, d, lines in revs:
        text(c, x, yy, r, 8.5, "Helvetica-Bold", "l")
        text(c, x + 5 * mm, yy, d, 8.5, "Helvetica", "l")
        for ln in lines:
            text(c, x + 28 * mm, yy, ln, 8, "Helvetica", "l")
            yy -= 3.6 * mm
        yy -= 1 * mm


def title_block(c):
    setc(c, BLACK)
    x0, y0, x1, y1 = 10 * mm, 10 * mm, PW - 10 * mm, 38 * mm
    c.setLineWidth(1.2)
    c.rect(x0, y0, x1 - x0, y1 - y0)
    cols = [x0, 200 * mm, 250 * mm, 305 * mm, 360 * mm, x1]
    c.setLineWidth(0.8)
    for cx in cols[1:-1]:
        c.line(cx, y0, cx, y1)
    ym = (y0 + y1) / 2
    c.line(x0, ym, cols[-2], ym)

    def cell(cx, cy, cap, val, vs=11, vf="Helvetica"):
        text(c, cx + 2 * mm, cy + 9.5 * mm, cap, 7, "Helvetica", "l")
        text(c, cx + 2 * mm, cy + 2.2 * mm, val, vs, vf, "l")

    cell(cols[0], ym, "PROJECT:", "COLD STORAGE ROOM LAYOUT", 13, "Helvetica-Bold")
    cell(cols[0], y0, "DRAWING TITLE:", "PLAN, ELEVATION AND SECTIONS", 12)
    cell(cols[1], ym, "PROJECT NO:", "CSR-001")
    cell(cols[1], y0, "SCALE:", "AS NOTED (NTS)")
    cell(cols[2], ym, "DATE:", "22 SEP 2026")
    cell(cols[2], y0, "DRAWN BY:", "---")
    cell(cols[3], ym, "REV:", "B", 12, "Helvetica-Bold")
    cell(cols[3], y0, "CHECKED BY:", "---")
    text(c, cols[4] + 2 * mm, y1 - 4.5 * mm, "SHEET NO:", 7, "Helvetica", "l")
    text(c, (cols[4] + x1) / 2, y0 + 7 * mm, "A1", 26, "Helvetica-Bold")


def main():
    c = canvas.Canvas(OUT, pagesize=(PW, PH))
    c.setTitle("CSR-001 Cold Storage Room Layout - Rev B")
    c.setAuthor("TNDK")
    c.setLineWidth(1.5)
    c.rect(6 * mm, 6 * mm, PW - 12 * mm, PH - 12 * mm)
    plan(c)
    elevations(c)
    notes(c)
    title_block(c)
    c.showPage()
    c.save()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
