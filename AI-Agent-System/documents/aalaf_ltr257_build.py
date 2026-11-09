# -*- coding: utf-8 -*-
import io
SP = "/tmp/claude-0/-home-user-ClaudeCode/f198eb8f-5169-5011-a0a8-bd4d87e7e71f/scratchpad"
TPL = "/home/user/ClaudeCode/.claude/skills/tndk-house-format/assets/letter_template.html"

BODY = u"""
<style>table.sig{margin-top:8pt;} .stamp{padding-top:8pt;} p{margin-bottom:7.5pt;} .cal{padding:7pt 12pt;margin:8pt 0;}</style>
<div class="to">
  <div class="nm">Al Mairqab Industrial Investment W.L.L. (Aalaf)</div>
  P.O. Box 295, Doha, State of Qatar<br/>
  <b>Kind attention:</b> Mr. Francis Lloyd De Ramos &mdash; Procurement Manager
</div>

<div class="subj">SUBJECT: CONTRACTING ENTITY FOR THE CHILLER ROOM WORKS &mdash; PURCHASE ORDER
TO BE RAISED ON THE NEW DOHA KITCHEN EQUIPMENT SERVICES W.L.L.</div>

<p>Dear Mr. Francis, with reference to your e-mail regarding the chiller room works and the
quotation and drawings submitted to you, we confirm the following for your procurement records so
that the purchase order may be raised without delay.</p>

<p><b>1. The purchase order is to be raised in the name of The New Doha Kitchen Equipment Services
W.L.L., Commercial Registration No. 199351.</b> That is the company which will execute the works,
raise the invoices and receive the payment for this transaction.</p>

<p><b>2. Both companies are under the same ownership and the same management.</b> The New Doha
Kitchen Equipment Services W.L.L. and Doha Cooling Trading &amp; Solutions W.L.L. share the same
owner, the same office, the same telephone and e-mail, and the same technical and site team. The
persons you have been dealing with throughout are unchanged. <b>For the avoidance of doubt these
are two separately registered companies, and this letter is not a change of name of one into the
other</b> &mdash; it confirms which of the two is to carry this order, stated plainly so that your
records are exact.</p>

<p><b>3. The offer itself does not change in any respect.</b> The New Doha Kitchen Equipment
Services W.L.L. hereby adopts and confirms the quotation and the drawings already submitted to
you in full &mdash; same scope, same drawings and revisions, same prices, same payment terms,
same delivery period and same validity. <b>Nothing is altered by this confirmation and no price
adjustment of any kind arises from it.</b></p>

<p><b>4. Doha Cooling Trading &amp; Solutions W.L.L. makes no claim in respect of this
transaction.</b> It will raise no invoice and seek no payment against this order, and payment made
to The New Doha Kitchen Equipment Services W.L.L. under the purchase order discharges your
obligation in full. <b>All obligations under the quotation are likewise undertaken by this
company</b> &mdash; the works, the warranty and any rectification arising under it &mdash; so that
your recourse for this order lies against it.</p>

<div class="cal">
<b>FOR YOUR PURCHASE ORDER AND PAYMENT RECORDS</b><br/>
<b>Company:</b> The New Doha Kitchen Equipment Services W.L.L. &nbsp;|&nbsp; <b>C.R.:</b> 199351
&nbsp;|&nbsp; P.O. Box 80247, Doha &nbsp;|&nbsp; Tel: 7706 0676 &nbsp;|&nbsp; farhan@dctsqatar.com<br/>
<b>Bank:</b> The Commercial Bank (P.S.Q.C.), Grand Hamad Branch &ndash; 4010 &nbsp;|&nbsp;
<b>A/C:</b> 4010-777739-001 &nbsp;|&nbsp; <b>SWIFT:</b> CBQAQAQA<br/>
<b>IBAN:</b> QA06 CBQA 0000 0000 4010 7777 3900 1 &nbsp;|&nbsp; <b>Account name:</b> exactly as above
&mdash; <i>no word between &ldquo;Equipment&rdquo; and &ldquo;Services&rdquo;</i>
</div>

<p><b>Enclosed herewith</b>, as requested: the Commercial Registration, the Establishment
(Computer) Card, the Tax Card, the bank account certificate issued by The Commercial Bank and the
identification of the authorised signatory. Should anything further be required, kindly advise
and it will be furnished the same day. We look forward to receiving the purchase order.</p>
"""

html = io.open(TPL, encoding="utf-8").read()
subs = {
    "__TITLE__": "Letter LTR/DCTS/257/2026 — Al Mairqab Industrial Investment (Aalaf)",
    "__CONAME__": "THE NEW DOHA KITCHEN EQUIPMENT SERVICES W.L.L.",
    "__COADDR__": "P.O. Box 80247, Doha, State of Qatar&nbsp; |&nbsp; C.R. 199351&nbsp; |&nbsp; "
                  "Tel: 7706 0676&nbsp; |&nbsp; farhan@dctsqatar.com",
    "__COLEGAL__": "The New Doha Kitchen Equipment Services W.L.L.",
    "__B0__": "LETTER",
    "__B1__": "CONFIRMATION",
    "__META__": "<b>REFERENCE:</b>&nbsp;LTR/DCTS/257/2026 &nbsp;&nbsp;&nbsp; "
                "<b>DATE:</b>&nbsp;01 November 2026 &nbsp;&nbsp;&nbsp; "
                "<b>PROJECT:</b>&nbsp;Chiller room works &mdash; Aalaf",
    "__BODY__": BODY,
    "__COFOOT__": "The New Doha Kitchen Equipment Services W.L.L.&nbsp; |&nbsp; P.O. Box 80247, "
                  "Doha, State of Qatar&nbsp; |&nbsp; C.R. 199351&nbsp; |&nbsp; Tel: 7706 0676&nbsp; |&nbsp; "
                  "farhan@dctsqatar.com",
    "__FOOTNOTE__": "This letter is valid when signed and stamped by an authorised signatory of the company.",
}
for k, v in subs.items():
    assert k in html, k
    html = html.replace(k, v)

out = SP + "/letter/aalaf_entity_confirmation.html"
io.open(out, "w", encoding="utf-8").write(html)
print("written", out, len(html))
