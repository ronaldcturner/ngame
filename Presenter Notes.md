# NGAME End-to-End — Presenter's Script
### One-Hour Live Demonstration for Accounting Students (No Technical Background)

---

## Pre-Presentation Checklist
*Complete the night before — none of this is done live*

- [ ] Terminal open, font size set to 18pt or larger (audience must read the screen)
- [ ] Working directory set: `cd ~/Developer/Projects/NGAME-POC`
- [ ] QuickBooks sandbox account connected and tested (`python3 run_data_extraction.py` runs clean)
- [ ] **TIME WARP ASSET**: A pre-built 30-day training matrix (`NGAME_Training_Matrix.xlsx`) already exists in the project folder. This was built by running `run_training_flow.py` on 30 consecutive days. Do NOT delete it.
- [ ] **ANOMALY ASSET**: No night-before injection step needed. The fraud analysis for Segment 5 is run using `python3 run_demo_scenario.py`, which reads μ and σ directly from the training matrix and injects mathematically controlled spikes for Vendors (z≈5.0), ChartOfAccounts (z≈4.0), and Contractors (z≈3.5) — guaranteeing exactly those three types surface as HIGH anomalies, regardless of live QuickBooks data.
- [ ] Have `NGAME_Training_Matrix.xlsx` open in Excel, ready to switch to
- [ ] Have the project folder open in Finder, ready to show files appearing
- [ ] Slide or whiteboard showing the 17 transaction types (optional but useful)
- [ ] **LIVE DASHBOARD**: Open a *second* terminal tab/window. Run the following two commands in sequence:
  ```
  cd ~/Developer/Projects/NGAME-POC/ngame_ui
  python3 app-simple.py
  ```
  Confirm the output says `Running on http://0.0.0.0:5001`. Leave this terminal running — do not close it at any point during the presentation.
- [ ] Open a browser and navigate to `http://localhost:5001/dashboard`. The page should load with NGAME branding and empty/unknown data panels — that is expected and correct; the data will not appear until `run_demo_scenario.py` runs. Minimize the browser; you will switch to it at the climax of Segment 5.
- [ ] Make sure you have **three** things ready to switch between: (1) main terminal, (2) Excel, (3) browser at `http://localhost:5001/dashboard`.

---

## Timing Overview

| Segment | Time | Content |
|---|---|---|
| Opening | 0:00–0:08 | What NGAME is and the problem it solves |
| Setup | 0:08–0:15 | Show configuration and connection |
| Phase I Live | 0:15–0:28 | Run Day 1 and Day 2 training live |
| Time Warp | 0:28–0:35 | Skip to 30-day matrix; examine it |
| Phase II Live | 0:35–0:52 | Run fraud analysis; watch detection |
| Artifacts | 0:52–0:58 | Open and explain all output files |
| Close + Q&A | 0:58–1:00 | Summary and questions |

---

---

## SEGMENT 1 — Opening
### *0:00–0:08 · 8 minutes · No typing yet*

---

**[SAY]**

> "What I'm going to show you today is a system called NGAME. Before I touch the keyboard, I want to give you just two minutes of context — because everything you're about to see will make much more sense if you understand the problem it's solving.

> Every organization — every business, every non-profit, every government agency — has financial records kept in an accounting system. For most small organizations, that's QuickBooks. Those records are updated daily: invoices come in, bills get paid, payroll runs, vendors get added.

> Now here's the audit problem. The traditional way to detect fraud is to write rules. 'If a bill is paid twice, flag it.' 'If an employee is added outside of normal hours, flag it.' Rules work — but a sophisticated fraudster knows the rules and works around them.

> NGAME takes a completely different approach. Instead of rules, it asks one question every single day: **does today's financial activity look like this organization's normal behavior?**

> To answer that question, NGAME first needs to learn what normal looks like. That's Phase I — Training. NGAME watches the organization's books every day for 30 business days and builds a mathematical picture of normal activity across 17 categories of financial transactions.

> After training, NGAME runs every day in Phase II — Fraud Analysis. It compares today's activity against the trained baseline. If something is statistically unusual — not just a little unusual, but 'this would happen by chance less than 0.3% of the time' unusual — NGAME generates a management warning.

