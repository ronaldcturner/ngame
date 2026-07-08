# NGAME and Auditor Use Cases — Scope Boundary

**Status:** Draft  
**Purpose:** Clarify which auditor-facing requests belong inside NGAME versus QuickBooks Online (QBO) and its Audit Log, and state NGAME’s product positioning relative to Intuit.  
**Audience:** Co-authors, auditors, FRPs, technical partners, and backlog reviewers.

---

## Product positioning (read first)

**NGAME is a companion application, not a QuickBooks Online add-on.**

| Term | What it means for NGAME |
|------|-------------------------|
| **Companion app** | Runs on a separate surveillance workstation; reads company data through Intuit’s **read-only** API; presents its own dashboard and artifacts. It does not install inside QBO, extend QBO screens, or replace QBO workflows. |
| **Not an add-on** | NGAME is not marketed, architected, or licensed as a QBO marketplace extension or in-product module. |
| **Not an Audit Log substitute** | NGAME does not replicate, enrich, or compete with QBO’s Audit Log. Attribution (“who changed what, when”), void/delete audit trails, and field-level change history are **Intuit’s domain**. NGAME deliberately **defers** those questions to human review of the Audit Log (or to auditor-built SQL over Audit Log exports). |

**Strategic intent:** Remain well separated from Audit Log functionality so NGAME is not viewed as a competitor to Intuit. NGAME’s role is **early statistical triage** on aggregate churn patterns; the Audit Log remains the **system of record** for transactional forensics and user attribution.

**Operational handoff (by design):**

```
QBO books (bookkeeper)          NGAME (surveillance PC, read-only API)
        │                                    │
        │                                    ├─ Layer 1–2: category-level churn signals
        │                                    └─ “Unusual today” → FRP / auditor
        │                                              │
        └─ Audit Log (browser, Intuit) ◄───────────────┘
              who / what / when / field-level detail
```

---

## What NGAME is built to do

NGAME is an almost **stateless** surveillance machine:

- **Primary memory:** yesterday’s ontology snapshot (`Yesterday.ttl`) compared to today’s (`Today.ttl`).
- **Secondary memory:** a 30-day **training baseline** (μ, σ per transaction type) and an optional rolling buffer of **aggregate** CPI arrays (default ~30 days) for multi-day sequence analysis.
- **Alert voice:** **general** — flags are at the **transaction-type** level (18 φ categories: Vendors, Bill_Payments, Invoices, …), not at the level of named entities, individual payments, or user sessions.
- **Ground truth for follow-up:** QuickBooks **Audit Log** (in QBO browser), per FRP operations guides.

NGAME does **not** prove fraud. A flag means activity is statistically unusual relative to the organization’s trained baseline. The FRP or auditor adjudicates using professional judgment and Audit Log review.

---

## Auditor wish list vs. NGAME scope

Most auditor-requested capabilities are, in substance, a desire for the **Audit Log to be extended and enriched** — entity-level manifests, attribution, and field-level diffs with user identity. That is appropriate for Intuit’s product; it is **out of scope** for NGAME as a companion churn sentinel.

The table below classifies representative use cases. **In scope** items are limited to aggregate statistical triage already aligned with NGAME’s architecture. **Out of scope** items should be satisfied by Audit Log review, auditor SQL/reporting over QBO or audit exports, or Intuit platform evolution — not by NGAME absorbing Audit Log responsibilities.

| # | Auditor use case | NGAME scope | Rationale |
|---|------------------|:-----------:|-----------|
| 1 | **Per-vendor report: payments to recently-added vendors** | **Out** | Requires longitudinal vendor registry (creation dates), per-entity payment rollups, and cross-entity joins. NGAME retains day-pair churn and type-level z-scores only; it does not maintain “vendor age × payment history.” |
| 2 | **Show deleted transactions** | **Out** (as a manifest) | NGAME **measures** deletions structurally (Removed / δ in Layer 1; deletion rates in CPI arrays) and deletion can **drive** category-level HIGH alerts. It does **not** persist or display **which** records were deleted (IDs, doc numbers, amounts, who deleted). That is Audit Log territory. |
| 3 | **For mutations, show exactly what changed** | **Out** (as Audit Log–class detail) | NGAME’s property-mutation diff (same record ID, field yesterday → today) is a **separate structural signal** from CPI; it may be surfaced in future as supplementary triage. It still lacks **user attribution**, session context, and the authoritative change narrative the Audit Log provides. Auditors asking “show me exactly what changed” in the forensic sense should use the Audit Log. *(Statistical treatment of mutation in NGAME alarms is addressed in a separate design thread.)* |
| — | **Who** created, edited, voided, or deleted a record | **Out** | Not extracted; explicitly deferred to QBO Audit Log in FRP documentation. |
| — | **Line-level edits** on an unchanged record ID (e.g., invoice amount change) | **Partial signal only** | May affect mutation stats or leave CPI stable; FRP guides direct users to Audit Log for line edits. |
| — | **Is today’s vendor / invoice / bill churn unusual vs. our baseline?** | **In** | Core Layer 1–2 function: CPI, z-scores, Top Anomalies, Multi-Day Pattern Alert. |
| — | **Sustained slow-burn churn over several days?** | **In** (aggregate) | Sequence CPI over rolling buffer — still per **type**, not per entity. |
| — | **Today’s credit card activity flags** | **In** (limited) | Credit Card Watch — today’s card transactions with risk heuristics; not a full card audit trail. |

---

## Use case notes (enumerated)

### 1. Payments to recently-added vendors (per-vendor basis)

**Auditor ask:** List each vendor added within a window; show all payments to each.

**Why out of scope:**

