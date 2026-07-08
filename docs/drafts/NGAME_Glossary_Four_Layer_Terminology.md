# NGAME Terminology Glossary  
## Four-Layer Model for Churn, Detection, Interpretation, and Adjudication

**Status:** Draft for journal manuscript  
**Purpose:** Assign precise, layer-specific vocabulary across the NGAME pipeline; retire confusion-matrix labels (TP / FP / FN / TN) on the Jaccard 2×2 (Layer 1); separate statistical detection (Layer 2), LLM taxonomy linkage (Layer 3), and FRP adjudication (Layer 4).  
**Audience:** Co-authors, reviewers, and readers of the NGAME design-science evaluation.

---

## Why This Glossary Exists

NGAME uses “positive,” “negative,” “reliable,” and “triage” in several distinct senses. Conflating them invites reviewer criticism and misstates what the artifact does. This glossary assigns **one vocabulary per layer** and directs each layer’s **trust property** — the kind of warrant the layer can honestly claim — without imposing a single global definition of “reliability.”

For the anticipated reviewer question **“What about false positives and false negatives?”** see **Tables A–E** (below the layer overview).

| Layer | Retires or restricts |
|:-----:|----------------------|
| **1 — Structural** | TP/FP/FN/TN on the day-over-day Jaccard 2×2; use retained / added / removed / excluded |
| **2 — Detection** | Standard IR / confusion-matrix terms **only** in controlled evaluation against ground truth |
| **3 — Scheme interpretation** | “Triage,” “reliable ranking,” and fraud-verdict language for LLM taxonomy output |
| **4 — FRP adjudication** | Unqualified “true/false positive” and autonomous fraud verdicts |

---

## Layer Overview

| Layer | Question answered | Primary outputs | Ground truth | Trust property |
|:-----:|-------------------|-----------------|--------------|----------------|
| **1 — Structural** | How stable is each transaction-type population from yesterday to today? | CPI, α (addition rate), δ (deletion rate), wCPI | None required; descriptive set overlap | **Reproducibility** — same snapshots → same CPI |
| **2 — Detection** | Which φ dimensions deviate enough from the trained baseline to rank in the top-*k* alert set? | z-scores, HIGH / MEDIUM / LOW bands, top-*k* rankings | Injected or known anomalies (evaluation only) | **Detection validity** — precision/recall on dimension ranking (eval. only) |
| **3 — Scheme interpretation** | Given flagged dimensions, how plausibly do patterns align with asset-misappropriation scheme classes? | Taxonomy mappings, LLM narrative, model-reported confidence, deterministic anchor scores | Curated ontology + ACFE priors; not adjudicated fraud | **Interpretive fidelity** — grounded, auditable, non-authoritative |
| **4 — FRP adjudication** | What did human review conclude, and what action followed? | Corroborated / benign / missed outcomes; management warnings as briefing artifacts | FRP professional judgment after review | **Adjudication outcome** — operational ground truth in production |

**Pipeline order:** Layer 1 → Layer 2 → Layer 3 → Layer 4. Layer 2 produces the **statistical alert set** (deterministic top-*k* ranking). Layer 3 **enriches** that set with scheme labels and narrative; it does not replace Layer 2 as the primary trigger for FRP attention. Layer 4 is where “what actually happened” is established.

---

## Answering “But is it reliable?”

Readers will ask **“Is it reliable?”** at every layer. Do not answer with one global yes or no. Point to the **trust property** for that layer:

| Layer | Reader’s question | Answer in one line |
|:-----:|-------------------|-------------------|
| **1** | Is CPI measurement trustworthy? | Same Y/T inputs yield the same CPI; descriptive, not evaluative. |
| **2** | Does it flag the right φ dimensions? | Top-*k* ranking is deterministic given μ, σ; precision/recall apply under controlled evaluation. |
| **3** | Is the scheme label / LLM narrative trustworthy? | Grounded in `Asset_Misappropriation.ttl`, auditable against a deterministic anchor; **not** a fraud verdict and not evaluated with Layer 2 IR metrics. |
| **4** | Was the management action correct? | FRP judgment is ground truth in production; outcomes are corroborated, benign, or missed. |

