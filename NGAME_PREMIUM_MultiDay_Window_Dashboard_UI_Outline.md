# NGAME Premium — Multi-Day Pattern Window (Dashboard UI) — Feature Outline

**Document ID (for search):** `NGAME_PREMIUM_MultiDay_Window_Dashboard_UI_Outline.md`  
**Status:** Proposal / might-ship for subscription tier  
**Audience:** Product owner, implementation lead (not FRP-facing prose)  
**Related code today:** `ngame_fraud_analysis_flow_manager.py` (`sequence_window`, default `5`), `run_fraud_analysis.py`, `ngame_ui/app-simple.py`, `ngame_ui/templates/dashboard.html` (read-only display)

---

## 1. Feature summary

| Item | Description |
|------|-------------|
| **User-facing name** | **Multi-Day Pattern Window** (or **Slow-Burn Lookback**) |
| **Premium?** | Yes — adjustable window length is a **subscription** capability |
| **Free tier** | Fixed window (e.g. **5 business days**), display-only on dashboard |
| **Premium tier** | FRP chooses lookback **L** from dashboard before each run (within allowed bounds) |
| **Problem solved** | Organizations differ: some want tighter 3-day sensitivity, others 7–10 day slow-burn detection |
| **Constraint** | FRP still uses **dashboard only** — no Terminal, no file paths |

---

## 2. What the FRP sees (premium)

### 2.1 Placement on dashboard

In the existing **Multi-Day Pattern Alert** card (Phase II / fraud runs):

1. **Label:** “Lookback period (business days)”
2. **Control:** Dropdown or stepper (not free-text) — e.g. `3`, `4`, `5`, `6`, `7`, `10`
3. **Helper text:** “How many consecutive business days NGAME combines to detect slow-building patterns.”
4. **Default:** Last value used on this machine, or product default `5` if never set
5. **Lock icon / badge:** “Premium” when subscription active; control disabled + tooltip when not

### 2.2 Interaction with daily run

- **Run Today's NGAME Check** (or **Run Churn Analysis**) sends the **selected L** with the run request.
- After the run, the card shows: “Sustained-pattern scan over the last **L** business days” (already partially supported in display logic).
- If the rolling buffer has fewer than **L** days of history, show the existing “building up” message (no error).

### 2.3 Free vs premium UX

| Tier | Multi-Day card |
|------|----------------|
| **Free** | Summary + results only; footnote: “Lookback: 5 days (standard). Upgrade to adjust.” |
| **Premium** | Same + **enabled** lookback selector |
| **Expired subscription** | Selector visible but disabled; revert to 5 on run |

---

## 3. What happens under the hood (architecture)

```
┌─────────────────────────────────────────────────────────────┐
│  Dashboard (FRP)                                             │
│  [ Lookback: 5 ▼ ]  [ Run Today's NGAME Check ]              │
└──────────────────────────┬──────────────────────────────────┘
                           │ POST /api/run-fraud-analysis
                           │      { "sequence_window": 7 }
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  app-simple.py                                               │
│  • Verify subscription / license flag                          │
│  • Clamp L to min/max (e.g. 3–10)                            │
│  • Pass L to subprocess or in-process runner                 │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  run_fraud_analysis.py  OR  direct FlowManager call          │
│  NGameFraudAnalysisFlowManager(sequence_window=L)            │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Existing pipeline (unchanged logic)                         │
│  sequence_cpi_agent.compute_scpi(window=L)                   │
│  churn_comparison_agent.compare_sequence_profiles(..., L)    │
│  → NGAME_Fraud_Analysis.json includes sequence_window: L     │
└─────────────────────────────────────────────────────────────┘
```

### 3.1 Persistence (no FRP file editing)

| Option | Pros | Cons |
|--------|------|------|
| **A. `ngame_ui_settings.json`** in repo root (consultant-writable, FRP reads via API) | Simple, survives restart | FRP doesn’t edit file; server writes on change |
| **B. Server-side only (in-memory + optional SQLite)** | Clean for multi-user later | Lost on restart unless persisted |
| **C. QuickBooks company–scoped config** | One setting per org | More plumbing |

**Recommended for POC → v1:** **A** — `ngame_ui_settings.json` with keys:

