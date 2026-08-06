#!/usr/bin/env python3
"""
TNDK payroll, compliance and end-of-service calculator.

Three jobs, all deterministic:

  1. `run`   — monthly payroll register + a draft WPS SIF file
  2. `check` — roster compliance sweep + accrued end-of-service liability
  3. `eos`   — final settlement for one leaver

Design intent matches scripts/margin.py: compute the number, show the build-up,
and fail loudly rather than produce a plausible-looking answer. A blocking
compliance failure exits with code 2 so a wrapper can gate on it.

Every statutory parameter lives in DEFAULT_POLICY below and is overridable from
the roster file. None of them has been verified against the current ADLSA text
by this system — see agents/hr/LABOUR_LAW.md. Confirm before the first live run.

Usage
-----
    python3 payroll.py check --roster roster.json
    python3 payroll.py run   --roster roster.json --period 2026-08.json
    python3 payroll.py run   --roster roster.json --period 2026-08.json --sif out/
    python3 payroll.py eos   --roster roster.json --employee TNDK-003 \
                             --last-day 2026-09-30 --reason resignation

File formats: scripts/examples/payroll_roster.json, payroll_2026_08.json
"""

import argparse
import calendar
import datetime as dt
import json
import os
import sys

# --- Statutory / policy parameters -----------------------------------------
# Sources named in agents/hr/LABOUR_LAW.md. Verification status of every one:
# TO VERIFY. Override in the roster's "policy" block, never by editing a run.
DEFAULT_POLICY = {
    # Minimum wage — Law No. 17 of 2020 (in force March 2021)
    "min_basic": 1000.0,
    "min_food_allowance": 500.0,           # waived if food is actually provided
    "min_accommodation_allowance": 300.0,  # waived if accommodation is provided

    # Overtime — Labour Law Art. 74-75
    "ot_divisor_hours": 240.0,             # basic / 240 = hourly (30 days x 8h)
    "ot_normal_multiplier": 1.25,
    "ot_night_multiplier": 1.50,
    "ot_restday_multiplier": 1.50,

    # Absence / unpaid leave
    "absence_divisor_days": 30.0,
    "absence_basis": "total",              # "total" (basic + allowances) or "basic"

    # Deduction cap — Art. 71
    "deduction_cap_pct": 0.10,

    # Annual leave — Art. 79
    "annual_leave_days_under_5y": 21.0,
    "annual_leave_days_from_5y": 28.0,

    # End of service gratuity — Art. 54: 3 weeks basic per year, min 1 year
    "gratuity_days_per_year": 21.0,
    "gratuity_divisor_days": 30.0,
    "gratuity_min_service_days": 365.0,

    # Wage payment window — Art. 66 as amended by Decree-Law No. 1 of 2015
    "payment_window_days": 7,

    # Warning horizon for QID / contract / health card expiry
    "expiry_warning_days": 90,

    # Social insurance — Qatari nationals only. Expatriate rate is zero.
    "social_insurance_employee_pct": 0.05,

    "salary_frequency": "M",               # WPS: M = monthly
    "sif_version": "1",
}

BLOCK = "BLOCK"
FLAG = "FLAG"


# --- helpers ---------------------------------------------------------------

def money(x):
    return f"{x:>12,.2f}"


def d(s):
    return dt.date.fromisoformat(s)


def days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


def service_days(joined, as_of):
    return (as_of - joined).days


def service_text(days):
    y, rem = divmod(days, 365)
    return f"{y}y {rem // 30}m ({days} days)"


def allowance_total(emp):
    return sum(float(v) for v in emp.get("allowances", {}).values())


def policy_of(roster):
    p = dict(DEFAULT_POLICY)
    p.update(roster.get("policy", {}))
    return p


def active(roster):
    return [e for e in roster["employees"] if e.get("status", "active") == "active"]


def find(roster, emp_id):
    for e in roster["employees"]:
        if e["id"] == emp_id:
            return e
    raise SystemExit(f"employee not found in roster: {emp_id}")


# --- compliance ------------------------------------------------------------

