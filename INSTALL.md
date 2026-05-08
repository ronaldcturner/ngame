# NGAME — Installation Guide

> **Who should perform this installation?**
> Installation is intended for a **systems administrator or technical consultant** who is comfortable installing Python, running Terminal / PowerShell commands, and handling API credentials securely. End-user operation of the NGAME dashboard requires no technical expertise after installation is complete.

---

## Contents

- [Prerequisites — both platforms](#prerequisites)
- [macOS installation (12 Monterey or later)](#macos)
- [Windows installation (Windows 10 / 11)](#windows)
- [Credentials and configuration](#credentials)
- [Running NGAME](#running-ngame)
- [Daily automation](#daily-automation)
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

## Running NGAME

> **macOS:** use `python3`. **Windows:** use `python`.

### Training Mode — first 30 days

Build the behavioral baseline from your accounting data. Run once per day for at least 30 days before switching to Fraud Analysis Mode.

```bash
python3 run_training_flow.py      # macOS
python  run_training_flow.py      # Windows
```

### Fraud Analysis Mode — once baseline is established

Compare today's data against the baseline and generate management warnings.

```bash
python3 run_fraud_analysis.py     # macOS
python  run_fraud_analysis.py     # Windows
```

### Auto Mode — recommended for daily operation

Automatically selects Training or Fraud Analysis mode based on the state of the training matrix.

```bash
python3 ngame_dual_mode.py        # macOS
python  ngame_dual_mode.py        # Windows
```

### Web Dashboard

Displays risk summary, management warnings, and top anomalies in a browser-based interface.

```bash
# macOS
cd ngame_ui
python3 app-simple.py

# Windows
cd ngame_ui
python app-simple.py
```

Open your browser and go to: **http://localhost:5001/dashboard**

> The dashboard reads JSON output files generated by the analysis pipeline. Run at least one analysis command first to populate it.

---

## Daily Automation

### macOS — cron

To run NGAME automatically each morning at 7 am, add a cron entry:

```bash
crontab -e
```

Add this line (adjust the paths to your actual install location):

```
0 7 * * * /path/to/ngame/.venv/bin/python3 /path/to/ngame/ngame_dual_mode.py >> /path/to/ngame/logs/ngame_daily.log 2>&1
```

### Windows — Task Scheduler

1. Open **Task Scheduler** (search in Start menu).
2. Click **Create Basic Task**.
3. Set the trigger to **Daily** at your preferred time.
4. Action: **Start a Program**.
5. Program: `C:\Users\YourName\Documents\ngame\.venv\Scripts\python.exe`
6. Arguments: `C:\Users\YourName\Documents\ngame\ngame_dual_mode.py`
7. Adjust paths to match your actual install location.

---

## Troubleshooting

| Symptom | Resolution |
|---|---|
| `python3: command not found` (Mac) | Python is not installed or not on PATH. Re-install from python.org and ensure the installer adds it to PATH. |
| `python: command not found` (Windows) | Python was installed without "Add to PATH". Re-run the installer and check that option, or add Python manually to your system PATH. |
| `pip install` fails with compiler error (Windows) | Install Microsoft C++ Build Tools from visualstudio.microsoft.com/visual-cpp-build-tools/ and retry. |
| Virtual environment activation blocked (Windows) | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell, then retry. |
| Dashboard shows no data | Run `python3 run_fraud_analysis.py` (or `run_training_flow.py`) at least once to generate the JSON output files. |
| Ollama not responding | Ensure `ollama serve` is running (Mac) or that the Ollama service is active in Task Manager (Windows). Without Ollama, fraud analysis mode will run but produce no LLM reasoning — management warnings will be empty or minimal. |
| QuickBooks / Wave authentication error | Verify that `quickbooks_config.json` or `wave_config.json` contains valid, non-expired credentials. Re-generate tokens at the respective developer portal if needed. |

For additional UI troubleshooting, see `ngame_ui/TROUBLESHOOTING.md`.

---

*NGAME · Apache 2.0 · Copyright 2026 Ron Turner*
