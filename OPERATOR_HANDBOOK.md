# NGAME Operator Handbook (Short)

## Purpose

Run NGAME safely day-to-day and respond quickly to alerts or failures.

---

## 1) Daily Operations

### Start-of-Day Checks (2-5 min)

- Confirm Python environment is active.
- Confirm required files exist:
  - `Curated Transaction Types.ttl`
  - `Asset_Misappropriation.ttl` (needed for fraud mode)
- Confirm data source config is valid:
  - `quickbooks_config.json` or `wave_config.json`
- If using LLM stage, confirm Ollama is up (`http://localhost:11434`).

### Run Pipeline

Preferred:

```bash
python3 ngame_dual_mode.py
```

Alternative explicit runs:

```bash
python3 run_training_flow.py
python3 run_fraud_analysis.py
```

### End-of-Run Checks

- New `*_ontology_Today.ttl` exists.
- If training mode: `NGAME_Training_Matrix.xlsx` updated.
- If fraud mode: `NGAME_Fraud_Analysis*.json` and `management_dashboard.json` updated.
- No fatal errors in console output.

---

## 2) Mode Behavior

### Training Mode

- Trigger: matrix missing or training days < target.
- Outcome: adds day-column phi values to matrix and refreshes averages.
- Success signal: training day incremented.

### Fraud Analysis Mode

- Trigger: training baseline complete.
- Outcome:
  1. Compare today vs baseline CPI array
  2. Rank deviations
  3. Analyze top 3 anomalies
  4. Map to accounts
  5. LLM risk analysis
  6. Generate management warnings
- Success signal: fraud analysis JSON + dashboard generated.

---

## 3) Operator Decision Rules

### If Overall Risk = HIGH

- Escalate to finance/security lead immediately.
- Review top anomalies and affected accounts same day.
- Create incident ticket and attach generated JSON artifacts.

### If Overall Risk = MEDIUM

- Start enhanced monitoring.
- Request account owner validation on flagged areas.
- Re-run next business day and compare trend.

### If Overall Risk = LOW

- Record run as normal.
- Continue daily cadence.

---

## 4) Common Failure Playbook

### A) Missing Training Matrix

- Symptom: fraud mode prerequisite failure.
- Action: run training flow until baseline complete.

### B) Missing `Yesterday.ttl`

- Symptom: first run cannot compare day-over-day.
- Action: run again next day; first run is expected to bootstrap.

### C) LLM/Ollama Unavailable

- Symptom: errors in LLM analysis stage.
- Action: start/restart Ollama, verify model availability, re-run fraud analysis.

### D) Credential/API Errors

- Symptom: extraction/auth failures.
- Action: validate tokens/keys/realm/business ID, refresh credentials, retry run.

### E) Excel/openpyxl Errors

- Symptom: matrix update/load failure.
- Action: verify file is not locked, reinstall `openpyxl`, re-run.

---

## 5) Artifacts to Retain (Audit Minimum)

Per run, archive:

- `*_ontology_Today.ttl`
- `NGAME_Training_Matrix.xlsx` (snapshot/backup)
- `NGAME_Fraud_Analysis*.json` (if fraud mode)
- `management_dashboard.json`
- Run timestamp + mode + operator name

---

## 6) Weekly/Monthly Tasks

### Weekly

- Verify matrix growth and no missing days.
- Spot-check warning quality with finance owner.
- Review repeated anomaly types.

### Monthly

- Rotate API credentials/tokens.
- Validate dependency/environment consistency.
- Confirm taxonomy alignment with business controls.

---

## 7) Quick Commands

```bash
source .venv/bin/activate
python3 ngame_dual_mode.py
python3 run_training_flow.py
python3 run_fraud_analysis.py
```

---

## 8) Escalation Template

**Subject:** NGAME Alert - `<HIGH|MEDIUM>` Risk - `<DATE>`

Include:

- Run time
- Mode
- Top anomalies
- Affected accounts
- Artifact paths
- Immediate actions taken
- Owner assigned
- Next review time

