# Entity Surveillance — One-Page Product Concept

**Status:** Exploration draft (no design or implementation)  
**Relationship to NGAME:** Sibling companion product — not an extension of the CPI pipeline  
**Audience:** Product owners, co-authors, technical partners, FRP operations planners  
**Date:** June 2026

---

## Problem

Occupational fraud schemes such as **fictitious vendors** follow a recognizable sequence: elevated vendor creation → payment to one or more of those vendors. NGAME detects the **aggregate** signal (unusual Vendors dimension churn) but cannot answer the forensic question: *which vendors were added, and did any receive payment?* Auditors and FRPs need **entity-level dossiers and payment manifests**, not category z-scores alone.

---

## Product definition

**Entity Surveillance (working name)** is a **stateful, read-only companion** that runs on the same surveillance workstation as NGAME. It maintains a longitudinal **entity ledger**, applies **rule packs** to watch specific entities over time, and emits **FRP briefings** when defined events occur (e.g., first payment to a recently added vendor).

| Principle | Commitment |
|-----------|------------|
| **Companion, not QBO add-on** | Separate dashboard/artifacts; read-only Intuit API; no in-product QBO integration |
| **Not an Audit Log substitute** | No user attribution, void/delete taxonomy, or authoritative change narrative — **defer to QBO Audit Log** |
| **Not a fraud verdict engine** | Reports statistically or rule-triggered events; FRP adjudicates at Layer 4 |
| **Stateful by design** | Persistent entity registry, watch lists, event log, adjudication outcomes |

---

## Architecture (conceptual)

```
QuickBooks Online (cloud)
        ↑ read-only API
Surveillance workstation
  ├─ NGAME (optional upstream trigger)
  │     └─ Layer 2: "Vendors HIGH" → triage signal
  │
  └─ Entity Surveillance
        ├─ Extract: Vendor, Bill, BillPayment, Check, Expense, …
        ├─ Entity ledger (persistent store)
        ├─ Rule packs (watch criteria + event predicates)
        ├─ Correlation engine (cross-entity joins)
        └─ FRP briefing generator (HTML / PDF / XLS)
              └─ Handoff → FRP reviews Audit Log for attribution
```

**Trigger modes:** (a) daily scan independent of NGAME; (b) escalated when NGAME fires a category alert on a related φ dimension; (c) manual watch registration by consultant.

---

## Core data model (minimal)

| Store | Contents | Retention |
|-------|----------|-----------|
| **Entity snapshot** | Vendor (or other entity) fields at extract time: Id, DisplayName, CreateTime, address, terms, balance, custom fields available via API | Versioned; latest + first-seen |
| **Watch registry** | Entity Id, rule pack id, watch start, status (active / cleared / expired), trigger reason | Until adjudicated or TTL |
| **Payment events** | Txn Id, type, date, amount, VendorRef, linked Bill/Check refs | Append-only |
| **Alert record** | Rule fired, entity dossier snapshot, payment event(s), timestamp, NGAME cross-ref (if any) | Permanent audit trail |
| **Adjudication** | FRP outcome: corroborated / benign / missed; notes; reviewer, date | Operational ground truth (Layer 4) |

Storage: embedded SQL (e.g., SQLite) per company file; consultant-managed backup on surveillance PC.

---

## Rule-pack interface

A **rule pack** is a named forensic use case: watch criteria + event predicate + briefing template.

| Field | Example (ghost vendor) |
|-------|------------------------|
| **Entity type** | Vendor |
| **Watch criteria** | First seen within *N* days **or** org vendor-creation rate > baseline **or** NGAME Vendors ∈ top-*k* |
| **Event predicate** | Any BillPayment, Check, or Expense with VendorRef = watched entity |
| **Thresholds** | First payment; cumulative payments > $X; payment within *M* days of CreateTime |
| **Expiry** | Watch ends after *P* days with no event, or on FRP benign resolution |
| **Briefing template** | Vendor dossier + payment manifest + scheme hypothesis (Layer 3) + Audit Log review checklist |