> The warning does not say someone committed fraud. It says: 'something in this category of transactions looks different from what we've seen in the past 30 days. An auditor should look at it.'

> That's the system. Let me show you how it works."

---

**[SAY]**

> "I'm going to work in a terminal window — the black screen with text. I'll narrate every step. Nothing I type is complicated. In fact, there are just four commands in this entire demonstration — and two of those are the same command run twice."

---

## SEGMENT 2 — Setup
### *0:08–0:15 · 7 minutes*

---

**[DO]** Switch to the terminal. Show the working directory.

**[SAY]**

> "This is the NGAME project folder on my computer. Everything NGAME needs lives here — the code, the configuration, and all the output files it generates.

> The first thing NGAME needs to know is: *whose QuickBooks account should I connect to?* That information lives in a configuration file — think of it as a key that unlocks the accounting system. The configuration holds the organization's QuickBooks credentials. Critically, NGAME is connected with *read-only* access — it can look at the books, but it cannot change anything. That's an important safeguard."

---

**[DO]** In the terminal, type:

```
python3 run_data_extraction.py
```

**[SAY while it runs]**

> "This command tests the connection to QuickBooks and pulls today's data. Watch for the green checkmarks — those are NGAME's way of reporting that each step succeeded."

**[POINT TO]** Each ✅ line as it appears.

**[SAY when it finishes]**

> "Every ✅ means that step worked. If we saw a ❌, that would mean something needs attention — wrong credentials, expired authorization, network problem. The system tells you exactly what it is.

> What just happened behind the scenes: NGAME connected to QuickBooks, pulled all transactions across the 17 categories, and built two files: a snapshot of today's financial activity, and it preserved yesterday's snapshot. We'll look at those files in a moment.

> Now — I want to show you something before we train."

---

**[DO]** Switch to the browser. It should already be open at `http://localhost:5001/dashboard`.

**[POINT TO]** The dashboard — specifically the empty Risk Level badge and the blank anomalies/warnings panels.

**[SAY]**

> "NGAME also ships a management dashboard — a web interface designed for people who never work in a terminal. Right now the data panels are empty, because we haven't run fraud analysis yet. The dashboard reads directly from NGAME's output files. Watch what happens to this screen after we run the full pipeline — I'll bring it back up at the end.

> For now — let's train."

---

**[DO]** Switch back to the terminal.

## SEGMENT 3 — Phase I Training (Live)
### *0:15–0:28 · 13 minutes*

---

**[SAY]**

> "Phase I is the training period. NGAME runs once per business day for 30 days. Each run takes the data it just pulled from QuickBooks and adds one day's worth of information to the training matrix — the spreadsheet where it builds up its picture of normal behavior.

> I'm going to run it right now for Day 1."

---

**[DO]** Before running, ensure a clean slate for the live demo. This single command backs up the pre-built 30-day matrix automatically:

```
python3 run_training_flow.py --demo
```

**[EXPECTED OUTPUT]**

```
✅ 30-day matrix backed up → NGAME_Training_Matrix_SAVED.xlsx
   Fresh slate — Day 1 values will be replayed from saved matrix.
```

*(If it says "No existing matrix found — proceeding straight to Day 1" that is also fine.)*

**[SAY]** *(do not narrate the --demo flag — describe it simply as:)*

> "I'm starting the training system."

---

**[DO]** Type:

```
python3 run_training_flow.py
```

**[SAY while the environment check runs]**

> "It always starts by checking that the software environment is healthy. Again, green checkmarks."

**[POINT TO]** The status display:

```
📊 Current Training Status:
   Matrix exists    : False
   Days recorded    : 0 of 30
```

**[SAY]**

> "It's telling us: no training matrix exists yet, and we're at Day 0 of 30. This is the very first run."

**[POINT TO]** The prompt:

```
❓ Add Day 1 of 30 to the training matrix? (y/n):
```

**[SAY]**

> "NGAME always asks for confirmation before doing anything. This is intentional — the person running it stays in control."

**[DO]** Type `y` and press Enter.

**[SAY while it runs]**

> "It's recording the first day of transaction measurements across all 17 categories in the training matrix."

**[POINT TO when finished]**

```
✅ Day 1 recorded — 29 day(s) remaining.
```

**[SAY]**

