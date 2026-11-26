# -*- coding: utf-8 -*-
import io
SP = "/tmp/claude-0/-home-user-ClaudeCode/f198eb8f-5169-5011-a0a8-bd4d87e7e71f/scratchpad"
TPL = "/home/user/ClaudeCode/.claude/skills/tndk-house-format/assets/letter_template.html"

BODY = u"""
<div class="to">
  <div class="nm">One A Design, Build and Trading W.L.L.</div>
  Doha, State of Qatar<br/>
  <b>Kind attention:</b> The Management
</div>

<div class="subj">SUBJECT: REQUEST FOR RELEASE OF THE PAYMENT DUE &mdash; WATER-COOLED CONDENSING UNIT HELD IN RESERVE</div>

<p>Dear Sir,</p>

<p>Good day, and thank you as always for your valued business. We write with reference to the
payment presently due to us under the above project, which we should be grateful if you would
kindly arrange to release.</p>

<p><b>The water-cooled condensing unit required for your works has been reserved and is being
held for you.</b> It was secured on your account and has been set aside since, and we have not
offered it elsewhere in the meantime because it is earmarked for your project.</p>

<p>We have now been awaiting the credit of the payment for some days and have not had a reply
from your side on the matter, which we are sure is no more than an oversight in a busy period.</p>

<p><b>We have, however, received a fresh enquiry for a unit of the same specification</b>, and we
are not able to hold the unit in reserve indefinitely. We would therefore request, most humbly,
that <b>the payment be released within the coming two (2) days</b>. Should it not be possible for
you to do so, we shall unfortunately be left with no choice but to release the unit to another
client, which neither of us would wish.</p>

<p><b>We would ask you to note the consequence of that carefully.</b> A replacement unit of this
specification is not available from stock. Once a fresh order is placed with the manufacturer,
the delivery lead time is <b>60 to 75 days</b>. Losing the unit now would therefore put the
completion of your works back by that period, and no effort on our part could recover it.</p>

<p>Our materials are ready, our team is available, and we are in every respect prepared to carry
the works through to completion within the agreed programme. <b>The release of the payment is the
only step now outstanding on our side.</b> We should accordingly be most grateful for your kind
support in arranging it at the earliest, so that the unit remains reserved for you and the work
is completed in the time given.</p>

<p>Any delay in completion arising from the awaited payment, or from the consequent unavailability
of the unit, will not be attributable to us, and we record the position here in good faith and in
the spirit of keeping you fully informed rather than by way of any complaint.</p>

<p>We remain at your service, and should you wish to discuss the matter we would be glad to
attend your office at your convenience. Thanking you in anticipation of your kind and prompt
support.</p>
"""

html = io.open(TPL, encoding="utf-8").read()
subs = {
    "__TITLE__": "Letter LTR/DCTS/256/2026 — One A Design, Build and Trading W.L.L.",
    "__CONAME__": "THE NEW DOHA KITCHEN EQUIPMENT SERVICES W.L.L.",
    "__COADDR__": "P.O. Box 80247, Doha, State of Qatar&nbsp; |&nbsp; C.R. 199351&nbsp; |&nbsp; "
                  "Tel: 7706 0676&nbsp; |&nbsp; farhan@dctsqatar.com",
    "__COLEGAL__": "The New Doha Kitchen Equipment Services W.L.L.",
    "__B0__": "LETTER",
    "__B1__": "REMINDER",
    "__META__": "<b>REFERENCE:</b>&nbsp;LTR/DCTS/256/2026 &nbsp;&nbsp;&nbsp; "
                "<b>DATE:</b>&nbsp;31 October 2026 &nbsp;&nbsp;&nbsp; "
                "<b>PROJECT:</b>&nbsp;Chiller and freezer rooms &mdash; Capital Grille at ABESQ Hotel",
    "__BODY__": BODY,
    "__COFOOT__": "The New Doha Kitchen Equipment Services W.L.L.&nbsp; |&nbsp; P.O. Box 80247, "
                  "Doha, State of Qatar&nbsp; |&nbsp; C.R. 199351&nbsp; |&nbsp; Tel: 7706 0676&nbsp; |&nbsp; "
                  "farhan@dctsqatar.com",
    "__FOOTNOTE__": "This letter is valid when signed and stamped by an authorised signatory of the company.",
}
for k, v in subs.items():
    assert k in html, k
    html = html.replace(k, v)

out = SP + "/letter/onea_payment_reminder.html"
io.open(out, "w", encoding="utf-8").write(html)
print("written", out, len(html))