- “Recently added” requires **retained history** of vendor first-seen or `CreateTime`, not just “added since yesterday.”
- Per-vendor payment totals require **entity-level reporting**, not φ18/φ7 category z-scores.
- NGAME may **indirectly** sense a related fraud **pattern** (simultaneous spikes in Vendors + Bill_Payments CPI) but emits a **category alert**, not a vendor roster.

**Appropriate resolution:** Audit Log (vendor Created events + payment events) or SQL over QBO entity and transaction exports.

---

### 2. Show deleted transactions

**Auditor ask:** Present a list (or report) of transactions deleted in a period.

**What NGAME already does:**

- Layer 1 **Removed** (*b*): records in yesterday’s snapshot absent today.
- `deletion_rate_array` and dollar-weighted deletion rates per transaction type.
- Large deletion volume can contribute to **unusual CPI** and category-level alerts.

**What NGAME does not do:**

- Emit a **deletion manifest** (which invoice #, amount, date, payee).
- Rank alerts on **deletion rate δ** as a first-class FRP panel (today: CPI z-score dominates).
- Attribute deletions to a **user** or distinguish void vs. delete vs. merge in QBO semantics.

**Scope verdict:** Statistical detection of “more deletion churn than usual” is **in scope**; **enumerating deleted transactions** is **out of scope** — functionally equivalent to Audit Log enrichment.

**Appropriate resolution:** QBO Audit Log filtered for deletions/voids; auditor queries over audit export tables.

---

### 3. Show exactly what changed (mutations)

**Auditor ask:** Field-level diff — what attribute changed, from what to what.

**What NGAME already does (engineering, not yet FRP-facing at full depth):**

- **Property mutations:** for record IDs present in **both** snapshots, compare stored ontology fields (added / removed / modified).
- Distinct from CPI (Jaccard on ID sets): an invoice can show CPI = 1.0 (same ID retained) while an **amount** mutates.

**What NGAME does not do:**

- Replace Audit Log as the **authoritative** change record.
- Provide **who** made the change, from which session, or Intuit’s full event taxonomy.
- Guarantee coverage of all QBO fields (extraction writes a curated ontology subset; `MetaData.CreateTime` and many audit-oriented fields are not in today’s extract).

**Scope verdict:** Surfacing **aggregate or supplementary** mutation signals for triage may be **in scope** as a companion check (parallel to CPI, not merged into a single score). Delivering an **auditor-grade “exactly what changed” report with attribution** is **out of scope** — that is Audit Log (or Audit Log plus export tooling).

**Appropriate resolution:** Audit Log for attributed field history; optional future NGAME panel limited to **anonymous structural diffs** that **point to** Audit Log review, not replace it.

*(Relationship of mutation to NGAME’s statistical alarms — wiring, baselines, dashboard — is documented separately.)*

---

## General principle

| Auditor request pattern | Typical NGAME answer | Typical Audit Log / SQL answer |
|-------------------------|----------------------|--------------------------------|
| “Is something **unusual** today vs. our learned normal?” | Yes — category z-scores, warnings | Overkill |
| “**Which** records** were added, removed, or paid?” | No — count only at type level | Yes |
| “**Who** did it and **what exactly** changed?” | No | Yes |
| “**Report** per vendor / per employee / per period?” | No | Yes (SQL or QBO reports) |

When in doubt, ask: **Does this require a stateful entity ledger, user attribution, or a scrollable transaction manifest?** If yes, it belongs with the **Audit Log or auditor analytics**, not NGAME.

---

## Language for external audiences

**Say:**

- “NGAME is a **companion** churn-surveillance tool that runs beside QuickBooks.”
- “NGAME flags **unusual patterns by category**; your auditor uses the **QuickBooks Audit Log** for detail and attribution.”
- “NGAME is **read-only** and does not modify QuickBooks.”

**Avoid:**

- “NGAME shows you deleted transactions” or “NGAME replaces audit trail review.”
- “NGAME add-on for QuickBooks” or language implying in-product integration or Audit Log parity.
- Implying NGAME **confirms** fraud or **identifies** perpetrators.

---

## Backlog guardrails

Before accepting an “auditor feature” into NGAME backlog, apply:

1. **Companion test:** Can this ship without embedding in QBO or duplicating Audit Log screens?
2. **Attribution test:** Does it require **who** changed a record? → **Defer to Audit Log** (or explicit non-goal).
3. **Manifest test:** Does it require listing **named entities** across time? → **Defer to Audit Log / SQL**.
4. **State test:** Does it require history beyond yesterday + trained μ/σ + optional CPI rolling buffer? → **Likely out of scope** unless narrowly justified as aggregate-only.
5. **Intuit relationship test:** Would a reasonable Intuit product manager read this as **competing with Audit Log**? → **Do not build.**

Acceptable NGAME enhancements near the boundary: **aggregate** deletion or mutation **rates** as supplementary triage signals that **increase the urgency** of Audit Log review — never manifests with user attribution.

---

## Related documents

| Document | Relevance |
|----------|-----------|
| `FRP_OPERATIONS_GUIDE.md` | Audit Log protocol; warning response |
| `Training, Marketing, and Documentation/NGAME_FRP_PhaseII_Dashboard_Guide.md` | What dashboard shows vs. gaps |
| `docs/drafts/NGAME_Glossary_Three_Layer_Terminology.md` | Layer 1 Added / Removed / Retained; triage vocabulary |
| `Training, Marketing, and Documentation/cursor_ngame_enhancements_and_mutation.md` | Mutation vs. CPI; feasibility without Audit Log parity |
| `IMPLEMENTATION_GUIDE.md` | Companion architecture; read-only API path |

---

*NGAME · Auditor use case scope boundary · Draft · June 2026*