> "Day 1 done. The training matrix now exists with one day of data. Let me show you something — watch the project folder."

**[DO]** Type `n` at the "Add Day 2?" prompt to pause the script. Switch to Finder. Show `NGAME_Training_Matrix.xlsx` has just appeared.

**[SAY]**

> "That file didn't exist before I ran that command. NGAME created it. Let me run Day 2 so you can see the matrix growing."

---

**[DO]** Type again:

```
python3 run_training_flow.py
```

**[POINT TO]** The updated status:

```
📊 Current Training Status:
   Matrix exists    : True
   Days recorded    : 1 of 30
```

**[SAY]**

> "Now it knows the matrix exists and we have one day recorded. Asking for Day 2."

**[DO]** Type `y`.

**[SAY while it runs]**

> "Same process — record the second day of measurements and add a new column to the matrix."

**[POINT TO when finished]**

```
✅ Day 2 recorded successfully.
   28 day(s) remaining.
```

**[SAY]**

> "Day 2 is in. This is the full daily procedure — open the terminal, type one command, press y, done. Takes about two to three minutes. A bookkeeper or office manager can do this with no technical knowledge whatsoever.

> Now I need to do something that I'm going to be completely transparent about — because it's important you understand the time requirement."

---

**[DO]** Restore the pre-built 30-day matrix for the Time Warp segment. One command — no file renaming needed:

```
python3 run_training_flow.py --restore
```

**[EXPECTED OUTPUT]**

```
🗑️  Removed 2-day demo matrix.
✅ 30-day training matrix restored → NGAME_Training_Matrix.xlsx
   Pipeline is ready for fraud analysis.
```

**[SAY]** *(do not narrate this command — if the audience asks, say: "I'm switching to the full 30-day baseline we prepared in advance.")*

---

## SEGMENT 4 — The Time Warp
### *0:28–0:35 · 7 minutes*

---

**[SAY]**

> "In a real deployment, what I just showed you happens 28 more times — once per business day for the next six calendar weeks. NGAME is a patient system. It needs 30 days of real activity to build a statistically reliable picture of what 'normal' looks like. You cannot shortcut this.

> For the purposes of this demonstration, I prepared ahead of time. I have a 30-day training matrix that was already built. I'm going to open it now."

---

**[DO]** Switch to Excel. Open `NGAME_Training_Matrix.xlsx`.

**[SAY]**

> "This is what the training matrix looks like after 30 days. Let me walk you through what you're seeing.

> Column A is the list of 17 transaction types NGAME monitors — Customers, Invoices, Bill Payments, Expenses, Payroll, and so on.

> Column B is labeled μ — that's the Greek letter for 'mean,' or average. For each transaction type, this is the average stability score observed across all 30 training days. The score ranges from 0 to 1. A score near 1 means that transaction type is very stable day to day — most of the same records carry over. A score near 0 means it's highly volatile — records come and go constantly.

> Column C is labeled σ — standard deviation. This tells NGAME how much Column B *normally varies*. This is the key to principled fraud detection.

> Let me give you an audit analogy. Suppose Payroll has an average stability score of 0.85, with a standard deviation of 0.02. That means normal Payroll looks nearly identical every day, and it almost never varies by more than a couple of percent. If NGAME sees Payroll drop to 0.60 one day, that's not just below average — it's *far below anything we've ever seen*. That triggers a HIGH warning.

> Now compare that to Expenses, which might have an average of 0.45 with a standard deviation of 0.15. Expenses are naturally volatile — they fluctuate a lot day to day. A score of 0.60 for Expenses is actually above average. Without that standard deviation, NGAME couldn't tell the difference between routine fluctuation and a genuine anomaly.

> Columns D onward are the raw daily scores — one column per training day. You can see the history."

**[DO]** Scroll right slowly to show the daily columns.

**[SAY]**

> "This is the baseline. Thirty days of the organization's normal financial behavior, captured in 17 numbers. Now I'm going to use it."

---

## SEGMENT 5 — Phase II Fraud Analysis (Live)
### *0:35–0:52 · 17 minutes*

---

**[SAY]**

> "Phase II is what happens every day *after* training is complete. This is the daily fraud check.

> Before I run it, I need to tell you about something I prepared in advance — the scenario.

