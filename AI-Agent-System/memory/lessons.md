# LESSONS

What went wrong, what rule changed as a result. Every entry names the playbook it modified.
This file is how the system stops repeating a mistake — an entry with no rule change is just
a complaint.

---

### L-001 — A documented default is not a control
**Observed:** 2026-08-03 · **Source:** pricing-guide.md worked example

The pricing guide names 30% as the default markup for new clients. The guide's own worked
example prices the job at 14.6%. The policy was written down, understood, and not followed —
in the same document that stated it.

**Cause:** nothing computed realised margin at the moment of quoting. The default existed as
guidance, not as a gate.

**Rule change:** PRICE computes realised margin on every quote and blocks below-floor prices
pending a logged override. Written into `agents/price/PLAYBOOK.md` §5 and enforced by
`scripts/margin.py` exit code 2.

**Generalisation:** a rule that is not computed at the decision point is a preference, not a
control. When adding any future rule, ask where it gets *checked*.

---

### L-002 — Spreadsheet totals fail silently
**Observed:** 2026-08-03 · **Source:** live `approved_register.xlsx`

The register's total row summed only the first three of eight rows, returning 18,250 against a
real book of 758,100. The balance column read 0.00 on every row. The summary block read zero.
Nothing in the file looked broken — the numbers were plausible-looking and confidently wrong.

**Cause:** formula ranges not extended as rows were added, and/or the recalculation step
(`recalc.py`) not run before upload. Both are silent failures.

**Rule change:** the monthly register integrity audit in `HEARTBEAT.md` explicitly verifies
that Contract − Received = Balance on **every** row and that the total covers **all** rows.
Registers are rebuilt from source data with computed values, not trusted formulas.

**Generalisation:** a number that displays is not a number that is correct. Any figure used for
a decision gets recomputed independently, not read.

---

### L-003 — Copies of data diverge; there must be one source
**Observed:** 2026-08-03 · **Source:** Samoosa figures in three places

Samoosa's contract value appears as 38,500 in the live register, 39,375 in the skill's sample
data, and its received amount as 20,000 or 31,500 depending which file is read. All three were
written by the same operation.

**Cause:** register data was duplicated into the skill's assets. Copies drift by default.

**Rule change:** `DECISIONS.md` D-001 — Drive is the single operational source of truth. The
repo holds instructions only; data is never duplicated into it. `MEMORY_POLICY.md` conflict
rule: when memory disagrees with a live document, the document wins **and the conflict is
reported**, not silently resolved.

---

### L-004 — Making the bottleneck faster does not remove it
**Observed:** 2026-08-03 · **Source:** structure of the three existing TNDK skills

The quotation, LPO and accounts skills are genuinely good engineering — templates, schemas,
generators, QA checks. They cut the time to produce each document substantially. But every one
of them still starts with Farhan deciding to run it, and ends with Farhan checking the output.

**Cause:** the skills automated *production*, which was never the constraint. The constraint is
that one person holds every decision, every trigger, and every follow-up.

**Rule change:** the agent architecture assigns **triggers** (`HEARTBEAT.md`) and **ownership**
(each agent's Definition of Done), not just execution. `GOALS.md` G6 measures owner-touches per
job rather than time per document.

**Generalisation:** before automating a task, ask whether the task or the *decision to do the
task* is the bottleneck.
