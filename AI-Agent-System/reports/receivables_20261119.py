# -*- coding: utf-8 -*-
"""Receivables from customers, as at 19-11-2026. HBK-BWTC-BEIL JV excluded at Farhan's instruction."""
import io

SP = "/tmp/claude-0/-home-user-ClaudeCode/f198eb8f-5169-5011-a0a8-bd4d87e7e71f/scratchpad"
q = lambda n: "{:,.2f}".format(n)

# client, project, contract, received, invoiced_unpaid, not_invoiced, note
ROWS = [
    ("Consolidated Contractors (CCC)", "Cold rooms — CCC Labor Camp", 253500, 76050, 76050, 101400,
     "INV-293 for the second 30%. Work complete; the third 30% and the 10% retention have never been invoiced."),
    ("M/s. Q Fish Trading", "Freezer room enlargement, 1,512 cbm", 150000, 75000, 0, 75000,
     "Advance settled in full. INV-310 for the 30% is prepared but must wait until the panel is installed."),
    ("Al Mairqab Industrial Investment (Aalaf)", "Chiller room, civil works, SS shelving", 95000, 28500, 0, 66500,
     "30% advance paid 12-11 by crossed cheque (RCT-313). Their LPO delivery date of 17-11 has passed."),
    ("Oscar Prime Trading (2nd job)", "Five cold rooms", 170000, 119000, 0, 51000,
     "The 119,000 advice read “Pending Approval” and has never been confirmed on a statement."),
    ("Bismi Group International", "Freezer room, preparation room, epoxy", 110000, 60000, 0, 50000,
     "Advance complete 17-11. Stage 2 of 28,000 is payable before the machine goes to site."),
    ("One A Design, Build and Trading", "Chiller + freezer — Capital Grille, ABESQ", 73500, 67125, 6375, 0,
     "INV-275 settled in full on 19-10-2026 (advice produced 19-11). Only 6,375 of INV-300 remains."),
    ("M/s. Day to Day Hypermarket", "Chiller room + freezer room", 52000, 26000, 0, 26000,
     "Advance paid in cash. 30% due on panel installation, before the machines go out; 20% at handover."),
    ("Home-Made by Earth", "Chiller + freezer rooms", 46900, 32830, 11725, 2345,
     "INV-290 for the 25% delivery stage. LPO words still read 45,300 against figures of 46,900 (OL-084)."),
    ("Oscar Prime Trading (3rd job)", "Chiller room 4.00 x 3.90 x 2.70 m", 38000, 24700, 0, 13300,
     "65% advance received same day. Balance on completion. No written order on file."),
    ("M/s. Gozl Veterinary Services", "Chiller room, duty and standby", 59800, 47840, 0, 11960,
     "Both stages paid on uncrossed bearer cheques, neither confirmed cleared. Split of the 20% not yet set."),
    ("Oscar Prime Trading (1st job)", "Cold room — final balance", 75000, 64250, 10750, 0,
     "INV-265 issued 29-08-2026. Unpaid for almost three months."),
    ("M/s. Panda Cakes", "Chiller room 4.35 x 2.00 x 2.40 m", 29000, 27550, 0, 1450,
     "INV-295 settled in cash 05-11-2026 (RCT-314). Only the 5% handover retention remains."),
]

UNKNOWN = [
    ("Mr. Hamad Abdulla Al-Sulaiti", "Flower chiller cold room, Semaisma", 25000,
     "Completed in 2026 per Farhan. NO PAYMENT RECORD ON FILE — the balance cannot be stated."),
]

DCTS = [
    ("Oriental Agro Trading", "Cold storage project", 1103286, 1093000, 10286,
     "Doha Cooling contract. 1,093,000 collected across three cheques and eight cash receipts."),
]

tot_contract = sum(r[2] for r in ROWS)
tot_recd = sum(r[3] for r in ROWS)
tot_inv = sum(r[4] for r in ROWS)
tot_notinv = sum(r[5] for r in ROWS)
tot_out = tot_inv + tot_notinv


def rows_main():
    out = []
    for i, (cl, pr, c, r, iv, ni, note) in enumerate(ROWS, 1):
        out.append(
            '<tr><td class="n">%d</td><td><b>%s</b><div class="sub">%s</div></td>'
            '<td class="r">%s</td><td class="r">%s</td><td class="r">%s</td>'
            '<td class="r">%s</td><td class="r b">%s</td></tr>'
            '<tr class="note"><td></td><td colspan="6">%s</td></tr>'
            % (i, cl, pr, q(c), q(r), q(iv) if iv else "&ndash;",
               q(ni) if ni else "&ndash;", q(iv + ni), note))
    return "".join(out)