> I staged a controlled fraud scenario targeting three transaction categories that ACFE research consistently identifies as the most prevalent vehicles for occupational fraud and asset misappropriation.

> The primary target is Vendors — φ18 in NGAME's framework. The ACFE Report to the Nations identifies fictitious vendor schemes, shell company billing, and vendor master file manipulation as the single most common category of asset misappropriation in small and mid-size organizations. We staged a sudden surge of new, unrecognized vendor activity — the signature that appears when someone is creating fictitious vendors to route payments to themselves or a related party.

> The second target is Chart of Accounts — φ16. When someone commits a vendor scheme, they typically need to manipulate the chart of accounts to conceal where the cash is going — adding new accounts, restructuring existing ones, or reclassifying expense categories. NGAME watches for exactly this pattern.

> The third target is Contractors — φ14. Payments to fictitious or related-party contractors — inflated 1099 invoicing, shell contractor entities — is the second most common asset misappropriation scheme in organizations without a dedicated internal audit function.

> NGAME is about to analyze today's data against its 30-day baseline. Let's see what it finds."

---

**[DO]** Type:

```
python3 run_demo_scenario.py
```

**[SAY as the spikes print]**

> "You can see it reading the 30-day baseline and injecting exactly the scenario we staged. Watch the three lines that start with the syringe symbol — those are the three anomalies going in."

**[POINT TO]** The three spike lines:

```
💉 Spike injected → φ18 Vendors: …  z≈5.0
💉 Spike injected → φ16 ChartOfAccounts: …  z≈4.0
💉 Spike injected → φ14 Contractors: …  z≈3.5
```

**[SAY]**

> "Each one shows how far today's value has been pushed from the 30-day average — measured in standard deviations. Then the full analysis pipeline runs automatically."

**[POINT TO as each step runs]**

> "Step 1: Churn comparison — computing today's deviation from the 30-day baseline for all 18 transaction types."

> "Step 2: Ranking — ordering all 18 by how anomalous they are."

> "Step 3: Top-3 identification — picking the three most deviant types and labeling them. This is where NGAME surfaces the findings."

> "Step 4: Account mapping — connecting each flagged transaction type back to the specific general ledger accounts involved."

> "Step 5: LLM analysis — the AI language model is comparing the flagged accounts against the asset misappropriation taxonomy and generating a plain-language interpretation."

> "Step 6: Management warnings — converting the technical output into action items for a non-technical reader."

**[PAUSE — let the summary block print]**

**[POINT TO]** The top-3 anomaly lines:

```
🚨 #1  φ18  Vendors          z=5.00  [HIGH]
🚨 #2  φ16  ChartOfAccounts  z=4.00  [HIGH]
🚨 #3  φ14  Contractors      z=3.50  [HIGH]
```

**[SAY]**

> "There it is. All three flagged. All three HIGH. Let me read what NGAME found.

> Vendors — a z-score of 5.0. In 30 days of training, Vendor activity never moved more than a fraction of a standard deviation from its normal range. Today it moved five standard deviations. Something changed dramatically in the vendor master file. NGAME is saying: look at what was added to Vendors today.

> Chart of Accounts — 4.0 standard deviations. Accounts were created or restructured in a pattern we have never seen during training. This is the concealment layer.

> Contractors — 3.5 standard deviations. New contractor activity appeared that has no precedent in the baseline period.

> A z-score above 3 is expected by random chance less than 0.3% of the time — less than once per calendar year under normal operations. Three simultaneous HIGH z-scores is not a coincidence. This is a pattern.

> NGAME isn't accusing anyone. It is saying: an auditor needs to look at these three categories today."

---

**[POINT TO when finished]**

```
✅ Artifacts saved — refresh the Dashboard to see results.
```

**[SAY]**

> "And the run is complete. Under two minutes. The person responsible for financial oversight at this organization did nothing more than type one command. NGAME does the rest."

---

**[DO]** Switch to the browser. Press **⌘R** (Mac) or **Ctrl+R** (Windows) to refresh the dashboard page.

**[PAUSE]** for 2–3 seconds while the page reloads and pulls the new results.

**[POINT TO]** The Overall Risk Level badge at the top of the dashboard as it changes from "UNKNOWN" to "HIGH" (or whatever severity NGAME assigned).

