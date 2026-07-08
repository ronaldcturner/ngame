# NGAME agent functions and testing procedures
_Exported on 5/26/2026 at 16:14:30 PDT from Cursor (3.5.33)_

---

**User**

   My co-author of the NGAME report we are-resubmitting for publication is a professor of accounting and an experienced auditor. Our topic of interest is how NGAME gets tested and approved for fraudulent data entry. We already have the procedure for testing this mannually. But NGAME furthermore has an agent that will do this-on its own-for a production-level installation that accesses live QBO data. My two requests: (1) a thumbnail definition of the function of each NGAME agent, (2) a detailed description of how the NGAME  testing agent "spikes' a live dataset in order to provide on-going testing at a live site.

---

**Cursor**

Searching the codebase and documentation for NGAME agents and how the testing agent spikes live datasets.


Below is publication-oriented material you can adapt for your co-author. It distinguishes **manual / offline validation** from **automated ongoing validation on a live QBO installation**.

---

## (1) Thumbnail definitions — NGAME agents

NGAME is organized as a **daily pipeline** of specialized agents. Each agent owns one transformation step; a flow manager (`ngame_training_flow_manager.py` for Phase I, `ngame_fraud_analysis_flow_manager.py` for Phase II) sequences them.

### Phase I — Training (Days 1–30): establish “normal”

| Agent | One-line function |
|--------|-------------------|
| **Data Extraction Agent** | Connects to QuickBooks Online (or Wave) via read-only API, pulls the day’s ledger snapshot, and writes semantic ontology files (`Yesterday.ttl` / `Today.ttl`). |
| **CPI Analysis Agent** | Compares yesterday vs. today ontologies and computes the 18-element **Churn Persistence Index (CPI)** array—one stability score per transaction type (Customers through Vendors, φ₁–φ₁₈). |
| **Matrix Management Agent** | Appends each day’s CPI array to the **Training Matrix** (Excel), and recalculates per-type mean (μ) and standard deviation (σ)—the organization-specific baseline. |

### Phase II — Fraud analysis (Day 31+): detect deviation from normal

| Agent | One-line function |
|--------|-------------------|
| **Data Extraction Agent** | Same as Phase I: live pull at end of business day; rotates TTL snapshots. |
| **CPI Analysis Agent** | Same as Phase I: produces today’s CPI (and dollar-weighted wCPI) profile. |
| **Credit Card Watch Agent** | Independent rule-based scan of credit-card charges in `Today.ttl` (vendor name vs. GL account coding, structuring, weekend/holiday patterns)—does not use the Training Matrix. |
| **Churn Comparison Agent** | Computes z-scores: \((\text{CPI}_\text{today} - \mu) / \sigma\) for each of 18 types; ranks anomalies and assigns HIGH / MEDIUM / LOW alerts. |
| **Sequence CPI Agent** | Computes **SCPI** (geometric mean of the last *L* days’ CPIs) and sequence z-scores (σ scaled by √*L*) to surface **slow-burn** fraud that no single day would flag. |
| **Anomaly Identification Agent** | Selects top-*k* ranked transaction-type dimensions (e.g., Vendors, Contractors) for escalation. |
| **Account Mapping Agent** | Maps flagged φ indices to concrete Chart of Accounts entries and record identifiers in `Today.ttl`. |
| **LLM Analysis Agent** | Matches flagged accounts to an asset-misappropriation taxonomy (RAG over `Asset_Misappropriation.ttl`) and produces narrative risk interpretation. |
| **Management Warning Agent** | Synthesizes findings into the FRP-facing deliverable (`management_dashboard.json`, optional email)—overall risk level, ranked anomalies, LLM narrative, recommended actions. |

### Validation / continuous assurance (not part of daily fraud detection)

| Agent | One-line function |
|--------|-------------------|
| **Anomaly Injection Agent** | **System test agent**: arms the pipeline with known synthetic fraud signals so operators can verify end-to-end detection on a schedule without corrupting the live ledger. |

### Supporting paths (not daily production agents)

| Component | Role |
|-----------|------|
| **`run_demo_scenario.py`** | Offline demo: spikes selected φ dimensions directly in memory (no QBO, no TTL)—useful for lectures and dry runs. |
| **Phase 1 / Phase 2 Director agents** | Earlier orchestration wrappers around extraction and reporting; superseded for daily ops by the dedicated flow managers above. |

---

## (2) How the testing agent “spikes” a live dataset for ongoing validation

In NGAME terminology, the testing agent is the **Anomaly Injection Agent** (`ngame_anomaly_injection_agent.py`). For an auditor, the important design point is:

> **It does not post fraudulent entries into QuickBooks.**  
> It spikes the **ontology layer** that NGAME builds *after* each live API extraction—so detection is exercised on the same code path as production, without altering the books.

That matches a familiar audit concept: **inject known misstatements into a copy of the population the control sees**, then verify the control fires.

### What “live” means here

1. **Live QBO read** — Data Extraction uses OAuth and pulls the organization’s real transactions into `Today.ttl`.
2. **Controlled spike** — Before CPI analysis, five synthetic vendor entities are **appended** to `Today.ttl` only.
3. **Normal detection** — CPI Analysis, Churn Comparison, and downstream agents run unchanged; the spike must produce a statistically extreme Vendors (φ₁₈) signal if the system is healthy.

QuickBooks itself is never written to; bank and GL balances in QBO are unaffected.

### Two-phase arming and firing

**Phase A — Arm (scheduled or manual, e.g., quarterly)**

`inject_test_anomalies()` (or `run_anomaly_injection_test.py`) does four things:

