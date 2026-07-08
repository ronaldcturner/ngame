---
title: "NGAME Churn Persistence Index (CPI) and Dollar-Weighted CPI (wCPI): Full Derivation"
subtitle: "Per-transaction daily measures rolled up into composite CPI / wCPI and scored against a trained baseline"
date: "July 6, 2026"
---

# NGAME CPI / wCPI — Full Derivation

This document gives the end-to-end computation NGAME uses for each transaction
type's daily measures — the Churn Persistence Index (CPI), its dollar-weighted
variant (wCPI), the trained baseline ($\mu$, $\sigma$), and the $z$-scores and
sequence roll-ups that drive dashboard warnings. NGAME tracks **18 transaction
types** (Customers through Vendors); pipeline output labels them $\varphi_1
\ldots \varphi_{18}$ for indexing only.

---

## 1. Daily set-up — the per-type contingency counts

For each transaction type $k$, `NGameCpiAnalysisAgent` compares yesterday's URI
set $Y_k$ (from `Yesterday.ttl`) against today's URI set $T_k$ (from
`Today.ttl`).

> **URI (Uniform Resource Identifier).** NGAME operates on RDF/OWL ontology
> snapshots in which **every individual transaction is named by a unique URI**
> — e.g. `qb:Invoice_4821`. The URI is the stable identity used to decide
> whether a transaction observed today is the *same* transaction seen yesterday.
> The sets $Y_k$ and $T_k$ are sets of transaction URIs of type $k$; every count
> below is a count of URIs.
>
> **QuickBooks-specific caveat.** The metric is only as reliable as QuickBooks'
> URI assignment. QuickBooks mints a new identifier when a transaction is
> *deleted and recreated* (or voided and re-entered) rather than edited in
> place. The original URI is counted in $b_k$ (removed) and the replacement in
> $c_k$ (added) — registering as churn even when the transaction is
> economically unchanged. An *in-place* edit (amount or memo changed without a
> new URI) leaves set membership intact, so count-based $\mathrm{CPI}_k$ may not
> move; such edits can surface through dollar-weighted $\mathrm{wCPI}_k$ (§3).
> The AdditionRate / DeletionRate split (§2) distinguishes directional churn
> (additions vs. removals).

| Symbol | Definition | Meaning |
|---|---|---|
| $a_k$ | $\lvert Y_k \cap T_k \rvert$ | Present in **both** snapshots (retained) |
| $b_k$ | $\lvert Y_k \setminus T_k \rvert$ | Yesterday **only** (removed) |
| $c_k$ | $\lvert T_k \setminus Y_k \rvert$ | Today **only** (new additions) |
| $n_k$ | $a_k + b_k + c_k$ | Total unique transactions across both days |

Cell $d$ (transactions absent from both days) is **not used**: the universe of
non-occurring transactions is undefined for financial ledger data.

---

## 2. Daily per-type measures — CPI and directional rates

The **Churn Persistence Index** is the **Jaccard similarity** of the two URI
populations, with two directional companions that sum to $1$:

$$
\boxed{\;\mathrm{CPI}_k \;=\; \frac{a_k}{a_k + b_k + c_k} \;=\; \frac{a_k}{n_k}\;}
$$

$$
\mathrm{AdditionRate}_k = \frac{c_k}{n_k}, \qquad
\mathrm{DeletionRate}_k = \frac{b_k}{n_k},
$$

$$
\mathrm{CPI}_k + \mathrm{AdditionRate}_k + \mathrm{DeletionRate}_k = 1.0 .
$$

If $n_k = 0$ (no transactions of type $k$ in either snapshot), then
$\mathrm{CPI}_k = 1.0$ by convention ("absence is stable").

The triplet $(\mathrm{CPI}_k,\ \mathrm{AdditionRate}_k,\ \mathrm{DeletionRate}_k)$
characterises the day's dynamics for type $k$. A **low** CPI (high churn) is the
primary fraud concern; a **high** AdditionRate flags bulk insertion; a **high**
DeletionRate flags retroactive deletion.

### Worked example — single-day CPI