**Repertoire (future packs, same engine):** rapid pay-after-create; dormant vendor reactivation; duplicate-address cluster payment; employee-name ≈ vendor-name overlap.

Rule packs ship as configuration + SQL templates — not hard-coded one-offs.

---

## FRP artifact format

Each fired event produces a **briefing packet** the FRP can act on without Terminal access:

1. **Summary line** — e.g., *"Payment $4,200 to vendor ACME LLC (created 12 days ago)"*
2. **Vendor dossier** — name, CreateTime, address, contact, open balance, days on watch
3. **Payment manifest** — txn type, date, amount, doc number, linked bills
4. **Scheme hypothesis (Layer 3)** — ACFE-aligned class (e.g., fictitious vendor / billing scheme); non-authoritative
5. **Audit Log checklist** — explicit prompts: who created vendor; who approved payment; field-level changes
6. **Adjudication control** — corroborated / benign / missed; optional notes

Deliverables: in-app panel + export to **XLS** (workpaper) and **PDF/HTML** (board packet). Parameterized SQL templates support consultant/auditor ad-hoc queries over the ledger.

---

## Four-layer mapping

| Layer | Entity Surveillance role |
|-------|--------------------------|
| **1 — Structural** | Entity Added/Removed vs. prior extract; dossier versioning |
| **2 — Detection** | Rule-pack predicates; optional NGAME φ-dimension trigger |
| **3 — Scheme interpretation** | ACFE taxonomy hypothesis in briefing; auditable anchor; not a verdict |
| **4 — FRP adjudication** | Human outcome recorded; feeds retrospective eval. labels |

Terminology per `NGAME_Glossary_Four_Layer_Terminology.md`. Alerts resolved as legitimate onboarding are **benign resolutions**, not system errors.

---

## Boundaries (explicit non-goals)

| In scope | Out of scope |
|----------|--------------|
| Named-entity watch lists and payment correlation | User/session attribution ("who clicked Save") |
| Vendor CreateTime and entity metadata from API | Replacing QBO Audit Log screens or exports |
| Generated XLS/SQL workpapers from ledger | Modifying QuickBooks data |
| Recording FRP adjudication outcomes | Autonomous fraud accusations |
| Optional NGAME alert as upstream trigger | Absorbing NGAME CPI pipeline or φ-dimension scoring |

**Intuit relationship test:** Product surfaces *what was paid to whom and when* from read-only books data; FRP establishes *who did it* via Audit Log. Does not compete with Audit Log enrichment.

---

## Deployment sketch

| Component | Location |
|-----------|----------|
| Entity Surveillance service + ledger | Surveillance workstation (same as NGAME) |
| QBO read-only credentials | Shared or parallel config with NGAME |
| FRP briefing UI | Localhost browser (separate bookmark from NGAME dashboard) |
| NGAME integration | Optional webhook or shared flag file: `vendors_high_today` |

Two bookmarks for the FRP: **NGAME** (daily category triage) and **Entity Surveillance** (entity dossiers when rules fire). Consultant installs, backs up ledger, maintains rule packs.

---

## Success criteria (exploration level)

1. FRP receives a actionable dossier within one business day of payment to a watched new vendor.
2. Benign resolutions are fast to record (legitimate supplier onboarding).
3. Consultant can add a new rule pack without rewriting the correlation engine.
4. Manuscript and sales language keep NGAME (aggregate triage) and Entity Surveillance (entity forensics) distinct.

---

## Open questions (defer to design phase)

- Per-company vs. multi-tenant ledger layout  
- Default watch TTL and false-positive volume for high-churn nonprofits  
- Minimum QBO entity fields required for duplicate-vendor clustering  
- Whether Layer 3 reuses NGAME's LLM + TTL anchor or a lighter template-only briefing  
- Retention and GDPR/privacy policy for entity dossiers after FRP benign resolution  

---

*Exploration draft · Entity Surveillance companion concept · June 2026 · Aligns with `NGAME_Auditor_Use_Cases_Scope.md` use case #1 and four-layer glossary.*
