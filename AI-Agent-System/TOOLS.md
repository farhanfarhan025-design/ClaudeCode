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
| CRM | **Not connected** | The registers *are* the CRM — `pipeline_register.xlsx` is the whole of it. PROSPECT produces a list and a draft; Farhan makes every approach personally. |

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
│   ├── margin_log.xlsx                  NEW — quoted vs cost vs realised margin
│   └── pipeline_register.xlsx           NEW — every quotation, issue → decision, with reason
└── 03 - Under process/                  [1wKVUqP5iZdUCsBKR-HdLkRTiAC-K-8Xj]
    └── live jobs not yet awarded
```

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
| TNDK-SALES (manager) | ✅ | ✅ | ❌ | ❌ | ❌ |
| PROSPECT | ✅ | ✅ | ✅ | ❌ | ❌ |
| QUALIFY | ✅ | ✅ | ✅ | ❌ | ❌ |
| **PURSUE** | ✅ | ✅ | ✅ | ❌ | ❌ |
| ACCOUNT | ✅ | ✅ | ✅ | ❌ | ❌ |

**No agent has external action at any trust stage.** That column stays ❌ until Farhan
separately decides to connect a sending capability — a decision, not a drift.

## Pricing data — read access by lane

A permission the table above cannot express, and the one that matters most for the sales lanes.

| File | May be read by | Never read by |
|---|---|---|
| Pricing guide / rate card | PRICE, PROCURE | **Every sales lane** |
| Cost build-ups, `margin.py` output | PRICE | **Every sales lane** |
| `margin_log.xlsx` | PRICE, TNDK-OPS | **Every sales lane** |
| `pipeline_register.xlsx` | PURSUE, TNDK-SALES, PRICE *(for win/loss by tier)* | — |

PRICE passes the **tier and reason code** to PURSUE for win/loss analysis. That is the only
pricing data that crosses into the sales division, it arrives as analysis data, and it may be
reported to Farhan but never repeated to a client. `RULES.md` A9.

The restriction is deliberate rather than bureaucratic: a lane that cannot see a cost cannot
be argued into quoting one.
