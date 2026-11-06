# -*- coding: utf-8 -*-
"""Project status report — approved projects and finished projects, as at 06-11-2026."""
import io

SP = "/tmp/claude-0/-home-user-ClaudeCode/f198eb8f-5169-5011-a0a8-bd4d87e7e71f/scratchpad"

def q(n):
    return "{:,.2f}".format(n)

# ---------------------------------------------------------------- live, finished
FINISHED_OWED = [
    ("Consolidated Contractors (CCC)", "Cold rooms — CCC Labor Camp", 253500, 76050,
     "Complete 28-09-2026. 2nd 30% invoiced (INV-293). Third 30% and final 10% not yet invoiced."),
    ("HBK-BWTC-BEIL JV", "Mesaieed animal waste cold room", 400000, 0,
     "Complete. Only the 15% advance of 60,000 invoiced (INV-276) — 340,000 never invoiced."),
    ("One A Design, Build and Trading", "Chiller + freezer — Capital Grille, ABESQ Hotel", 73500, 25725,
     "Invoiced in full to INV-300. Nothing left to invoice; 47,775 unpaid."),
    ("Everbloom", "Flower display chiller, frameless glass", 17000, 12750,
     "Complete and handed over. Final invoice INV-289 outstanding."),
    ("Mr. Hamad Abdulla Al-Sulaiti", "Flower chiller cold room, Semaisma", 25000, None,
     "Complete. NO PAYMENT RECORD ON FILE — see the note below."),
]

IN_PROGRESS = [
    ("M/s. Q Fish Trading", "Freezer enlargement to 18.00 x 14.00 x 6.00 m (1,512 cbm)", 150000, 20000,
     "Approved and stamped 06-11-2026. 50% advance invoiced; 55,000 of it still awaited. Not started."),
    ("Oscar Prime Trading (2nd job)", "Five cold rooms — thawing chiller, 2 chillers, 2 freezers", 170000, 119000,
     "The 119,000 transfer advice read &ldquo;Pending Approval&rdquo; and has never been confirmed on a statement."),
    ("Bismi Group International", "Freezer room + preparation room, epoxy floor", 110000, 30000,
     "Contract signed. 25,000 of the advance due before commencement. Not started."),
    ("Al Mairqab Industrial Investment (Aalaf)", "Chiller room + civil works + uPVC ventilation + SS shelving", 95000, 0,
     "Won 03-11-2026 on LPO 26-00330. 30% advance invoiced, not yet paid."),
    ("Home-Made by Earth", "Chiller + freezer rooms", 46900, 32830,
     "25% delivery stage invoiced (INV-290). 5% handover to follow."),
    ("M/s. Gozl Veterinary Services", "Chiller room 4.00 x 4.00 x 2.50 m, duty and standby", 59800, 47840,
     "Materials delivered and paid for. Installation, testing and commissioning to follow."),
    ("Oscar Prime Trading (3rd job)", "Chiller room 4.00 x 3.90 x 2.70 m", 38000, 24700,
     "65% advance received 03-11-2026. Not started. No written order on file."),
    ("M/s. Panda Cakes", "Chiller room 4.35 x 2.00 x 2.40 m", 29000, 21750,
     "Materials delivered; 20% delivery stage invoiced (INV-295). Installation to follow."),
]

CLOSED = [
    ("Sunrise Trading & Food Stuff", "Jollibee Rasaboud cold room + condensing unit relocation", 53000),
    ("Stop n Shop — Bin Omran", "Cold room — chiller + freezer", 45000),
    ("Samoosa Shop", "Samoosa cold room (freezer)", 38500),
    ("Lean N Fit", "Freezer unit replacement", 17000),
    ("Green Land Qatar", "3 nos Carrier air curtains to a 4.50 x 3.00 m door", 7300),
    ("Ruwais Farm", "Expansion valve replacement + system gas charging", 1750),
    ("Ruwais Farm", "Refrigeration maintenance", 1850),
    ("Lean N Fit", "Drainage system replacement", 1200),
    ("Al Noor Bakery", "Refrigeration maintenance", 800),
    ("BSI (Mr. Lijo)", "Cold room checkup + gas charging", 750),
    ("BSI (Mr. Lijo)", "Cold room maintenance", 450),
]

