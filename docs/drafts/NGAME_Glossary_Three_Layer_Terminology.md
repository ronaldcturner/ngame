# NGAME Terminology Glossary  
## Three-Layer Model for Churn, Detection, and Triage

**Status:** Draft for journal manuscript  
**Purpose:** Replace confusion-matrix labels (TP / FP / FN / TN) on the Jaccard 2×2 with precise, layer-specific terms.  
**Audience:** Co-authors, reviewers, and readers of the NGAME design-science evaluation.

---

## Why This Glossary Exists

NGAME uses “positive” and “negative” in three distinct senses. Conflating them invites reviewer criticism and misstates what the artifact does. This glossary assigns **one vocabulary per layer** and retires TP/FP/FN/TN on the day-over-day record-overlap matrix (Layer 1). Standard confusion-matrix language is reserved for **controlled evaluation against ground truth** (Layer 2). FRP-facing outcomes use **triage vocabulary** that does not imply autonomous fraud verdicts (Layer 3).

---

## Layer Overview

| Layer | Question answered | Primary outputs | Ground truth |
|:-----:|-------------------|-----------------|--------------|
| **1 — Structural** | How stable is each transaction-type population from yesterday to today? | CPI, α (addition rate), δ (deletion rate), wCPI | None required; descriptive set overlap |
| **2 — Detection** | Which φ dimensions deviate enough from the trained baseline to rank in the top-*k* alert set? | z-scores, HIGH / MEDIUM / LOW bands, top-*k* rankings | Injected or known anomalies (evaluation only) |
| **3 — Triage** | What should the Financially Responsible Person (FRP) review, and what did review conclude? | Management warnings, overall risk, dashboard artifacts | FRP professional judgment after review |

---

## Table 1 — Layer 1: Day-over-Day Record Overlap (Jaccard / CPI)

**Replaces the Jaccard 2×2 labels TP, FP, FN, TN in the journal version.**

Rows: presence in **Yesterday’s** snapshot (Y). Columns: presence in **Today’s** snapshot (T).

| Cell | Preferred term | Symbol | Set notation | Role in CPI | Interpretation |
|:----:|----------------|:------:|:------------:|:-----------:|----------------|
| Upper-left | **Retained** | *a* | Y ∩ T | Numerator of CPI | Record URI present in both snapshots; continuity across days |
| Upper-right | **Removed** | *b* | Y \\ T | Contributes to δ (deletion rate) | Record existed yesterday, absent today; churn or deletion |
| Lower-left | **Added** | *c* | T \\ Y | Contributes to α (addition rate) | Record absent yesterday, present today; new entry |
| Lower-right | **Excluded** | — | (not counted) | **Not in formula** | Absent both days; universe of non-occurring records is undefined |

**Core formulas (Layer 1 only):**

| Quantity | Formula | Range |
|----------|---------|:-----:|
| CPI (Churn Persistence Index) | CPI = *a* / *n*, where *n* = *a* + *b* + *c* | [0, 1] |
| Addition rate (α) | α = *c* / *n* | [0, 1] |
| Deletion rate (δ) | δ = *b* / *n* | [0, 1] |
| Partition identity | CPI + α + δ = 1 | — |

**Edge convention:** When *n* = 0 (no records of type *k* in either snapshot), CPI = 1.0 — absence is treated as stable.

**Dollar-weighted variant:** Same structure with dollar weights *w*ᵢ instead of URI counts → wCPI, wAdditionRate, wDeletionRate.

### Retired Layer 1 labels (do not use in journal prose)

| Retired label | Was used to mean | Use instead |
|---------------|------------------|-------------|
| TP (True Positive) | Retained | **Retained** (*a*) |
| FP (False Positive) | Added | **Added** (*c*) |
| FN (False Negative) | Removed | **Removed** (*b*) |
| TN (True Negative) | Excluded | **Excluded** (state explicitly that this cell is omitted from Jaccard) |

**Note:** “Added” is not a “false” outcome. A legitimate new vendor is **Added** at Layer 1 and may still yield a LOW z-score at Layer 2 if consistent with the trained baseline.

---

## Table 2 — Layer 2: Detector Evaluation Metrics (Ground-Truth Comparison)

**Use standard IR / confusion-matrix terms only here**, when comparing NGAME’s top-*k* flagged φ dimensions to known or injected anomalies.

**Detection task (evaluation):** Given an *N*-element daily φ (CPI) array, rank dimensions by |z| (or composite alarm) and treat the top-*k* as the alert set (*k* = 3 in current instantiation; *N* = 17–18).

| Term | Symbol | Definition | Formula |
|------|:------:|------------|---------|
| **True Positive (eval.)** | TP | Flagged dimension where an anomaly was knowingly introduced or present in ground truth | — |
| **False Positive (eval.)** | FP | Flagged dimension with only normal variation relative to ground truth | — |
| **False Negative (eval.)** | FN | Ground-truth anomaly dimension not in the top-*k* alert set | — |
| **True Negative (eval.)** | TN | Normal-variation dimension not flagged | — |
| **Precision** | — | Share of flagged dimensions that match ground truth | TP / (TP + FP) |
| **Recall (top-*k*)** | — | Share of anomalous dimensions captured in top-*k* | TP / (TP + FN) |
| **False Positive Rate** | FPR | Share of normal dimensions incorrectly flagged | FP / (FP + TN) |

