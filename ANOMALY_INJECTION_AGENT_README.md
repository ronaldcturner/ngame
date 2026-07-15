# NGAME Anomaly Injection Agent

## Overview

The **NGAME Anomaly Injection Agent** (`ngame_anomaly_injection_agent.py`) is a **controlled-evaluation agent** in NGAME’s hybrid agentic architecture. A technical operator **invokes** the agent (CLI); the agent then executes the injection test workflow. It does **not** run from the FRP dashboard and does **not** post records to the client’s QuickBooks ledger.

**Primary modules**

| Role | File |
|------|------|
| Agent | `ngame_anomaly_injection_agent.py` (`NGameAnomalyInjectionAgent`) |
| Test suite runner | `run_anomaly_injection_test.py` |

---

## Critical clarifications (read first)

### 1. Injection target = local TTL snapshot (not the client ledger)

**Injection** means appending synthetic vendor triples to NGAME’s **local day ontology** — typically `quickbooks_ontology_Today.ttl` — after data extraction and before CPI analysis.

It does **not** create vendors, bills, or payments in the client’s QuickBooks Online or Desktop company file. NGAME’s QBO access is **read-only**.

### 2. Who runs it

| Role | Action |
|------|--------|
| **Consultant / technician** | Invokes the agent via CLI from the project root (not the FRP via the dashboard) |
| **Anomaly Injection Agent** | Generates the synthetic payload, arms the one-shot flag, reports operability |
| **Fraud Analysis Flow Manager** (next daily run) | Sees the flag, calls `inject_into_ttl()`, then runs the normal hybrid pipeline |
| **FRP** | Reviews dashboard warnings after a fraud check; does **not** launch this suite |

### 3. Agentic hybrid framing

The human issues the run command; the **agent** executes the test workflow. Detection and briefing after TTL injection remain the same hybrid pipeline: deterministic statistical channels (CPI / wCPI / SCPI), optional rule-based Credit Card Watch, and RAG-based interpretation under the Fraud Analysis Flow Manager.

### 4. What this suite proves vs what it does not

| Proves (operability) | Does **not** by itself prove |
|----------------------|------------------------------|
| Synthetic cases can be generated and audit-logged | Formal Layer-2 precision/recall on five named “patterns” |
| Reports and validation checks complete | That offshore / duplicate / after-hours detail was scored as five separate TTL detectors |
| Flag + subsequent fraud run can append vendors to `Today.ttl` for **Vendors (φ18)** churn | Automatic assert that Vendors ∈ top-*k* (operator must compare fraud-run output to ground truth) |

**Honest scope:** The four-phase suite certifies **incorporation / operability** and produces an audit trail. **Detection performance** for the paper requires a subsequent fraud-analysis run and comparison of Top Anomalies (especially Vendors φ18) against `anomaly_injection_payload.json`.

### 5. Five scenario labels vs what lands in the TTL

The agent builds **five labeled synthetic vendor templates** (and matching fake transactions) in the **JSON payload** for audit narrative:

1. Offshore vendor activity  
2. Unusually high invoice amounts  
3. Rapid transaction frequency  
4. Duplicate invoice patterns  
5. After-hours transactions  

Those rich transaction details live in `anomaly_injection_payload.json`. When `inject_into_ttl()` runs, the ontology receives **five Vendor URIs** (`INJECT_SYNTH_001` … `_005`) with name / type / amount — enough to drive **vendor-population CPI churn**, not five independent pattern engines inside the TTL.

---

## Purpose

1. **Controlled evaluation** — documentable synthetic cases for system testing  
2. **Operability certification** — confirm injection, reporting, and validation steps complete  
3. **Audit trail** — payload + reports for compliance / manuscript appendix  
4. **Bridge into daily detection** — arm a one-shot path so the next fraud run mutates the local TTL and exercises CPI / top-*k* on Vendors  

---

## Who invokes the agent (usage)

### Recommended: full test suite (consultant / tech)

From the **repository root**:

```bash
cd /path/to/NGAME-POC
python3 run_anomaly_injection_test.py
```

This runs four phases:

1. **Phase 1** — Agent generates synthetic vendors/transactions; writes payload; arms `anomaly_injection_active.json`; may seed Vendors μ/σ if needed  
2. **Phase 2** — Detection-style report generated from the synthetic payload  
3. **Phase 3** — Management / operability report  
4. **Phase 4** — File/status validation (operability checks)

