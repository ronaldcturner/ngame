# NGAME — User's Guide for the Surveillance Computer

> **Superseded for new deployments.** Use **[INSTALL.md](INSTALL.md)** (technical consultant) and **[FRP_OPERATIONS_GUIDE.md](FRP_OPERATIONS_GUIDE.md)** (FRP, dashboard-only). This file is retained for reference only.

*For the Financially Responsible Person and the technical staff who install NGAME*

---

## Before You Read Anything Else — A Note on the Architecture

NGAME is installed on exactly **one computer**: the **surveillance computer**. The bookkeeper's computer, the QuickBooks user's computer, and any other machine in the organization play no role in NGAME's operation and require no modification.

This is possible because QuickBooks Online is a cloud service. Your bookkeeper reaches it through a web browser. NGAME reaches it through the same internet — but via Intuit's published programming interface — using a set of read-only credentials stored on the surveillance computer. The two paths are completely independent.

```
Bookkeeper's computer
  └─ browser → qbo.intuit.com (QuickBooks Online cloud)
                      ↑
Surveillance computer
  └─ NGAME → Intuit API (read-only) → same QuickBooks data
```

The bookkeeper never knows NGAME is running. They change nothing about how they use QuickBooks. NGAME watches silently, reads the same data, and reports what it finds to the person who runs the surveillance computer.

---

---

# PART I — For Technical Staff Only
### *One-Time Installation and Configuration*

---

## What You Are Setting Up

| What | Where |
|---|---|
| NGAME software | Surveillance computer |
| Python 3.10+ | Surveillance computer |
| QuickBooks credentials (read-only) | `quickbooks_config.json` on surveillance computer |
| Ollama AI service (for LLM stage) | Surveillance computer |
| NGAME web dashboard | Surveillance computer (local web server) |

**Nothing is installed on the bookkeeper's computer, the QBO user's computer, or any other machine.**

---

## Step 1 — Install Python

