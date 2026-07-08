# NGAME Training Matrix — Option D Replay Checklist (Days 1–12 stitch)

**Purpose:** Correct Days 1–12 (count-based CPI + dollar-weighted wCPI) in the completed 30-day matrix using a **fresh replay sandbox**, then merge into the original matrix. Days 13–30 stay from the original build.

**Scope:** Internal testing only. Published papers will use a full clean 30-day training run.

**Honesty note:** Days 1–12 come from the replay timeline; Days 13–30 from the original timeline. Document as a hybrid matrix for internal use.

---

## Before you start

- [ ] Fixed alias code is in place (`ngame_transaction_types.py` — already merged).
- [ ] Original matrix complete: **30 / 30** days.
- [ ] Session log for original build (optional, for matching session types).
- [ ] **Empty replay sandbox** (new QBO sandbox company, or wiped test company) — **not** the full Safe Landing with 30 days already posted.
- [ ] OAuth / `quickbooks_config.json` can point at replay company for Phase 1–3, then back to Safe Landing after.

---

## Phase 0 — Backup (repo root)

```bash
cd /Users/ronturner/Developer/Projects/NGAME-POC

cp NGAME_Training_Matrix.xlsx NGAME_Training_Matrix_30day_ORIGINAL.xlsx
cp quickbooks_ontology_Today.ttl quickbooks_ontology_Today_AFTER_D30.ttl
cp quickbooks_ontology_Yesterday.ttl quickbooks_ontology_Yesterday_AFTER_D30.ttl
```

- [ ] Backups created; `NGAME_Training_Matrix_30day_ORIGINAL.xlsx` untouched until merge succeeds.

---

## Phase 1 — Clear replay workspace

```bash
# Hide 30-day matrix; start fresh file on first training run
mv NGAME_Training_Matrix.xlsx NGAME_Training_Matrix_HOLD_30day.xlsx

# Clear TTL chain for replay
rm -f quickbooks_ontology_Today.ttl quickbooks_ontology_Yesterday.ttl
```

- [ ] Point NGAME QuickBooks OAuth at **replay sandbox** (empty company).
- [ ] Start dashboard: `python3 ngame_ui/app-simple.py`
- [ ] Dashboard shows **0 of 30** / “No training days recorded yet…”

---

## Phase 2 — Replay sessions 1–12 (12 times)

**Rotation (session type):**

| Session | Type | Post in QBO (Build Guide Part 3) |
|--------:|:----:|----------------------------------|
| 1 | A | Sales Day |
| 2 | B | Vendor Day |
| 3 | C | Payroll / Contractor Day |
| 4 | D | Collections Day |
| 5 | E | Mixed / Light Day |
| 6 | F | Admin Day |
| 7 | A | Sales Day |
| 8 | B | Vendor Day |
| 9 | C | Payroll / Contractor Day |
| 10 | D | Collections Day |
| 11 | E | Mixed / Light Day |
| 12 | F | Admin Day |

**Each session (repeat 12 times):**

1. [ ] Post that session’s transaction batch in QBO (**All apps** → correct form per type).
2. [ ] Save each transaction; minimal entity + amount is OK.
3. [ ] Dashboard → **Run Today’s Training Day** — wait for **exit 0**.
4. [ ] Training progress shows **N of 30** (N = 1 … 12).
5. [ ] Do **not** stop dashboard mid-run.

**Expect after replay:**

| Item | Expected |
|------|----------|
| Day 1 column | Often **blank** (no Yesterday yet) — normal |
| Days 2–12 | Real decimals on fixed rows (`Payments`, `Bill_Payments`, `Bank_Transactions`, …) |
| `wCPI_Baseline` sheet | **wDay 2 … wDay 12** populated (no wDay 1) |
| Red ❌ `quickbooks.objects.vehicle` etc. | Harmless — ignore if run completes |

**Terminal alternative** (instead of dashboard button):

```bash
python3 run_training_flow.py
# Answer y for each day; n to pause after Day 12
```

---

## Phase 3 — Save replay + restore production files

```bash
cp NGAME_Training_Matrix.xlsx NGAME_Training_Matrix_REPLAY_D12.xlsx

cp NGAME_Training_Matrix_30day_ORIGINAL.xlsx NGAME_Training_Matrix.xlsx

cp quickbooks_ontology_Today_AFTER_D30.ttl quickbooks_ontology_Today.ttl
cp quickbooks_ontology_Yesterday_AFTER_D30.ttl quickbooks_ontology_Yesterday.ttl
```

- [ ] Replay matrix saved as `NGAME_Training_Matrix_REPLAY_D12.xlsx`
- [ ] Active matrix is again the **30-day original**
- [ ] TTL files restored for **Phase II on Safe Landing**
- [ ] OAuth pointed back to **original Safe Landing** company

---

## Phase 4 — Merge Days 1–12 + recalculate baselines

```bash
python3 merge_training_matrix_days.py \
  --target NGAME_Training_Matrix.xlsx \
  --source NGAME_Training_Matrix_REPLAY_D12.xlsx \
  --days 1-12
```

Script actions:

1. Auto-backup → `NGAME_Training_Matrix_pre_merge_<timestamp>.xlsx`
2. Copy **Day 1–12** on **Training Matrix** sheet
3. Copy **wDay 2–12** on **wCPI_Baseline** sheet (dollar-weighted)
4. Recalculate **μ, σ** and **μ_w, σ_w**

- [ ] Merge completed without error

---

## Phase 5 — Verify

Open `NGAME_Training_Matrix.xlsx`:

**Training Matrix sheet**

- [ ] Columns **Day 1 … Day 12** updated on aliased rows (not all 1.0 except Day 1 blank / stable types)
- [ ] Columns **Day 13 … Day 30** unchanged from original
- [ ] **μ** (col B) and **σ** (col C) refreshed

**wCPI_Baseline sheet**

- [ ] **wDay 2 … wDay 12** updated where replay differed
- [ ] **wDay 13 … wDay 30** unchanged
- [ ] **μ_w** and **σ_w** refreshed

**Dashboard**

- [ ] Restart `app-simple.py` if needed
- [ ] Still **30 of 30**, Phase II ready

---

## Phase 6 — First Phase II smoke test (optional)

- [ ] Run one **daily fraud / churn check** on Safe Landing
- [ ] Confirm no extraction errors for types you use
- [ ] **Last Updated** reflects recent run

---

## Quick reference — file roles

| File | Role |
|------|------|
| `NGAME_Training_Matrix_30day_ORIGINAL.xlsx` | Untouched archive of first 30-day build |
| `NGAME_Training_Matrix_REPLAY_D12.xlsx` | Replay output (Days 1–12 only) |
| `NGAME_Training_Matrix.xlsx` | **Active** stitched matrix after merge |
| `quickbooks_ontology_*_AFTER_D30.ttl` | Phase II snapshots from end of original build |