**Scope limits (state in manuscript):**

- Metrics apply to **transaction-type dimension ranking**, not dollar amount of any single transaction.
- Formal element-level precision/recall requires per-pattern logging of top-*k* rankings against ground truth; pipeline pass/fail alone is insufficient.
- Design intent: triage favors **recall over precision** given ACFE-style detection lag without continuous monitoring.

**Layer 2 outputs (operational, pre-FRP):**

| Term | Definition |
|------|------------|
| **z-score** | *z*ₖ = (CPIₖ(today) − μₖ) / σₖ; signed deviation from trained mean |
| **Deviation band** | \|z\| > 3.0 → HIGH; \|z\| > 2.0 → MEDIUM; else LOW |
| **Composite alarm** | Fires when count-based or dollar-weighted signal reaches MEDIUM or HIGH |
| **Top-*k* alert set** | The *k* φ dimensions with largest \|z\| (or equivalent ranking rule) on a given day |

---

## Table 3 — Layer 3: FRP Triage Outcomes (Operational)

**NGAME does not accuse anyone of fraud.** A warning means activity is statistically unusual relative to the organization’s 30-day baseline; the FRP adjudicates.

| Term | Definition | Relation to Layer 2 |
|------|------------|---------------------|
| **Statistically warranted alert** | \|z\| or composite alarm exceeds threshold; signal is real relative to trained μ, σ | May correspond to FP (eval.) if ground truth is “normal business change” |
| **Corroborated alert** | FRP review finds material concern: fraud, control weakness, or required correction | Aligns with TP (eval.) when ground truth exists; broader in production |
| **Benign resolution** | Alert correctly reflected baseline deviation; FRP explains as legitimate (e.g., new GL accounts, seasonal vendor onboarding) | Often FP (eval.) under fraud ground truth; **not** a system failure under triage design |
| **Missed event** | Material misappropriation occurred but did not surface in warnings or top-*k* | FN (eval.) when ground truth is known |

### Terms to avoid at Layer 3

| Avoid | Reason | Prefer |
|-------|--------|--------|
| **False positive** (unqualified) | Implies detector error; conflates with Layer 2 | **Benign resolution** or **statistically warranted, benign on review** |
| **True positive** (unqualified) | Implies fraud confirmed by the system | **Corroborated alert** (after FRP review) |
| **Unreliable warning** | Suggests broken instrumentation | **Benign resolution** or **spurious for fraud purposes, valid for triage** |
| **Reliable** (for warnings) | Collides with “reliable μ and σ estimates” (Layer 1 training) | **Corroborated**, **warranted**, or **actionable after review** |

---

## Table 4 — Cross-Layer Mapping (Illustrative)

One day’s Vendors dimension can illustrate how layers diverge:

| Layer | Example reading |
|-------|-----------------|
| **1 — Structural** | High **Added** and **Removed** counts → low CPI (churn) |
| **2 — Detection** | \|z\| > 3 on Vendors → HIGH; Vendors in top-*k* |
| **3 — Triage** | FRP reviews Audit Log → **benign resolution** (legitimate vendor cleanup) or **corroborated alert** (shell-vendor pattern) |

**Chart of Accounts example (field deployment):** Layer 2 correctly flags HIGH deviation; Layer 3 **benign resolution** after FRP confirms legitimate new GL accounts. Not an eval. FN; triage behaved as designed.

---

## Table 5 — Notation Quick Reference

| Symbol | Meaning |
|:------:|---------|
| Y, T | Yesterday and Today ontology snapshots for a transaction type |
| *a*, *b*, *c*, *n* | Retained, removed, added, and union count (*n* = *a* + *b* + *c*) |
| φₖ, CPIₖ | Churn Persistence Index for transaction type *k* |
| μₖ, σₖ | Trained mean and standard deviation of CPIₖ (30-day baseline) |
| wCPIₖ | Dollar-weighted CPI for type *k* |
| SCPIₖ(*t*, *L*) | Sequence CPI: geometric mean of CPIₖ over window *L* |
| *z*ₖ | Standardized deviation: (CPIₖ(today) − μₖ) / σₖ |
| *k* (alert) | Number of top-ranked anomalous dimensions in evaluation (default 3) |
| FRP | Financially Responsible Person — designated reviewer |

---

## Suggested Manuscript Footnote (optional paste-in)

> *Terminology:* Day-over-day record overlap (retained, added, removed) describes structural churn only and is not labeled with confusion-matrix terms. True and false positives, precision, and recall apply solely to evaluation of top-*k* dimension ranking against known or injected anomalies. Management warnings indicate statistical departure from an organization-specific baseline; the FRP classifies outcomes as corroborated, benign on review, or missed—NGAME does not render autonomous fraud verdicts.

---

*Draft aligned with NGAME CPI analysis (`ngame_cpi_analysis_agent.py`), churn comparison thresholds (`ngame_churn_comparison_agent.py`), FRP Operations Guide, and DSRM Evaluation Draft §5.2.*