HTML = u"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>TNDK Receivables</title>
<style>
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; box-sizing: border-box; }
  @page { size: A4; margin: 12mm 9mm; }
  body { font-family: Arial, "Liberation Sans", Helvetica, sans-serif; font-size: 8.5pt;
         color: #222; margin: 0; line-height: 1.35; }
  .band { background: #1F3864; color: #fff; padding: 12pt 14pt 10pt 14pt; }
  .band .co { font-size: 14pt; font-weight: bold; line-height: 1.12; }
  .band .ad { font-size: 7.6pt; padding-top: 3pt; color: #D7DEEB; }
  .band .ttl { font-size: 10.5pt; font-weight: bold; color: #C9A24E; padding-top: 7pt; letter-spacing: .4pt; }
  .rule { background: #C9A24E; height: 3.5pt; font-size: 1pt; }
  .asat { background: #EEF2F8; padding: 5pt 14pt; font-size: 8.2pt; }
  h2 { font-size: 9.6pt; color: #fff; background: #1F3864; padding: 4.5pt 8pt; margin: 12pt 0 0 0; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #DCE3EF; color: #1F3864; font-size: 7.6pt; text-align: right;
       padding: 4pt 6pt; border: 0.5pt solid #C9CDD6; }
  th.l { text-align: left; }
  td { border: 0.5pt solid #C9CDD6; padding: 4pt 6pt; vertical-align: top; }
  td.n { width: 15pt; text-align: center; color: #666; }
  td.r { text-align: right; white-space: nowrap; width: 58pt; }
  td.b { font-weight: bold; color: #1F3864; }
  .sub { font-size: 7.5pt; color: #555; padding-top: 1pt; }
  tr.note td { border-top: 0; font-size: 7.4pt; color: #444; font-style: italic;
               background: #FAFBFD; padding-top: 0; }
  tr.tot td { background: #EEF2F8; font-weight: bold; color: #1F3864; border-top: 1pt solid #1F3864;
              font-style: normal; font-size: 8.5pt; }
  .cards { display: table; width: 100%; margin: 9pt 0 2pt 0; border-spacing: 6pt 0; }
  .card { display: table-cell; width: 33%; background: #EEF2F8; border-left: 3pt solid #C9A24E; padding: 7pt 9pt; }
  .card .k { font-size: 17pt; font-weight: bold; color: #1F3864; line-height: 1; }
  .card .l { font-size: 7.3pt; color: #444; padding-top: 3pt; text-transform: uppercase; letter-spacing: .3pt; }
  .note2 { background: #FFF8E1; border-left: 3pt solid #C9A24E; padding: 7pt 9pt; margin: 9pt 0 0 0; font-size: 7.9pt; }
  .note2 b { color: #1F3864; }
  .foot { background: #1F3864; color: #fff; text-align: center; padding: 6pt; font-size: 7.4pt; margin-top: 12pt; }
  .foot i { color: #C9A24E; }
</style></head><body>

<div class="band">
  <div class="co">THE NEW DOHA KITCHEN EQUIPMENT SERVICES W.L.L.</div>
  <div class="ad">P.O. Box 80247, Doha, State of Qatar&nbsp; |&nbsp; C.R. 199351&nbsp; |&nbsp; Tel: 7706 0676&nbsp; |&nbsp; farhan@dctsqatar.com</div>
  <div class="ttl">AMOUNTS RECEIVABLE FROM CUSTOMERS</div>
</div>
<div class="rule"></div>
<div class="asat"><b>As at 19 November 2026 (revised).</b> Figures in Qatari Riyals.
<b>Al Zahrawi Medical and Everbloom are settled and closed off this list. One A's INV-275 was settled on 19-10-2026 and the advice has only now been produced.</b> <b>HBK-BWTC-BEIL JV (Mesaieed) is excluded at your instruction</b> &mdash; that contract carries a further
QAR 400,000.00 receivable, of which 340,000.00 has never been invoiced.</div>

<div class="cards">
  <div class="card"><div class="k">__OUT__</div><div class="l">Total receivable from customers</div></div>
  <div class="card"><div class="k">__INV__</div><div class="l">Invoiced and awaiting payment</div></div>
  <div class="card"><div class="k">__NOTINV__</div><div class="l">Contracted, not yet invoiced</div></div>
</div>

<h2>RECEIVABLE BY CUSTOMER &mdash; largest first</h2>
<table>
<tr><th class="l">#</th><th class="l">Customer / project</th><th>Contract</th><th>Received</th><th>Invoiced,<br/>unpaid</th><th>Not yet<br/>invoiced</th><th>Total<br/>receivable</th></tr>
__ROWS__
<tr class="tot"><td></td><td>TOTAL &mdash; 12 customers, HBK excluded</td><td class="r">__CONTRACT__</td><td class="r">__RECD__</td><td class="r">__INV__</td><td class="r">__NOTINV__</td><td class="r">__OUT__</td></tr>
</table>

<h2>NOT INCLUDED IN THE TOTAL &mdash; no payment record on file</h2>
<table>
<tr><th class="l">#</th><th class="l">Customer / project</th><th>Contract</th><th class="l" style="text-align:left">Position</th></tr>
<tr><td class="n">1</td><td><b>Mr. Hamad Abdulla Al-Sulaiti</b><div class="sub">Flower chiller cold room, Semaisma</div></td><td class="r">25,000.00</td><td style="font-size:7.6pt">Completed in 2026 per Farhan. <b>No payment record on file</b>, so no balance can be stated. Excluded from every figure above.</td></tr>
</table>

<h2>DOHA COOLING TRADING &amp; SOLUTIONS W.L.L. &mdash; separate entity, C.R. 93354</h2>
<table>
<tr><th class="l">#</th><th class="l">Customer / project</th><th>Contract</th><th>Received</th><th>Receivable</th></tr>
<tr><td class="n">1</td><td><b>Oriental Agro Trading</b><div class="sub">Cold storage project</div></td><td class="r">1,103,286.00</td><td class="r">1,093,000.00</td><td class="r b">10,286.00</td></tr>
</table>

<div class="note2">
<b>Where the money actually is.</b>
&nbsp;<b>1.</b> <b>Three customers hold 59% of everything owed</b> &mdash; CCC 177,450, Aalaf 95,000 and Q Fish 75,000.
&nbsp;<b>2.</b> <b>101,400 of CCC's balance has never been invoiced</b> on a job completed in September, and is the
single easiest sum on this page to turn into cash: the third 30% of 76,050 and the 10% retention of 25,350.
&nbsp;<b>3.</b> <b>Oscar Prime owe 75,050 across three contracts</b>, and 10,750 of it has been invoiced since August.
Their 119,000 advance on the five cold rooms has never been confirmed on a bank statement; if it never landed,
the figure above understates their balance by that amount.
&nbsp;<b>4.</b> <b>One A's 47,775 is fully invoiced and wholly unpaid</b>, the oldest live debt here, chased by letter
on 31-10-2026 with no reply. Their work order carries a 2,000 per day delay penalty, so this one is not simply
a collection matter.
&nbsp;<b>5.</b> <b>Aalaf have paid nothing at all</b> &mdash; 95,000 contracted, advance invoiced on 03-11 and still
outstanding, with their own delivery date of 17-11 already past.
</div>

<div class="foot">
The New Doha Kitchen Equipment Services W.L.L.&nbsp; |&nbsp; P.O. Box 80247, Doha, State of Qatar&nbsp; |&nbsp; C.R. 199351&nbsp; |&nbsp; Tel: 7706 0676<br/>
<i>Internal receivables report &mdash; prepared 19 November 2026 from the order book.</i>
</div>
</body></html>"""

html = (HTML.replace("__ROWS__", rows_main())
        .replace("__CONTRACT__", q(tot_contract))
        .replace("__RECD__", q(tot_recd))
        .replace("__INV__", q(tot_inv))
        .replace("__NOTINV__", q(tot_notinv))
        .replace("__OUT__", q(tot_out)))

out = SP + "/report/receivables.html"
io.open(out, "w", encoding="utf-8").write(html)
print("contract", q(tot_contract), "received", q(tot_recd))
print("invoiced unpaid", q(tot_inv), "| not invoiced", q(tot_notinv), "| TOTAL RECEIVABLE", q(tot_out))
print("check contract-received =", q(tot_contract - tot_recd))
