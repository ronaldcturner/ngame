# NGAME churn analysis enhancement
_Exported on 4/28/2026 at 23:36:19 PDT from Cursor (3.2.11)_

---

**User**

Can NGAME be enhanced so that instead of comparing a single day's Churn to the baseline indices in the Training Matrix, it presents a sequence of days' churns? Case is a QBO user who creates an anomalous number of vendors, but over a period of several days. This woulld entail injecting a new computation, formulating a CPI measurement for the sequence of current days and then comparing that combined CPI to the baseline in the training matrix. Do not change the existing codebase yet, but give me an architecture and revised pipeline that would make this possible.

---

**Cursor**

Let me explore the codebase thoroughly before designing the architecture.

Now let me read the canvas skill before designing the architecture document.

Good. Now I have everything I need. Let me write the architecture canvas.

I've created a canvas you can open beside the chat — it's a live, interactive architecture document. Here's the full design:

---

## Architecture Overview

### The Core Problem SCPI Solves

The current pipeline compares each day's CPI vector to the Training Matrix independently. An attacker who adds 3 new shell vendors per day never triggers HIGH because each individual day scores MEDIUM at most. The anomaly only becomes visible when you observe the *pattern* across days.

The key statistical insight: if a transaction type deviates by k standard deviations every day, a window of L days produces a sequence z-score of approximately **k√L**. A sustained MEDIUM (−2σ/day) becomes HIGH in just 3 days: √3 × 2 = 3.46σ.

---

### The New Metric: SCPI (Sequence Churn Proximity Index)

For a window of L days ending at day t, for each of the 18 transaction types k:

```
SCPI_k(t, L) = ( ∏ CPI_k(t−i+1) )^(1/L)    for i = 1…L
```

This is the **geometric mean** of L daily CPIs — appropriate because CPI is a multiplicative persistence measure in [0,1]. It's computed in log space for numerical stability.

The sequence z-score uses the same Training Matrix μ and σ, but divides by √L:

```
z_k^seq = ( SCPI_k − μ_k ) / (σ_k / √L)
```

The σ/√L derivation comes from the delta-method standard error of the geometric mean, valid when σ ≪ μ — exactly the case for any well-trained baseline. **No Training Matrix schema changes are needed.**

---

### Revised Pipeline

The sequence path runs in **parallel** with the existing single-day path, branching from CPI Analysis and merging back at Anomaly Identification:

```
[CPI Analysis] ──────────────────────────────► [Single-Day Compare] ─┐
     │                                                                  │
     └──► [CPI Rolling Buffer] ──► [Sequence CPI Agent] ──► [Seq Compare] ─┘
                                                                           │
                                                         [Anomaly ID] ◄────┘
                                                              ▼
                                                     [Account Map → LLM → Warnings]
```

When the buffer has fewer than L days, the sequence path silently skips — the existing pipeline is completely unaffected.

---

### Slow-Burn Vendor Scenario (Concrete Numbers)

With μ_vendors = 0.995, σ = 0.005, and 3 new shell vendors added per day:

| Day | Vendor CPI | Single-Day z | Alert | 5-Day SCPI | Seq z | Seq Alert |
|-----|-----------|-------------|-------|-----------|-------|-----------|
| 1 | 0.987 | −1.60 | LOW | — | — | — |
| 2 | 0.983 | −2.40 | MEDIUM | — | — | — |
| 3 | 0.986 | −1.80 | LOW | — | — | — |
| 4 | 0.984 | −2.20 | MEDIUM | — | — | — |
| **5** | 0.982 | −2.60 | MEDIUM | **0.9844** | **−4.74** | **HIGH** |
| 6 | 0.985 | −2.00 | MEDIUM | 0.9840 | −4.92 | HIGH |
| 7 | 0.983 | −2.40 | MEDIUM | 0.9840 | −4.92 | HIGH |

Single-day analysis never exceeds MEDIUM. The sequence path triggers HIGH on day 5.

---

### New Components (5 total)

| Component | Type |
|-----------|------|
| `NGAME_CPI_Rolling_Buffer.json` | New file — persists 18-element daily CPI records |
| `NGameSequenceCpiAgent` | New agent — computes SCPI and σ_seq |
| `NGameChurnComparisonAgent` | Modified — adds `compare_sequence_profiles()` |
| `run_sequence_analysis.py` | New entry script — `--window L` flag |
| `run_demo_sequence_scenario.py` | New demo — slow-burn 7-day vendor scenario |

---

### Three Implementation Phases

- **Phase 1 — Rolling Buffer:** Touch only `NGameCpiAnalysisAgent`; append each day's CPI/rate arrays to the buffer. Nothing else changes.
- **Phase 2 — Sequence CPI Agent:** New standalone agent, unit-testable without any API calls or live data.
- **Phase 3 — Integration:** Wire the comparison agent extension, the entry script, and the demo. Optionally surface sequence z-scores in the management dashboard JSON alongside existing single-day results.

Ready to start implementing any phase whenever you give the go-ahead.