**[SAY]**

> "Watch the dashboard. This is what I showed you at the beginning — empty panels. Now refresh."

**[POINT TO]** Each panel as it populates:

- The **Risk Level** badge (color-coded: red = HIGH)
- The **Management Warnings** list — fraud indicators in plain language, no z-scores, no jargon
- The **Top Anomalies** panel — the same ranked results we just saw in the terminal, presented for a non-technical reader

**[SAY]**

> "This is the same data we just saw in the terminal — but formatted for a CFO, a board member, or an audit committee chair. No terminal required. No technical knowledge required. They open a browser, they see this page, and they know whether to call their auditor today.

> In a production deployment, this dashboard updates automatically every time NGAME runs its daily check. The organization's leadership sees the current risk status without touching a keyboard."

## SEGMENT 6 — Artifacts Walkthrough
### *0:52–0:58 · 6 minutes*

---

**[DO]** Switch to Finder. Show all files in the project folder. Point out each artifact as you open it.

---

**[OPEN]** `quickbooks_ontology_Today.ttl`

**[SAY]**

> "This is the daily snapshot NGAME builds from QuickBooks data. It's a structured representation of every transaction category — the raw material NGAME analyzes. You'll never need to read this file. NGAME generates it automatically and uses it as input for the comparison."

---

**[OPEN]** `NGAME_Training_Matrix.xlsx`

**[SAY]**

> "You've already seen this. The 30-day baseline. This is the memory of normal operations. It doesn't change during fraud analysis — it only grows during training."

---

**[OPEN]** `NGAME_Fraud_Analysis_readable_clean.json` in a text editor

**[SAY]**

> "This is the full fraud analysis output — every number NGAME computed, every comparison it made, every anomaly it ranked. This is the working document for a forensic auditor who wants to trace NGAME's logic step by step.

> [Point to the top_anomalies section]

> Here are the top three anomalies, in rank order. For each one you can see: the transaction type, the z-score, the severity, the addition rate — how many new transactions appeared — and the deletion rate — how many disappeared. That directional information matters for an auditor. Different fraud schemes leave different directional signatures."

---

**[OPEN]** `management_dashboard.json`

**[SAY]**

> "And this is the source file behind the dashboard you just saw update. Plain language. Designed to be read by someone who doesn't know what a z-score is. This is what goes to the board of a non-profit, or to a CFO, or to an audit committee. It says what was flagged, how serious it is, and what the recommended next step is.

> The web dashboard you saw a moment ago reads this file every time you refresh the page. In a production deployment, a scheduled job runs NGAME every evening at close of business, writes this file, and the dashboard is ready for leadership the next morning — with no one having to interpret a spreadsheet or a terminal window."

---

## SEGMENT 7 — Close and Q&A
### *0:58–1:00 · 2 minutes*

---

**[SAY]**

> "Let me summarize what you just watched.

> We connected NGAME to a QuickBooks account. We watched it learn — one day at a time — what normal financial activity looks like for this organization. We watched it detect a simulated fraud scenario — anomalous activity across Vendors, Chart of Accounts, and Contractors, all three flagged as HIGH severity — in under two minutes, with one command. And we watched a management dashboard update in real time with findings that require no technical knowledge to read.

> The person who runs this system every day needs no technical knowledge. No accounting expertise. They type one command. NGAME does the rest — and the results land on a dashboard that the organization's leadership can act on without ever opening a terminal.

> The value is not in replacing the auditor. The value is in giving the auditor a daily early-warning system that watches every transaction category, every day, against a statistically rigorous baseline — something no human auditor can do manually at this scale and frequency.

> Questions?"

---

---

## Presenter Recovery Guide
*What to say if something goes wrong live*