---

## Answering “What about false positives and false negatives?”

Reviewers and readers trained in machine learning will ask this question early. **NGAME does not retire confusion-matrix language globally.** It **relocates** TP, FP, FN, and TN to the layer where ground truth and a defined detection task exist, and **replaces** those labels elsewhere with terms that do not imply classifier error.

**Direct answer (one paragraph for manuscript adaptation):**

> False positives and false negatives are standard information-retrieval terms for comparing a detector’s output to **known ground truth**. In NGAME they apply **only at Layer 2**, where top-*k* transaction-type dimensions are evaluated against injected or known anomalies. They do **not** apply to the Layer 1 Jaccard partition (retained, added, removed), which is descriptive set overlap without a reference “correct” class. At Layer 3, scheme labels are hypotheses auditable against a curated taxonomy anchor—not TP/FP outcomes. At Layer 4, an alert that proves benign on FRP review may resemble a Layer 2 false positive under a fraud-only ground-truth definition, but under NGAME’s triage design it is a **benign resolution**, not evidence of broken detection.

### Table A — Where TP / FP / FN / TN belong (and where they do not)

| Layer | Do TP / FP / FN / TN apply? | Ground truth required? | Correct vocabulary |
|:-----:|:-----------------------------:|:----------------------:|--------------------|
| **1 — Structural** | **No** | No | Retained (*a*), Removed (*b*), Added (*c*), Excluded |
| **2 — Detection** | **Yes** (evaluation only) | Yes — injected or otherwise **documented** anomalies per the **evaluation protocol** (test harness, injection log, researcher record). **Not** FRP pre-awareness. | TP, FP, FN, TN (eval.); precision, recall, FPR |
| **3 — Scheme interpretation** | **No** | Partial — ontology + ACFE priors, not adjudicated fraud | Scheme-concordant mapping, interpretive divergence, narrative adjunct |
| **4 — FRP adjudication** | **No** (avoid unqualified use) | FRP judgment in production (operational ground truth **after** review; may inform **retrospective** eval. labels, not pre-run TP/FP/FN/TN) | Corroborated alert, benign resolution, missed event |

### Table B — What the reader may call a “false positive” vs what NGAME means

| Reader’s informal claim | Layer | NGAME term | Why the distinction matters |
|-------------------------|:-----:|------------|------------------------------|
| “A new vendor is a false positive on the Jaccard grid.” | **1** | **Added** (*c*) | Layer 1 does not judge correctness; new records are structural facts, not errors. |
| “CPI flagged Vendors but no fraud was injected.” | **2** | **FP (eval.)** — if and only if ground truth is defined | Valid eval. metric under controlled test; requires explicit anomaly injection record. |
| “CPI flagged Vendors but FRP found legitimate cleanup.” | **4** | **Benign resolution** | Statistically warranted alert + legitimate business explanation; **not** a detector fault under triage design. |
| “The LLM named the wrong fraud scheme.” | **3** | **Interpretive divergence** | Scheme label is a hypothesis, not a detection verdict; audit against deterministic anchor. |
| “The LLM said HIGH risk but there was no fraud.” | **3** + **4** | **Benign resolution** (after FRP) | LLM enriches briefing; Layer 2 triggered review; FRP adjudicates. |
| “Fraud occurred but NGAME stayed quiet.” | **2** + **4** | **FN (eval.)** if ground truth known; **missed event** in production | FN requires eval. ground truth; missed event is the operational Layer 4 label. |

### Table C — Layer 1 retired labels (Jaccard 2×2): why “false” is misleading

Training materials sometimes overlay confusion-matrix names on the Jaccard grid. **Do not carry that overlay into manuscript prose.**

| Retired label | Was used to mean | Problem if kept | Use instead |
|---------------|------------------|-----------------|-------------|
| TP | Retained | Implies a “correct detection” where no detector exists | **Retained** (*a*) |
| FP | Added | Implies a **new record is an error**; legitimate vendors become “false alarms” | **Added** (*c*) |
| FN | Removed | Implies a **missed detection** where churn is a structural fact | **Removed** (*b*) |
| TN | Excluded | Implies correct rejection in a classifier sense | **Excluded** (omitted from Jaccard denominator) |