1. **Builds ground truth** — Creates five synthetic vendor personas (offshore activity, high invoices, rapid frequency, duplicate invoices, after-hours activity) and ~60–75 synthetic transactions in `anomaly_injection_payload.json`, each marked `synthetic_flag: true` and `Vendor_Type: Test_Anomaly_Injection`.

2. **Seeds baseline if needed** — `seed_vendor_training_baseline()` checks the Vendors row (φ₁₈) in `NGAME_Training_Matrix.xlsx`. If training never populated Vendors (μ/σ zero or blank), it fills 30 simulated “stable vendor” CPI values so z-scores are mathematically meaningful when the spike hits.

3. **Sets a one-shot flag** — Writes `anomaly_injection_active.json` (`active: true`, injection ID, timestamp).

4. **Produces management evidence** — Detection test report and optional PASS/FAIL management report for the audit file.

**Phase B — Fire (next daily fraud analysis run on live data)**

`NGameFraudAnalysisFlowManager.execute_daily_fraud_analysis()` implements the hook:

```mermaid
sequenceDiagram
    participant QBO as QuickBooks Online
    participant DE as Data Extraction Agent
    participant TTL as Today.ttl
    participant INJ as Anomaly Injection Agent
    participant CPI as CPI Analysis Agent
    participant CC as Churn Comparison Agent

    QBO->>DE: Read-only API pull (live data)
    DE->>TTL: Write Today.ttl (real population)
    Note over INJ: anomaly_injection_active.json present?
    INJ->>TTL: Append 5 INJECT_SYNTH_* vendor triples
    INJ->>INJ: Delete flag (one-shot)
    CPI->>TTL: Compare Yesterday vs Today (includes synthetics)
    CPI->>CC: Today's CPI array
    CC->>CC: z-scores vs trained μ, σ
```

Concretely, after live extraction:

- The flow manager detects `anomaly_injection_active.json`.
- **`inject_into_ttl()`** appends five RDF vendor resources with IDs `INJECT_SYNTH_001` … `005` (prefix chosen so they cannot collide with real QBO entity IDs).
- Each triple is tagged `qb:hasVendorType "Test_Anomaly_Injection"` and bounded by comment markers in the TTL file.
- The flag file is **removed** so injection does not repeat on subsequent days unless re-armed.

### Why this produces a detectable “spike”

CPI for Vendors measures **overnight persistence** of the vendor population: how much of yesterday’s vendor set still appears today, versus additions and deletions.

Synthetic vendors exist only in **Today.ttl**, not in **Yesterday.ttl**. They behave like a burst of **new, unrecognized payees**—the same structural signal as fictitious-vendor billing schemes in the ACFE taxonomy.

With a seeded or trained Vendors baseline (high μ, low σ = stable vendor master), injecting five new vendor entities drives the Vendors CPI **below** μ by several σ, yielding a **HIGH** z-score on φ₁₈. Your evaluation draft already ties that mechanism to Billing Schemes — Fictitious Vendor.

### Audit and control properties (for your co-author)

| Property | Implication |
|----------|-------------|
| **Non-destructive** | No CREATE/UPDATE to QBO; spike is file-level on NGAME’s ontology copy. |
| **Labeled synthetics** | `INJECT_SYNTH_*`, `Test_Anomaly_Injection`, JSON `synthetic_flag`. |
| **One-shot per arm** | Flag deleted after injection; avoids cumulative pollution of daily runs. |
| **Reproducible ground truth** | Payload JSON records injection ID, timestamp, patterns, and transaction counts for workpaper cross-reference. |
| **Full pipeline under test** | Extraction → CPI → z-score → identification → mapping → LLM → management warning—all exercised, not a unit test of one formula. |
| **Separable from manual testing** | Manual procedure: operator enters test vendors in QBO sandbox. Automated procedure: operator arms injection, then runs normal daily analysis on **production** read access. |

### “Ongoing” operation in practice

NGAME does not continuously inject in the background. **Ongoing assurance** is operational:

1. **Arm** the injection agent (calendar: e.g., quarterly, or before board reporting season).
2. **Run** the next scheduled daily fraud analysis (same job that processes live QBO).
3. **Verify** that Vendors (and related dimensions, if configured) appear in the top-ranked anomalies and that the management report reflects HIGH severity.
4. **Archive** `anomaly_injection_payload.json`, management report, and that day’s `NGAME_Fraud_Analysis*.json` as **completeness testing** evidence (analogous to ITGC walkthrough documentation).
5. **Re-arm** only when the next test cycle is due.

For publication, you may want to state explicitly (as your DSRM draft’s interpretive note already hints) that the current harness certifies **pipeline operability and end-to-end integration**; element-level precision/recall per injected pattern would require extending the harness to log top-*k* φ rankings against ground truth—a natural “future work” sentence for §Evaluation.

### Contrast with your existing manual procedure

| Method | Where the spike occurs | Best for |
|--------|------------------------|----------|
| **Manual** (QBO sandbox / test vendors entered by person) | Real QBO ledger | Teaching, student labs, mirror testing |
| **Anomaly Injection Agent** (production path) | `Today.ttl` after live API pull | Proving controls on the **actual** production monitoring installation |
| **`run_demo_scenario.py`** | In-memory CPI array only | Lectures, no API, no ontology files |

---

If useful for the paper, I can turn this into a formal subsection (e.g., “§4.3 Continuous Control Validation” or “Appendix B — Agent Registry”) in JFAR voice, or produce a one-page table for your co-author’s review packet.

