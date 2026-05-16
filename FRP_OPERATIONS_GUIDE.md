# NGAME — Financially Responsible Person (FRP) Operations Guide

**Audience:** The Financially Responsible Person (owner, board treasurer, nonprofit director) who runs NGAME daily.

**How you operate NGAME:** Entirely through the **NGAME Dashboard** in your web browser. You do not use Terminal, do not open project folders, and do not run commands.

**Who sets things up:** Your NGAME technical contact installs the software, starts the dashboard service, and gives you a browser bookmark. That work is documented in [INSTALL.md](INSTALL.md) — not in this guide.

---

## What NGAME Does (In Plain Language)

NGAME runs on your **surveillance computer** once per business day. It reads your organization's QuickBooks Online activity over the internet — the same cloud data your bookkeeper uses in a browser. NGAME **never changes** anything in QuickBooks. It only reads.

Each day, NGAME compares today's activity to a picture of what is **normal for your organization**. During the first 30 business days, it **learns** that picture (training). After that, it **checks** each new day against it and tells you if something is statistically unusual.

You are not expected to understand the math. You **are** expected to:

1. Open the NGAME Dashboard each business day and run the correct operation.
2. Review the results on screen.
3. Follow the warning procedures when NGAME flags something.
4. Inspect the QuickBooks **Audit Log** on a regular schedule (in QuickBooks Online — not in NGAME).

Your bookkeeper's computer is **not** involved. NGAME does not install on the bookkeeper's machine.

---

## Opening NGAME

Your NGAME contact will give you a **browser bookmark** (for example, labeled **NGAME Dashboard**).

1. Make sure the surveillance computer is **on** and connected to the **internet**.
2. Click your **NGAME Dashboard** bookmark.
3. The dashboard opens at a local address (your contact configures this — typically `http://localhost:5001/dashboard`).

If the page says it cannot connect, the dashboard service may not be running. **Call your NGAME technical contact** — do not try to fix it yourself.

---

## Before Each Daily Run