**Same grid, different semantics:** The 2×2 layout matches intersection-over-union (IoU) in segmentation, where TP/FP/FN are defined against a **reference mask**. NGAME Layer 1 compares **yesterday vs today** with no reference mask and no prediction task. CPI = *a*/*n* is Jaccard set similarity, not classifier accuracy.

### Table D — Layer 2 detection task (the only home for standard FP / FN metrics)

**Detection task (evaluation):** Rank each of *N* φ dimensions by |z| (or composite alarm); treat the top-*k* as the alert set (*k* = 3; *N* = 17–18).

| Term | Definition |
|------|------------|
| **TP (eval.)** | Flagged dimension where an anomaly was knowingly introduced or present in ground truth |
| **FP (eval.)** | Flagged dimension with only normal variation relative to ground truth |
| **FN (eval.)** | Ground-truth anomaly dimension **not** in the top-*k* alert set |
| **TN (eval.)** | Normal-variation dimension not flagged |
| **Precision** | TP / (TP + FP) |
| **Recall (top-*k*)** | TP / (TP + FN) |
| **False positive rate** | FP / (FP + TN) |

**Scope:** Metrics measure **transaction-type dimension ranking**, not dollar amount of a single transaction and not LLM scheme labels. Pipeline pass/fail alone is insufficient for formal precision/recall; per-pattern top-*k* logging against ground truth is required.

### Table E — Layer 4 outcomes that resemble—but are not—the same as—Layer 2 FP / FN

| Layer 4 outcome | Resembles (informally) | Is it the same as Layer 2 FP or FN? |
|-----------------|------------------------|-------------------------------------|
| **Benign resolution** | “False alarm” / FP | **No** — alert was statistically warranted; FRP established legitimate context. Often **would** count as FP (eval.) only if ground truth were strictly “no anomaly of any kind.” |
| **Corroborated alert** | “True hit” / TP | **Aligns with TP (eval.)** when eval. ground truth exists; broader in production (includes control weaknesses, not only fraud). |
| **Missed event** | “Miss” / FN | **Aligns with FN (eval.)** when ground truth is known; operational label when fraud was material but did not surface in top-*k* or warnings. |

**Design intent:** NGAME is a **triage instrument**. A moderate Layer 2 FP rate under fraud-only ground truth is acceptable when the cost of late detection (ACFE-style median lag without continuous monitoring) dominates the cost of FRP review of statistically warranted alerts.

### Suggested manuscript paste-in (false positives / negatives)

> *False positives and false negatives:* Confusion-matrix terms apply only to Layer 2 evaluation of top-*k* φ-dimension ranking against known or injected anomalies. Day-over-day record overlap (Layer 1) uses retained, added, and removed—not TP, FP, FN, or TN—because it is descriptive Jaccard similarity, not classifier output. Scheme interpretation (Layer 3) produces taxonomy-grounded hypotheses, not FP/FN outcomes. At Layer 4, alerts resolved as benign after FRP review are not classified as false positives in the detector-error sense; they are **benign resolutions** of statistically warranted signals.

---

## Table 1 — Layer 1: Day-over-Day Record Overlap (Jaccard / CPI)

**Replaces the Jaccard 2×2 labels TP, FP, FN, TN in manuscript prose.**

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

### Jaccard vs confusion-matrix layout (reader bridge)

In mainstream usage, Jaccard similarity is a **set-similarity coefficient**: |A ∩ B| / |A ∪ B|. The 2×2 partition (present/absent in Y × present/absent in T) has the **same grid shape** as a confusion matrix and as intersection-over-union (IoU) in segmentation, where cells are sometimes labeled TP/FP/FN relative to a **reference mask**. NGAME Layer 1 uses **no such reference**: rows and columns index **temporal membership** (yesterday vs today), not predicted vs correct. CPI = *a*/*n* is descriptive churn measurement, not classifier performance.

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
- Design intent: the alert instrument favors **recall over precision** given ACFE-style detection lag without continuous monitoring.

**Layer 2 outputs (operational, pre-interpretation):**

