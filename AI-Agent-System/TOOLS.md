# TOOLS & PERMISSION REGISTER

Current authorised toolset, as decided by Farhan on **3 August 2026**:
**Google Drive only.** Nothing else is connected, and nothing else may be assumed.

## Authorised

| Tool | Level | Scope | Guardrail |
|---|---|---|---|
| **Google Drive — read** | Allowed | `TNDK Documents/` tree only | No unrelated folders. Do not browse the wider Drive. |
| **Google Drive — create** | Allowed | Inside `TNDK Documents/` | New files only. Dated filenames. |
| **Google Drive — overwrite** | **Approval** | Registers especially | Prefer a new dated version over replacing. |
| **Google Drive — delete** | **Forbidden** | — | Supersede and mark. Escalate if removal seems needed. |
| **Local scripts** | Allowed | Generators, calculators, register builders | Deterministic. Output verified before delivery. |
| **Document generation** | Allowed | Invoice / receipt / LPO / quotation / register | Draft status until Farhan approves. |

## Not connected — do not assume, do not simulate

| Capability | Status | Consequence for design |
|---|---|---|
| Email | **Not connected** | COLLECT and ANNUITY draft messages as text. Farhan sends them. |
| WhatsApp | **Not connected** | Enquiries arrive by paste-in only. |
| Bank / accounting system | **Not connected** | Payments are recorded only from what Farhan reports or a slip he provides. |
| Calendar | **Not connected** | Milestone dates tracked in the register, not a calendar. |
| CRM | **Not connected** | The registers *are* the CRM. |
| **Bank WPS upload portal** | **Not connected** | PAYROLL produces a **draft** SIF file. Farhan checks it against the bank's template and uploads it himself. |
| **ADLSA / MOL portal** | **Not connected** | Contracts, permits and cancellations are prepared as checklists and drafts. Nothing is filed by any agent. |
| **HR / attendance system** | **Not connected** | TIME's records are whatever Farhan can actually maintain — a sheet in Drive. A system nobody fills in produces no data. |
| **Biometric / time clock** | **Not connected** | Attendance is entered, not captured. Treat it as a reported figure, not a measured one. |

> An agent that needs a capability it does not have must **say so and stop**, not approximate it.
> "I have drafted the follow-up for you to send" is correct.
> "I have followed up" would be a fabrication.

## The Drive tree — operational source of truth

```
TNDK Documents/                          [1LE14moXA1X6paSMc5dLrOCFz2tlBbLkZ]
├── 01 - Projects/                       [1qTIHCaShk7nCrIPea8DQUdw6iDlC38gy]
│   └── <Client>/                        quotation · invoices · receipts · DN · workbook
├── 02 - Registers/                      [1vJaTmO-LjkwDlmGz09kO96tzQc1H6TVu]
│   ├── approved_register.xlsx           every award to date
│   ├── amounts_to_receive.xlsx          outstanding, split maintenance / project
│   └── margin_log.xlsx                  NEW — quoted vs cost vs realised margin
├── 03 - Under process/                  [1wKVUqP5iZdUCsBKR-HdLkRTiAC-K-8Xj]
│   └── live jobs not yet awarded
└── 04 - HR/                             NEW — to be created
    ├── roster.json                      the one record of who works here
    ├── Personnel/<employee-id>/          contract · QID · health card · certificates
    ├── Timesheets/YYYY-MM/               attendance · overtime · leave · job hours
    ├── Payroll/YYYY-MM/                  register · payslips · draft WPS file
    └── Settlements/                      end-of-service calculations and clearances
```

**`04 - HR/` holds personal data and nothing in it is ever copied into this repo** — not a
name, not a QID, not a wage. `RULES.md` A11. Folders are per employee ID, so a file can be
shared for one purpose without exposing the rest.

`AI-Agent-System/` (this repo) holds the **operating instructions**. Drive holds the **data**.
Instructions are version-controlled; data is live. Do not duplicate data into the repo —
it will drift, which is the exact failure this system exists to fix.

## Permission levels by agent

| Agent | Read | Draft | Create in Drive | Overwrite register | External action |
|---|---|---|---|---|---|
| TNDK-OPS (manager) | ✅ | ✅ | ❌ | ❌ | ❌ |
| SCOPE | ✅ | ✅ | ✅ | ❌ | ❌ |
| **PRICE** | ✅ | ✅ | ✅ | ❌ | ❌ |
| PROCURE | ✅ | ✅ | ✅ | ❌ | ❌ |
| LEDGER | ✅ | ✅ | ✅ | **approval** | ❌ |
| COLLECT | ✅ | ✅ | ✅ | ❌ | ❌ |
| ANNUITY | ✅ | ✅ | ✅ | ❌ | ❌ |
| TNDK-HR (manager) | ✅ HR only | ✅ | ❌ | ❌ | ❌ |
| PEOPLE | ✅ HR only | ✅ | ✅ | **approval** | ❌ |
| TIME | ✅ HR only, **no wage data** | ✅ | ✅ | ❌ | ❌ |
| **PAYROLL** | ✅ HR only | ✅ | ✅ | ❌ | ❌ |
| EXIT | ✅ HR only | ✅ | ✅ | ❌ | ❌ |

**No agent has external action at any trust stage.** That column stays ❌ until Farhan
separately decides to connect a sending capability — a decision, not a drift.

**The HR lanes read `04 - HR/` and nothing else.** They have no reason to open a client
folder or a register, and the commercial lanes have no reason to open a personnel file. That
boundary is the practical form of `RULES.md` A10 — the narrowest access that does the job.

TIME is deliberately the tightest: it records hours and never needs to know what an hour
costs. Wage data would let it check its own arithmetic against a payroll, which is exactly the
independence the two-lane split exists to preserve.