Download Python 3.10 or later from [python.org](https://www.python.org/downloads/) and install it on the surveillance computer. Accept all defaults. Confirm installation by opening Terminal and typing:

```
python3 --version
```

You should see `Python 3.10.x` or higher. If you see an error, stop and resolve the Python installation before continuing.

---

## Step 2 — Copy the NGAME Project to the Surveillance Computer

Place the NGAME project folder at:

```
~/Developer/Projects/NGAME-POC
```

If your technical team uses a different path, note it here and substitute it wherever you see the above path in this guide:

**Actual path on this computer:** _______________________________________________

---

## Step 3 — Create the Python Environment and Install Dependencies

Open Terminal. Type each line, pressing Enter after each:

```
cd ~/Developer/Projects/NGAME-POC
python3 -m venv .venv
source .venv/bin/activate
pip install numpy openpyxl rdflib requests flask python-dotenv
```

Wait for each command to finish before typing the next. You should see no errors in red.

---

## Step 4 — Configure QuickBooks Credentials

NGAME connects to QuickBooks Online with **read-only** credentials. These credentials live in a file called `quickbooks_config.json` in the NGAME project folder. This file must be in place before NGAME can connect.

### What you need from Intuit Developer Portal

Log into [developer.intuit.com](https://developer.intuit.com) with the credentials your team uses for this client's app:

- **Client ID** — a long string beginning with `AB`
- **Client Secret** — a long string (treat this like a password)
- **Redirect URI** — set to `http://localhost:8080/callback` in the app settings
- **Environment** — `production` for a live QuickBooks company; `sandbox` for testing

### Create the config file

In the NGAME project folder, create a file named `quickbooks_config.json` with the following structure (substitute the real values):

```json
{
  "quickbooks": {
    "client_id": "YOUR_CLIENT_ID_HERE",
    "client_secret": "YOUR_CLIENT_SECRET_HERE",
    "redirect_uri": "http://localhost:8080/callback",
    "environment": "production",
    "realm_id": "",
    "access_token": "",
    "refresh_token": ""
  }
}
```

Leave `realm_id`, `access_token`, and `refresh_token` blank. They will be filled in automatically during the OAuth step below.

**Security note**: This file contains sensitive credentials. Do not share it, email it, or copy it to any cloud storage service (Dropbox, Google Drive, iCloud, etc.).

---

## Step 5 — Authorize NGAME with QuickBooks (One-Time OAuth)

This step opens a web browser on the surveillance computer and asks you to log into QuickBooks to grant NGAME its read-only access token. You will do this exactly once. After it completes, NGAME renews its own authorization automatically and this screen never appears again.

In Terminal (with the virtual environment active):

```
cd ~/Developer/Projects/NGAME-POC
source .venv/bin/activate
python3 run_data_extraction.py
```

A browser window will open showing the Intuit login page. Log in with the QuickBooks account credentials for this organization. When prompted, click **Connect** (or **Authorize**). The browser will redirect to a local page and close or show a success message.

Return to Terminal. You should see a series of ✅ lines. When complete, `quickbooks_config.json` now contains the access and refresh tokens.

If you see any ❌ lines, stop. Do not proceed. Contact your NGAME technical lead.

---

## Step 6 — Install Ollama (AI Language Model)

NGAME uses a local AI model to generate plain-language explanations of flagged anomalies. This model runs entirely on the surveillance computer and never sends data to the internet.

1. Download Ollama from [ollama.com](https://ollama.com) and install it.
2. After installation, open Terminal and run:

```
ollama pull llama3
```

This downloads the language model (approximately 4 GB). Wait for the download to complete.

3. Confirm Ollama is running:

```
curl http://localhost:11434
```

You should see `Ollama is running`. If not, start Ollama from your Applications folder and retry.

---

## Step 7 — Verify Required Reference Files

Confirm the following files are present in the NGAME project folder:

- [ ] `Curated Transaction Types.ttl` — the transaction taxonomy (note: filename contains a typo by design — do not rename it)
- [ ] `Asset_Misappropriation.ttl` — the fraud ontology used in Phase II

If either file is missing, contact your NGAME technical lead before proceeding.

---

## Step 8 — Set Up the Web Dashboard

The NGAME dashboard is a local web page that shows the FRP the results of each daily run. Set it up once so the FRP can launch it without using Terminal.

**Test that it runs:**

```
cd ~/Developer/Projects/NGAME-POC/ngame_ui
pip install -r requirements-minimal.txt
python3 app-simple.py
```

Open a browser and go to `http://localhost:5001/dashboard`. You should see the NGAME dashboard. (It will show no data yet — that is normal.)

**Create a launch shortcut for the FRP.** The simplest method on macOS is a shell script. In the NGAME project folder, create a file called `launch_dashboard.command` with this content:

```bash
#!/bin/bash
cd "$(dirname "$0")/ngame_ui"
source ../.venv/bin/activate
python3 app-simple.py
```

Make it executable:

```
chmod +x ~/Developer/Projects/NGAME-POC/launch_dashboard.command
```

The FRP can now double-click `launch_dashboard.command` in Finder to start the dashboard, then open `http://localhost:5001/dashboard` in their browser.

---

## Step 9 — Run Day 1 of Training

With everything installed and verified, run the first training day to confirm the full pipeline is working end-to-end:

```
cd ~/Developer/Projects/NGAME-POC
source .venv/bin/activate
python3 run_training_flow.py
```

When prompted with `❓ Add Day 1 of 30 to the training matrix? (y/n):`, type `y` and press Enter.

When the run finishes, you should see:

```
✅ Day 1 recorded successfully.
   29 day(s) remaining.
   Run again tomorrow to add Day 2.
```

The file `NGAME_Training_Matrix.xlsx` will now exist in the project folder. Installation is complete.

---

## Step 10 — Hand Off to the Financially Responsible Person

Walk the FRP through Part II of this guide. Confirm they can:
- Open Terminal
- Navigate to the NGAME folder
- Run the training command and type `y`

Leave this guide — printed or bookmarked — accessible to the FRP. The FRP does not need to read Part I again.

---

---

# PART II — For the Financially Responsible Person
### *What You Do, Day by Day*

---

## What NGAME Is Doing on This Computer

NGAME runs on this computer once per business day. It connects to your organization's QuickBooks account over the internet — the same internet your bookkeeper uses — and reads the day's accounting activity. It does not change anything in QuickBooks. It never writes to QuickBooks. It only reads.

What it reads, it compares against a mathematical picture of what "normal" looks like for your organization. If today's activity looks statistically unusual — not just a little different, but far outside anything seen in the past 30 business days — NGAME generates a warning for you to act on.

**You are not expected to understand the math.** You are expected to run NGAME every business day and respond to warnings when they appear.

---

## The Two Phases

| Phase | When | What it does |
|---|---|---|
| **Phase I — Training** | First 30 business days | Builds NGAME's picture of "normal" |
| **Phase II — Daily Fraud Check** | Day 31 onward, permanently | Compares today against normal; issues warnings |

NGAME tells you which phase you are in every time you run it.

---

## Before Your First Run Each Day

Make sure:
- The computer is on and connected to the internet
- Ollama is running (open Ollama from the Applications folder if you are unsure — it runs quietly in the menu bar)

That is all. Nothing else needs to be checked.

---

---

# PHASE I — Building the Baseline
### *Once per business day, for 30 business days*

**When to do this**: At the end of the business day — after your bookkeeper has finished posting the day's transactions. If your bookkeeper updates QuickBooks in the morning, run NGAME in the afternoon.

---

### Step 1 — Open Terminal

- **Mac**: Press `Command + Space`, type `Terminal`, press Enter.

A window with a blinking cursor appears. This is normal.

---

### Step 2 — Navigate to NGAME

Type this exactly and press Enter:

```
cd ~/Developer/Projects/NGAME-POC
```

*(If your technical contact gave you a different folder path, substitute it here.)*

---

### Step 3 — Activate the Software Environment

Type this exactly and press Enter:

```
source .venv/bin/activate
```

You will see `(.venv)` appear at the left side of the line. This means NGAME's software environment is ready.

---

### Step 4 — Run the Training Step

Type this exactly and press Enter:

```
python3 run_training_flow.py
```

The screen will show a status report, something like:

```
📊 Current Training Status:
   Matrix exists    : True
   Days recorded    : 7 of 30
   Training complete: False

❓ Add Day 8 of 30 to the training matrix? (y/n):
```

---

### Step 5 — Confirm

Type `y` and press Enter.

Wait. The run takes 1–3 minutes. When it finishes, you will see:

```
✅ Day 8 recorded successfully.
   22 day(s) remaining.
   Run again tomorrow to add Day 9.
```

You are done for today. Close the Terminal window.

---

### What "Training Complete" Looks Like

On Day 30, the screen will say:

```
🎉 All 30 training days collected!
   Matrix is ready for fraud analysis.
```

**From this day forward, switch to Phase II.** You will never run the training command again.

---

### Phase I Quick Reference

```
1.  Open Terminal
2.  cd ~/Developer/Projects/NGAME-POC
3.  source .venv/bin/activate
4.  python3 run_training_flow.py
5.  Type y, press Enter
6.  Wait for ✅
7.  Close Terminal
```

---

---

# PHASE II — Daily Fraud Check
### *Once per business day, permanently, starting on Day 31*

**When to do this**: At the end of the business day — same timing as Phase I.

---

### Step 1 — Open Terminal

Same as Phase I: `Command + Space` → `Terminal` → Enter.

---

### Step 2 — Navigate to NGAME

```
cd ~/Developer/Projects/NGAME-POC
```

---

### Step 3 — Activate the Software Environment

```
source .venv/bin/activate
```

---

### Step 4 — Run the Fraud Check

```
python3 run_fraud_analysis.py
```

The screen will check the system, then ask:

```
❓ Do you want to run the fraud analysis? (y/n):
```

---

### Step 5 — Confirm

Type `y` and press Enter. Wait 1–3 minutes.

---

### Step 6 — Read the Result

When the run finishes, look at the bottom of the screen.

---

**Normal result** — nothing unusual detected:

```
🎉 Fraud analysis completed successfully!
```

The dashboard will show LOW or no anomalies. You are done. Close the Terminal window.

---

**Warning result** — something unusual was detected:

```
⚠️ MEDIUM anomaly detected
```
or
```
🚨 HIGH anomaly detected
```

See the section **What To Do When NGAME Issues a Warning**, below.

---

**Error result** — something went wrong technically:

```
❌ [error message]
```

Do **not** re-run. Do not try to fix it. Contact your technical contact immediately. Note the exact error message on the screen.

---

### Phase II Quick Reference

```
1.  Open Terminal
2.  cd ~/Developer/Projects/NGAME-POC
3.  source .venv/bin/activate
4.  python3 run_fraud_analysis.py
5.  Type y, press Enter
6.  Wait for result
7.  If ✅: close Terminal
    If ⚠️ or 🚨: see warning procedure
    If ❌: call technical contact
```

---

---

# USING THE DASHBOARD

The Dashboard is a web page on this computer that shows you the current NGAME status in a readable format. You do not need it to run NGAME — the Terminal shows you everything — but it is available if you prefer a visual summary.

---

### Starting the Dashboard

Double-click `launch_dashboard.command` in the NGAME project folder in Finder.

A Terminal window will open and stay open. Do not close it while you are using the dashboard.

Open your web browser and go to:

```
http://localhost:5001/dashboard
```

The dashboard shows:
- **Overall risk level** (LOW / MEDIUM / HIGH) from the most recent run
- **Top anomalies** — the transaction categories NGAME flagged, ranked by severity
- **Management warnings** — plain-language descriptions of what was found

---

### When to Check the Dashboard

After any Phase II run that produced a ⚠️ MEDIUM or 🚨 HIGH result, open the dashboard before calling your contact. It gives you a plain-language summary you can read aloud or share by screenshot.

---

### Closing the Dashboard

Close the browser tab. Then close the Terminal window that opened when you launched the dashboard.

---

---

# WHAT TO DO WHEN NGAME ISSUES A WARNING

NGAME does not accuse anyone of committing fraud. A warning means:

> "Today's accounting activity in one or more transaction categories is statistically far from what we observed over the past 30 business days. This may have an innocent explanation. It may not. A qualified person should look at it."

---

## MEDIUM Warning

**What it means**: Today's activity deviated significantly from the baseline. Elevated attention is warranted.

**What you do**:

1. Open the Dashboard. Note which transaction category was flagged and the severity level.
2. Take a screenshot of the Terminal output and the Dashboard.
3. Contact your **designated contact** (fill in below) within one business day:

   **Designated contact name**: _______________________________________________

   **Phone / email**: _______________________________________________

4. Continue running NGAME the next business day as normal. Note whether the same category is flagged again.

---

## HIGH Warning

**What it means**: Today's activity deviated to a degree that would occur by random chance fewer than 3 times in 1,000 days under normal conditions. This requires same-day attention.

**What you do**:

1. Open the Dashboard immediately.
2. Take a screenshot of the Terminal output and the Dashboard.
3. Contact your **designated contact** (above) **today** — do not wait until the next business day.
4. Do **not** inform the bookkeeper or any staff who have access to the flagged accounts until your designated contact advises you to.

---

## The Most Important Rule

**NGAME does not change, delete, or write anything in QuickBooks.** It is a read-only observer. Whatever it flags, it found already there. No action NGAME takes can harm or alter the accounting records.

---

---

# WHAT TO DO WHEN SOMETHING GOES WRONG TECHNICALLY

| What you see | What to do |
|---|---|
| `❌` on screen during any run | Do not re-run. Note the error message. Call technical contact. |
| Screen asks for a web browser login (QuickBooks authorization) | Call technical contact. OAuth tokens may have expired. |
| Run never finishes (waiting more than 10 minutes) | Press `Control + C` to stop it. Call technical contact. |
| Dashboard page shows "Unable to connect" | Make sure you started the dashboard with `launch_dashboard.command` first. |
| Ollama error during fraud analysis | Open Ollama from the Applications folder. Wait 30 seconds. Re-run. If still failing, call technical contact. |
| `Prerequisites not met` during fraud analysis | Training is not yet complete. Switch back to Phase I until Day 30 is reached. |

---

**Technical contact name**: _______________________________________________

**Phone / email**: _______________________________________________

---

---

# MONTHLY TASKS

Once per month, your technical contact should:

- Rotate QuickBooks API credentials (refresh the access tokens)
- Verify the NGAME software environment is intact
- Review the training matrix for missing days or gaps

You do not perform these tasks. They are the responsibility of whoever installed NGAME.

---

---

# QUICK-REFERENCE CARD
*Cut out and tape to the monitor*

---

**Every business day — end of day:**

| Phase | Command | When |
|---|---|---|
| **Phase I** (Days 1–30) | `python3 run_training_flow.py` → type `y` | Every business day until Day 30 |
| **Phase II** (Day 31+) | `python3 run_fraud_analysis.py` → type `y` | Every business day, permanently |

**Before running either command, always do this first:**

```
cd ~/Developer/Projects/NGAME-POC
source .venv/bin/activate
```

---

**Results:**

| Symbol | Meaning | What to do |
|---|---|---|
| ✅ | Success, all normal | Close Terminal. Done for today. |
| ⚠️ MEDIUM | Unusual activity detected | Screenshot → call contact within 1 business day |
| 🚨 HIGH | Highly unusual activity | Screenshot → call contact TODAY |
| ❌ | Technical error | Do not retry. Call technical contact now. |

---

**Dashboard**: Double-click `launch_dashboard.command`, then open `http://localhost:5001/dashboard`

**Technical contact**: _______________________________________________

**Designated contact (for warnings)**: _______________________________________________

---

*NGAME Surveillance Computer User's Guide*
*For technical questions, contact your NGAME implementation team.*