def wage_structure_checks(emp, pol):
    """Statutory minimums and WPS readiness. Independent of any month."""
    out = []
    eid = emp["id"]
    basic = float(emp["basic"])
    allow = emp.get("allowances", {})

    if basic < pol["min_basic"]:
        out.append((BLOCK, "MIN-BASIC",
                    f"{eid}: basic {basic:,.2f} is below the statutory minimum "
                    f"{pol['min_basic']:,.2f} (Law 17/2020)"))

    if not emp.get("food_provided", False):
        food = float(allow.get("food", 0.0))
        if food < pol["min_food_allowance"]:
            out.append((BLOCK, "MIN-FOOD",
                        f"{eid}: food allowance {food:,.2f} is below "
                        f"{pol['min_food_allowance']:,.2f} and food is not provided"))

    if not emp.get("accommodation_provided", False):
        acc = float(allow.get("accommodation", 0.0))
        if acc < pol["min_accommodation_allowance"]:
            out.append((BLOCK, "MIN-ACCOM",
                        f"{eid}: accommodation allowance {acc:,.2f} is below "
                        f"{pol['min_accommodation_allowance']:,.2f} and accommodation "
                        f"is not provided"))

    bank = emp.get("bank", {})
    if not bank.get("iban"):
        out.append((BLOCK, "NO-IBAN", f"{eid}: no IBAN — cannot be paid through WPS"))
    if not bank.get("short_name"):
        out.append((BLOCK, "NO-BANK",
                    f"{eid}: no bank short name — WPS record incomplete"))
    if not emp.get("qid"):
        out.append((BLOCK, "NO-QID", f"{eid}: no QID — WPS record incomplete"))

    return out


def expiry_checks(emp, pol, as_of):
    out = []
    eid = emp["id"]
    horizon = pol["expiry_warning_days"]
    for field, label in [("qid_expiry", "QID"),
                         ("contract_expiry", "contract"),
                         ("health_card_expiry", "health card"),
                         ("passport_expiry", "passport")]:
        raw = emp.get(field)
        if not raw:
            out.append((FLAG, "NO-EXPIRY", f"{eid}: {label} expiry not recorded"))
            continue
        left = (d(raw) - as_of).days
        if left < 0:
            out.append((BLOCK, "EXPIRED",
                        f"{eid}: {label} EXPIRED {abs(left)} days ago ({raw})"))
        elif left <= horizon:
            out.append((FLAG, "EXPIRING",
                        f"{eid}: {label} expires in {left} days ({raw})"))
    return out


def employer_checks(roster):
    out = []
    er = roster.get("employer", {})
    for key, label in [("establishment_id", "MOL establishment ID"),
                       ("qid", "company QID / CR"),
                       ("bank_short_name", "employer bank short name")]:
        val = str(er.get(key, "") or "")
        if not val or val.upper().startswith("REPLACE"):
            out.append((BLOCK, "EMPLOYER-ID",
                        f"employer {label} not supplied — no WPS file can be produced"))
    return out


# --- monthly payroll -------------------------------------------------------

