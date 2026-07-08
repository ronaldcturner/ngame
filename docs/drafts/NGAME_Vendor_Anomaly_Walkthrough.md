---
title: "Worked Example — The 6-Vendor Anomaly (Vendors, the 18th transaction type)"
subtitle: "Every equation NGAME runs, by example, from raw snapshot to the dashboard's HIGH warning"
date: "June 28, 2026"
---

# Worked Example — The 6-Vendor Anomaly ($\varphi_{18}$)

A bookkeeper added **6 new vendors in a single day**. This note traces every
equation NGAME executes on the real numbers from
`NGAME_Fraud_Analysis_readable_truly_clean.json` and the Vendors row of
`NGAME_Training_Matrix.xlsx` — each value plugged in — to show exactly how the
dashboard arrives at **8.9% · $z \approx -7.28$ · HIGH**, ranked first of all 18
transaction types.

## What the $-7.28$ means (the short answer)

The $-7.28$ is the **$z$-score**: today's Vendors CPI sits **7.28 standard
deviations below** the mean stability NGAME learned for Vendors during training.
Anything past $3\sigma$ is astronomically unlikely under normal operation — hence
HIGH. The $8.9\%$ shown beside it is a softer, secondary readout (how far below
normal as a plain percentage); the $-7.28$ is what the alarm logic keys on.

## The inputs (pulled straight from the files)

| Quantity | Symbol | Value | Source |
|---|---|---|---|
| Today's Vendors CPI | $\mathrm{CPI}_{18}$ | $0.90625$ | `today_cpi_array` → Vendors (JSON) |
| Trained mean CPI | $\mu_{18}$ | $0.994794174882256$ | Vendors row, col B (matrix) |
| Trained std deviation | $\sigma_{18}$ | $0.01216178288304404$ | Vendors row, col C (matrix) |
| New vendors added today | $c_{18}$ | $6$ | stated scenario |
| Vendors removed today | $b_{18}$ | $0$ | stated scenario |

---

## Step 1 — Daily set-up: recover the contingency counts

The dashboard stores the resulting CPI, not the raw counts. But with 6 added and
0 removed, the counts are forced by the CPI value. Solve
$\mathrm{CPI} = a / (a + b + c)$ for $a$:

$$
0.90625 = \frac{a}{a + 0 + 6}
$$

$$
0.90625\,(a + 6) = a \;\Rightarrow\; 0.90625\,a + 5.4375 = a
$$

$$
5.4375 = a - 0.90625\,a = 0.09375\,a
\;\Rightarrow\;
a = \frac{5.4375}{0.09375} = 58
$$

$$
\boxed{\; a_{18} = 58 \text{ retained}, \quad b_{18} = 0 \text{ removed}, \quad
c_{18} = 6 \text{ added}, \quad n_{18} = 58 + 0 + 6 = 64 \;}
$$

---

## Step 2 — Daily per-type measures: CPI and its companions

$$
\mathrm{CPI}_{18} = \frac{a}{n} = \frac{58}{64} = 0.90625
$$

$$
\mathrm{AdditionRate}_{18} = \frac{c}{n} = \frac{6}{64} = 0.09375
\qquad
\mathrm{DeletionRate}_{18} = \frac{b}{n} = \frac{0}{64} = 0
$$

$$
0.90625 + 0.09375 + 0 = 1.0 \quad \checkmark
$$

Already the signal is visible: nearly **one in ten** vendors in today's ledger did
not exist yesterday ($\mathrm{AdditionRate} = 9.375\%$).

---

## Step 3 — Percent deviation (the 8.9% on the dashboard)

A plain "how far below normal" readout — the absolute gap from the mean, expressed
as a percent of the mean.

$$
\text{absolute\_difference} = \lvert \mathrm{CPI}_{18} - \mu_{18} \rvert
= \lvert 0.90625 - 0.994794174882256 \rvert = 0.088544174882256
$$

$$
\text{percent\_deviation}
= \frac{\text{absolute\_difference}}{\mu_{18}} \times 100
= \frac{0.088544174882256}{0.994794174882256} \times 100
= 8.90\%
$$

---

## Step 4 — The $z$-score (the $-7.28$, the real alarm driver)

Percent deviation ignores *how steady Vendors normally is*. The $z$-score divides
the gap by the trained $\sigma$, so a tiny $\sigma$ makes a small gap enormous.

$$
z_{18} = \frac{\mathrm{CPI}_{18} - \mu_{18}}{\sigma_{18}}
= \frac{0.90625 - 0.994794174882256}{0.01216178288304404}
= \frac{-0.088544174882256}{0.01216178288304404}
= -7.280525868
$$