| Term | Definition |
|------|------------|
| **z-score** | *z*ₖ = (CPIₖ(today) − μₖ) / σₖ; signed deviation from trained mean |
| **Deviation band** | \|z\| > 3.0 → HIGH; \|z\| > 2.0 → MEDIUM; else LOW |
| **Composite alarm** | Fires when count-based or dollar-weighted signal reaches MEDIUM or HIGH |
| **Top-*k* alert set** | The *k* φ dimensions with largest \|z\| (or equivalent ranking rule) on a given day; **primary statistical trigger** for downstream steps |

---

## Table 3 — Layer 3: Scheme Interpretation (Taxonomy Linkage)

**Question:** Given the Layer 2 alert set, how plausibly do observed patterns align with known asset-misappropriation scheme classes?

After top-*k* dimensions are flagged, NGAME maps associated accounts to classes in `Asset_Misappropriation.ttl` using a locally hosted LLM with retrieval-style prompting (`ngame_llm_analysis_agent.py`). A **deterministic anchor** — curated QuickBooks transaction-type → taxonomy mapping with ACFE evidence priors (`ngame_misappropriation_mapping_and_scoring.py`) — provides a reproducible baseline for audit.

**NGAME does not treat Layer 3 output as a fraud verdict.** Scheme labels and narrative **brief the FRP**; they do not alone escalate severity or replace Layer 2 alerting.

| Term | Definition |
|------|------------|
| **Statistical alert set** | Top-*k* φ dimensions from Layer 2; primary trigger for FRP attention |
| **Scheme-concordant mapping** | Taxonomy class assignment consistent with both the flagged transaction type and curated ACFE/QBO priors |
| **Taxonomy grounding** | Assigned scheme classes must exist in `Asset_Misappropriation.ttl`; no free-form scheme invention |
| **Deterministic anchor** | Reproducible misappropriation-likelihood score from curated mapping rules and ACFE evidence weights |
| **Interpretive divergence** | LLM-assigned scheme class or emphasis disagrees with the deterministic anchor |
| **Narrative adjunct** | LLM explanation text supporting FRP review; subordinate to statistical alerting |
| **Model-reported confidence** | LLM self-assessed confidence (0–1 in prompts); **epistemic, not calibrated** — not treated as probability of fraud |

### Warranted claims at Layer 3 (interpretive fidelity)

State explicitly what Layer 3 **does** warrant:

1. **Taxonomy grounding** — outputs reference ontology-defined scheme classes.
2. **Reproducibility under fixed model and temperature** — repeated runs with identical inputs are expected to be substantially stable, not necessarily bit-identical.
3. **Concordance with deterministic anchor** — LLM outputs can be audited against the curated mapping/scoring module.
4. **Non-authoritative role** — Layer 2 triggers review; Layer 3 enriches the briefing.

### Layer 3 evaluation (lightweight; not a confusion matrix)

If quantitative reporting is required without a fourth metric grid:

| Check | What it measures |
|-------|------------------|
| **Grounding rate** | Fraction of LLM-assigned taxonomy classes that exist in the TTL |
| **Anchor concordance** | Fraction of flagged transaction types where LLM top scheme class matches deterministic anchor top class |
| **Rerun stability** | Qualitative agreement of scheme classes across repeated runs (fixed model, temperature) |

Formal calibration of scheme labels against adjudicated outcomes (Layer 4 → retrospective labels) may be deferred; state as a limitation if not yet measured.

### Terms to avoid at Layer 3

| Avoid | Reason | Prefer |
|-------|--------|--------|
| **The triage** (for LLM output) | Collides with Layer 4 FRP adjudication | **Scheme interpretation** or **taxonomy enrichment** |
| **Reliable ranking** (LLM) | Implies Layer 2–style detection validity | **Concordant with deterministic anchor** or **grounded scheme mapping** |
| **False positive** (scheme label) | Conflates with Layer 2 eval. | **Interpretive divergence** or **scheme mismatch on review** |
| **Fraud confirmed** | NGAME does not adjudicate | **Scheme-concordant hypothesis** (FRP decides at Layer 4) |
| **Reliable** (unqualified, for LLM) | Reader imports Layer 1–2 meaning | **Grounded**, **auditable**, or **interpretively concordant** |