| Problem | What to say | What to do |
|---|---|---|
| ❌ during extraction | "This is what a configuration error looks like — NGAME tells you exactly what failed and stops. In a real deployment, this means call the technical contact." | Show the error message; explain it; move on to the pre-built assets |
| Training run takes too long | "While this finishes, let me show you the 30-day matrix we prepared." | Switch to Excel immediately; return to terminal when done |
| Day 1 prompt doesn't appear (says "Training complete") | "Let me restore the demo state." | Run `python3 run_training_flow.py --demo` — this automatically backs up the complete matrix and starts fresh. |
| `run_demo_scenario.py` errors or shows no HIGH anomaly | "Let me re-run the scenario." | Re-run `python3 run_demo_scenario.py` — it is fully deterministic and does not depend on live data. If it still fails, open a saved `NGAME_Fraud_Analysis_readable_clean.json` from a prior run. |
| Dashboard still shows "UNKNOWN" after refresh | "The dashboard is reading the output files — let me give it a moment." | Wait 5 seconds and refresh again. If still blank, check that `app-simple.py` is still running in its terminal (it may have crashed — restart it with `cd ngame_ui && python3 app-simple.py`, then refresh the browser). |
| Dashboard server not running (`localhost:5001` refuses connection) | No narration needed — audience won't know about it unless you switch to the browser | Restart: open a new terminal tab, `cd ~/Developer/Projects/NGAME-POC/ngame_ui && python3 app-simple.py`, wait for "Running on…", refresh browser. |
| Audience asks "how do we know it's right?" | "Great question — NGAME's detection threshold is 3 standard deviations. In the absence of fraud, that threshold is expected to trigger by random chance less than 0.3% of the time — about once every 333 days. False positives are rare. False negatives are a risk, which is why dollar-weighted analysis is the next development priority." | No action needed |
| Audience asks "can it be fooled?" | "Yes — any detection system can be evaded by a sufficiently sophisticated and patient adversary. NGAME is designed to catch the statistically detectable patterns that characterize most common fraud schemes. It is one layer of a defense-in-depth audit strategy, not the only layer." | No action needed |

---

## Command Reference
*Everything you type during the demo — in order*

```
# NIGHT BEFORE — nothing needed for anomaly injection; scenario is built into run_demo_scenario.py

# IF RESETTING AFTER A TEST RUN (clears demo matrix; keeps saved 30-day matrix intact):
python3 run_training_flow.py --reset        ← run this anytime you need to start the demo over from Day 1

# DEMO DAY — Terminal 1 (main, working dir: ~/Developer/Projects/NGAME-POC)
python3 run_data_extraction.py              ← test QB connection; then briefly show browser

python3 run_training_flow.py --demo         ← backs up pre-built matrix; type y → Day 1 runs
                                            ← type n to pause (show Finder: matrix appeared)
python3 run_training_flow.py                ← type y for Day 2

python3 run_training_flow.py --restore      ← restores 30-day matrix; then switch to Excel

[TIME WARP — show 30-day matrix in Excel]

python3 run_demo_scenario.py                ← no prompt; runs instantly; Vendors · ChartOfAccounts · Contractors flagged HIGH
                                            ← when finished: switch to browser, press ⌘R

# DEMO DAY — Terminal 2 (background server; start BEFORE the demo, leave running)
cd ~/Developer/Projects/NGAME-POC/ngame_ui
python3 app-simple.py                       ← leave running; serves http://localhost:5001/dashboard
```

Five spoken pipeline commands. Two `y` confirmations. One `n` to pause. One background server process.

---

*Presenter Notes prepared for NGAME End-to-End Demonstration.*
*For setup questions contact your NGAME technical contact before the session.*

---

---

## Day of Demonstration — Cheatsheet
*Run top-to-bottom. Working directory for all Terminal 1 commands: `~/Developer/Projects/NGAME-POC`*

---

### AT A GLANCE — Segment 3 Training Commands

| Step | What you type | Prompt response | What to do next |
|---|---|---|---|
| Start demo / Day 1 | `python3 run_training_flow.py --demo` | Type `y` | Day 1 runs; script asks about Day 2 |
| Pause to show matrix | *(still in same session)* | Type `n` | Switch to Finder — show `NGAME_Training_Matrix.xlsx` appeared |
| Day 2 | `python3 run_training_flow.py` | Type `y` | Day 2 runs; type `n` to exit |
| Reset after a test run | `python3 run_training_flow.py --reset` | *(no prompt)* | Clears demo matrix; saved 30-day matrix stays intact |

---

### BEFORE AUDIENCE ARRIVES