DCTS = [
    ("Oriental Agro Trading", "Cold storage project", 1103286, 1093000, "Balance 10,286."),
    ("Oriental Agro Trading", "Insulated sectional overhead doors (4 nos.)", 81000, 81000, "Settled 11-05-2026."),
    ("Westin Hotel", "3 nos ALCO power assemblies XB-1019-NW100-1B", 1800, 1800, "Settled."),
    ("Paramount Trading Co.", "10 nos 40 ft container cold rooms, Ras Laffan", 635000, None, "No payment record on file."),
    ("Alayees General Trading", "Cold storage facility — 3 chiller rooms, epoxy, racking, doors", 595000, None, "No payment record on file."),
    ("Paramount Trading Co.", "7 nos walk-in chiller rooms (4 + 3 laboratory)", 210000, None, "No payment record on file."),
    ("Oriental Agro Trading", "Additional sandwich panel shifting, Street 36", None, None, "Price never given; not invoiced."),
]

QUOTED = [
    ("Mr. Akbar", "100 mm sandwich panel 73 sqm, 17 angles, hinged door", 11180, "QUT/DCTS/254/2026 Rev."),
    ("The Private Office of H.H. The Father Amir", "2 nos Rotorup axial fans 4T-S500S — supply only", 3300, "QUT/DCTS/258/2026"),
    ("M/s. Kalima", "Leak testing, gas charging, complete water service", 2350, "QUT/DCTS/259/2026"),
    ("Iranian Kitchen", "Expansion valve, dryer filter, complete system service", 1500, "QUT/DCTS/253/2026 Rev."),
]

live = FINISHED_OWED + IN_PROGRESS
live_contract = sum(c for _, _, c, _, _ in live)
live_recd = sum(r for _, _, _, r, _ in live if r is not None)
live_out = sum(c - (r or 0) for _, _, c, r, _ in live if r is not None)
closed_total = sum(v for _, _, v in CLOSED)
quoted_total = sum(v for _, _, v, _ in QUOTED)


def rows_live(items):
    out = []
    for i, (client, proj, c, r, note) in enumerate(items, 1):
        recd = q(r) if r is not None else "<i>not recorded</i>"
        bal = q(c - r) if r is not None else "<i>not recorded</i>"
        out.append(
            '<tr><td class="n">%d</td><td><b>%s</b><div class="sub">%s</div></td>'
            '<td class="r">%s</td><td class="r">%s</td><td class="r b">%s</td>'
            '<td class="st">%s</td></tr>' % (i, client, proj, q(c), recd, bal, note))
    return "".join(out)


def rows_closed(items):
    return "".join(
        '<tr><td class="n">%d</td><td><b>%s</b><div class="sub">%s</div></td>'
        '<td class="r b">%s</td></tr>' % (i, cl, pr, q(v))
        for i, (cl, pr, v) in enumerate(items, 1))


def rows_dcts(items):
    out = []
    for i, (cl, pr, c, r, note) in enumerate(items, 1):
        cc = q(c) if c is not None else "<i>no price</i>"
        rr = q(r) if r is not None else "<i>not recorded</i>"
        out.append('<tr><td class="n">%d</td><td><b>%s</b><div class="sub">%s</div></td>'
                   '<td class="r">%s</td><td class="r">%s</td><td class="st">%s</td></tr>'
                   % (i, cl, pr, cc, rr, note))
    return "".join(out)


def rows_quoted(items):
    return "".join(
        '<tr><td class="n">%d</td><td><b>%s</b><div class="sub">%s</div></td>'
        '<td class="r b">%s</td><td class="st">%s</td></tr>' % (i, cl, pr, q(v), ref)
        for i, (cl, pr, v, ref) in enumerate(items, 1))