**Customers: one record added.**

$$
\text{Before:}\quad a=50,\ b=0,\ c=0 \;\Rightarrow\; \mathrm{CPI} = \tfrac{50}{50} = 1.000
$$
$$
\text{After:}\quad a=50,\ b=0,\ c=1 \;\Rightarrow\; \mathrm{CPI} = \tfrac{50}{51} = 0.980
$$

**Partial churn (illustrative), $a=2,\ b=2,\ c=1,\ n=5$:**

$$
\mathrm{CPI} = \tfrac{2}{5} = 0.400, \quad
\mathrm{DeletionRate} = \tfrac{2}{5} = 0.400, \quad
\mathrm{AdditionRate} = \tfrac{1}{5} = 0.200,
$$

with $\mathrm{CPI} + \mathrm{AdditionRate} + \mathrm{DeletionRate} = 1.000$.

---

## 3. Dollar-weighted CPI (wCPI)

Unweighted CPI treats a \$50 expense identically to a \$500{,}000 wire. The
weighted form keeps the Jaccard structure but replaces set cardinality with the
sum of transaction amounts $w_i$ (from `qb:hasTotalAmount`; entity-type records
with no dollar amount default to $w_i = \$1$):

$$
\mathrm{wCPI}_k \;=\;
\frac{\displaystyle\sum_{i \,\in\, Y_k \cap T_k} w_i}
     {\displaystyle\sum_{i \,\in\, Y_k \cup T_k} w_i}
\;=\;
\frac{\text{retained dollars}}{\text{total dollars in play}} .
$$

Retained URIs use **today's** amount; removed URIs use **yesterday's** amount.

### Worked example — a \$50,000 expense hidden in a normal day

Twenty transactions: 19 of \$50 retained, plus one new \$50{,}000 expense ($a=19,
b=0, c=1$).

$$
\text{Unweighted:}\quad \mathrm{CPI} = \frac{19}{20} = 0.9500 \quad(\text{looks normal})
$$

$$
\text{Weighted:}\quad
\text{retained } \$ = 19 \times \$50 = \$950, \qquad
\text{union } \$ = \$950 + \$50{,}000 = \$50{,}950,
$$

$$
\mathrm{wCPI} = \frac{950}{50{,}950} = 0.0186 \quad(\text{alarm fires}),
$$

$$
\text{Divergence} = \lvert \mathrm{CPI} - \mathrm{wCPI} \rvert
= \lvert 0.9500 - 0.0186 \rvert = 0.931 \;\rightarrow\; \textbf{HIGH}.
$$

| Metric | Value | Reading |
|---|---|---|
| Unweighted CPI | $0.9500$ | Looks normal (19 of 20 URIs retained) |
| Dollar-weighted wCPI | $0.0186$ | Exposure is overwhelmingly new dollars |
| Divergence | $0.931$ | **HIGH** |