def compute_month(emp, per, pol, year, month):
    """One employee, one month. Returns the full build-up."""
    basic = float(emp["basic"])
    allow = allowance_total(emp)
    dim = days_in_month(year, month)

    hourly = basic / pol["ot_divisor_hours"]
    ot_lines = []
    for key, mult_key, label in [
        ("ot_normal_hours", "ot_normal_multiplier", "Overtime — normal"),
        ("ot_night_hours", "ot_night_multiplier", "Overtime — night 21:00-06:00"),
        ("ot_restday_hours", "ot_restday_multiplier", "Overtime — rest day / Friday"),
    ]:
        hours = float(per.get(key, 0) or 0)
        if hours:
            rate = hourly * pol[mult_key]
            ot_lines.append({
                "item": label,
                "detail": f"{hours:g} h @ {rate:,.4f}"
                          f"   ({hourly:,.4f} basic hourly x {pol[mult_key]})",
                "amount": hours * rate,
            })
    ot_total = sum(l["amount"] for l in ot_lines)

    unpaid_days = float(per.get("unpaid_days", 0) or 0)
    absence_base = basic + allow if pol["absence_basis"] == "total" else basic
    absence = (absence_base / pol["absence_divisor_days"]) * unpaid_days

    additions = [{"item": f"Addition — {a['item']}",
                  "amount": float(a["amount"])} for a in per.get("additions", [])]
    deductions = [{"item": f"Deduction — {x['item']}",
                   "amount": float(x["amount"])} for x in per.get("deductions", [])]
    addition_total = sum(a["amount"] for a in additions)
    deduction_total = sum(x["amount"] for x in deductions)

    social_pct = (pol["social_insurance_employee_pct"]
                  if emp.get("qatari", False) else 0.0)
    social = basic * social_pct

    gross = basic + allow + ot_total + addition_total - absence
    net = gross - deduction_total - social

    return {
        "id": emp["id"], "name": emp["name"],
        "basic": basic, "allowances": allow,
        "allowance_detail": emp.get("allowances", {}),
        "ot_lines": ot_lines, "ot_total": ot_total, "hourly": hourly,
        "unpaid_days": unpaid_days, "absence": absence,
        "additions": additions, "addition_total": addition_total,
        "deductions": deductions, "deduction_total": deduction_total,
        "social": social, "social_pct": social_pct,
        "gross": gross, "net": net,
        "working_days": dim - unpaid_days, "days_in_month": dim,
        "job_hours": per.get("job_hours", {}),
    }


def month_checks(r, pol):
    out = []
    eid = r["id"]
    if r["net"] < 0:
        out.append((BLOCK, "NEGATIVE-NET",
                    f"{eid}: net pay is negative ({r['net']:,.2f}) — "
                    f"deductions exceed the wage"))
    if r["gross"] > 0 and r["deduction_total"] > 0:
        pct = r["deduction_total"] / r["gross"]
        if pct > pol["deduction_cap_pct"] + 1e-9:
            out.append((FLAG, "DEDUCTION-CAP",
                        f"{eid}: deductions are {pct*100:.1f}% of gross, above the "
                        f"{pol['deduction_cap_pct']*100:.0f}% cap (Art. 71) — needs "
                        f"Farhan's written instruction before this run is approved"))
    return out


# --- end of service --------------------------------------------------------

def compute_eos(emp, pol, last_day, reason, leave_balance=None,
                notice_days=0.0, outstanding=0.0):
    basic = float(emp["basic"])
    allow = allowance_total(emp)
    total_wage = basic + allow
    joined = d(emp["joined"])
    sdays = service_days(joined, last_day)
    years = sdays / 365.0

    daily_basic = basic / pol["gratuity_divisor_days"]
    daily_total = total_wage / pol["gratuity_divisor_days"]

    eligible = sdays >= pol["gratuity_min_service_days"]
    gratuity = daily_basic * pol["gratuity_days_per_year"] * years if eligible else 0.0

    entitlement = (pol["annual_leave_days_from_5y"] if years >= 5
                   else pol["annual_leave_days_under_5y"])

    if leave_balance is None:
        leave_balance = emp.get("leave_balance_days")
    leave_pay = None if leave_balance is None else daily_total * float(leave_balance)
    notice_pay = daily_total * float(notice_days) if notice_days else 0.0

    dim = days_in_month(last_day.year, last_day.month)
    final_month = (total_wage / dim) * last_day.day

    flags = []
    if not eligible:
        flags.append((FLAG, "NO-GRATUITY",
                      f"service {service_text(sdays)} is under "
                      f"{pol['gratuity_min_service_days']:.0f} days — no gratuity "
                      f"accrues (Art. 54)"))
    if leave_balance is None:
        flags.append((BLOCK, "NO-LEAVE-BALANCE",
                      "accrued leave balance unknown — the settlement is incomplete. "
                      f"TIME must supply days taken against {entitlement:.0f} days/year"))
    if reason == "dismissal":
        flags.append((FLAG, "ART-61",
                      "dismissal — entitlement may be affected under Art. 61. That is a "
                      "legal determination, not a calculation. Escalate before paying."))
    if not emp.get("repatriation_ticket_estimate"):
        flags.append((FLAG, "REPATRIATION",
                      "repatriation obligation not costed (Art. 55) — it is a real cost "
                      "of this exit and belongs in the figure Farhan approves"))

    total = final_month + gratuity + (leave_pay or 0.0) + notice_pay - outstanding

    return {
        "id": emp["id"], "name": emp["name"], "joined": joined, "last_day": last_day,
        "service_days": sdays, "service_text": service_text(sdays), "years": years,
        "basic": basic, "allowances": allow, "total_wage": total_wage,
        "daily_basic": daily_basic, "daily_total": daily_total,
        "eligible": eligible, "gratuity": gratuity, "entitlement": entitlement,
        "leave_balance": leave_balance, "leave_pay": leave_pay,
        "notice_days": notice_days, "notice_pay": notice_pay,
        "final_month": final_month, "outstanding": outstanding,
        "total": total, "reason": reason, "flags": flags,
    }