HTML = u"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>TNDK Project Status</title>
<style>
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; box-sizing: border-box; }
  @page { size: A4; margin: 12mm 10mm; }
  body { font-family: Arial, "Liberation Sans", Helvetica, sans-serif; font-size: 8.6pt;
         color: #222; margin: 0; line-height: 1.38; }
  .band { background: #1F3864; color: #fff; padding: 12pt 14pt 10pt 14pt; }
  .band .co { font-size: 14pt; font-weight: bold; line-height: 1.12; }
  .band .ad { font-size: 7.6pt; padding-top: 3pt; color: #D7DEEB; }
  .band .ttl { font-size: 10.5pt; font-weight: bold; color: #C9A24E; padding-top: 7pt;
               letter-spacing: .4pt; }
  .rule { background: #C9A24E; height: 3.5pt; font-size: 1pt; }
  .asat { background: #EEF2F8; padding: 5pt 14pt; font-size: 8.2pt; }
  h2 { font-size: 9.6pt; color: #fff; background: #1F3864; padding: 4.5pt 8pt;
       margin: 13pt 0 0 0; }
  h2 span { color: #C9A24E; font-weight: normal; }
  table { width: 100%; border-collapse: collapse; margin: 0; }
  th { background: #DCE3EF; color: #1F3864; font-size: 7.8pt; text-align: left;
       padding: 4pt 6pt; border: 0.5pt solid #C9CDD6; }
  td { border: 0.5pt solid #C9CDD6; padding: 4pt 6pt; vertical-align: top; }
  td.n { width: 16pt; text-align: center; color: #666; }
  td.r { text-align: right; white-space: nowrap; width: 62pt; }
  td.b { font-weight: bold; color: #1F3864; }
  td.st { font-size: 7.6pt; color: #444; width: 33%; }
  .sub { font-size: 7.6pt; color: #555; padding-top: 1pt; }
  tr.tot td { background: #EEF2F8; font-weight: bold; color: #1F3864; border-top: 1pt solid #1F3864; }
  .cards { display: table; width: 100%; margin: 9pt 0 2pt 0; border-spacing: 6pt 0; }
  .card { display: table-cell; width: 25%; background: #EEF2F8; border-left: 3pt solid #C9A24E;
          padding: 7pt 9pt; }
  .card .k { font-size: 20pt; font-weight: bold; color: #1F3864; line-height: 1; }
  .card .l { font-size: 7.4pt; color: #444; padding-top: 3pt; text-transform: uppercase;
             letter-spacing: .3pt; }
  .card .v { font-size: 8pt; color: #1F3864; font-weight: bold; padding-top: 3pt; }
  .note { background: #FFF8E1; border-left: 3pt solid #C9A24E; padding: 7pt 9pt;
          margin: 9pt 0 0 0; font-size: 8pt; }
  .note b { color: #1F3864; }
  .foot { background: #1F3864; color: #fff; text-align: center; padding: 6pt;
          font-size: 7.4pt; margin-top: 14pt; }
  .foot i { color: #C9A24E; }
</style></head><body>

<div class="band">
  <div class="co">THE NEW DOHA KITCHEN EQUIPMENT SERVICES W.L.L.</div>
  <div class="ad">P.O. Box 80247, Doha, State of Qatar&nbsp; |&nbsp; C.R. 199351&nbsp; |&nbsp; Tel: 7706 0676&nbsp; |&nbsp; farhan@dctsqatar.com</div>
  <div class="ttl">PROJECT STATUS REPORT &mdash; APPROVED AND COMPLETED WORKS</div>
</div>
<div class="rule"></div>
<div class="asat"><b>As at 06 November 2026.</b> Prepared from the order book. Figures in Qatari Riyals.
Doha Cooling Trading &amp; Solutions W.L.L. contracts are listed separately at the end.</div>

<div class="cards">
  <div class="card"><div class="k">13</div><div class="l">Approved projects live</div><div class="v">__LIVEC__</div></div>
  <div class="card"><div class="k">16</div><div class="l">Projects finished</div><div class="v">11 closed + 5 owed</div></div>
  <div class="card"><div class="k">8</div><div class="l">Still in progress</div><div class="v">__WIPC__</div></div>
  <div class="card"><div class="k">__OUT__</div><div class="l">Outstanding to collect</div><div class="v">of __LIVEC__ approved</div></div>
</div>

<h2>A. APPROVED AND FINISHED &mdash; work done, money still owed <span>&nbsp;&nbsp;5 projects</span></h2>
<table>
<tr><th>#</th><th>Client / project</th><th style="text-align:right">Contract</th><th style="text-align:right">Received</th><th style="text-align:right">Balance</th><th>Position</th></tr>
__FIN__
</table>

<h2>B. APPROVED AND IN PROGRESS <span>&nbsp;&nbsp;8 projects</span></h2>
<table>
<tr><th>#</th><th>Client / project</th><th style="text-align:right">Contract</th><th style="text-align:right">Received</th><th style="text-align:right">Balance</th><th>Position</th></tr>
__WIP__
<tr class="tot"><td></td><td>TOTAL &mdash; the 12 approved projects that have a payment record</td><td class="r">__LIVE12__</td><td class="r">__RECD__</td><td class="r">__OUT__</td><td class="st">The 13th, Semaisma (25,000), has no payment record and is excluded from these totals. Contract value of all 13 is __LIVEC__.</td></tr>
</table>

<h2>C. FINISHED AND CLOSED &mdash; completed and paid in full <span>&nbsp;&nbsp;11 projects</span></h2>
<table>
<tr><th>#</th><th>Client / project</th><th style="text-align:right">Value</th></tr>
__CLOSED__
<tr class="tot"><td></td><td>TOTAL CLOSED</td><td class="r">__CLOSEDT__</td></tr>
</table>

<h2>D. QUOTED, AWAITING THE CLIENT'S DECISION <span>&nbsp;&nbsp;4 offers</span></h2>
<table>
<tr><th>#</th><th>Client / project</th><th style="text-align:right">Value</th><th>Reference</th></tr>
__QUOTED__
<tr class="tot"><td></td><td>TOTAL QUOTED, NOT YET WON</td><td class="r">__QUOTEDT__</td><td></td></tr>
</table>

<h2>E. DOHA COOLING TRADING &amp; SOLUTIONS W.L.L. &mdash; separate entity, C.R. 93354</h2>
<table>
<tr><th>#</th><th>Client / project</th><th style="text-align:right">Contract</th><th style="text-align:right">Received</th><th>Position</th></tr>
__DCTS__
</table>

<div class="note">
<b>What these numbers do and do not say.</b>
&nbsp;<b>1.</b> &ldquo;Finished&rdquo; means the work is done, not that it is paid for. Five finished projects still owe
money, <b>629,475</b> of it, and the two largest &mdash; CCC and Mesaieed &mdash; account for <b>577,450</b> of that.
&nbsp;<b>2.</b> <b>340,000 of the Mesaieed contract has never been invoiced</b>, and CCC's third 30% and final
10% (101,400) have not been invoiced either. That is <b>441,400 of completed work with no invoice behind it.</b>
&nbsp;<b>3.</b> Oscar Prime's <b>119,000</b> is counted as received, but the transfer advice read &ldquo;Pending
Approval&rdquo; and has never been confirmed on a bank statement.
&nbsp;<b>4.</b> The Semaisma flower chiller (25,000) and the three older Doha Cooling contracts
(1,440,000 together) carry <b>no payment record at all</b> and are excluded from every total above.
</div>

<div class="foot">
The New Doha Kitchen Equipment Services W.L.L.&nbsp; |&nbsp; P.O. Box 80247, Doha, State of Qatar&nbsp; |&nbsp; C.R. 199351&nbsp; |&nbsp; Tel: 7706 0676<br/>
<i>Internal management report &mdash; prepared 06 November 2026 from the order book.</i>
</div>
</body></html>"""

html = (HTML
        .replace("__FIN__", rows_live(FINISHED_OWED))
        .replace("__WIP__", rows_live(IN_PROGRESS))
        .replace("__CLOSED__", rows_closed(CLOSED))
        .replace("__DCTS__", rows_dcts(DCTS))
        .replace("__QUOTED__", rows_quoted(QUOTED))
        .replace("__LIVE12__", q(live_contract - 25000))
        .replace("__LIVEC__", q(live_contract))
        .replace("__RECD__", q(live_recd))
        .replace("__OUT__", q(live_out))
        .replace("__WIPC__", q(sum(c for _, _, c, _, _ in IN_PROGRESS)))
        .replace("__CLOSEDT__", q(closed_total))
        .replace("__QUOTEDT__", q(quoted_total)))

out = SP + "/report/project_status.html"
io.open(out, "w", encoding="utf-8").write(html)
print("live contract", q(live_contract), "| received", q(live_recd), "| outstanding", q(live_out))
print("closed", q(closed_total), "| quoted", q(quoted_total))
print("written", out)