Dollar-alarm thresholds on divergence: $>0.30 =$ HIGH, $>0.15 =$ MEDIUM. A
parallel **dollar $z$-score** (today's wCPI vs. trained $\mu_w$, $\sigma_w$) is
also computed when wCPI baselines exist in the matrix.

---

## 4. The trained baseline — daily $\mu$ and $\sigma$ per type

Over an $N$-day training window, each type accumulates a distribution of daily
CPI values. The Training Matrix stores **Mean CPI ($\mu$)** and **Std Dev CPI ($\sigma$)**
per row (columns B and C), plus daily CPI values in columns Day 1 … Day $N$.

$$
\mu_k = \frac{1}{N} \sum_{t=1}^{N} \mathrm{CPI}_k^{(t)},
\qquad
\sigma_k = \sqrt{\frac{1}{N-1} \sum_{t=1}^{N}\left(\mathrm{CPI}_k^{(t)} - \mu_k\right)^2}.
$$

A separate **wCPI_Baseline** sheet stores $(\mu_w, \sigma_w)$ for dollar-weighted
CPI. Optional day-of-week stratification computes separate $(\mu_k, \sigma_k)$
per weekday (requires roughly 60–90 training days for a stable $\sigma$).

---

## 5. Daily anomaly score — $z$ against the trained distribution

`NGameChurnComparisonAgent` compares today's CPI array to the matrix baseline:

$$
z_k = \frac{\mathrm{CPI}_k^{\text{today}} - \mu_k}{\sigma_k}.
$$

| Condition | Level | Statistical meaning |
|---|---|---|
| $\lvert z_k \rvert \le 2.0$ | LOW | Within roughly 95% of training distribution |
| $2.0 < \lvert z_k \rvert \le 3.0$ | MEDIUM | Outside 95%, within 99.7% |
| $\lvert z_k \rvert > 3.0$ | HIGH | Beyond $3\sigma$ — rare under normal operations |

**Percent deviation** (secondary dashboard readout):

$$
\text{percent\_deviation}_k
= \frac{\lvert \mathrm{CPI}_k^{\text{today}} - \mu_k \rvert}{\mu_k} \times 100 .
$$

**Composite alarm** fires when deviation level is HIGH or MEDIUM, or when the
dollar signal (divergence or dollar $z$-score) is elevated.

### Worked example — ChartOfAccounts

With today's $\mathrm{CPI} = 0.065$ against trained $\mu = 0.049,\ \sigma = 0.004$:

$$
z = \frac{0.065 - 0.049}{0.004} = 4.0 \;\rightarrow\; \textbf{HIGH}.
$$

---

## 6. Composite roll-up — multi-day sequence (SCPI / weighted SCPI)

A slow-burn pattern spreads small daily moves that never trip a single-day alarm.
`NGameSequenceCpiAgent` computes the **geometric mean** of the last $L$ daily
CPIs (default $L=5$), scored with a $\sqrt{L}$-tightened $z$:

$$
\mathrm{SCPI}_k(t, L) = \left(\prod_{i=1}^{L} \mathrm{CPI}_k(t - i + 1)\right)^{1/L},
$$

$$
z_k^{\text{seq}} = \frac{\mathrm{SCPI}_k - \mu_k}{\sigma_k / \sqrt{L}}.
$$

The same $\mu_k, \sigma_k$ from the Training Matrix are used — no schema change.
Weighted SCPI applies the same construction over the daily wCPI buffer.

A type drifting at only $-2\sigma/\text{day}$ (MEDIUM at most on any single day)
can score $z^{\text{seq}} \approx -4.47$ on day 5 — a HIGH alert the per-day
detector would not raise alone.

The rolling buffer (`NGAME_CPI_Rolling_Buffer.json`) retains up to **30 days**
of 18-element CPI (and wCPI) arrays — a storage ceiling set independently of
the sequence window. The sequence path returns `ready=False` until at least $L$
days are present; $L$ (default 5) controls which window length SCPI is computed
over and can be changed at any time without reconfiguring the buffer. The 30-day
capacity means any window from $L=2$ up to $L=30$ can be served from the same
file without waiting for a new accumulation period.

---

## 7. Core implementation (`ngame_cpi_analysis_agent.py`)

Per-type CPI from `_calculate_cpi_for_transaction_type`:

```python
a = len(yesterday_uris & today_uris)   # retained
b = len(yesterday_uris - today_uris)   # removed
c = len(today_uris - yesterday_uris)   # added
n = a + b + c                          # total unique

if n == 0:                             # stable by convention
    return {'cpi': 1.0, 'addition_rate': 0.0, 'deletion_rate': 0.0,
            'retained': 0, 'added': 0, 'removed': 0}

return {
    'cpi':           a / n,
    'addition_rate': c / n,
    'deletion_rate': b / n,
    'retained': a, 'added': c, 'removed': b,
}
```

Dollar-weighted CPI: `_calculate_weighted_cpi_for_transaction_type`. Comparison
and alarms: `ngame_churn_comparison_agent.py`. Sequence path:
`ngame_sequence_cpi_agent.py`.

---

*Verified against NGAME POC codebase and `NGAME_Training_Matrix.xlsx` (Training
Matrix + wCPI_Baseline sheets). The \$50{,}000 wCPI example is from agent test W2.*