| Check | What to do |
|-------|------------|
| Internet | Open any website. If it loads, you are connected. |
| Ollama (AI service) | Look for the **Ollama** icon in the menu bar (top right on Mac). If it is missing, open **Ollama** from Applications and wait about 30 seconds. Ollama is required for daily fraud checks after training; your contact will confirm whether it must be running during training. |
| QuickBooks Audit Log | During the **first 30 business days**, review the Audit Log at least weekly (see [Audit Log protocol](#quickbooks-audit-log-protocol) below). Before running training on a day when the log shows anything suspicious, **call your NGAME contact first** — do not run training that day until they advise. |

---

## The Two Phases

The dashboard shows your phase at the top in **Training Progress** (Phase I) or **Daily Fraud Monitoring** (Phase II), including a progress bar during training.

| Phase | When | Dashboard control | What it does |
|-------|------|-------------------|--------------|
| **Phase I — Training** | Business days 1 through 30 | **Run Today's NGAME Check** (or **Run Training Day**) | Adds one day of data to NGAME's baseline ("normal") |
| **Phase II — Daily fraud check** | Day 31 onward, permanently | **Run Today's NGAME Check** (or **Run Churn Analysis**) | Compares today to the baseline; may produce warnings |

The primary button label changes automatically when training is complete. You can also confirm progress in the **live output** panel after each run.

**When the progress bar shows 30 of 30 days**, you are in Phase II permanently.

---

## Daily Procedure — Phase I (Training, Days 1–30)

**When:** End of the business day — after your bookkeeper has posted that day's transactions.

1. Open your **NGAME Dashboard** bookmark.
2. Scroll to the section titled **NGAME Operations**.
3. Click **Run Training Day** (green button).
4. A **live output** panel appears. Wait until it shows the run has **finished** (usually 1–3 minutes). Do not close the browser tab while it is running.
5. Read the last lines of the output:
   - **Success:** Look for a message that the day was recorded and how many days remain (for example, `Day 8 recorded successfully` / `22 day(s) remaining`).
   - **Day 30 complete:** Look for a message that all 30 training days are collected and the matrix is ready for fraud analysis. **From the next business day, switch to Phase II.**
6. Scroll up on the dashboard to review **Overall Risk**, **Management Warnings**, and **Top Anomalies** if they updated.
7. You are done for today. You may close the browser tab.

### Phase I quick reference

| Step | Action |
|------|--------|
| 1 | Open NGAME Dashboard bookmark |
| 2 | Click **Run Training Day** |
| 3 | Wait for finished message in live output |
| 4 | Confirm day count increased |
| 5 | Close browser |

---

## Daily Procedure — Phase II (Fraud Check, Day 31+)

**When:** Same time of day as during training — end of business day.

1. Open your **NGAME Dashboard** bookmark.
2. Scroll to **NGAME Operations**.
3. Click **Run Churn Analysis** (blue button).
4. Wait in the **live output** panel until the run **finishes** (usually 1–3 minutes).
5. Read the result:

| What you see | Meaning | What you do |
|--------------|---------|-------------|
| Success with **LOW** risk or no warnings | Within normal range | Done for today. Close the browser. |
| **MEDIUM** warning | Unusual activity — needs attention | Follow [MEDIUM warning](#medium-warning) below |
| **HIGH** warning | Highly unusual activity | Follow [HIGH warning](#high-warning) below |
| Error (❌ or "Exited with code" other than success) | Technical problem — **not** a fraud signal | [Technical problems](#when-something-goes-wrong) — call your NGAME contact; do not re-run |

6. Review **Management Warnings** and **Top Anomalies** on the dashboard for plain-language detail.

### Phase II quick reference

| Step | Action |
|------|--------|
| 1 | Open NGAME Dashboard bookmark |
| 2 | Click **Run Churn Analysis** |
| 3 | Wait for finished message |
| 4 | Read Overall Risk and warnings |
| 5 | Act on MEDIUM/HIGH per tables below, or close browser if normal |

---

## Reading the Dashboard

After each run, review these sections (scroll as needed):

| Section | What it tells you |
|---------|-------------------|
| **Training Progress** | Current phase, days recorded (e.g. 8 of 30), progress bar |
| **Overall Risk** | Summary level: LOW, MEDIUM, HIGH, or similar |
| **Multi-Day Pattern Alert** | **Slow-burn** detection — unusual activity sustained over several business days (not only today) |
| **Credit Card Watch** | Flags on today's credit card transactions (misuse patterns, structuring, etc.) |
| **Management Warnings** | Plain-language descriptions of what NGAME found |
| **Top Anomalies** | Which transaction categories were most unusual **today** |
| **Last Updated** | When the displayed results were generated |

The **live output** panel under **NGAME Operations** shows the log of the run you just started. Use it to confirm the run finished.

> **Multi-day vs. single-day:** **Top Anomalies** reflects today's snapshot. **Multi-Day Pattern Alert** reflects the rolling window (typically 5 business days) and can flag a scheme that builds gradually even when today alone looks normal.

---

## Warning Response Protocol

NGAME does **not** accuse anyone of fraud. A warning means:

> Today's activity in one or more categories is statistically far from what NGAME observed during your 30-day training baseline. That may have an innocent explanation. A qualified person should review it.

### MEDIUM warning

1. Note **Overall Risk**, **Management Warnings**, and **Top Anomalies** on the dashboard.
2. Take **screenshots** of the dashboard (and the live output panel if it still shows the warning).
3. Contact your **designated contact** within **one business day**:

   **Name:** _______________________________________________

   **Phone / email:** _______________________________________________

4. Inspect the QuickBooks **Audit Log** for the flagged date (see below).
5. Continue running NGAME on the next business day. Note if the same category is flagged again.

### HIGH warning

1. Screenshot the dashboard **immediately**.
2. Contact your **designated contact** **today** — do not wait until the next business day.
3. Inspect the QuickBooks **Audit Log** for that date **before** other action.
4. Do **not** tell the bookkeeper or staff who can alter flagged accounts until your designated contact advises you.

### The most important rule

NGAME is **read-only**. It cannot change, delete, or post anything in QuickBooks. Whatever it flags was already in your books.

---

## QuickBooks Audit Log Protocol

The Audit Log is **not** part of NGAME. NGAME cannot read it. You review it in **QuickBooks Online** in your browser — the same way you would check any QBO report.

### Why it matters during training

NGAME's baseline is built from your first **30 business days** of data. If someone hid misappropriation during those days and NGAME trains on it, that activity can become part of "normal." The Audit Log is your independent check that each day's books were legitimate **before** you click **Run Training Day**.

### How to open the Audit Log

1. Go to [https://qbo.intuit.com](https://qbo.intuit.com) and sign in with your **administrator** login.
2. Click the **gear** icon (Settings), upper right.
3. Under **Tools**, click **Audit Log**.
4. Use the **Date** filter to focus on the current week or a specific day.

### Inspection schedule

| When | How often | What to review |
|------|-----------|----------------|
| Days 1–30 (training) | At least **once per week** (twice is better) | Current week: deletions, voids, unusual logins, changed amounts |
| After any MEDIUM or HIGH NGAME warning | **Same day**, before other action | Entries on the date NGAME flagged |
| Day 30 (end of training) | **Once** — full sweep | All 30 training days |
| Day 31 onward (Phase II) | **Monthly** minimum | Prior month |

### Red flags — call your NGAME contact before running NGAME that day

| What you see | Why it matters |
|--------------|----------------|
| Transaction **deleted** or **voided** | NGAME may not see the original amount; the baseline can be skewed |
| Login from an **unexpected** user | Possible unauthorized access |
| Login at **odd hours** (nights, weekends, holidays) | May indicate covert changes |
| **Dollar amount changed** on an existing transaction | Common concealment pattern |
| **New vendor/payee** created and paid the same day | Possible fictitious vendor scheme |

---

## When Something Goes Wrong

Do **not** try to reinstall software, open Terminal, or delete files. Contact your **NGAME technical contact**:

**Name:** _______________________________________________

**Phone / email:** _______________________________________________

| What you see | What to do |
|--------------|------------|
| Dashboard will not load | Call technical contact — service may be stopped |
| Browser asks you to log into QuickBooks during a run | Call technical contact — authorization may need refresh |
| Run runs more than **10 minutes** without finishing | Note the time; call technical contact |
| Live output shows **error** or failed exit | Do **not** click the button again; screenshot; call technical contact |
| **Prerequisites not met** during churn analysis | Training may not be finished — you may still be in Phase I; call technical contact |
| Ollama error during churn analysis | Open Ollama from Applications; wait 30 seconds; try **one** more run. If it fails again, call technical contact |
| Overall Risk stays UNKNOWN with empty warnings after Phase II | Call technical contact — Ollama or pipeline may need attention |

---

## What You Never Do

- Use Terminal or command-line windows for NGAME
- Move, rename, or copy NGAME files or folders (backups are handled by your NGAME contact)
- Tell the bookkeeper about flagged accounts until your designated contact advises you (especially for HIGH warnings)
- Use **Demo Scenario** unless your NGAME contact authorized a demonstration
- Install NGAME on the bookkeeper's computer

---

## Monthly Reminders (Your NGAME Contact Handles Technical Tasks)

You do **not** perform these; your NGAME technical contact typically:

- Refreshes QuickBooks API credentials before they expire (~90–100 days)
- Verifies the dashboard service still starts correctly
- Backs up the training baseline file on the surveillance computer

You **do** continue monthly Audit Log review in Phase II.

---

## Quick-Reference Card

*Print and post near the surveillance computer.*

| Phase | Dashboard button | When |
|-------|------------------|------|
| **Phase I** (days 1–30) | **Run Today's NGAME Check** | End of each business day |
| **Phase II** (day 31+) | **Run Today's NGAME Check** | End of each business day |

**Open NGAME:** Use your **NGAME Dashboard** bookmark only.

| Result | Action |
|--------|--------|
| Success, LOW / normal | Done for today |
| MEDIUM | Screenshot → designated contact within 1 business day |
| HIGH | Screenshot → designated contact **today** |
| Error | Do not retry → NGAME technical contact |

**Designated contact (warnings):** _______________________________________________

**NGAME technical contact:** _______________________________________________

---

*NGAME FRP Operations Guide · Dashboard-only · Pairs with [INSTALL.md](INSTALL.md) for technical setup*

**Print / PDF:** Open [FRP_OPERATIONS_GUIDE.html](FRP_OPERATIONS_GUIDE.html) in a browser → Print → Save as PDF.