| # | Terminal | Command | Confirm |
|---|---|---|---|
| 1 | T2 | `cd ~/Developer/Projects/NGAME-POC/ngame_ui` | — |
| 2 | T2 | `python3 app-simple.py` | Output: `Running on http://0.0.0.0:5001` — **leave running** |
| 3 | Browser | Navigate to `http://localhost:5001/dashboard` | Page loads with empty/UNKNOWN panels — expected |
| 4 | Excel | Open `NGAME_Training_Matrix.xlsx` | File open, ready to switch to |
| 5 | Finder | Open `~/Developer/Projects/NGAME-POC` folder | Visible, ready to switch to |

---

### SEGMENT 2 — Connection Test

| # | Terminal | Command | Output to inspect | Where |
|---|---|---|---|---|
| 6 | T1 | `python3 run_data_extraction.py` | Green checkmarks; TTL files written | Terminal |
| — | Browser | *(briefly show empty dashboard)* | Empty panels — correct | `localhost:5001/dashboard` |

---

### SEGMENT 3 — Live Training (Day 1 & Day 2)

| # | Terminal | Command | Prompt | Output to inspect | Where |
|---|---|---|---|---|---|
| 7 | T1 | `python3 run_training_flow.py --demo` | Type `y` → Day 1 runs → type **`n`** to pause | `✅ Day 1 recorded — 29 day(s) remaining` · `Paused at Day 1` | Terminal |
| — | Finder | Show `NGAME_Training_Matrix.xlsx` just appeared | — | Finder window |
| 8 | T1 | `python3 run_training_flow.py` | Type `y` | `✅ Day 2 recorded — 28 day(s) remaining` | Terminal |

---

### SEGMENT 4 — Time Warp

| # | Terminal | Command | Output to inspect | Where |
|---|---|---|---|---|
| 9 | T1 | `python3 run_training_flow.py --restore` | `✅ 30-day training matrix restored` | Terminal |
| — | Excel | Switch to Excel · open `NGAME_Training_Matrix.xlsx` | 18 rows · cols A (type) · B (μ) · C (σ) · D–AG (30 days) | Excel |

---

### SEGMENT 5 — Fraud Analysis (Demo Scenario)

| # | Terminal | Command | Output to inspect | Where |
|---|---|---|---|---|
| 10 | T1 | `python3 run_demo_scenario.py` | Three spike lines (φ18, φ16, φ14) · then pipeline steps 1–6 | Terminal |
| — | Terminal | *(scan summary block)* | `🚨 #1 φ18 Vendors z=5.00 [HIGH]` · `#2 φ16 ChartOfAccounts z=4.00 [HIGH]` · `#3 φ14 Contractors z=3.50 [HIGH]` · Overall risk: `HIGH` | Terminal |
| — | Browser | Press **⌘R** | Risk badge → **HIGH** (red) · Management Warnings populated · Top Anomalies panel shows 3 flagged types | `localhost:5001/dashboard` |

---

### SEGMENT 6 — Artifacts

| File | Open in | What to show |
|---|---|---|
| `quickbooks_ontology_Today.ttl` | Text editor | RDF/Turtle snapshot — generated automatically |
| `NGAME_Training_Matrix.xlsx` | Excel | 30-day baseline: μ, σ, daily columns |
| `NGAME_Fraud_Analysis_readable_clean.json` | Text editor | `top_anomalies` block · z-scores · deviation levels |
| `management_dashboard.json` | Text editor | Plain-language findings — source file for the live dashboard |
| `http://localhost:5001/dashboard` | Browser | Same data rendered for a non-technical reader |

---

### QUICK RECOVERY

| Problem | Fix |
|---|---|
| Ran too many test days; prompt shows Day 4 or higher | `python3 run_training_flow.py --reset` — clears demo matrix; then run `--demo` to start from Day 1 |
| Day 1 prompt skipped (says "Training complete") | `python3 run_training_flow.py --demo` — automatically backs up complete matrix and starts fresh |
| `run_demo_scenario.py` fails or shows no HIGH | Re-run — it is deterministic; always produces same three spikes |
| Dashboard still UNKNOWN after ⌘R | Wait 5 s · refresh again · if blank: check T2 is still running (`python3 app-simple.py`) |
| T2 crashed | `cd ~/Developer/Projects/NGAME-POC/ngame_ui && python3 app-simple.py` · then ⌘R |