def accrued_gratuity(emp, pol, as_of):
    """What this employee would be owed if they left today — the hidden liability."""
    sdays = service_days(d(emp["joined"]), as_of)
    if sdays < pol["gratuity_min_service_days"]:
        return 0.0, sdays
    daily = float(emp["basic"]) / pol["gratuity_divisor_days"]
    return daily * pol["gratuity_days_per_year"] * (sdays / 365.0), sdays


# --- WPS SIF ---------------------------------------------------------------

SIF_WARNING = ("DRAFT — the record layout below follows the commonly published Qatar "
               "WPS structure and has NOT been validated against TNDK's own bank "
               "template. Check every field against the bank's current spec before "
               "upload. Nothing here submits anything (RULES.md A2).")


def sif_records(roster, results, pol, year, month, created):
    """Qatar WPS Salary Information File — EDR lines, then the SCR control line."""
    emp_by_id = {e["id"]: e for e in roster["employees"]}
    er = roster.get("employer", {})
    rows = []
    for r in results:
        e = emp_by_id[r["id"]]
        rows.append([
            "EDR",
            e.get("qid", ""),
            e.get("visa_id", ""),
            e["name"],
            e.get("bank", {}).get("short_name", ""),
            e.get("bank", {}).get("iban", ""),
            pol["salary_frequency"],
            f"{r['working_days']:g}",
            f"{r['net']:.2f}",
            f"{r['basic']:.2f}",
            f"{r['ot_total']:.2f}",
            f"{r['allowances'] + r['addition_total']:.2f}",
            f"{r['deduction_total'] + r['absence'] + r['social']:.2f}",
            "1",                                   # payment type 1 = bank transfer
            e.get("wps_note", ""),
        ])
    rows.append([
        "SCR",
        er.get("establishment_id", ""),
        created.strftime("%d%m%Y"),
        created.strftime("%H%M"),
        f"{year:04d}{month:02d}",
        er.get("establishment_id", ""),
        er.get("qid", ""),
        pol["salary_frequency"],
        f"{sum(r['net'] for r in results):.2f}",
        str(len(results)),
        pol["sif_version"],
        er.get("bank_short_name", ""),
    ])
    return rows


def write_sif(path, rows):
    with open(path, "w", newline="") as f:
        for row in rows:
            f.write(",".join(str(c) for c in row) + "\n")
    return path


# --- reports ---------------------------------------------------------------

def issue_block(issues, header="COMPLIANCE"):
    blocks = [i for i in issues if i[0] == BLOCK]
    flags = [i for i in issues if i[0] == FLAG]
    out = ["=" * 74,
           f"  {header}   ·   {len(blocks)} blocking, {len(flags)} to review",
           "=" * 74]
    if not issues:
        out.append("  Nothing found against the parameters in this roster.")
    for level, code, msg in blocks + flags:
        marker = "***" if level == BLOCK else "  -"
        out.append(f"  {marker} [{code}] {msg}")
    return "\n".join(out)


