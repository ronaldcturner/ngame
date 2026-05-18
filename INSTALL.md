# NGAME — Installation Guide

**Audience:** Systems administrator or **technical consultant** (NGAME implementation lead) — comfortable with Python, Terminal or PowerShell, and secure handling of API credentials.

**Not for:** The **Financially Responsible Person (FRP)**. The FRP uses only the web dashboard. Give them **[FRP_OPERATIONS_GUIDE.html](FRP_OPERATIONS_GUIDE.html)** (print/PDF) or **[FRP_OPERATIONS_GUIDE.md](FRP_OPERATIONS_GUIDE.md)** — not this file.

---

## Documentation map

| Document | Who reads it | What it covers |
|----------|--------------|----------------|
| **This file (`INSTALL.md`)** | Technical consultant | Clone, Python env, credentials, Ollama, dashboard service, verification, FRP handoff |
| **[FRP_OPERATIONS_GUIDE.md](FRP_OPERATIONS_GUIDE.md)** / **[.html](FRP_OPERATIONS_GUIDE.html)** | FRP | Bookmark, daily training/fraud checks, warnings, QuickBooks Audit Log |
| **[README.md](README.md)** | Developers / consultants | Architecture, pipeline modules, CLI reference |
| **[ngame_ui/README.md](ngame_ui/README.md)** | Consultants | Dashboard URLs, API endpoints, UI troubleshooting |

Older guides (`SURVEILLANCE_COMPUTER_USERS_GUIDE.md`, `Non-Technical Training.md`) are **superseded** by the pair above for new deployments.

### Who does what

| Task | Technical consultant | FRP |
|------|---------------------|-----|
| Install Python, Git, NGAME, Ollama | Yes | No |
| Configure Wave / QuickBooks credentials | Yes | No |
| Start dashboard service and auto-start at login | Yes | No |
| Open Terminal or run `git` / `pip` daily | Yes (setup only) | **Never** |
| Run training or fraud checks | Optional (verification) | Yes — **dashboard only** |
| Review QuickBooks Audit Log | Advises on protocol | Yes — in QBO browser |
| Respond to MEDIUM/HIGH warnings | May assist designated contact | Yes — per FRP guide |

---

## Consultant checklist (end to end)

Use this order. Check off each item before handoff.

1. [ ] Install prerequisites (Python 3.10+, Git, accounting API access)
2. [ ] Clone repo and create `.venv` at **repository root**
3. [ ] `pip install -r requirements.txt`
4. [ ] Copy and fill `wave_config.json` and/or `quickbooks_config.json` (or `.env`)
5. [ ] Install Ollama and `ollama pull llama3` (required before Phase II)
6. [ ] Smoke-test CLI: `python3 run_training_flow.py` from repo root (optional if dashboard works)
7. [ ] Start dashboard; confirm **http://localhost:5001/dashboard** loads
8. [ ] Configure LaunchAgent (macOS) or Task Scheduler (Windows) so dashboard survives reboot
9. [ ] Run **one** training day from dashboard; confirm `NGAME_Training_Matrix.xlsx` appears
10. [ ] Print/PDF FRP guide; fill contact blanks; create **NGAME Dashboard** bookmark on surveillance PC
11. [ ] Supervise FRP through one **Run Training Day** (or primary green button in Phase I)
12. [ ] Hand off — FRP gets guide + bookmark only (no Terminal instructions for daily use)

---

## Where to run commands

| Location | Use for |
|----------|---------|
| **Repository root** (`ngame/` or `NGAME-POC/`) | `git`, `pip install`, `run_training_flow.py`, config files, credentials |
| **`ngame_ui/`** subfolder | `python3 app-simple.py` (dashboard server only) |

After `cd` to the repo root, activate the virtual environment **once per Terminal session**:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Your prompt shows `(.venv)` when active. Dashboard logs (`GET /api/...`) in Terminal are normal — they mean the browser is refreshing, not an error.

---

## Contents

