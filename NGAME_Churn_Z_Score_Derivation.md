# NGAME Churn Z-Score Derivation

*A layered mathematical construction — from raw ontology records to a per-transaction-type z-score.*

---

## Notation Conventions

| Symbol | Meaning |
|---|---|
| \( k \) | Transaction type index, \( k \in \{1, 2, \ldots, K\} \), \( K = 18 \) |
| \( t \) | Day index (integer); \( t \) = today, \( t-1 \) = yesterday |
| \( r \) | A single record (ontology individual), identified by its URI |
| \( S_k(t) \) | Set of all record URIs of type \( k \) present at the end of day \( t \) |
| \( n_k(t) \) | Cardinality of the snapshot: \( n_k(t) = \lvert S_k(t) \rvert \) |
| \( \mathrm{CPI}_k(t) \) | Churn Persistence Index for type \( k \) on day \( t \) |
| \( \mu_k,\, \sigma_k \) | Baseline mean and standard deviation of \( \mathrm{CPI}_k \) over the training period |
| \( z_k \) | Z-score deviation of today's CPI from its trained baseline |

---

## Layer 1 — End-of-Day Record Set for a Single Transaction Type

The most elemental object is the **daily snapshot** of a transaction type: the complete collection of record identifiers (URIs) that QBO reports as active at close of business on day \( t \).

\[
S_k(t) \;=\; \bigl\{\, r \;\mid\; r \text{ is a record of type } k \text{ present at end of day } t \,\bigr\}
\]

with cardinality

\[
n_k(t) \;=\; \lvert S_k(t) \rvert
\]

> **Reading:** \( S_k(t) \) is simply the set of unique record identifiers belonging to transaction type \( k \) that exist in the `*_Today.ttl` ontology snapshot. The count \( n_k(t) \) tells you how many records of that type were present today.

---

## Layer 2 — End-of-Day Status Across All Transaction Types

Collecting the snapshot for every transaction type yields the **full daily state vector**:

\[
\mathbf{S}(t) \;=\; \bigl(\, S_1(t),\; S_2(t),\; \ldots,\; S_K(t) \,\bigr)
\]

This is the semantic analogue of the QBO data extract for day \( t \): one set per transaction type, together covering all \( K = 18 \) types in fixed positional order:

| \( k \) | Transaction Type |
|---|---|
| 1 | Customers |
| 2 | Recurring\_payments |
| 3 | Invoices |
| 4 | Payments |
| 5 | Time\_Activities |
| 6 | Bills |
| 7 | Bill\_Payments |
| 8 | Expenses |
| 9 | Bank\_Transactions |
| 10 | Sales\_transactions |
| 11 | Products |
| 12 | PurchaseOrders |
| 13 | Recurring\_Transactions |
| 14 | Contractors |
| 15 | Mileage |
| 16 | ChartOfAccounts |
| 17 | EmployeePayroll |
| 18 | Vendors *(high-risk fraud hot-spot)* |

---

## Layer 3 — Day-to-Day Change for Each Transaction Type

To measure how much the record population of type \( k \) changed overnight, compare \( S_k(t-1) \) (yesterday's snapshot, from `*_Yesterday.ttl`) with \( S_k(t) \) (today's snapshot, from `*_Today.ttl`).

The comparison produces a **three-way contingency partition** of the total unique URI pool:

\[
a_k \;=\; \lvert\, S_k(t-1) \;\cap\; S_k(t) \,\rvert \qquad \text{(retained — present in both days)}
\]

\[
b_k \;=\; \lvert\, S_k(t-1) \;\setminus\; S_k(t) \,\rvert \qquad \text{(removed — in yesterday only)}
\]

\[
c_k \;=\; \lvert\, S_k(t) \;\setminus\; S_k(t-1) \,\rvert \qquad \text{(added — in today only)}
\]

\[
n_k \;=\; a_k + b_k + c_k \;=\; \lvert\, S_k(t-1) \;\cup\; S_k(t) \,\rvert \qquad \text{(total unique URIs seen across both days)}
\]

> **Note on the absent fourth cell:** Classical contingency tables include a fourth count \( d \) for the "double-absent" case — records that appeared in neither day. That cell is formally excluded here because the universe of non-occurring financial transactions is unbounded and undefined. The universe for this measure is \( S_k(t-1) \cup S_k(t) \) only.

**Edge case:** When \( n_k = 0 \) (type \( k \) has no records in either snapshot), the type is treated as stably absent:

\[
n_k = 0 \;\Rightarrow\; a_k = b_k = c_k = 0, \quad \mathrm{CPI}_k(t) := 1.0 \text{ (by convention)}
\]

---

## Layer 4 — Churn Scalar for Each Transaction Type (CPI)

The **Churn Persistence Index** \( \mathrm{CPI}_k(t) \) rolls up the three-way contingency into a single scalar that expresses how much of the combined record population persisted unchanged:

