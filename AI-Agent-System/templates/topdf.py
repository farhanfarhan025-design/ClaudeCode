"""Render the filled GWC forms to PDF.

LibreOffice's import filters do not work in this container, so the PDF is built from the
same .docx cells rather than converted from them — the two cannot drift apart, because the
text is read out of the Word file at render time.
"""
import html, subprocess, docx

SP = "/tmp/claude-0/-home-user-ClaudeCode/f198eb8f-5169-5011-a0a8-bd4d87e7e71f/scratchpad/hse/"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

CSS = """
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; box-sizing: border-box; }
@page { size: %(size)s; margin: 12mm 10mm; }
body { font-family: Arial, "Liberation Sans", Helvetica, sans-serif; font-size: %(fs)s;
       color: #000; margin: 0; line-height: 1.35; }
table { width: 100%%; border-collapse: collapse; }
td, th { border: 0.8pt solid #000; padding: 3pt 5pt; vertical-align: top; }
.hdr td { background: #D9D9D9; font-weight: bold; text-align: center; font-size: 13pt;
          letter-spacing: 0.5pt; }
.sect td { background: #BFBFBF; font-weight: bold; text-transform: uppercase; font-size: 9.5pt; }
.lbl { background: #F2F2F2; font-weight: bold; width: 22%%; }
.ref { text-align: right; font-weight: bold; font-size: 9pt; width: 26%%; }
.narrow { white-space: pre-line; }
table.sigblock { page-break-inside: avoid; }
.sig td { height: 58pt; font-size: 9pt; }
tr { page-break-inside: avoid; }
.sig td div { margin-bottom: 9pt; }
h1 { font-size: 0; margin: 0; }
"""


def cells(t, r):
    seen, out = [], []
    for c in t.rows[r].cells:
        if any(id(c._tc) == id(x._tc) for x in seen):
            continue
        seen.append(c)
        out.append(c.text.strip())
    return out


def esc(s):
    return html.escape(s).replace("\n", "<br/>")


def render(name, body, size="A4 portrait", fs="9pt"):
    doc = ("<!DOCTYPE html><html><head><meta charset='utf-8'><style>"
           + CSS % {"size": size, "fs": fs} + "</style></head><body>" + body + "</body></html>")
    open(SP + name + ".html", "w").write(doc)
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", f"--print-to-pdf={SP + name}.pdf",
                    f"file://{SP + name}.html"], capture_output=True)
    return SP + name + ".pdf"


# ------------------------------------------------------------------ method statement
d = docx.Document(SP + "MethodStatement_AlZehrabi_ColdRoomMaintenance_GWC-HSE-FM11-MS.00.docx")
t0, t1, t2 = d.tables[0], d.tables[1], d.tables[2]

rows = ["<table>",
        "<tr class='hdr'><td colspan='4'>METHOD STATEMENT</td>"
        "<td class='ref' style='background:#D9D9D9'>GWC-HSE-FM11-MS.00</td></tr>",
        "<tr class='sect'><td colspan='5'>Client / Contractor / Department Details</td></tr>"]
for r, label in ((2, "Client/Company/Department Name"), (3, "Scope of Work")):
    rows.append(f"<tr><td class='lbl'>{label}</td><td colspan='4'>{esc(cells(t0, r)[1])}</td></tr>")
c4 = cells(t0, 4)
rows.append(f"<tr><td class='lbl'>Location of Work</td><td colspan='2'>{esc(c4[1])}</td>"
            f"<td class='lbl' style='width:12%'>Exact Site</td><td>{esc(c4[3])}</td></tr>")
rows.append("<tr class='sect'><td colspan='5'>Work / Job Method Details</td></tr>")
rows.append(f"<tr><td class='lbl'>Work Title</td><td colspan='4'>{esc(cells(t0, 7)[0])}</td></tr>")
rows.append("<tr class='sect'><td colspan='5'>Tools and Equipment</td></tr>")
for r in range(9, 14):
    c = cells(t0, r)
    while len(c) < 3:
        c.append("")
    spans = (2, 1, 2)
    rows.append("<tr>" + "".join(
        f"<td colspan='{spans[i]}' style='font-weight:normal'>{esc(v)}</td>"
        for i, v in enumerate(c[:3])) + "</tr>")
rows.append("<tr class='sect'><td colspan='5'>Site Preparation</td></tr>")
rows.append(f"<tr><td colspan='5' class='narrow'>{esc(cells(t0, 15)[0])}</td></tr>")
rows.append("<tr class='sect'><td colspan='5'>Work Methodology</td></tr>")
rows.append(f"<tr><td colspan='5' class='narrow'>{esc(cells(t0, 17)[0])}</td></tr>")
rows.append(f"<tr><td colspan='4'>{esc(cells(t0, 18)[0])}</td>"
            f"<td style='text-align:center;font-weight:bold'>{esc(cells(t0, 19)[0])}</td></tr>")