def report_run(roster, results, pol, year, month, issues):
    out = []
    A = out.append
    er = roster.get("employer", {})
    A("=" * 74)
    A(f"  PAYROLL — {calendar.month_name[month]} {year}")
    A(f"  {er.get('name', 'TNDK')}   ·   {len(results)} employee(s)"
      f"   ·   {days_in_month(year, month)} calendar days")
    A("=" * 74)

    for r in results:
        A(f"  {r['id']}  {r['name']}")
        A(f"      {'Basic':<42}{money(r['basic'])}")
        for k, v in r["allowance_detail"].items():
            A(f"      {'Allowance — ' + k:<42}{money(float(v))}")
        for l in r["ot_lines"]:
            A(f"      {l['item']:<42}{money(l['amount'])}")
            A(f"          {l['detail']}")
        for a in r["additions"]:
            A(f"      {a['item'][:42]:<42}{money(a['amount'])}")
        if r["unpaid_days"]:
            label = f"Unpaid absence ({r['unpaid_days']:g} days)"
            A(f"      {label:<42}{money(-r['absence'])}")
        A(f"      {'GROSS':<42}{money(r['gross'])}")
        for x in r["deductions"]:
            A(f"      {x['item']:<42}{money(-x['amount'])}")
        if r["social"]:
            label = f"Social insurance ({r['social_pct']*100:.0f}% of basic)"
            A(f"      {label:<42}{money(-r['social'])}")
        A(f"      {'NET PAYABLE':<42}{money(r['net'])}")
        A("")

    A("-" * 74)
    absence = sum(r["absence"] for r in results)
    A(f"  {'TOTAL EARNED (basic + allowances + OT + additions)':<44}"
      f"{money(sum(r['gross'] + r['absence'] for r in results))}")
    if absence:
        A(f"  {'Less unpaid absence':<44}{money(-absence)}")
    A(f"  {'TOTAL GROSS':<44}{money(sum(r['gross'] for r in results))}")
    A(f"  {'Less deductions and social insurance':<44}"
      f"{money(-sum(r['deduction_total'] + r['social'] for r in results))}")
    A(f"  {'TOTAL NET — WPS TRANSFER VALUE':<44}{money(sum(r['net'] for r in results))}")
    A("=" * 74)
    A(issue_block(issues))
    A("")
    A("  DRAFT — NOT PAID, NOT UPLOADED. Farhan approves the run, Farhan uploads.")
    return "\n".join(out)


def report_check(roster, pol, as_of, issues, liability):
    out = []
    A = out.append
    A("=" * 74)
    A(f"  HR COMPLIANCE SWEEP — as at {as_of.isoformat()}")
    A(f"  {roster.get('employer', {}).get('name', 'TNDK')}"
      f"   ·   {len(active(roster))} active employee(s)")
    A("=" * 74)
    A("  ACCRUED END-OF-SERVICE LIABILITY  (if everyone left today)")
    for row in liability:
        A(f"  {row['id']:<10}{row['name']:<26}{row['service']:<20}"
          f"{money(row['gratuity'])}")
    A("-" * 74)
    A(f"  {'TOTAL ACCRUED GRATUITY':<56}"
      f"{money(sum(r['gratuity'] for r in liability))}")
    A("=" * 74)
    A(issue_block(issues))
    return "\n".join(out)


