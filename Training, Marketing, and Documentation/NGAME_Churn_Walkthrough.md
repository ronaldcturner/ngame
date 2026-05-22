# NGAME Overnight Churn Walkthrough

*For accounting reviewers — one example night, three parallel checks.*

---

## What happened overnight (example)

| # | Change in QuickBooks | Type |
|---|----------------------|------|
| 1 | **Invoice #1039**: total **$1,200 → $12,000** (same invoice ID) | Edit on existing record |
| 2 | **New vendor** “Acme Office Supply LLC” | New record ID |

Everything else unchanged.

---

## Three checks NGAME runs (not one)

| Check | Question it asks | This example |
|-------|------------------|--------------|
| **CPI (Jaccard)** | Which **record IDs** were added, removed, or kept? | Invoices CPI = **1.00** (all IDs retained). Vendors CPI = **0.75** (one new vendor ID). |
| **wCPI (dollar-weighted)** | When IDs are added/removed, were the **dollars** unusually large? | Invoices: no signal (no add/remove). Vendors: usually mild for a $0-balance new vendor. |
| **Property mutations** | For IDs in **both** days, did any **field** change? | Invoice #1039: **amount modified**. New vendor: N/A (not in yesterday’s snapshot). |

**CPI formula (per transaction type):** Retained ÷ (Retained + Added + Removed)

---

## Why the invoice edit does not lower CPI

Jaccard compares **identity** (attendance), not field values. Same invoice ID yesterday and today = **retained**, even when the amount changes. That edit appears under **property mutations**, not in the z-score churn alarm today.

---

## What triggers the morning alarm (Phase II)

| Signal | Invoice edit | New vendor |
|--------|--------------|------------|
| CPI / z-score | Usually quiet | May flag if vendors are normally very stable |
| wCPI / dollar z-score | No effect without add/remove | Often small |
| Property mutations | **Listed for FRP review** | Not applicable (new ID) |
| Composite ranking | Unlikely top alert | Possible vendor churn flag |

Mutations are **supplementary** — they do not currently drive the statistical z-score vector.

---

## Three questions → three answers

| Your question | NGAME answers with |
|---------------|-------------------|
| Did we gain or lose **records**? | **CPI (Jaccard)** |
| Was churn mostly **small** or **large** dollars? | **wCPI** |
| Did someone **change** an existing record’s fields? | **Property mutations** |

**Analogy:** CPI = attendance; wCPI = attendance weighted by wallet size when people enter or leave; mutations = line-by-line diff on the same file folder.

---

## File locations (this project)

| Artifact | Path |
|----------|------|
| This walkthrough (Markdown) | `Training, Marketing, and Documentation/NGAME_Churn_Walkthrough.md` |
| One-page printable (HTML) | `Training, Marketing, and Documentation/NGAME_Churn_Walkthrough.html` |
| Jaccard deep-dive (HTML) | `Training, Marketing, and Documentation/Jaccard_Presentation.html` |
| Canvas source (archive) | `canvases/jaccard-presentation.canvas.tsx` |

*NGAME · May 2026*
