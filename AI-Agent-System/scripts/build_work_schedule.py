#!/usr/bin/env python3
"""Build a TNDK construction work schedule (programme) on letterhead.

    python3 build_work_schedule.py --spec schedule.json --outdir out/

A client-facing programme: phased activities with durations, predecessors and
responsibilities, a week-by-week bar chart, the contractual hold points, and
the payment milestones tied to the programme days that trigger them.

The dates are computed here, not typed. Each activity carries a start day and a
duration in working days; the finish is derived. A predecessor that has not
finished before its successor starts fails the build unless the overlap is
declared, because an unstated overlap is the difference between a programme a
client can hold you to and one you cannot meet. Phase spans are derived from
their activities, and the bar chart is drawn from the same numbers as the table
— there is no second copy of the schedule to drift out of step.

Working days, not calendar days: a six-day week (Sat-Thu) with Fridays and
public holidays excluded, per `working_week`.

No tax or VAT wording, per DECISIONS.md D-005 — the build fails if any appears.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

CHROME = ["/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
          "/opt/pw-browsers/chromium/chrome-linux/chrome",
          "chromium", "chromium-browser", "google-chrome"]

TAX_WORDS = re.compile(r"\b(tax|taxes|taxable|vat)\b", re.I)


def esc(v) -> str:
    return html.escape(str(v if v is not None else ""))


def money(v) -> str:
    return f"{v:,.0f}" if float(v) == int(v) else f"{v:,.2f}"


CSS = """
@page { size: A4 portrait; margin: 12mm 11mm 14mm; }
* { box-sizing: border-box; }
body { font-family: 'Calibri','Carlito','Liberation Sans',sans-serif; font-size: 8.4pt;
       line-height: 1.32; color: #333; margin: 0;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }

.letterhead { display: flex; justify-content: space-between; align-items: flex-start;
              gap: 6mm; background: #1F3864; color: #fff; padding: 5mm 6mm; }
.letterhead__name { font-size: 12pt; font-weight: 700; line-height: 1.15; white-space: nowrap; }
.letterhead__sub  { font-size: 8pt; margin-top: 1.4mm; opacity: .92; }
.letterhead__addr { font-size: 7.5pt; margin-top: 1mm; opacity: .85; }
.badge { background: #C9A24E; color: #1F3864; text-align: center; padding: 2.6mm 4mm;
         min-width: 38mm; flex-shrink: 0; }
.badge .small { font-size: 8pt; font-weight: 700; letter-spacing: .04em; }
.badge .big   { font-size: 11.5pt; font-weight: 700; letter-spacing: .05em; margin-top: .6mm; }
.gold-stripe { height: 1.4mm; background: #C9A24E; margin: 0 0 3.5mm; }

h1 { font-size: 11pt; font-weight: 700; color: #1F3864; margin: 0 0 1.5mm; }
.project { font-size: 9pt; color: #333; margin: 0 0 3mm; }
.meta { width: 100%; border-collapse: collapse; margin-bottom: 3.5mm; }
.meta td { border: .25mm solid #BFC7D5; padding: 1.3mm 2mm; font-size: 8pt; vertical-align: top; }
.meta .k { background: #D6E4F0; font-weight: 700; color: #1F3864; width: 26mm; white-space: nowrap; }

.banner { background: #FFF2CC; border-left: 1.2mm solid #C9A24E; padding: 2.2mm 3mm;
          font-size: 8.4pt; font-weight: 700; color: #7A5A00; margin-bottom: 4mm; }

h2 { font-size: 9.4pt; font-weight: 700; color: #fff; background: #1F3864;
     padding: 1.6mm 2.4mm; margin: 5.5mm 0 2.5mm; letter-spacing: .05em;
     text-transform: uppercase; break-after: avoid; }
h2:first-of-type { margin-top: 0; }

table.grid { width: 100%; border-collapse: collapse; }
table.grid thead th { background: #2F5496; color: #fff; font-size: 7.6pt; text-align: left;
                      padding: 1.6mm 1.4mm; text-transform: uppercase; letter-spacing: .03em;
                      border: .25mm solid #2F5496; }
table.grid td { border: .25mm solid #D6E4F0; padding: 1.4mm 1.4mm; vertical-align: top; }
table.grid tbody tr:nth-child(even) td { background: #FAFBFD; }

.c-id   { width: 12mm; text-align: center; color: #1F3864; font-weight: 700; }
.c-num  { width: 13mm; text-align: center; }
.c-dur  { width: 15mm; text-align: center; }
.c-resp { width: 26mm; }
.c-pred { width: 15mm; text-align: center; color: #6B7280; }
.c-amt  { width: 26mm; text-align: right; white-space: nowrap;
          font-weight: 700; color: #1F3864; }
.c-day  { width: 20mm; text-align: center; }

/* Scoped through tbody so these outrank the zebra rule above. Without the
   extra specificity the striped background wins on every even row and the
   white phase text prints white-on-white — invisible on paper, and the page
   still looks plausible on screen. */
table.grid tbody tr.phase td { background: #1F3864; color: #fff; font-weight: 700;
              font-size: 8.6pt; padding: 1.9mm 2mm; letter-spacing: .03em;
              border-color: #1F3864; }
table.grid tbody tr.phase td.c-dur, table.grid tbody tr.phase td.c-num,
table.grid tbody tr.phase td.c-id { color: #C9A24E; }
table.grid tbody tr.hold td { background: #FDECEA; }
table.grid tbody tr.hold td.c-id { color: #C00000; }
table.grid tbody tr.total td { background: #1F3864; color: #fff; font-weight: 700;
              font-size: 9.4pt; padding: 2.2mm 2mm; border-color: #1F3864; }
table.grid tbody tr.total td.c-amt { color: #C9A24E; }

/* Bar chart. One column per week; a bar is a run of filled cells, so the
   drawing and the table are the same numbers. */
table.gantt { width: 100%; border-collapse: collapse; table-layout: fixed; }
table.gantt th { background: #2F5496; color: #fff; font-size: 7.2pt; padding: 1.4mm .6mm;
                 border: .25mm solid #2F5496; text-align: center; }
table.gantt th.task { text-align: left; width: 64mm; }
table.gantt td { border: .25mm solid #D6E4F0; padding: 1.1mm 1.2mm; font-size: 7.8pt;
                 height: 4.6mm; }
table.gantt td.task { color: #333; }
table.gantt td.cell { padding: 0; }
table.gantt td.on { background: #2F5496; }
table.gantt td.on.crit { background: #C9A24E; }
table.gantt tr.phaserow td { background: #1F3864; color: #fff; font-weight: 700;
                             font-size: 8.2pt; border-color: #1F3864; }
table.gantt tr.phaserow td.on { background: #1F3864; }
.legend { margin-top: 2.5mm; font-size: 7.6pt; color: #555; }
.swatch { display: inline-block; width: 4mm; height: 2.4mm; vertical-align: middle;
          margin: 0 1mm 0 3mm; border: .2mm solid #BFC7D5; }
.swatch.a { background: #2F5496; } .swatch.b { background: #C9A24E; }

ol.notes, ul.notes { margin: 0; padding-left: 5.5mm; }
ol.notes li, ul.notes li { margin-bottom: 1.8mm; font-size: 8.4pt; text-align: justify; }

.sign { margin-top: 9mm; break-inside: avoid; }
.sign__for { font-weight: 700; color: #1F3864; margin-bottom: 13mm; font-size: 9pt; }
.sign__line { border-top: .3mm solid #1F3864; width: 66mm; padding-top: 1.6mm; }
.sign__name { font-weight: 700; color: #1F3864; font-size: 9.4pt; }
.sign__role { font-size: 8.6pt; color: #555; }
.foot { margin-top: 6mm; border-top: .25mm solid #D6E4F0; padding-top: 1.4mm;
        font-size: 7pt; color: #6B7280; text-align: center; }
.pagebreak { break-before: page; }
"""


def flatten(spec: dict) -> list[dict]:
    return [a for ph in spec["phases"] for a in ph["activities"]]


def verify(spec: dict) -> list[str]:
    """Derive every finish day; check the logic holds and nothing overruns."""
    problems: list[str] = []
    acts = flatten(spec)
    by_id = {a["id"]: a for a in acts}

    if len(by_id) != len(acts):
        seen: set[str] = set()
        for a in acts:
            if a["id"] in seen:
                problems.append(f"duplicate activity id {a['id']}")
            seen.add(a["id"])

    for a in acts:
        start, dur = int(a["start"]), int(a["duration"])
        if start < 1:
            problems.append(f"{a['id']}: start day {start} — day 1 is the first working day")
        if dur < 1:
            problems.append(f"{a['id']}: duration {dur} — an activity occupies at least one day")
        finish = start + dur - 1
        if "finish" in a and int(a["finish"]) != finish:
            problems.append(f"{a['id']}: start {start} + {dur} WD finishes day {finish}, "
                            f"stated {a['finish']}")
        a["finish"] = finish

    # Logic: a predecessor finishes before its successor starts, unless the
    # activity declares the overlap. An undeclared overlap is a programme that
    # reads as sequential and is not.
    for a in acts:
        # "—" is how the table spells "no predecessor"; it is not an activity.
        preds = [p.strip() for p in str(a.get("pred", "")).split(",")]
        for pred in [p for p in preds if p and p not in ("—", "-", "–")]:
            if pred not in by_id:
                problems.append(f"{a['id']}: predecessor {pred} does not exist")
                continue
            if by_id[pred]["finish"] >= int(a["start"]) and not a.get("overlap"):
                problems.append(
                    f"{a['id']} starts day {a['start']} but predecessor {pred} runs to day "
                    f"{by_id[pred]['finish']} — set \"overlap\": true if that is intended")

    # Phase spans are derived, never typed.
    for ph in spec["phases"]:
        if not ph["activities"]:
            problems.append(f"phase {ph['key']} has no activities")
            continue
        first = min(int(a["start"]) for a in ph["activities"])
        last = max(int(a["finish"]) for a in ph["activities"])
        for field, value in (("start", first), ("finish", last)):
            if field in ph and int(ph[field]) != value:
                problems.append(f"phase {ph['key']}: {field} day {value} from its activities, "
                                f"stated {ph[field]}")
        ph["start"], ph["finish"] = first, last
        ph["duration"] = last - first + 1

    completion = max(int(a["finish"]) for a in acts) if acts else 0
    if "completion_day" in spec and int(spec["completion_day"]) != completion:
        problems.append(f"completion: last activity finishes day {completion}, "
                        f"stated {spec['completion_day']}")
    spec["completion_day"] = completion

    # Milestones must sit on a day the programme actually reaches.
    for m in spec.get("milestones", []):
        if int(m["day"]) > completion:
            problems.append(f"milestone {m['event']!r} on day {m['day']} is beyond "
                            f"completion day {completion}")

    # The payment schedule must add up to the contract value.
    value = spec.get("contract_value")
    stages = spec.get("payments", [])
    if value and stages:
        pct = round(sum(float(s["percent"]) for s in stages), 4)
        if abs(pct - 100.0) > 0.01:
            problems.append(f"payment stages sum to {pct}%, not 100%")
        for s in stages:
            expected = round(float(value) * float(s["percent"]) / 100.0, 2)
            if "amount" in s and abs(expected - float(s["amount"])) > 0.01:
                problems.append(f"payment {s['percent']}%: {value:,.0f} x {s['percent']}% = "
                                f"{expected:,.2f}, stated {float(s['amount']):,.2f}")
            s["amount"] = expected

    return problems


def week_of(day: int, per_week: int) -> int:
    return math.ceil(day / per_week)


def render(spec: dict) -> str:
    c = spec.get("company", {})
    badge = spec.get("badge", ["", ""])
    per_week = int(spec.get("working_days_per_week", 6))
    weeks = week_of(spec["completion_day"], per_week)

    meta = "".join(
        f'<tr><td class="k">{esc(a)}</td><td>{esc(b)}</td>'
        f'<td class="k">{esc(c2)}</td><td>{esc(d)}</td></tr>'
        for a, b, c2, d in spec.get("meta_rows", []))

    # --- Activity schedule -------------------------------------------------
    rows = []
    for ph in spec["phases"]:
        rows.append(
            f'<tr class="phase"><td class="c-id">{esc(ph["key"])}</td>'
            f'<td>{esc(ph["title"])}</td>'
            f'<td class="c-dur">{ph["duration"]} WD</td>'
            f'<td class="c-num">{ph["start"]}</td><td class="c-num">{ph["finish"]}</td>'
            f'<td class="c-resp"></td><td class="c-pred"></td></tr>')
        for a in ph["activities"]:
            cls = "hold" if a.get("hold") else ""
            marker = " ▲" if a.get("hold") else ""
            rows.append(
                f'<tr class="{cls}"><td class="c-id">{esc(a["id"])}</td>'
                f'<td>{esc(a["description"])}{marker}</td>'
                f'<td class="c-dur">{a["duration"]}</td>'
                f'<td class="c-num">{a["start"]}</td><td class="c-num">{a["finish"]}</td>'
                f'<td class="c-resp">{esc(a.get("resp",""))}</td>'
                f'<td class="c-pred">{esc(a.get("pred","—"))}</td></tr>')
    rows.append(
        f'<tr class="total"><td class="c-id"></td>'
        f'<td>{esc(spec.get("completion_label", "PROGRAMME COMPLETE"))}</td>'
        f'<td class="c-dur"></td><td class="c-num"></td>'
        f'<td class="c-num">{spec["completion_day"]}</td>'
        f'<td class="c-resp"></td><td class="c-pred"></td></tr>')

    # --- Bar chart ---------------------------------------------------------
    heads = "".join(f"<th>W{w}</th>" for w in range(1, weeks + 1))
    bars = []
    for ph in spec["phases"]:
        cells = "".join(
            f'<td class="cell{" on" if week_of(ph["start"], per_week) <= w <= week_of(ph["finish"], per_week) else ""}"></td>'
            for w in range(1, weeks + 1))
        bars.append(f'<tr class="phaserow"><td class="task">{esc(ph["key"])}. '
                    f'{esc(ph["title"])}</td>{cells}</tr>')
        for a in ph["activities"]:
            crit = " crit" if a.get("critical") else ""
            cells = "".join(
                f'<td class="cell{(" on" + crit) if week_of(a["start"], per_week) <= w <= week_of(a["finish"], per_week) else ""}"></td>'
                for w in range(1, weeks + 1))
            bars.append(f'<tr><td class="task">{esc(a["id"])} &nbsp;{esc(a["description"])}</td>'
                        f'{cells}</tr>')

    # --- Milestones and payments -------------------------------------------
    miles = "".join(
        f'<tr><td class="c-day">Day {m["day"]}</td>'
        f'<td class="c-day">W{week_of(int(m["day"]), per_week)}</td>'
        f'<td>{esc(m["event"])}</td><td class="c-resp">{esc(m.get("resp",""))}</td></tr>'
        for m in spec.get("milestones", []))

    pays = "".join(
        f'<tr><td class="c-num">{esc(s["percent"])}%</td>'
        f'<td>{esc(s["trigger"])}</td>'
        f'<td class="c-day">{esc(s.get("day","—"))}</td>'
        f'<td class="c-amt">{money(s["amount"])}</td></tr>'
        for s in spec.get("payments", []))
    if pays:
        pays += (f'<tr class="total"><td class="c-num">100%</td>'
                 f'<td>CONTRACT VALUE</td><td class="c-day"></td>'
                 f'<td class="c-amt">QAR {money(spec["contract_value"])}</td></tr>')

    def block(title: str, items: list, ordered: bool = True) -> str:
        if not items:
            return ""
        tag = "ol" if ordered else "ul"
        lis = "".join(f"<li>{esc(i)}</li>" for i in items)
        return f'<h2>{esc(title)}</h2><{tag} class="notes">{lis}</{tag}>'

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{esc(spec.get('reference',''))}</title><style>{CSS}</style></head><body>

<div class="letterhead">
  <div>
    <div class="letterhead__name">{esc(c.get('name','THE NEW DOHA KITCHEN EQUIPMENT SERVICES W.L.L.'))}</div>
    <div class="letterhead__sub">{esc(c.get('subtitle',''))}</div>
    <div class="letterhead__addr">{esc(c.get('address',''))} &nbsp;·&nbsp; {esc(c.get('contact',''))}</div>
  </div>
  <div class="badge"><div class="small">{esc(badge[0])}</div><div class="big">{esc(badge[1])}</div></div>
</div>
<div class="gold-stripe"></div>

<h1>{esc(spec.get('doc_title',''))}</h1>
<div class="project">{esc(spec.get('project',''))}</div>
<table class="meta">{meta}</table>
<div class="banner">{esc(spec.get('banner',''))}</div>

{block('Basis of Programme', spec.get('basis', []))}

<h2>Key Dates &amp; Hold Points</h2>
<table class="grid">
  <thead><tr><th class="c-day">Working Day</th><th class="c-day">Week</th>
  <th>Event</th><th class="c-resp">Responsibility</th></tr></thead>
  <tbody>{miles}</tbody>
</table>

<div class="pagebreak"></div>
<h2>Detailed Activity Schedule</h2>
<table class="grid">
  <thead><tr><th class="c-id">Ref</th><th>Activity</th><th class="c-dur">Dur. (WD)</th>
  <th class="c-num">Start</th><th class="c-num">Finish</th>
  <th class="c-resp">Responsibility</th><th class="c-pred">Pred.</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
<div class="legend">▲ Hold point — the activity cannot proceed until the party named has
released it. Days are working days from Day 0 as defined above.</div>

<div class="pagebreak"></div>
<h2>Programme Bar Chart — {weeks} Working Weeks</h2>
<table class="gantt">
  <thead><tr><th class="task">Activity</th>{heads}</tr></thead>
  <tbody>{''.join(bars)}</tbody>
</table>
<div class="legend">
  <span class="swatch a"></span> Activity
  <span class="swatch b"></span> Critical path — a day lost here is a day lost to completion.
  One column = one working week of {per_week} days.
</div>

{f'''<h2>Payment Schedule Against the Programme</h2>
<table class="grid">
  <thead><tr><th class="c-num">Stage</th><th>Trigger event</th>
  <th class="c-day">Prog. day</th><th class="c-amt">Amount (QAR)</th></tr></thead>
  <tbody>{pays}</tbody>
</table>''' if pays else ""}

<div class="pagebreak"></div>
{block('Client / Main Contractor Obligations', spec.get('client_obligations', []))}
{block('Assumptions & Qualifications', spec.get('qualifications', []))}

<div class="sign">
  <div class="sign__for">For {esc(c.get('name',''))}</div>
  <div class="sign__line">
    <div class="sign__name">{esc(spec.get('signatory',{}).get('name',''))}</div>
    <div class="sign__role">{esc(spec.get('signatory',{}).get('role',''))}</div>
  </div>
</div>

<div class="foot">{esc(c.get('address',''))} &nbsp;·&nbsp; {esc(c.get('contact',''))}</div>
</body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text())

    problems = verify(spec)
    if problems:
        print("REFUSING TO BUILD — the programme does not reconcile:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2
    print(f"programme verified: {len(flatten(spec))} activities, "
          f"completion day {spec['completion_day']}")

    page = render(spec)
    text = re.sub(r"<[^>]+>", " ", page)
    found = {m.group(0).lower() for m in TAX_WORDS.finditer(text)}
    if found:
        print(f"REFUSING TO BUILD: tax wording present ({', '.join(sorted(found))}) — "
              f"see DECISIONS.md D-005.", file=sys.stderr)
        return 2

    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9]+", "-", spec.get("filename") or spec["reference"]).strip("-")
    html_path = outdir / f"{name}.html"
    html_path.write_text(page)

    chrome = next((x for x in CHROME if (x.startswith("/") and Path(x).exists()) or shutil.which(x)), None)
    if not chrome:
        print(f"HTML → {html_path}  (no Chromium; print to PDF at A4)", file=sys.stderr)
        return 0
    chrome = chrome if chrome.startswith("/") else shutil.which(chrome)

    pdf = outdir / f"{name}.pdf"
    r = subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", f"--print-to-pdf={pdf}",
                        "--no-pdf-header-footer", html_path.as_uri()],
                       capture_output=True, text=True)
    print(f"PDF  → {pdf}" if r.returncode == 0 else "PDF render failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
