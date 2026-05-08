# NGAME: Generative AI Positioning (Reconstructed Analysis)

## Is NGAME truly Generative AI?

NGAME is best described as a **hybrid system**:

- deterministic pipeline components (data flow, scoring math, orchestration), plus
- generative AI components (retrieval, semantic alignment, interpretation/explanation).

The most defensible phrasing is:

**"Generative-AI-assisted, ontology-grounded fraud analysis."**

---

## What is clearly Generative AI in NGAME

- Autonomous retrieval and synthesis of external fraud knowledge (for example, scheme priors).
- Semantic mapping from external fraud scheme labels to internal ontology classes.
- LLM-driven interpretation/explanation over anomaly outputs and account context.
- Prompted reasoning that can generalize to unfamiliar descriptions and narrative patterns.

---

## What is clearly bespoke/deterministic in NGAME

- Fixed ETL and execution flow (daily orchestration steps, matrix and file operations).
- Hard-coded or rule-based transaction-to-bucket mapping tables.
- Deterministic scoring formulas (`risk`, `frequency`, evidence prior weighting).
- Predefined thresholds, ranking/sorting logic, and output schemas.

---

## Defensible claim language

- NGAME is **not** a pure end-to-end generative system.
- NGAME **is** a **generative AI component embedded in a deterministic risk pipeline**.
- The generative value appears in retrieval, semantic alignment, and explanation under ontology constraints.

Suggested report sentence:

**"The NGAME workflow uses generative AI agents to autonomously discover, retrieve, and synthesize external fraud-typology evidence, then integrates those outputs into an ontology-grounded deterministic scoring pipeline for auditable, context-specific risk ranking."**

---

## Guardrails

- **Source provenance:** Store URL, retrieval timestamp, and extracted fields for each external prior.
- **Deterministic fallback:** If retrieval/LLM fails, continue with rule-based scoring and cached priors.
- **Versioned mapping:** Treat transaction-to-misappropriation mapping as a versioned policy artifact.
- **Separation of roles:** LLM proposes/normalizes; deterministic code computes final risk scores.
- **Auditability:** Persist intermediate artifacts (raw extract, normalized table, mapping, scoring inputs).
- **No silent drift:** Require explicit approval for changes to priors, weights, or mapping rules.
- **Confidence and uncertainty:** Report low-confidence classifications explicitly; avoid false precision.
- **Reproducibility:** Same inputs + same model/config should reproduce equivalent outputs, or log variance cause.

---

## Practical conclusion

If asked whether NGAME "qualifies" as Generative AI, the strongest accurate answer is:

**Yes, as a hybrid GenAI system, not as a purely generative end-to-end system.**