def report_eos(e, pol):
    out = []
    A = out.append
    A("=" * 74)
    A(f"  FINAL SETTLEMENT — {e['id']}  {e['name']}")
    A(f"  Joined {e['joined']}   ·   Last day {e['last_day']}   ·   "
      f"Service {e['service_text']}")
    A(f"  Reason: {e['reason']}")
    A("=" * 74)
    A(f"  {'Basic wage':<44}{money(e['basic'])}")
    A(f"  {'Allowances':<44}{money(e['allowances'])}")
    A(f"  {'Daily rate on basic (basic / 30)':<44}{money(e['daily_basic'])}")
    A(f"  {'Daily rate on total wage':<44}{money(e['daily_total'])}")
    A("-" * 74)
    A(f"  {'Final month wage to last working day':<44}{money(e['final_month'])}")
    if e["eligible"]:
        A(f"  {'Gratuity — Art. 54':<44}{money(e['gratuity'])}")
        A(f"      {e['daily_basic']:,.4f} x {pol['gratuity_days_per_year']:.0f} days "
          f"x {e['years']:.4f} years")
    else:
        A(f"  {'Gratuity — under 1 year, none accrues':<44}{money(0.0)}")
    if e["leave_pay"] is None:
        A(f"  {'Leave encashment — BALANCE UNKNOWN':<44}{'—':>12}")
    else:
        A(f"  {'Leave encashment':<44}{money(e['leave_pay'])}")
        A(f"      {e['leave_balance']:g} days @ {e['daily_total']:,.4f}"
          f"   (entitlement {e['entitlement']:.0f} days/year)")
    if e["notice_pay"]:
        A(f"  {'Notice paid in lieu':<44}{money(e['notice_pay'])}")
        A(f"      {e['notice_days']:g} days @ {e['daily_total']:,.4f}")
    if e["outstanding"]:
        A(f"  {'Less outstanding advances':<44}{money(-e['outstanding'])}")
    A("-" * 74)
    A(f"  {'TOTAL SETTLEMENT':<44}{money(e['total'])}")
    if e["leave_pay"] is None:
        A("  (incomplete — leave encashment not included)")
    A("=" * 74)
    A(issue_block(e["flags"], "SETTLEMENT NOTES"))
    A("")
    A("  DRAFT — NOT PAID. Requires Farhan's approval (RULES.md B).")
    return "\n".join(out)


# --- commands --------------------------------------------------------------

def load(path):
    with open(path) as f:
        return json.load(f)


def cmd_check(args):
    roster = load(args.roster)
    pol = policy_of(roster)
    as_of = d(args.as_of) if args.as_of else dt.date.today()

    issues = employer_checks(roster)
    liability = []
    for emp in active(roster):
        issues += wage_structure_checks(emp, pol)
        issues += expiry_checks(emp, pol, as_of)
        g, sdays = accrued_gratuity(emp, pol, as_of)
        liability.append({"id": emp["id"], "name": emp["name"],
                          "service": service_text(sdays), "gratuity": g})

    if args.json:
        print(json.dumps({
            "as_of": as_of.isoformat(),
            "headcount": len(active(roster)),
            "accrued_gratuity_total": round(sum(r["gratuity"] for r in liability), 2),
            "accrued_gratuity": [{"id": r["id"], "amount": round(r["gratuity"], 2)}
                                 for r in liability],
            "blocking": [{"code": c, "message": m} for lv, c, m in issues if lv == BLOCK],
            "flags": [{"code": c, "message": m} for lv, c, m in issues if lv == FLAG],
        }, indent=2))
    else:
        print(report_check(roster, pol, as_of, issues, liability))

    return 2 if any(lv == BLOCK for lv, _, _ in issues) else 0