rows.append("<tr class='sect'><td colspan='5'>Responsible Personnel</td></tr>")
hd = cells(t1, 1)
rows.append("<tr>" + "".join(f"<td class='lbl' style='width:auto'>{esc(h)}</td>" for h in hd[:2])
            + f"<td class='lbl' style='width:auto'>{esc(hd[2])}</td>"
              f"<td class='lbl' colspan='2' style='width:auto'>{esc(hd[3])}</td></tr>")
p = cells(t1, 2)
rows.append(f"<tr><td>{esc(p[0])}</td><td>{esc(p[1])}</td><td>{esc(p[2])}</td>"
            f"<td colspan='2'>{esc(p[3])}</td></tr>")
rows.append("<tr class='sect'><td colspan='5'>Work Force</td></tr>")
rows.append(f"<tr><td colspan='5' class='narrow'>{esc(cells(t1, 7)[0])}</td></tr>")
rows.append("<tr class='sect'><td colspan='5'>Additional Documents</td></tr>")
rows.append(f"<tr><td colspan='5'>{esc(cells(t1, 9)[0])}</td></tr>")
rows.append("</table><br/>")

sig_hd = cells(t2, 0)
sig = ["<table class='sigblock'><tr>" + "".join(f"<td class='lbl' style='width:25%'>{esc(h)}</td>" for h in sig_hd)
       + "</tr><tr class='sig'>"]
for i in range(4):
    lines = [cells(t2, r)[i] for r in range(1, 5)]
    sig.append("<td>" + "".join(f"<div>{esc(x)}</div>" for x in lines) + "</td>")
sig.append("</tr></table>")

print(render("MethodStatement_AlZehrabi_GWC-HSE-FM11-MS.00", "".join(rows) + "".join(sig)))

# ------------------------------------------------------------------------------ JHA
j = docx.Document(SP + "JHA_AlZehrabi_ColdRoomMaintenance_GWC-HSE-FM-JHA.00.docx")
jt = j.tables[0]


def jc(r, c):
    return jt.rows[r].cells[c].text.strip()


b = ["<table>",
     "<tr class='hdr'><td colspan='4'>JOB HAZARD ANALYSIS</td>"
     "<td class='ref' style='background:#D9D9D9'>GWC-HSE-FM-JHA.00</td></tr>",
     "<tr class='sect'><td colspan='5'>Client Details</td></tr>",
     f"<tr><td colspan='3'>{esc(jc(2, 0))}</td><td colspan='2'>{esc(jc(2, 6))}</td></tr>",
     f"<tr><td colspan='5'>{esc(jc(3, 0))}</td></tr>",
     f"<tr><td colspan='3' style='height:44pt'>{esc(jc(4, 0))}</td>"
     f"<td colspan='2'>{esc(jc(4, 6))}</td></tr>",
     "<tr class='sect'><td colspan='5'>Personal Protective Equipment (tick applicable PPE)</td></tr>"]
ppe = [("Safety Shoes", "Safety Vest"), ("Safety Hardhat", "Ear Plugs / muffs"),
       ("Safety Gloves", "Safety Glass")]
for i, (left, right) in enumerate(ppe):
    other = (f"<td rowspan='3' style='width:40%'>{esc(jc(6, 9))}</td>") if i == 0 else ""
    b.append("<tr>"
             f"<td style='width:5%;text-align:center;font-weight:bold'>X</td>"
             f"<td style='width:20%'>{left}</td>"
             f"<td style='width:5%;text-align:center;font-weight:bold'>X</td>"
             f"<td style='width:20%'>{right}</td>{other}</tr>")
b.append("<tr class='sect'><td colspan='5'>Hazard Identification</td></tr></table>")

b.append("<table style='margin-top:0'><tr>"
         "<td class='lbl' style='width:15%'>Activity<br/>(key activities under the scope)</td>"
         "<td class='lbl' style='width:18%'>Hazard<br/>(potential to do harm)</td>"
         "<td class='lbl' style='width:17%'>Effects of the Hazard</td>"
         "<td class='lbl' style='width:38%'>Control Measures<br/>(PPE, procedures, training)</td>"
         "<td class='lbl' style='width:12%'>Responsible</td></tr>")
for r in range(11, len(jt.rows)):
    if not jc(r, 0):
        continue
    b.append("<tr>" + "".join(f"<td>{esc(jc(r, c))}</td>" for c in (0, 2, 4, 7, 11)) + "</tr>")
b.append("</table>")

print(render("JHA_AlZehrabi_GWC-HSE-FM-JHA.00", "".join(b), size="A4 landscape", fs="8pt"))