**Not launched from** the dashboard “Run Today's Fraud Check” button.

### Then: exercise the detector (required for detection evidence)

With the flag still present (or after TTL append):

```bash
python3 run_fraud_analysis.py
```

Or restart the dashboard and use **Run Today's Fraud Check**. During that run the Fraud Analysis Flow Manager should inject into `Today.ttl` (one-shot; flag cleared), then continue CPI → *z* → top-*k* → warnings.

Archive:

- `anomaly_injection_payload.json`  
- `anomaly_injection_management_report.json`  
- `anomaly_injection_test_suite_final_report.json`  
- `NGAME_Fraud_Analysis*.json` (or readable variant)  
- Note whether **Vendors (φ18)** appears in Top Anomalies with HIGH  

Human-readable example from a July 2026 run: `docs/drafts/Anomaly_Injection_Test_Report_2026-07-14.md` (and `.docx`).

### Direct agent entry points

```bash
python3 ngame_anomaly_injection_agent.py
```

Or in Python:

```python
from ngame_anomaly_injection_agent import NGameAnomalyInjectionAgent

agent = NGameAnomalyInjectionAgent()
result = agent.inject_test_anomalies(num_vendors=5)
if result['success']:
    manager_report = agent.generate_manager_report(result['detection_report'])
```

---

## Output files

| File | Purpose |
|------|---------|
| `anomaly_injection_payload.json` | Ground-truth audit of synthetic vendors/transactions |
| `anomaly_injection_active.json` | One-shot flag for the next fraud-analysis run (consumed when TTL is injected) |
| `anomaly_injection_management_report.json` | Operability / executive-style summary |
| `anomaly_injection_test_suite_final_report.json` | Four-phase suite summary |

---

## Synthetic vendor templates (payload labels)

| Template name | Pattern label | Role in payload |
|---------------|---------------|-----------------|
| Offshore Tech Solutions | Offshore vendor activity | Scenario narrative in JSON |
| Premium Consulting Group | Unusually high invoice amounts | Scenario narrative in JSON |
| Rapid Services Corp | Rapid transaction frequency | Scenario narrative in JSON |
| Global Trade Partners | Duplicate invoice patterns | Scenario narrative in JSON |
| Night Operations LLC | After-hours transactions | Scenario narrative in JSON |

TTL injection (fraud-run path) appends five Vendor triples with ids `INJECT_SYNTH_001` … `INJECT_SYNTH_005`.

---

## Compliance & safety

- Injected data is marked synthetic (`synthetic_flag`, `Test_Anomaly_Injection`, `INJECT_SYNTH_*` URIs)  
- **Client QuickBooks ledger is not modified**  
- Injection is confined to NGAME’s local workspace artifacts (TTL / JSON / matrix seed as applicable)  
- Keep an audit trail of payload + fraud-run outputs for evaluation write-ups  

---

## Integration (hybrid pipeline)

| Component | Relationship |
|-----------|----------------|
| **Anomaly Injection Agent** | Invoked by tech; prepares payload / flag / TTL append |
| **Fraud Analysis Flow Manager** | Orchestrates daily run; performs TTL inject when flag present |
| **CPI / Churn / Anomaly Identification Agents** | Score Vendors churn after synthetic URI adds |
| **LLM / Management Warning Agents** | Downstream briefing (unchanged path) |
| **FRP dashboard** | Displays results; does not start this suite |

---

## Troubleshooting

**Working directory:** Always run from the repo root so relative paths (`Today.ttl`, matrix, JSON outputs) resolve.

**Dashboard “Network error”:** Usually means the Flask app (`ngame_ui/app-simple.py`, port 5001) is not running. Restart the dashboard or use `run_fraud_analysis.py` instead. Injection suite completion does not depend on the dashboard.

**Flag already gone / vendors already in TTL:** A fraud run may have already consumed `anomaly_injection_active.json` and appended `INJECT_SYNTH_*`. Re-run the suite only if you want a fresh payload and flag.

---

## Recommendations

- Run from a **consultant / tech** account or workstation, not as an FRP dashboard click  
- Treat phase-4 PASS as **operability**, then run fraud analysis for **detection** evidence  
- Archive payload + fraud JSON for the evaluation / manuscript record  
- Do not describe injection as writing to the client’s live ledger  

---

**Agent version:** 1.1  
**Last updated:** 15 July 2026  
**Status:** Operational (evaluation harness; local TTL only)