- [Prerequisites](#prerequisites)
- [macOS installation](#macos-installation)
- [Windows installation](#windows-installation)
- [Credentials and configuration](#credentials-and-configuration)
- [Dashboard service (required for FRP)](#dashboard-service-required-for-frp)
- [Verify installation](#verify-installation)
- [Hand off to the FRP](#hand-off-to-the-frp)
- [Optional: CLI and scheduled runs](#optional-cli-and-scheduled-runs)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| Python 3.10 or later | `python3 --version` (Mac) or `python --version` (Windows) |
| Git | Clone and updates from GitHub |
| QuickBooks Online **or** Wave | Credentials configured after install (see below) |
| Ollama | **Required for Phase II (fraud analysis).** Not required for the 30-day training phase. Without Ollama, fraud runs produce little or no LLM reasoning in management warnings. |
| Surveillance computer | Dedicated machine the FRP can reach daily; stable internet |

---

## macOS installation

Tested on macOS 12 Monterey and later. All commands assume **repository root** unless noted.

### 1 — Python 3.10+

[python.org/downloads](https://python.org/downloads) or:

```bash
brew install python@3.13
python3 --version
```

### 2 — Git

```bash
xcode-select --install   # if Git not already present
git --version
```

### 3 — Clone the repository

```bash
git clone https://github.com/ronaldcturner/ngame.git
cd ngame
```

Use your fork URL if different.

### 4 — Virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Allow 2–5 minutes on first install.

### 5 — Credentials

See [Credentials and configuration](#credentials-and-configuration).

### 6 — Ollama (before Phase II)

Download from [ollama.com/download](https://ollama.com/download):

```bash
ollama serve &           # or use the Ollama app
ollama pull llama3       # ~4 GB
```

### 7 — Quick smoke test (optional)

```bash
python3 run_training_flow.py
```

No errors → core pipeline is reachable. Full verification is in [Verify installation](#verify-installation) after the dashboard is running.

---

## Windows installation

Tested on Windows 10 (1909+) and Windows 11. Use **PowerShell** unless you prefer Git Bash.

### 1 — Python 3.10+

[python.org/downloads](https://python.org/downloads) — check **Add Python to PATH** during install.

```powershell
python --version
```

### 2 — Git

[git-scm.com/download/win](https://git-scm.com/download/win) — defaults are fine.

```powershell
git --version
```

### 3 — Clone

```powershell
cd $env:USERPROFILE\Documents
git clone https://github.com/ronaldcturner/ngame.git
cd ngame
```

### 4 — Virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If activation is blocked:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

If `pip install` fails with compiler errors, install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and retry.

### 5 — Credentials

See [Credentials and configuration](#credentials-and-configuration).

### 6 — Ollama

Install from [ollama.com/download](https://ollama.com/download) (runs as a service). Then:

```powershell
ollama pull llama3
```

### 7 — Quick smoke test (optional)

```powershell
python run_training_flow.py
```

---

## Credentials and configuration

Configure **one** accounting source (or both if you are testing).

### Wave (simplest)

```bash
# macOS
cp wave_config.example.json wave_config.json

# Windows
Copy-Item wave_config.example.json wave_config.json
```

Edit `wave_config.json` — token and business ID from [developer.waveapps.com](https://developer.waveapps.com). Details: **[NGAME_WAVE_GRAPHQL_README.md](NGAME_WAVE_GRAPHQL_README.md)**.

### QuickBooks Online

```bash
cp quickbooks_config.example.json quickbooks_config.json   # macOS
Copy-Item quickbooks_config.example.json quickbooks_config.json   # Windows
```

OAuth fields from [developer.intuit.com](https://developer.intuit.com).

### Environment variables

Alternatively: copy `.env.example` to `.env` and set variables listed there.

> **Security:** `wave_config.json`, `quickbooks_config.json`, and `.env` are in `.gitignore`. Keep them only on the surveillance machine.

---

## Dashboard service (required for FRP)

The FRP never uses Terminal for daily work. They use a **browser bookmark** to the dashboard, which you install and keep running.

**Your responsibilities:**

1. Run `app-simple.py` and confirm **http://localhost:5001/dashboard**
2. Auto-start at login (LaunchAgent / Task Scheduler)
3. Create bookmark **NGAME Dashboard** on the FRP's browser
4. Retain `launch_dashboard.command` (repo root) as **consultant fallback** only — double-click on macOS if auto-start fails

### Start manually (testing)

From **repository root**, venv active:

```bash
cd ngame_ui
python3 app-simple.py          # macOS
python app-simple.py           # Windows
```

Stop with **Ctrl+C** when testing. Production should use auto-start, not a Terminal window the FRP must manage.

### macOS — auto-start at login

Create `~/Library/LaunchAgents/com.ngame.dashboard.plist`. Replace `/NGAME_ROOT` with your install path (e.g. `/Users/you/Developer/Projects/NGAME-POC`):

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

```bash
mkdir -p /NGAME_ROOT/logs
launchctl load ~/Library/LaunchAgents/com.ngame.dashboard.plist
```

Reboot or `launchctl start com.ngame.dashboard`, then open the dashboard URL.

### Windows — auto-start at login

1. Create `C:\NGAME\start-dashboard.bat` (adjust paths):

   ```bat
   @echo off
   cd /d C:\NGAME\ngame_ui
   C:\NGAME\.venv\Scripts\python.exe app-simple.py
   ```

2. **Task Scheduler** → trigger **At log on** → action = that `.bat` file.

3. Confirm **http://localhost:5001/dashboard** after sign-in.

> Do **not** schedule `ngame_dual_mode.py` on the same machine if the FRP runs from the dashboard — that can double-run the pipeline.

---

## Verify installation

Complete **before** FRP handoff.

| # | Check | How |
|---|--------|-----|
| 1 | Dashboard loads | Open **http://localhost:5001/dashboard** (empty results OK until first run) |
| 2 | Training via UI | **NGAME Operations** → **Run Training Day** (or primary green **Run Today's Training Day**) → live output shows success / day recorded |
| 3 | Matrix file | `NGAME_Training_Matrix.xlsx` exists in repo root |
| 4 | Ollama (before Day 31) | `ollama` responds; test fraud run when 30 days complete: `python3 run_fraud_analysis.py` |
| 5 | CLI fallback (optional) | `python3 run_training_flow.py` only if dashboard run failed — for debugging |

---

## Hand off to the FRP

Deliver **only** what the FRP needs:

| Deliverable | Notes |
|-------------|--------|
| **[FRP_OPERATIONS_GUIDE.html](FRP_OPERATIONS_GUIDE.html)** (print/PDF) | Fill **designated contact** and **NGAME technical contact** blanks |
| **NGAME Dashboard** bookmark | `http://localhost:5001/dashboard` |
| **One supervised run** | FRP clicks training button while you observe |
| **Tour of results** | Overall Risk, Management Warnings, Top Anomalies, Training Progress |

**Do not give the FRP:** Terminal steps, repo path, `pip`/`git` commands, or `launch_dashboard.command` unless auto-start failed and you trained them on a single double-click shortcut only.

**Two contacts (explain to FRP):**

- **Designated contact** — business/accounting lead for MEDIUM/HIGH warnings  
- **NGAME technical contact** — you (or your firm) for dashboard, credentials, and errors  

---

## Optional: CLI and scheduled runs

For **consultant, lab, or unattended** machines — not for dashboard-only FRP operation.

| Mode | Command (repo root, venv active) |
|------|----------------------------------|
| Training | `python3 run_training_flow.py` |
| Fraud analysis | `python3 run_fraud_analysis.py` |
| Auto mode | `python3 ngame_dual_mode.py` |

**macOS cron example:**

```
0 7 * * * /path/to/ngame/.venv/bin/python3 /path/to/ngame/ngame_dual_mode.py >> /path/to/ngame/logs/ngame_daily.log 2>&1
```

**Windows Task Scheduler:** program = `.venv\Scripts\python.exe`, arguments = path to `ngame_dual_mode.py`.

---

## Troubleshooting

| Symptom | Resolution |
|---------|------------|
| `python3` / `python` not found | Reinstall Python; on Windows enable **Add to PATH** |
| `pip install` compiler error (Windows) | Install Microsoft C++ Build Tools; retry |
| PowerShell blocks venv activation | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Dashboard empty | Run one training or churn day from dashboard |
| FRP cannot connect | Check LaunchAgent / Task Scheduler; read `logs/dashboard.err.log` |
| Ollama errors in Phase II | Start Ollama app/service; confirm `llama3` is pulled |
| QBO / Wave auth error | Refresh tokens in config JSON or `.env` |
| Terminal flooded with `GET /api/...` | Normal — dashboard auto-refresh; stop server with Ctrl+C when testing |

UI details: **[ngame_ui/TROUBLESHOOTING.md](ngame_ui/TROUBLESHOOTING.md)**.

---

*NGAME · Apache 2.0 · Copyright 2026 Ron Turner*