---

## Table 4 — Layer 4: FRP Adjudication Outcomes (Operational)

**NGAME does not accuse anyone of fraud.** A management warning means activity is statistically unusual relative to the organization’s 30-day baseline; the FRP adjudicates at Layer 4.

| Term | Definition | Relation to prior layers |
|------|------------|------------------------|
| **Statistically warranted alert** | \|z\| or composite alarm exceeds threshold; signal is real relative to trained μ, σ | Layer 2; may correspond to FP (eval.) if ground truth is “normal business change” |
| **Scheme-concordant hypothesis** | Layer 3 mapping plausibly names an ACFE-style scheme class for flagged activity | Layer 3; may still yield **benign resolution** at Layer 4 |
| **Corroborated alert** | FRP review finds material concern: fraud, control weakness, or required correction | Aligns with TP (eval.) when ground truth exists; broader in production |
| **Benign resolution** | Alert correctly reflected baseline deviation; FRP explains as legitimate (e.g., new GL accounts, seasonal vendor onboarding) | Often FP (eval.) under fraud ground truth; **not** a system failure under triage design |
| **Missed event** | Material misappropriation occurred but did not surface in warnings or top-*k* | FN (eval.) when ground truth is known |

### Terms to avoid at Layer 4

| Avoid | Reason | Prefer |
|-------|--------|--------|
| **False positive** (unqualified) | Implies detector error; conflates with Layer 2 | **Benign resolution** or **statistically warranted, benign on review** |
| **True positive** (unqualified) | Implies fraud confirmed by the system | **Corroborated alert** (after FRP review) |
| **Unreliable warning** | Suggests broken instrumentation | **Benign resolution** or **spurious for fraud purposes, valid for triage** |
| **Reliable** (for warnings) | Collides with “reliable μ and σ estimates” (Layer 1 training) | **Corroborated**, **warranted**, or **actionable after review** |

---

## Table 5 — Cross-Layer Mapping (Illustrative)

One day’s Vendors dimension can illustrate how layers diverge:

| Layer | Example reading |
|-------|-----------------|
| **1 — Structural** | High **Added** and **Removed** counts → low CPI (churn) |
| **2 — Detection** | \|z\| > 3 on Vendors → HIGH; Vendors in top-*k* |
| **3 — Scheme interpretation** | LLM maps to fictitious-vendor / billing-scheme class; deterministic anchor agrees Vendors is high-evidence; narrative cites vendor churn |
| **4 — FRP adjudication** | FRP reviews Audit Log → **benign resolution** (legitimate vendor cleanup) or **corroborated alert** (shell-vendor pattern) |

**Chart of Accounts example (field deployment):** Layer 2 correctly flags HIGH deviation; Layer 3 may propose a master-data scheme hypothesis; Layer 4 **benign resolution** after FRP confirms legitimate new GL accounts. Not an eval. FN; adjudication behaved as designed.

**Scheme-concordant but benign:** Layer 3 can be scheme-concordant while Layer 4 is benign — the statistical signal was real and the scheme hypothesis was plausible, but FRP established legitimate business context. That is not interpretive or detection failure.

---

## Table 6 — Notation Quick Reference

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

> *Terminology:* Day-over-day record overlap (retained, added, removed) describes structural churn only and is not labeled with confusion-matrix terms. True and false positives, precision, and recall apply solely to evaluation of top-*k* dimension ranking against known or injected anomalies (Layer 2). Scheme interpretation (Layer 3) maps flagged activity to ontology-defined misappropriation classes via a locally hosted LLM and is auditable against a deterministic curated anchor; it does not render fraud verdicts. The Financially Responsible Person adjudicates outcomes at Layer 4 as corroborated, benign on review, or missed.

---

*Draft aligned with NGAME CPI analysis (`ngame_cpi_analysis_agent.py`), churn comparison thresholds (`ngame_churn_comparison_agent.py`), LLM taxonomy linkage (`ngame_llm_analysis_agent.py`), deterministic scheme scoring (`ngame_misappropriation_mapping_and_scoring.py`), FRP Operations Guide, and DSRM Evaluation Draft §5.2.*
