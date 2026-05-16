# NGAME — Installation Guide

> **Who should perform this installation?**
> Installation is intended for a **systems administrator or technical consultant** (NGAME implementation lead) who is comfortable installing Python, running Terminal / PowerShell commands, and handling API credentials securely.

> **Who runs NGAME day to day?**
> The **Financially Responsible Person (FRP)** uses only the **web dashboard** — no Terminal, no file manipulation. Give the FRP **[FRP_OPERATIONS_GUIDE.md](FRP_OPERATIONS_GUIDE.md)** and nothing that references command-line daily runs.

### Documentation model (two documents)

| Document | Audience | Covers |
|----------|----------|--------|
| **This file (`INSTALL.md`)** | Technical consultant | Install, credentials, dashboard service, verification, handoff |
| **[FRP_OPERATIONS_GUIDE.md](FRP_OPERATIONS_GUIDE.md)** | FRP | Dashboard-only training and daily fraud checks, warnings, QBO Audit Log |

Older guides (`SURVEILLANCE_COMPUTER_USERS_GUIDE.md`, `Non-Technical Training.md`) are **superseded** by this pair for new deployments.

---

## Contents

- [Prerequisites — both platforms](#prerequisites)
- [macOS installation (12 Monterey or later)](#macos)
- [Windows installation (Windows 10 / 11)](#windows)
- [Credentials and configuration](#credentials)
- [Dashboard service (required for FRP)](#dashboard-service-required-for-frp)
- [Verify installation](#verify-installation)
- [Hand off to the FRP](#hand-off-to-the-frp)
- [Optional: CLI and scheduled runs](#optional-cli-and-scheduled-runs)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

The following are required regardless of operating system.

| Requirement | Notes |
|---|---|
| Python 3.10 or later | Check with `python3 --version` (Mac) or `python --version` (Windows) |
| Git | Used to clone the repository |
| QuickBooks Online account **or** Wave account | API credentials are configured after install |
| Ollama — **required for fraud analysis** | Provides the generative AI reasoning that identifies specific misappropriation schemes and severity. NGAME can complete the 30-day training phase without it, but fraud analysis output is not meaningful without Ollama. |

---

## macOS Installation

Tested on macOS 12 Monterey and later.

### Step 1 — Install Python 3.10+

Download the macOS installer from [python.org/downloads](https://python.org/downloads), or install via Homebrew:

```bash
brew install python@3.13
```

Verify:

```bash
python3 --version
```

### Step 2 — Install Git

Open Terminal (`Cmd+Space` → type `Terminal`) and run:

```bash
xcode-select --install
```

A system prompt will appear. Follow it to install the Xcode Command Line Tools, which includes Git. Verify:

```bash
git --version
```

### Step 3 — Clone the Repository

```bash
git clone https://github.com/<your-github-username>/ngame.git
cd ngame
```

### Step 4 — Create a Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your Terminal prompt will show `(.venv)` when the environment is active. **You must activate it every time you open a new Terminal session before running NGAME.**

### Step 5 — Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs approximately 30 packages (numpy, pandas, rdflib, scikit-learn, Flask, and others). Allow 2–5 minutes on first install.

### Step 6 — Configure Credentials

See [Credentials and Configuration](#credentials) below.

### Step 7 — Install Ollama (required for fraud analysis)

Ollama runs a local LLM that is the generative AI core of NGAME. It consults the fraud taxonomy (`Asset_Misappropriation.ttl`) to reason about which specific misappropriation schemes each anomaly resembles and how severe they are. This narrative reasoning is what makes management warnings actionable. **Without Ollama, fraud analysis mode produces no meaningful output.**

Download from [ollama.com/download](https://ollama.com/download) and run:

```bash
ollama serve &           # starts the server in the background
ollama pull llama3       # download a model (llama3 recommended; ~4 GB download)
```

> Ollama only needs to be running when NGAME is in **fraud analysis mode**. It is not required during the 30-day training phase.

### Step 8 — Verify the Installation

```bash
python3 run_training_flow.py
```

If no errors appear, the installation is complete.

---

## Windows Installation

Tested on Windows 10 (version 1909 and later) and Windows 11.

All commands below are for **Windows PowerShell**. Right-click the Start menu → **Windows PowerShell**, or search for `PowerShell`.

### Step 1 — Install Python 3.10+

Download the Windows installer from [python.org/downloads](https://python.org/downloads).

> **Important:** During installation, check the box **"Add Python to PATH"** before clicking Install. If you miss this step, Python commands will not work in PowerShell.

Verify:

```powershell
python --version
```

### Step 2 — Install Git for Windows

Download and run the installer from [git-scm.com/download/win](https://git-scm.com/download/win). Accept the defaults. This also installs Git Bash if you prefer a Unix-style terminal.

Verify:

```powershell
git --version
```

### Step 3 — Clone the Repository

```powershell
# Navigate to a convenient location, e.g. your Documents folder
cd $env:USERPROFILE\Documents
git clone https://github.com/<your-github-username>/ngame.git
cd ngame
```

### Step 4 — Create a Python Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> **Execution policy error?** If PowerShell blocks the activation script, run this one-time fix:
>
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
>
> Then re-run `.venv\Scripts\Activate.ps1`

Your prompt will show `(.venv)` when the environment is active. **You must activate it every time you open a new PowerShell window before running NGAME.**

### Step 5 — Install Python Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

Allow 3–7 minutes on first install. If any package fails with a compiler error, install **Microsoft C++ Build Tools** from [visualstudio.microsoft.com/visual-cpp-build-tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and retry.

### Step 6 — Configure Credentials

See [Credentials and Configuration](#credentials) below.

### Step 7 — Install Ollama (required for fraud analysis)

Ollama runs a local LLM that is the generative AI core of NGAME. It consults the fraud taxonomy (`Asset_Misappropriation.ttl`) to reason about which specific misappropriation schemes each anomaly resembles and how severe they are. **Without Ollama, fraud analysis mode produces no meaningful output.**

Download the Windows installer from [ollama.com/download](https://ollama.com/download). Ollama installs as a background service and starts automatically. Then pull a model (~4 GB download):

```powershell
ollama pull llama3
```

> Ollama only needs to be running when NGAME is in **fraud analysis mode**. It is not required during the 30-day training phase.

### Step 8 — Verify the Installation

```powershell
python run_training_flow.py
```

If no errors appear, the installation is complete.

---

## Credentials and Configuration

NGAME supports two accounting data sources. Configure one (or both).

### Wave (recommended — simplest setup)

1. Copy the example config:

   ```bash
   # macOS
   cp wave_config.example.json wave_config.json

   # Windows PowerShell
   Copy-Item wave_config.example.json wave_config.json
   ```

2. Open `wave_config.json` in a text editor and fill in your values:

   ```json
   {
     "wave_graphql": {
       "endpoint": "https://gql.waveapps.com/graphql/public",
       "access_token": "YOUR_WAVE_ACCESS_TOKEN",
       "business_id": "YOUR_WAVE_BUSINESS_ID"
     }
   }
   ```

   Your Wave access token and business ID are obtained from the Wave Developer Portal at [developer.waveapps.com](https://developer.waveapps.com). See `NGAME_WAVE_GRAPHQL_README.md` in this repository for detailed Wave setup steps.

### QuickBooks Online

1. Copy the example config:

   ```bash
   # macOS
   cp quickbooks_config.example.json quickbooks_config.json

   # Windows PowerShell
   Copy-Item quickbooks_config.example.json quickbooks_config.json
   ```

2. Open `quickbooks_config.json` and enter your QuickBooks OAuth credentials (Client ID, Client Secret, Company ID, Redirect URI). These are obtained from the [QuickBooks Developer Portal](https://developer.intuit.com).

### Environment variables (alternative)

All credential values can also be set as environment variables instead of JSON files. Copy `.env.example` to `.env` and fill in the values. See `.env.example` for the full list of variable names.

> **Security:** `wave_config.json`, `quickbooks_config.json`, and `.env` are listed in `.gitignore` and will **never** be committed to the repository. Store them only on the local surveillance machine.

---

## Dashboard service (required for FRP)

The FRP runs NGAME only through the dashboard (`ngame_ui/app-simple.py`). The dashboard can **launch training and fraud-analysis runs** via on-screen buttons (`/api/run-training`, `/api/run-fraud-analysis`) — the FRP never uses Terminal for daily work.

Your job as installer:

1. **Start the dashboard** and confirm it loads at **http://localhost:5001/dashboard**
2. **Keep it running** across reboots (LaunchAgent / Task Scheduler — below)
3. **Give the FRP a browser bookmark** to that URL (label it **NGAME Dashboard**)
4. **Consultant fallback:** `launch_dashboard.command` in the repo root (double-click on macOS if auto-start fails — FRP still uses the bookmark only)

### Start the dashboard manually (for testing)

> **macOS:** use `python3`. **Windows:** use `python`.

```bash
# macOS — from repository root, venv active
cd ngame_ui
python3 app-simple.py

# Windows
cd ngame_ui
python app-simple.py
```

Leave this process running while the FRP uses the browser. For production, use auto-start below instead of asking the FRP to start it.

### macOS — auto-start dashboard at login (recommended)

Create `~/Library/LaunchAgents/com.ngame.dashboard.plist` (adjust `NGAME_ROOT` to your install path):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.ngame.dashboard</string>
  <key>ProgramArguments</key>
  <array>
    <string>/NGAME_ROOT/.venv/bin/python3</string>
    <string>/NGAME_ROOT/ngame_ui/app-simple.py</string>
  </array>
  <key>WorkingDirectory</key>
  <string>/NGAME_ROOT/ngame_ui</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/NGAME_ROOT/logs/dashboard.log</string>
  <key>StandardErrorPath</key>
  <string>/NGAME_ROOT/logs/dashboard.err.log</string>
</dict>
</plist>
```

Then:

```bash
mkdir -p /NGAME_ROOT/logs
launchctl load ~/Library/LaunchAgents/com.ngame.dashboard.plist
```

Verify: reboot (or `launchctl start com.ngame.dashboard`), open **http://localhost:5001/dashboard**.

### Windows — auto-start dashboard at login (recommended)

1. Create a small batch file, e.g. `C:\NGAME\start-dashboard.bat`:

   ```bat
   @echo off
   cd /d C:\NGAME\ngame_ui
   C:\NGAME\.venv\Scripts\python.exe app-simple.py
   ```

2. **Task Scheduler** → Create Task → trigger **At log on** for the FRP user → action **Start a program** → program = the `.bat` file → run whether user is logged on or not (as appropriate for your policy).

3. Verify **http://localhost:5001/dashboard** after sign-in.

> **Do not** also schedule `ngame_dual_mode.py` on the same machine if the FRP runs manually from the dashboard — that can double-run the pipeline.

---

## Verify installation

Perform these checks **before** handing off to the FRP.

### 1. Dashboard loads

Open **http://localhost:5001/dashboard**. The page should render (results may be empty until the first run).

### 2. Day 1 training via dashboard

1. On the dashboard, scroll to **NGAME Operations**.
2. Click **Run Training Day**.
3. Confirm the **live output** panel shows success and `Day 1 recorded successfully` (or similar).
4. Confirm `NGAME_Training_Matrix.xlsx` exists in the repository root.

### 3. Optional — CLI smoke test

```bash
python3 run_training_flow.py      # macOS
python  run_training_flow.py      # Windows
```

Use CLI only for debugging if the dashboard run fails. The FRP does not need this step.

### 4. Ollama (before Phase II)

Before the FRP reaches Day 31, confirm Ollama responds and fraud analysis produces management warnings in a test run:

```bash
python3 run_fraud_analysis.py     # macOS — only after 30 training days, or for installer test
```

---

## Hand off to the FRP

1. Print or PDF **[FRP_OPERATIONS_GUIDE.html](FRP_OPERATIONS_GUIDE.html)** (or the `.md` source) — fill in designated contact and technical contact blanks.
2. Create the **NGAME Dashboard** browser bookmark on the surveillance computer.
3. Walk through **one** supervised **Run Training Day** from the dashboard (Day 2 if you already ran Day 1 during verify).
4. Show where **Overall Risk**, **Management Warnings**, and **Top Anomalies** appear after a run.
5. Explain **Audit Log** review in QuickBooks Online (in the FRP guide) — not Terminal.
6. Do **not** give the FRP Terminal instructions, project paths, or `launch_dashboard.command` unless you have no auto-start (then train them only to double-click an installer-provided shortcut — still not daily commands).

---

## Optional: CLI and scheduled runs

For **consultant / lab / unattended** use only — not for dashboard-only FRP operation.

| Mode | Command |
|------|---------|
| Training (CLI) | `python3 run_training_flow.py` |
| Fraud analysis (CLI) | `python3 run_fraud_analysis.py` |
| Auto mode (CLI) | `python3 ngame_dual_mode.py` |

### macOS — cron (unattended daily run)

```bash
crontab -e
```

```
0 7 * * * /path/to/ngame/.venv/bin/python3 /path/to/ngame/ngame_dual_mode.py >> /path/to/ngame/logs/ngame_daily.log 2>&1
```

### Windows — Task Scheduler (unattended)

Program: `C:\path\to\ngame\.venv\Scripts\python.exe`  
Arguments: `C:\path\to\ngame\ngame_dual_mode.py`

---

## Troubleshooting

| Symptom | Resolution |
|---|---|
| `python3: command not found` (Mac) | Python is not installed or not on PATH. Re-install from python.org and ensure the installer adds it to PATH. |
| `python: command not found` (Windows) | Python was installed without "Add to PATH". Re-run the installer and check that option, or add Python manually to your system PATH. |
| `pip install` fails with compiler error (Windows) | Install Microsoft C++ Build Tools from visualstudio.microsoft.com/visual-cpp-build-tools/ and retry. |
| Virtual environment activation blocked (Windows) | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell, then retry. |
| Dashboard shows no data | Run **Run Training Day** or **Run Churn Analysis** once from the dashboard, or run the CLI scripts once as installer. |
| FRP reports dashboard will not connect | Confirm LaunchAgent / Task Scheduler is running `app-simple.py`; check `logs/dashboard.err.log`. |
| Ollama not responding | Ensure `ollama serve` is running (Mac) or that the Ollama service is active in Task Manager (Windows). Without Ollama, fraud analysis mode will run but produce no LLM reasoning — management warnings will be empty or minimal. |
| QuickBooks / Wave authentication error | Verify that `quickbooks_config.json` or `wave_config.json` contains valid, non-expired credentials. Re-generate tokens at the respective developer portal if needed. |

For additional UI troubleshooting, see `ngame_ui/TROUBLESHOOTING.md`.

---

*NGAME · Apache 2.0 · Copyright 2026 Ron Turner*
