# NGAME — Non-Technical Curriculum

---

## DOCUMENT 1: Consultant Setup Guide
### *One-time setup — for the QBO instructor/consultant*

**Your job**: Get NGAME installed, connected to the client's QuickBooks account, and confirmed working. You do not need to understand what happens inside — you only need to follow these steps in order.

---

### Before you arrive at the client

Confirm with your NGAME technical contact that the following are already done:
- [ ] NGAME software is installed on the client's computer
- [ ] Python is installed on that computer
- [ ] The client's QuickBooks credentials (Client ID, Client Secret) have been entered into the NGAME configuration file
- [ ] The QuickBooks account is set to **read-only access** for NGAME

If any of these are not done, stop and contact your technical contact. Do not proceed until they are complete.

---

### Step 1 — Open the terminal

On the client's computer:
- **Mac**: Press `Command + Space`, type `Terminal`, press Enter
- **Windows**: Press the Windows key, type `cmd`, press Enter

A black (or white) window with a blinking cursor will appear. This is normal.

---

### Step 2 — Navigate to the NGAME folder

Type exactly this and press Enter:

```
cd ~/Developer/Projects/NGAME-POC
```

*(If your technical contact gave you a different folder path, use that instead.)*

---

### Step 3 — Test the connection to QuickBooks

Type exactly this and press Enter:

```
python3 run_data_extraction.py
```

Watch the screen. You are looking for lines that say ✅. If you see ❌ anywhere, stop and contact your technical contact — do not continue.

---

### Step 4 — Run the first training day

Type exactly this and press Enter:

```
python3 run_training_flow.py
```

The screen will show the current status, then ask:

> `❓ Add Day 1 of 30 to the training matrix? (y/n):`

Type `y` and press Enter.

Wait. The screen will finish and show:

> `✅ Day 1 recorded successfully. 29 day(s) remaining. Run again tomorrow to add Day 2.`

That's it. Day 1 is done.

---

### Step 5 — Hand off to the financial responsible person

Show them Document 2 (below). Walk through it with them once. Confirm they can open the terminal and type the command themselves. Leave Document 2 printed and posted near the computer.

**Training takes 30 business days.** The financial responsible person runs Document 2 — Step A once per day for 30 days. After Day 30, they switch to Step B.

---

### What to do if something goes wrong during setup

| What you see | What to do |
|---|---|
| ❌ anywhere on screen | Stop. Do not type `y`. Contact your technical contact. |
| "Prerequisites not met" | Training is not finished yet. Normal during setup. |
| Screen asks for a web browser login | QuickBooks needs to re-authorize. Contact your technical contact. |
| Nothing happens after you press Enter | Wait 60 seconds. If still nothing, contact your technical contact. |

---

---

## DOCUMENT 2: Daily Operations Guide
### *For the financial responsible person — post this near the computer*

**There are two phases. You are in Phase A for the first 30 business days. After that you switch to Phase B and stay there permanently.**

---

## PHASE A — Building the Baseline
### *Run once per day, every business day, for 30 days*

**When to do this**: At the end of the business day, before you close QuickBooks.

**Step 1** — Open the terminal (the black window).
- Mac: `Command + Space` → type `Terminal` → Enter
- Windows: Windows key → type `cmd` → Enter

**Step 2** — Type this exactly and press Enter:
```
cd ~/Developer/Projects/NGAME-POC
```

**Step 3** — Type this exactly and press Enter:
```
python3 run_training_flow.py
```

**Step 4** — The screen will show something like:
> `Days recorded: 7 of 30`
> `❓ Add Day 8 of 30 to the training matrix? (y/n):`

Type `y` and press Enter.

**Step 5** — Wait. When you see:
> `✅ Day 8 recorded successfully. 22 day(s) remaining.`

You are done for today. Close the window.

**When you reach Day 30**, the screen will say:
> `🎉 All 30 training days collected! Matrix is ready for fraud analysis.`

**From that day forward, switch to Phase B.**

---

## PHASE B — Daily Fraud Check
### *Run once per day, every business day, permanently*

**When to do this**: At the end of the business day, before you close QuickBooks.

**Step 1** — Open the terminal. *(Same as Phase A.)*

**Step 2** — Type this exactly and press Enter:
```
cd ~/Developer/Projects/NGAME-POC
```

**Step 3** — Type this exactly and press Enter:
```
python3 run_fraud_analysis.py
```

**Step 4** — The screen will check the system, then ask:
> `❓ Do you want to run the fraud analysis? (y/n):`

Type `y` and press Enter.

**Step 5** — Wait (usually 1–3 minutes). When it finishes, look at the summary on screen.

---

### Reading the result — what it means

**If you see this** → Everything looks normal today. You are done. Close the window.
> `🎉 Fraud analysis completed successfully!`
> No anomalies above threshold — or — LOW severity only

**If you see this** → Something unusual was detected. Do not panic. Save a screenshot and contact your designated contact.
> `⚠️ MEDIUM` or `🚨 HIGH` anomaly detected

**If you see** ❌ → Something went wrong technically. Do not retry. Contact your technical contact.

---

### The most important rule

**NGAME does not accuse anyone of anything.** A warning means: "something in today's QuickBooks activity was statistically unusual compared to recent history." Your designated contact will investigate and decide what it means.

---

### Quick-reference card *(cut out and tape to the monitor)*

| Phase | Command to type | When |
|---|---|---|
| **A** (Days 1–30) | `python3 run_training_flow.py` | End of every business day |
| **B** (Day 31+) | `python3 run_fraud_analysis.py` | End of every business day |

**If anything looks wrong: do not retry. Call your technical contact.**

---

*Document prepared as part of the NGAME Training Curriculum.*
*For technical questions, contact your NGAME implementation team.*
