# NGAME Gen AI — Scope and Limits (Manuscript Paste-In)

**Status:** Draft for journal manuscript  
**Purpose:** Align Evaluation §§5.6–5.8 with the four-layer trust properties (`NGAME_Glossary_Four_Layer_Terminology.md`)  
**Audience:** Co-authors revising `NGAME_DSRM_Evaluation_Draft.html` (or successor §7 Evaluation)

---

## Primary paste-in (recommended: new subsection after §5.6 Table 5.4, or opening paragraph of §5.8)

> **Generative AI scope and evaluation bounds.** NGAME is a hybrid surveillance artifact, not a generative-AI-first detector. Layers 1 and 2 — day-over-day churn measurement (CPI) and top-*k* φ-dimension ranking by standardized deviation — are fully deterministic and constitute the **primary statistical trigger** for Financially Responsible Person (FRP) attention. Layer 3 adds **scheme interpretation**: a locally hosted large language model (LLM), prompted with retrieval-style context from `Asset_Misappropriation.ttl`, maps flagged transaction types and associated accounts to ontology-defined asset-misappropriation classes and produces plain-language narrative for management briefing. This layer **enriches** review; it does not replace Layer 2 alerting or render a fraud verdict. A parallel **deterministic anchor** — curated QuickBooks transaction-type → taxonomy mapping with ACFE evidence priors (`ngame_misappropriation_mapping_and_scoring.py`) — supplies a reproducible baseline for audit and convergent analytical comparison; it is not presented as a substitute for generative interpretation but as governance infrastructure against which LLM outputs may be checked for **interpretive divergence**. Layer 4 adjudication remains with the FRP (corroborated alert, benign resolution, or missed event).
>
> The Phase II evaluation therefore demonstrates **incorporation** of generative AI in the operational pipeline (end-to-end test suite execution; observational finding that FRP-facing output was interpretable without technical explanation) but does **not** yet demonstrate formal **evaluation** of Layer 3 interpretive fidelity. Convergent validity evidence in this study — z-score decomposition, independent phi-coefficient similarity, and *a priori* misappropriation risk ranking — bears on **detection and triage** (Layers 1–2) and theory-aligned priors, not on LLM scheme-label accuracy, anchor concordance, or narrative stability. Precision, recall, and false-positive rate apply only to top-*k* dimension ranking under controlled ground truth (Layer 2); they do not apply to LLM taxonomy output. Systematic characterization of LLM grounding rate, anchor concordance, rerun stability, and calibration against adjudicated outcomes is deferred to subsequent research, consistent with the proof-of-concept stage of this design-science contribution.

---

## Short variant (footnote or abstract-adjacent sentence)

> Generative AI in NGAME operates at Layer 3 (taxonomy-grounded scheme interpretation and FRP briefing) and is subordinate to deterministic statistical alerting (Layers 1–2); Phase II evaluates pipeline integration and detection triage, not LLM interpretive performance.

---

## Targeted revisions to existing §5.6 prose

### Replace (§5.6, paragraph after Table 5.4)

**Current (overstated):**

> …by replacing the auditor-as-operator with a behaviorally-trained automated pipeline, and by replacing the auditor's interpretive judgment with an LLM-assisted risk assessment aligned to a published fraud taxonomy.

**Suggested:**

> …by replacing the auditor-as-operator with a behaviorally-trained automated pipeline, and by **augmenting** FRP review with an LLM-assisted scheme interpretation layer aligned to a published fraud taxonomy — **subordinate to deterministic statistical alerting and non-authoritative for fraud adjudication**.

### Optional Table 5.4 row refinement

| Capability dimension | ACL / IDEA | NGAME (revised wording) |
|----------------------|------------|-------------------------|
| LLM-assisted analysis | None | Local LLM provides **taxonomy-grounded scheme interpretation and plain-language briefing** for flagged dimensions; statistical alerting remains deterministic; no transaction data leaves the FRP's Surveillance Computer |

---

## §5.7 convergent-validity clarification (one sentence after the convergence table)

> Convergent findings reported here validate the **CPI-based detection and triage method** (Layers 1–2) and theory-aligned *a priori* risk priors; they do not constitute independent validation of Layer 3 generative outputs.

---

## §5.8 limitation paragraph (expand or replace current “Fourth” limitation)

**Current fourth limitation** (retain substance; optional merge with primary paste-in):

> Fourth, the LLM reasoning layer (Ollama RAG) introduces output variability that has not been systematically characterized…

**Suggested expansion (if not using the full primary paste-in in §5.8):**

> Fourth, the Layer 3 LLM reasoning component introduces output variability that has not been systematically characterized. Scheme labels and narratives are **hypotheses for FRP review**, auditable against a deterministic curated anchor but not evaluated in this study for grounding rate, anchor concordance, rerun stability, or calibration against adjudicated outcomes. The anomaly injection suite confirms end-to-end pipeline operability including the LLM step; it does not score interpretive fidelity. Formal Layer 3 evaluation is a necessary component of a full generative-AI claims program and is beyond the scope of the current proof-of-concept instantiation.

---

## Placement map

| Manuscript location | Use |
|---------------------|-----|
| **§5.6** (after Table 5.4) | Primary paste-in + §5.6 revision |
| **§5.7** (after convergence table) | One-sentence clarification |
| **§5.8** | Expanded fourth limitation (or reference primary paste-in if placed earlier) |
| **Abstract / contribution statement** | Short variant |
| **Four-layer glossary** | Cross-reference only; terminology source remains `NGAME_Glossary_Four_Layer_Terminology.md` |

---

*Aligned with `docs/drafts/NGAME_Glossary_Four_Layer_Terminology.md`, `NGAME_DSRM_Evaluation_Draft.html` §§5.6–5.8, `ngame_llm_analysis_agent.py`, and `ngame_misappropriation_mapping_and_scoring.py`.*