$$
\boxed{\; z_{18} \approx -7.28 \;}
$$

The sign is negative because today's CPI is *below* the mean (more churn than
normal). Vendors is normally extremely steady ($\sigma \approx 0.0122$), so even an
$0.0885$ drop lands $7.28\sigma$ away.

---

## Step 5 — Deviation band: turn $z$ into HIGH / MEDIUM / LOW

| Rule | Level | This case |
|---|---|---|
| $\lvert z \rvert > 3.0$ | HIGH | $7.28 > 3.0 \Rightarrow$ **HIGH** $\checkmark$ |
| $2.0 < \lvert z \rvert \le 3.0$ | MEDIUM | — |
| $\lvert z \rvert \le 2.0$ | LOW | — |

$\lvert z \rvert = 7.28$ clears the $3\sigma$ bar by more than double, so
`deviation_level = "HIGH"`; and because it is the largest $\lvert z \rvert$ of all
18 types, it is ranked **#1**.

---

## Step 6 — Dollar path (wCPI): why the dollar signal matches

Vendors are master-data entities with no `hasTotalAmount`, so each weight falls back
to $\$1$. The dollar-weighted Jaccard therefore collapses onto the unweighted one:

$$
\text{every } w_i = \$1 \;\Rightarrow\;
\mathrm{wCPI}_{18} = \frac{W_{\text{retained}}}{W_{\text{union}}}
= \frac{58}{64} = 0.90625 = \mathrm{CPI}_{18}
$$

$$
\text{dollar\_}z_{18} = \frac{0.90625 - 0.994794}{0.012162} = -7.2805
\quad(\text{identical to the count } z)
$$

The dollar divergence $\lvert \mathrm{wCPI} - \mathrm{CPI} \rvert = 0$, so the HIGH
comes from the dollar **$z$-score**, not divergence:
`dollar_alarm_level = "HIGH"`, `dollar_alarm = true`. This is expected for
master-data types — the dollar signal duplicates the count signal rather than adding
new information.

---

## Step 7 — Composite alarm and final ranking

$$
\text{composite\_alarm}
= \big(\text{deviation\_level} \in \{\text{HIGH}, \text{MEDIUM}\}\big)
\;\lor\; \text{dollar\_alarm}
= \text{HIGH} \;\lor\; \text{true}
= \textbf{TRUE}
$$

$$
\text{rank} = 1 \quad (\text{largest } \lvert z \rvert = 7.2805 \text{ across all 18 types})
$$

**What the FRP sees on the dashboard:** *Vendors ($\varphi_{18}$) — 8.9% · $z \approx -7.28$ ·
HIGH*, ranked #1 of 18. Translation: vendor turnover today is 7.28 standard
deviations beyond this organization's learned norm — six brand-new payees appeared
at once in a category that almost never changes. That is the flagrant anomaly,
surfaced for Audit-Log follow-up.

---

## The whole chain on one line

| # | Equation | Plugged in | Result |
|---|---|---|---|
| 1 | $n = a + b + c$ | $58 + 0 + 6$ | $64$ |
| 2 | $\mathrm{CPI} = a/n$ | $58 / 64$ | $0.90625$ |
| 2 | $\mathrm{AdditionRate} = c/n$ | $6 / 64$ | $0.09375$ |
| 3 | $\%\text{dev} = \lvert \mathrm{CPI}-\mu\rvert/\mu \times 100$ | $0.088544 / 0.994794 \times 100$ | $8.90\%$ |
| 4 | $z = (\mathrm{CPI}-\mu)/\sigma$ | $-0.088544 / 0.012162$ | $-7.281$ |
| 5 | $\lvert z \rvert > 3 \Rightarrow$ HIGH | $7.28 > 3$ | HIGH |
| 6 | $\mathrm{wCPI} = W_{\text{ret}}/W_{\text{union}}$ | $58 / 64$ (\$1 each) | $0.90625$ |
| 7 | composite\_alarm | HIGH $\lor$ dollar\_alarm | TRUE |

---

*Sources: values read from `NGAME_Fraud_Analysis_readable_truly_clean.json`
(today_cpi_array, comparison_result, account_result) and the Vendors row of
`NGAME_Training_Matrix.xlsx`. Formulas verified against
`ngame_churn_comparison_agent.py` (z-score, bands, dollar/composite alarms) and
`ngame_cpi_analysis_agent.py` (CPI / wCPI). The $a/b/c$ counts are reconstructed
from the stated scenario (6 added, 0 removed) and the recorded CPI; the per-type
counts are not stored in this JSON.*
