# NGAME — FRP Guide: Reading the Phase II Dashboard

*One-page reference for the Financially Responsible Person — what each alert means and what to do.*

**You use:** NGAME Dashboard bookmark only (no Terminal). **Full daily ops:** [FRP_OPERATIONS_GUIDE.md](../../FRP_OPERATIONS_GUIDE.md).

---

## Phase I vs Phase II (30 seconds)

| Phase | Days | Button | What you are doing |
|-------|------|--------|-------------------|
| **Phase I** | 1–30 | **Run Today's Training Day** | NGAME **learns** normal churn — not daily fraud alerts |
| **Phase II** | 31+ | **Run Today's Fraud Check** | NGAME **compares** today to that 30-day baseline |

After **30 of 30** on the progress bar, use Phase II from the **next** business day.

---

## Every Phase II run: three checks at once

NGAME runs **three parallel readers** on the same QuickBooks data. **Read all three** once Multi-Day shows **active** (not “Building”).

| Dashboard section | Plain question | Time window |
|-------------------|----------------|-------------|
| **Top Anomalies** | Is **today's** activity unusual vs our 30-day training? | **Today only** |
| **Multi-Day Pattern Alert** | Was churn **sustained** over the last several fraud-check days? | **~5 days** (slow-burn) |
| **Credit Card Watch** | Any **card transactions today** that look risky? | **Today only** |

**Overall Risk** and **Management Warnings** come mainly from **today's** top categories (not from Multi-Day today).

> **Important:** Multi-Day can show **HIGH** while Top Anomalies looks quiet — that is normal for gradual schemes. Do **not** skip Multi-Day when today looks fine.

---

## Top Anomalies — how to read a row

Each row is a **category** of QuickBooks records (Invoices, Vendors, Bills, …), not one invoice or one person.

| On screen | Meaning |
|-----------|---------|
| **Transaction type** (e.g. Vendors) | Which bucket of records moved differently than usual |
| **Δ** and **%** | How far today's pattern is from the trained “normal” for that category |
| **HIGH / MEDIUM / LOW** | How unusual vs the 30-day baseline (stronger = review sooner) |

**Plain language:**

- **Many new or removed records** in a category → often shows here (CPI / “attendance” of record IDs).
- **Editing an existing invoice amount** → may **not** appear here; use QuickBooks **Audit Log** (see below).

NGAME does **not** prove fraud. A flag means **“far from what we learned in Phase I”** — may have an innocent explanation.

---

## Multi-Day Pattern Alert (slow-burn)

| Badge | Meaning |
|-------|---------|
| **Building** | Not enough Phase II daily runs yet — keep running fraud checks |
| **Clear** | Last ~5 days look normal in aggregate |
| **MEDIUM / HIGH** | Sustained unusual churn in one or more categories |

This is **not** “yesterday vs today only.” It smooths several days so a little change each day can add up to an alert.

**Does not replace Top Anomalies** — both can fire on the same run.

---

## Credit Card Watch

Flags **today's** company card activity (unusual vendor, amount, timing, etc.). Independent of churn rows above.

---

## Management Warnings & Overall Risk

| Level | What you do |
|-------|-------------|
| **LOW** or no warnings | Done for today (still skim Multi-Day and CC Watch) |
| **MEDIUM** | Note warnings + Top Anomalies; contact **designated contact** within one business day; check **Audit Log** |
| **HIGH** | Screenshot now; contact designated contact **today**; Audit Log **before** other action |

Details: [FRP_OPERATIONS_GUIDE.md](../../FRP_OPERATIONS_GUIDE.md) § Warning response protocol.

---

## What NGAME does not show on the dashboard

| Gap | What you do |
|-----|-------------|
| **Who** changed a record | QuickBooks **Audit Log** (in QBO browser, not in NGAME) |
| **Line edits** on same invoice ID | Audit Log; optional deep report from technical contact |
| **Slow-burn in Overall Risk** | Read **Multi-Day Pattern Alert** even when risk is LOW |

NGAME is **read-only** — it never changes QuickBooks.

---

## Daily Phase II checklist (after bookkeeper posts)

1. Open dashboard bookmark → **Run Today's Fraud Check** → wait until **finished**.
2. **Overall Risk** + **Management Warnings** — follow table above if MEDIUM/HIGH.
3. **Top Anomalies** — note categories flagged.
4. **Multi-Day Pattern Alert** — note if not Clear (once active).
5. **Credit Card Watch** — note any flags.
6. If anything needs follow-up → **Audit Log** for that date.
7. Close browser.

---

## When to call your NGAME technical contact

- Dashboard will not load or run errors (❌ in live output)
- QuickBooks login prompt during a run
- Ollama problems (Phase II)
- You need help interpreting a flag before contacting leadership

---

## Related documents

| Document | Path |
|----------|------|
| This guide (Markdown) | `Training, Marketing, and Documentation/NGAME_FRP_PhaseII_Dashboard_Guide.md` |
| Printable (HTML) | `Training, Marketing, and Documentation/NGAME_FRP_PhaseII_Dashboard_Guide.html` |
| FRP full operations | `FRP_OPERATIONS_GUIDE.md` / `.html` |
| Overnight churn example | `NGAME_Churn_Walkthrough.md` |

---

*NGAME · FRP Phase II dashboard · May 2026*
