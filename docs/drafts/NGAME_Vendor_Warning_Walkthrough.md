---
title: "Vendors Warning Walkthrough — How the HIGH Alert Is Generated"
subtitle: "Essential calculations only (Vendors / 18th transaction type)"
date: "July 6, 2026"
---

# Vendors Warning Walkthrough

This note traces **only** the calculations that turn today's Vendors signal into the
dashboard warning **8.9% · $z \approx -7.28$ · HIGH**, ranked #1. Values are taken from
`NGAME_Fraud_Analysis_readable_truly_clean.json` and the Vendors row of
`NGAME_Training_Matrix.xlsx`.

## Given (inputs to the warning path)

| Quantity | Symbol | Value |
|---|---|---|
| Today's Vendors CPI | $\mathrm{CPI}_{18}^{\text{today}}$ | $0.90625$ |
| Trained mean | $\mu_{18}$ | $0.994794174882256$ |
| Trained std dev | $\sigma_{18}$ | $0.01216178288304404$ |

---

## Step 1 — Percent deviation (dashboard readout: 8.9%)

$$
\text{absolute\_difference}
= \left\lvert \mathrm{CPI}_{18}^{\text{today}} - \mu_{18} \right\rvert
= \left\lvert 0.90625 - 0.994794174882256 \right\rvert
= 0.088544174882256
$$

$$
\text{percent\_deviation}
= \frac{\text{absolute\_difference}}{\mu_{18}} \times 100
= \frac{0.088544174882256}{0.994794174882256} \times 100
= 8.90\%
$$

---

## Step 2 — $z$-score (dashboard readout: $z \approx -7.28$)

$$
z_{18}
= \frac{\mathrm{CPI}_{18}^{\text{today}} - \mu_{18}}{\sigma_{18}}
= \frac{0.90625 - 0.994794174882256}{0.01216178288304404}
= \frac{-0.088544174882256}{0.01216178288304404}
= -7.280525868
\;\;\Rightarrow\;\; z \approx -7.28
$$

Negative $z$: today's CPI is **below** the trained mean (more churn than normal).

---

## Step 3 — Deviation level (HIGH)

| Rule | Level | This case |
|---|---|---|
| $\lvert z \rvert > 3.0$ | HIGH | $7.28 > 3.0 \Rightarrow$ **HIGH** |
| $2.0 < \lvert z \rvert \le 3.0$ | MEDIUM | — |
| $\lvert z \rvert \le 2.0$ | LOW | — |

---

## Step 4 — Dollar-weighted path (wCPI)

For Vendors, each record has no dollar amount; weights default to \$1, so the
dollar-weighted index equals the count-based CPI:

$$
\mathrm{wCPI}_{18}^{\text{today}} = 0.90625 = \mathrm{CPI}_{18}^{\text{today}}
$$

$$
\text{dollar\_}z_{18} = -7.280525868 \quad (\text{same as } z_{18})
$$

$$
\text{divergence} = \left\lvert \mathrm{wCPI}_{18}^{\text{today}} - \mathrm{CPI}_{18}^{\text{today}} \right\rvert = 0
$$

`dollar_alarm_level = "HIGH"` (driven by dollar $z$, not divergence).

---

## Step 5 — Composite alarm and rank

$$
\text{composite\_alarm}
= \big(\text{deviation\_level} \in \{\text{HIGH}, \text{MEDIUM}\}\big)
\;\lor\; \text{dollar\_alarm}
= \text{HIGH} \;\lor\; \text{true}
= \textbf{TRUE}
$$

$$
\text{rank} = 1 \quad (\text{largest } \lvert z \rvert \text{ among all 18 transaction types})
$$

---

## Summary chain

| Step | Formula | Plugged in | Result |
|---|---|---|---|
| 1 | $\%\text{dev} = \lvert \mathrm{CPI}-\mu\rvert/\mu \times 100$ | $0.088544 / 0.994794 \times 100$ | $8.90\%$ |
| 2 | $z = (\mathrm{CPI}-\mu)/\sigma$ | $-0.088544 / 0.012162$ | $-7.281$ |
| 3 | $\lvert z \rvert > 3 \Rightarrow$ HIGH | $7.28 > 3$ | HIGH |
| 4 | $\mathrm{wCPI} = \mathrm{CPI}$ (Vendors) | $0.90625$ | dollar HIGH |
| 5 | composite\_alarm | HIGH $\lor$ dollar\_alarm | TRUE, rank 1 |

**Dashboard line:** *Vendors (the 18th transaction type) — 8.9% · $z \approx -7.28$ · HIGH*, rank #1.

---

*Formulas per `ngame_churn_comparison_agent.py` (z-score, deviation bands, dollar/composite alarms).*