\[
\boxed{
\mathrm{CPI}_k(t) \;=\; \frac{a_k}{n_k} \;=\; \frac{\lvert S_k(t-1) \cap S_k(t) \rvert}{\lvert S_k(t-1) \cup S_k(t) \rvert}
\qquad \in \;[0,\, 1]
}
\]

This is the **Jaccard similarity** between the two URI sets. It is bounded:

- \( \mathrm{CPI}_k = 1 \): every record that existed yesterday still exists today, and no new records appeared — perfect persistence, zero churn.
- \( \mathrm{CPI}_k = 0 \): no records survived from yesterday into today — complete turnover.

Two companion rates are defined so that the three fractions partition unity:

\[
\alpha_k(t) \;=\; \frac{c_k}{n_k} \qquad \text{(Addition Rate — fraction of total pool that is new today)}
\]

\[
\delta_k(t) \;=\; \frac{b_k}{n_k} \qquad \text{(Deletion Rate — fraction of total pool removed since yesterday)}
\]

\[
\mathrm{CPI}_k(t) \;+\; \alpha_k(t) \;+\; \delta_k(t) \;=\; 1 \qquad \text{(always)}
\]

The full **CPI array** for day \( t \) is the ordered vector of CPI scalars across all \( K \) transaction types:

\[
\mathbf{CPI}(t) \;=\; \bigl(\, \mathrm{CPI}_1(t),\; \mathrm{CPI}_2(t),\; \ldots,\; \mathrm{CPI}_K(t) \,\bigr)
\]

---

## Layer 5 — Z-Score for Each Transaction Type

### 5a. Training Phase — Establish the Baseline

Over a training period of \( T \) days, collect \( \mathrm{CPI}_k(t) \) for each type \( k \). Compute the **baseline mean** and **baseline standard deviation**:

\[
\mu_k \;=\; \frac{1}{T} \sum_{t=1}^{T} \mathrm{CPI}_k(t)
\]

\[
\sigma_k \;=\; \sqrt{\;\frac{1}{T} \sum_{t=1}^{T} \bigl(\mathrm{CPI}_k(t) - \mu_k\bigr)^2\;}
\]

These two values — stored per row in the Training Matrix \( \mathbf{M} \) — define the expected daily behavior for transaction type \( k \).

### 5b. Analysis Phase — Compute the Z-Score

On a new analysis day \( t' \), compute \( \mathrm{CPI}_k(t') \) exactly as in Layer 4, then standardize against the trained baseline:

\[
\boxed{
z_k \;=\; \frac{\mathrm{CPI}_k(t') - \mu_k}{\sigma_k}
}
\]

with the degeneracy guard:

\[
\sigma_k = 0 \;\Rightarrow\; z_k := 0
\]

### 5c. Sign Interpretation

The z-score is **signed**. Both directions carry fraud-relevant meaning:

| Sign | Meaning |
|---|---|
| \( z_k \ll 0 \) | Today's CPI is far *below* baseline — more churn than usual. Signals possible **mass deletion or record suppression**. |
| \( z_k \gg 0 \) | Today's CPI is far *above* baseline — less churn than usual, or a **bulk-insertion day** with many new records persisting. |

### 5d. Deviation Bands

\[
\text{Deviation}(z_k) \;=\;
\begin{cases}
\textbf{HIGH}   & \lvert z_k \rvert > 3 \\
\textbf{MEDIUM} & 2 < \lvert z_k \rvert \leq 3 \\
\textbf{LOW}    & \lvert z_k \rvert \leq 2
\end{cases}
\]

### 5e. The Z-Score Vector

The final output of a daily analysis run is the **z-score vector** — one signed scalar per transaction type:

\[
\mathbf{z} \;=\; \bigl(\, z_1,\; z_2,\; \ldots,\; z_K \,\bigr)
\]

The element with the largest \( \lvert z_k \rvert \) identifies the transaction type whose churn behavior deviates most from its trained norm, and is ranked first among anomaly candidates.

---

## Summary: The Full Derivation Chain

```
Day-t Snapshot          S_k(t)  =  { URI₁, URI₂, … }              (Layer 1–2)
         │
         │  set intersection / difference with S_k(t−1)
         ▼
Contingency counts      a_k, b_k, c_k, n_k                          (Layer 3)
         │
         │  Jaccard ratio
         ▼
CPI scalar              CPI_k(t) = a_k / n_k  ∈ [0,1]              (Layer 4)
         │
         │  standardize against trained μ_k, σ_k
         ▼
Z-score                 z_k = (CPI_k(t') − μ_k) / σ_k              (Layer 5)
```

---

*Document version: 2026-04-16 | Matches implementation in `ngame_cpi_analysis_agent.py` and `ngame_churn_comparison_agent.py`*