def cmd_run(args):
    roster = load(args.roster)
    pol = policy_of(roster)
    period = load(args.period) if args.period else {}
    month_str = period.get("month") or args.month
    if not month_str:
        raise SystemExit("no month: give --month YYYY-MM or a period file with \"month\"")
    year, month = (int(x) for x in month_str.split("-")[:2])

    per_by_id = {p["id"]: p for p in period.get("entries", [])}
    issues = employer_checks(roster)
    results = []
    for emp in active(roster):
        per = per_by_id.get(emp["id"], {})
        r = compute_month(emp, per, pol, year, month)
        results.append(r)
        issues += wage_structure_checks(emp, pol)
        issues += month_checks(r, pol)

    unknown = set(per_by_id) - {e["id"] for e in active(roster)}
    for u in sorted(unknown):
        issues.append((BLOCK, "UNKNOWN-EMPLOYEE",
                       f"period file has an entry for {u}, who is not active in the "
                       f"roster — the two files disagree"))

    blocking = any(lv == BLOCK for lv, _, _ in issues)

    if args.sif:
        if blocking:
            issues.append((BLOCK, "SIF-WITHHELD",
                           "WPS file not written — blocking compliance failures above"))
        else:
            os.makedirs(args.sif, exist_ok=True)
            eid = roster.get("employer", {}).get("establishment_id", "EID")
            name = f"WPS-SIF-{eid}-{year:04d}{month:02d}-DRAFT.csv"
            path = write_sif(os.path.join(args.sif, name),
                             sif_records(roster, results, pol, year, month,
                                         dt.datetime.now()))
            issues.append((FLAG, "SIF-DRAFT", f"draft WPS file written: {path}. "
                                              + SIF_WARNING))

    if args.json:
        print(json.dumps({
            "month": f"{year:04d}-{month:02d}",
            "headcount": len(results),
            "total_gross": round(sum(r["gross"] for r in results), 2),
            "total_net": round(sum(r["net"] for r in results), 2),
            "employees": [{"id": r["id"], "gross": round(r["gross"], 2),
                           "overtime": round(r["ot_total"], 2),
                           "deductions": round(r["deduction_total"], 2),
                           "net": round(r["net"], 2),
                           "job_hours": r["job_hours"]} for r in results],
            "blocking": [{"code": c, "message": m} for lv, c, m in issues if lv == BLOCK],
            "flags": [{"code": c, "message": m} for lv, c, m in issues if lv == FLAG],
            "status": "BLOCKED_ON_COMPLIANCE" if blocking else "READY_FOR_APPROVAL",
            "human_review_required": True,
        }, indent=2))
    else:
        print(report_run(roster, results, pol, year, month, issues))

    return 2 if blocking else 0


def cmd_eos(args):
    roster = load(args.roster)
    pol = policy_of(roster)
    emp = find(roster, args.employee)
    e = compute_eos(emp, pol, d(args.last_day), args.reason,
                    leave_balance=args.leave_balance,
                    notice_days=args.notice_days,
                    outstanding=args.outstanding)
    if args.json:
        print(json.dumps({
            "id": e["id"], "last_day": e["last_day"].isoformat(),
            "service_days": e["service_days"],
            "final_month": round(e["final_month"], 2),
            "gratuity": round(e["gratuity"], 2),
            "leave_pay": None if e["leave_pay"] is None else round(e["leave_pay"], 2),
            "notice_pay": round(e["notice_pay"], 2),
            "outstanding": round(e["outstanding"], 2),
            "total": round(e["total"], 2),
            "blocking": [{"code": c, "message": m}
                         for lv, c, m in e["flags"] if lv == BLOCK],
            "flags": [{"code": c, "message": m}
                      for lv, c, m in e["flags"] if lv == FLAG],
            "human_review_required": True,
        }, indent=2))
    else:
        print(report_eos(e, pol))
    return 2 if any(lv == BLOCK for lv, _, _ in e["flags"]) else 0


def main():
    ap = argparse.ArgumentParser(description="TNDK payroll and HR compliance calculator")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="roster compliance sweep + accrued gratuity")
    c.add_argument("--roster", required=True)
    c.add_argument("--as-of", default=None, help="YYYY-MM-DD, default today")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_check)

    r = sub.add_parser("run", help="monthly payroll run")
    r.add_argument("--roster", required=True)
    r.add_argument("--period", default=None, help="month variables: OT, absence, etc.")
    r.add_argument("--month", default=None, help="YYYY-MM if no period file")
    r.add_argument("--sif", default=None, metavar="DIR",
                   help="write a draft WPS SIF file into DIR")
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_run)

    e = sub.add_parser("eos", help="end-of-service settlement for one employee")
    e.add_argument("--roster", required=True)
    e.add_argument("--employee", required=True)
    e.add_argument("--last-day", required=True, help="YYYY-MM-DD")
    e.add_argument("--reason", default="resignation",
                   choices=["resignation", "end_of_contract", "dismissal", "mutual"])
    e.add_argument("--leave-balance", type=float, default=None,
                   help="untaken annual leave days")
    e.add_argument("--notice-days", type=float, default=0.0)
    e.add_argument("--outstanding", type=float, default=0.0,
                   help="advances or loans still owed")
    e.add_argument("--json", action="store_true")
    e.set_defaults(func=cmd_eos)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
