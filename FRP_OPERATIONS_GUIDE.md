# NGAME — Financially Responsible Person (FRP) Operations Guide

**You are the FRP** if you are the owner, board treasurer, or nonprofit director responsible for daily NGAME checks.

**How you use NGAME:** Only through the **NGAME Dashboard** in your web browser — one bookmark, a few buttons, no Terminal and no project folders.

**Who sets things up:** Your **NGAME technical contact** (consultant or IT) installs software, keeps the dashboard running, and gives you this guide plus a bookmark. That setup is in **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** — you do not need that document for daily work.

---

## Two people you may call

| Role | When to call |
|------|----------------|
| **Designated contact** | MEDIUM or HIGH warnings — accounting or leadership review |
| **NGAME technical contact** | Dashboard won't load, errors in live output, QuickBooks login prompts during a run, Ollama problems |

Fill in names on the [quick-reference card](#quick-reference-card) at the end before you post it by the computer.

---

## What NGAME does (plain language)

NGAME runs on your **surveillance computer** once per business day. It reads QuickBooks Online over the internet — the same cloud data your bookkeeper uses. NGAME **never changes** anything in QuickBooks; it only reads.

- **Days 1–30 (Phase I):** NGAME **learns** what is normal for your organization (training).
- **Day 31 onward (Phase II):** NGAME **compares** each new day to that baseline and may flag unusual activity.

You are not expected to understand the math. You **are** expected to:

1. Open the dashboard each business day and run the correct check.
2. Read Overall Risk and warnings on screen.
3. Follow the warning steps when needed.
4. Review the QuickBooks **Audit Log** on the schedule below (in QuickBooks Online — not inside NGAME).

NGAME does **not** install on the bookkeeper's computer.

---

## Opening the dashboard

1. Surveillance computer **on**, **internet** working.
2. Click your **NGAME Dashboard** bookmark (your technical contact creates this — usually `http://localhost:5001/dashboard`).
3. The page title is **NGAME Daily Monitoring**. You see a simple layout — one main **Dashboard** link in the menu, not consultant-only pages (Analysis, Settings, Demo Scenario, and similar).
4. If the page will not load, call your **NGAME technical contact**. Do not open Terminal or reinstall software.

---

## Which button to click

Scroll to **NGAME Operations**. Your dashboard shows **one large green button** — NGAME picks training vs. fraud automatically from your phase.

| Your phase | Banner at top | Phase badge | Button label |
|------------|---------------|-------------|--------------|
| **Phase I** (days 1–30) | **Training Progress** + progress bar | **Phase I** (green) | **Run Today's Training Day** |
| **Phase II** (day 31+) | **Daily Fraud Monitoring** + progress bar | **Phase II** (blue) | **Run Today's Fraud Check** |

Click **that one button** once per business day. You do **not** see separate Training Mode or Daily Churn boxes — those are for your technical contact’s consultant view only.

Progress text examples:

- Phase I: `Day 8 of 30 recorded — 22 business day(s) remaining in Phase I.`
- After day 30: `Training complete (30 of 30 business days). Use Daily Fraud Check each business day.` — **tomorrow** the button reads **Run Today's Fraud Check**.

---

## Before each daily run

| Check | What to do |
|-------|------------|
| Internet | Open any website; if it loads, you are connected |
| Ollama (Phase II) | **Mac:** Ollama icon in menu bar, or open **Ollama** from Applications and wait ~30 seconds. **Windows:** llama icon in the system tray, or open **Ollama** from the Start menu. Required for fraud checks after training |
| Audit Log (Phase I) | At least weekly during days 1–30 (see [Audit Log protocol](#quickbooks-audit-log-protocol)). If the log looks suspicious **today**, call your technical contact **before** running training |

---

## Daily procedure — Phase I (days 1–30)

**When:** End of business day, after the bookkeeper posted that day's transactions.

1. Open **NGAME Dashboard** bookmark.
2. Scroll to **NGAME Operations**.
3. Click the large green **Run Today's Training Day** button.
4. A **live output** panel opens. Watch until the title shows **finished** (about 1–3 minutes). Do not close the tab while it runs.
5. Confirm success in the log — e.g. `✅ Day 8 recorded successfully.` and `📅 22 day(s) remaining.` On day 30: `🎉 All 30 training days collected!`
6. When training is complete, **tomorrow** the same button reads **Run Today's Fraud Check** (Phase II).
7. Glance at **Overall Risk**, **Top Anomalies**, and (in Phase II) **Management Warnings**. Quiet training days may show no anomalies — that is normal.
8. Close the browser when done.

---

## Daily procedure — Phase II (day 31+)

**When:** Same time of day as during training.

1. Open **NGAME Dashboard** bookmark.
2. Scroll to **NGAME Operations**.
3. Click the large green **Run Today's Fraud Check** button.
4. Wait until the live output title shows **Today's NGAME Check — finished** (or similar **finished** wording).
5. Use this table:

| What you see | Meaning | What you do |
|--------------|---------|-------------|
| Success, **LOW** risk or no warnings | Within normal range | Done for today |
| **MEDIUM** warning | Unusual — needs review | [MEDIUM warning](#medium-warning) |
| **HIGH** warning | Highly unusual | [HIGH warning](#high-warning) |
| Error (❌ or failed exit code) | Technical problem — **not** fraud | [When something goes wrong](#when-something-goes-wrong) — do **not** click again |

6. Read **Management Warnings** and **Top Anomalies** for detail.

---

## Reading the dashboard

| Section | What it tells you |
|---------|-------------------|
| **Training Progress** | Phase badge (I or II), days recorded (e.g. 8 of 30), progress bar |
| **Overall Risk** | LOW, MEDIUM, HIGH, or UNKNOWN (UNKNOWN is common early in Phase I) |
| **Last Updated** | When results were last generated |
| **Multi-Day Pattern Alert** | Slow-burn patterns over a rolling window (~5 business days in Phase II). Badge **Building** until enough history exists |
| **Credit Card Watch** | Card-misuse scan — runs automatically with each Phase II fraud check |
| **Management Warnings** | Plain-language summary (Phase II; may be empty on quiet days) |
| **Top Anomalies** | Elevated categories **today** (HIGH/MEDIUM only — quiet days may show **none**) |
| **Category Activity (Today vs Yesterday)** | Record IDs added or removed overnight by transaction type |
| **Dollar-Weighted Alerts** | Large dollar amounts out of proportion with record-count churn |
| **Analysis Trends** | Chart of daily churn over training / surveillance history |
| **Recent Activity** | Short log of recent runs |

**Multi-day vs. single-day:** **Top Anomalies** and **Dollar-Weighted Alerts** are today's snapshot. **Multi-Day Pattern Alert** looks across several business days and can flag gradual schemes when today alone looks normal.

The **live output** panel under **NGAME Operations** confirms the run you just started has finished.

---

## Warning response protocol

NGAME does **not** accuse anyone of fraud. A warning means today's activity is far from the 30-day training baseline — which may have an innocent explanation. A qualified person should review it.

### MEDIUM warning

1. Note **Overall Risk**, **Management Warnings**, and **Top Anomalies**.
2. **Screenshot** the dashboard (and live output if it still shows the warning).
3. Contact your **designated contact** within **one business day**:

   **Name:** _______________________________________________

   **Phone / email:** _______________________________________________

4. Inspect the QuickBooks **Audit Log** for the flagged date.
5. Continue NGAME on the next business day; note if the same category flags again.

### HIGH warning

1. Screenshot **immediately**.
2. Contact your **designated contact** **today**.
3. Inspect the **Audit Log** for that date **before** other action.
4. Do **not** tell the bookkeeper or staff who can alter flagged accounts until your designated contact advises.

### Remember

NGAME is **read-only**. It cannot change QuickBooks. Whatever it flags is already in your books.

---

## QuickBooks Audit Log protocol

The Audit Log is **not** in NGAME. Review it in **QuickBooks Online** in your browser.

### Why it matters in training

NGAME's baseline is your first **30 business days**. If misappropriation happened during training and you train on it, that activity can become "normal." The Audit Log checks books were legitimate **before** you click **Run Today's Training Day**.

### How to open the Audit Log

1. [https://qbo.intuit.com](https://qbo.intuit.com) — administrator login.
2. **Gear** (Settings) → **Tools** → **Audit Log**.
3. Filter by **Date** for the week or day you need.

### Inspection schedule

| When | How often | What to review |
|------|-----------|----------------|
| Days 1–30 | At least **weekly** (twice is better) | Deletions, voids, odd logins, changed amounts |
| After MEDIUM or HIGH warning | **Same day** | Entries on the flagged date |
| End of day 30 | **Once** — full sweep | All 30 training days |
| Phase II (day 31+) | **Monthly** minimum | Prior month |

### Red flags — call technical contact before running NGAME that day

| What you see | Why it matters |
|--------------|----------------|
| Transaction **deleted** or **voided** | Baseline may be skewed |
| Login from **unexpected** user | Possible unauthorized access |
| Login at **odd hours** | Possible covert changes |
| **Amount changed** on existing transaction | Common concealment |
| **New vendor** created and paid same day | Possible fictitious vendor |

---

## When something goes wrong

Do **not** reinstall, use Terminal, or delete files. Call your **NGAME technical contact**:

**Name:** _______________________________________________

**Phone / email:** _______________________________________________

| What you see | What to do |
|--------------|------------|
| Dashboard will not load | Call technical contact |
| QuickBooks login prompt during a run | Call technical contact |
| Run over **10 minutes** | Note time; call technical contact |
| Live output **error** | Screenshot; do **not** retry; call technical contact |
| **Prerequisites not met** on churn run | You may still be in Phase I; call technical contact |
| Ollama error | Open Ollama; wait 30s; try **once** more; if fail, call technical contact |
| UNKNOWN risk with empty warnings in Phase II | Call technical contact |

---

## What you never do

- Use Terminal or command windows for NGAME
- Move, rename, or copy NGAME folders (backups are your technical contact's job)
- Tell the bookkeeper about flagged accounts before your designated contact says to (especially HIGH)
- Use **Demo Scenario** (not shown on your FRP dashboard — consultant/lab only)
- Install NGAME on the bookkeeper's computer

---

## Monthly reminders

**Your technical contact** typically handles: API credential refresh (~90–100 days), dashboard auto-start checks, backup of the training matrix on the surveillance machine.

**You** continue monthly Audit Log review in Phase II.

---

## Quick-reference card

*Print and post near the surveillance computer.*

| Phase | Button (one green button in NGAME Operations) | When |
|-------|--------------------------------------------------|------|
| **I** (days 1–30) | **Run Today's Training Day** | End of each business day |
| **II** (day 31+) | **Run Today's Fraud Check** | End of each business day |

**Open:** **NGAME Dashboard** bookmark only.

| Result | Action |
|--------|--------|
| Success, LOW / normal | Done |
| MEDIUM | Screenshot → designated contact within 1 business day |
| HIGH | Screenshot → designated contact **today** |
| Error | Do not retry → NGAME technical contact |

**Designated contact (warnings):** _______________________________________________

**NGAME technical contact:** _______________________________________________

---

*NGAME FRP Operations Guide · Dashboard-only · Technical setup: [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)*

**Print / PDF:** Open [FRP_OPERATIONS_GUIDE.html](FRP_OPERATIONS_GUIDE.html) in a browser → Print → Save as PDF.