```json
{
  "sequence_window": 5,
  "subscription": {
    "tier": "premium",
    "expires_at": "2027-01-01T00:00:00Z"
  }
}
```

Consultant sets tier during install; FRP only changes `sequence_window` when premium is active.

---

## 4. API sketch (dashboard ↔ server)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/ui-config` | Returns `frp_mode`, `training_status`, **`sequence_window`**, **`premium_active`**, **`allowed_windows`** `[3,4,5,6,7,10]` |
| `POST` | `/api/settings/sequence-window` | Body `{ "days": 7 }` — premium only; validates and saves |
| `POST` | `/api/run-fraud-analysis` | Optional body `{ "sequence_window": 7 }` — overrides saved default for this run only |
| `POST` | `/api/run-daily` | Uses saved `sequence_window` when phase = fraud |

**Validation rules (example):**

- Integer only; `L ∈ {3,4,5,6,7,10}` or `3 ≤ L ≤ 10`
- Reject if `premium_active === false` (return 403 + message for UI)
- Training runs ignore `L` (sequence path inactive until Phase II)

---

## 5. Code touchpoints (implementation checklist)

| Layer | File | Change |
|-------|------|--------|
| Pipeline | `ngame_fraud_analysis_flow_manager.py` | Already accepts `sequence_window`; no change to core math |
| Launcher | `run_fraud_analysis.py` | Read `NGAME_SEQUENCE_WINDOW` env var or CLI `--window` for subprocess from UI |
| UI server | `ngame_ui/app-simple.py` | Load/save settings; pass `L` into `_stream_script` env; premium gate |
| UI template | `ngame_ui/templates/dashboard.html` | Selector in Multi-Day card; wire to API; disable when not premium |
| Artifacts | `NGAME_Fraud_Analysis.json` | Already has `summary.sequence_window` — keep populating |
| Docs | `FRP_OPERATIONS_GUIDE.md` | Premium section: how to change lookback (when subscribed) |
| Install | `INSTALL.md` | Consultant: enable premium flag / license file (not FRP) |

**Optional:** `run_sequence_analysis.py` remains consultant diagnostic tool with `--window` (unchanged).

---

## 6. Subscription / licensing (product, not FRP)

FRP never enters a license key in Terminal. Consultant or back-office enables premium:

| Mechanism | Description |
|-----------|-------------|
| **Local license file** | e.g. `ngame_license.json` (gitignored) written at install |
| **Online check** | Periodic validation against NGAME subscription API (future) |
| **Dashboard flag** | `premium_active` derived from license; UI gates selector |

**Graceful degradation:** If license expires mid-deployment, next run uses **L = 5** and UI shows upgrade message.

---

## 7. Safety and accounting notes (for FRP guide)

- **Larger L** → more sensitive to **sustained** drift; may increase MEDIUM/HIGH on multi-day card.
- **Smaller L** → faster reaction, more noise on volatile books.
- Window is **business days in the CPI rolling buffer**, not calendar days — document in helper text.
- Changing **L** does **not** retrain the 30-day matrix; it only changes how today's sequence comparison is scaled (√L in z_seq).

---

## 8. Phased delivery

| Phase | Deliverable |
|-------|-------------|
| **P0 (today)** | Fixed L=5; dashboard display only ✅ |
| **P1** | Consultant sets `sequence_window` in settings file; no FRP UI |
| **P2** | FRP dropdown + API; local `premium_active` flag (honor system / install-time) |
| **P3** | Subscription validation + audit log of window changes |
| **P4** | Per-organization defaults from cloud admin portal |

---

## 9. Acceptance criteria (when built)

- [ ] FRP can change lookback from dashboard **without** Terminal.
- [ ] Non-premium install cannot set L ≠ 5 via UI (API returns 403).
- [ ] **Run Churn Analysis** uses selected L; JSON and Multi-Day card show same L.
- [ ] Invalid values (e.g. 2, 99) rejected with clear on-screen message.
- [ ] `INSTALL.md` documents consultant premium enablement; FRP guide documents selector only.

---

## 10. Filename reminder

Save and search for:

**`NGAME_PREMIUM_MultiDay_Window_Dashboard_UI_Outline.md`**

Keywords: premium, subscription, multi-day, sequence window, SCPI, slow-burn, dashboard, FRP, lookback.

---

*Outline only — not implemented. Last updated: May 2026.*
