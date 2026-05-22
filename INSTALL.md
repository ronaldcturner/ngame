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

Historical guides (CLI-era FRP workflow) are in **[docs/archive/](docs/archive/)** — not for new deployments.

### Surveillance computer architecture

NGAME runs on **one machine only**: the **surveillance computer**. The bookkeeper's PC, other staff machines, and the QBO user's browser workstation require **no NGAME software**.

QuickBooks Online is cloud-hosted. The bookkeeper uses a browser; NGAME uses Intuit's **read-only** API with credentials stored on the surveillance PC. Both paths read the same company data; they are independent.

```
Bookkeeper's computer
  └─ browser → QuickBooks Online (cloud)
                      ↑
Surveillance computer
  └─ NGAME → Intuit API (read-only) → same company data
```

| Component | Location |
|-----------|----------|
| NGAME software, Python, Ollama | Surveillance computer |
| `quickbooks_config.json` / `wave_config.json` | Surveillance computer |
| NGAME web dashboard (`localhost:5001`) | Surveillance computer |
| Bookkeeper / other org PCs | **No NGAME install** |

The bookkeeper does not need to change how they use QuickBooks. NGAME does not write to QBO unless you configure otherwise; the default deployment is read-only surveillance.

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
5. [ ] Complete [§ 6 — Ollama](#6--ollama-before-phase-ii--fraud-analysis) (required before Phase II / Day 31)
6. [ ] Smoke-test CLI: `python3 run_training_flow.py` from repo root (optional if dashboard works)
7. [ ] Start dashboard; confirm **http://localhost:5001/dashboard** loads
8. [ ] Configure LaunchAgent (macOS) or Task Scheduler (Windows) so dashboard survives reboot
9. [ ] Run **one** training day from dashboard; confirm `NGAME_Training_Matrix.xlsx` appears
10. [ ] Print/PDF FRP guide; fill contact blanks; create **NGAME Dashboard** bookmark on surveillance PC
11. [ ] Supervise FRP through one **Run Training Day** (or primary green button in Phase I)
12. [ ] Hand off — FRP gets guide + bookmark only (no Terminal instructions for daily use)

---

## Windows surveillance PC — trial install (start here)

**This file is the single installer guide.** You do not need this chat, older root-level guides, or anything under **[docs/archive/](docs/archive/)** for a new Windows trial.

### Before you install on the surveillance PC

On the machine where you develop NGAME (for example your Mac):

1. Commit any doc or code changes.
2. Run `git push origin main` so **GitHub** has the latest version.

The Windows PC **downloads** the project with `git clone` (below). Pushing updates GitHub; the surveillance machine **pulls** when you need a newer copy later.

### On the Windows PC (fresh machine, no prior NGAME)

Use **PowerShell**. Follow the sections in this order:

| Step | What to do | Section below |
|------|------------|-----------------|
| 1 | Python 3.10+, Git, stable internet | [Prerequisites](#prerequisites) |
| 2 | Clone repo, create `.venv`, `pip install -r requirements.txt` | [Windows installation](#windows-installation) §§ 1–4 |
| 3 | `quickbooks_config.json` and/or `wave_config.json` | [Credentials and configuration](#credentials-and-configuration) |
| 4 | Complete Ollama setup (needed before Phase II / Day 31) | [Windows installation](#windows-installation) § 6 |
| 5 | Optional smoke test: `python run_training_flow.py` | [Windows installation](#windows-installation) § 7 |
| 6 | Start dashboard; confirm **http://localhost:5001/dashboard** | [Dashboard service](#dashboard-service-required-for-frp) |
| 7 | Task Scheduler auto-start at logon | [Windows — auto-start at login](#windows--auto-start-at-login) |
| 8 | One **Run Training Day** from dashboard; confirm `NGAME_Training_Matrix.xlsx` | [Verify installation](#verify-installation) |
| 9 | Print FRP guide, bookmark, supervised handoff | [Hand off to the FRP](#hand-off-to-the-frp) |

Also use the [Consultant checklist](#consultant-checklist-end-to-end) above and check off each box before you leave the site.

**Clone (default path on Windows):**

```powershell
cd "$env:USERPROFILE\Documents"
git clone https://github.com/ronaldcturner/ngame.git
cd ngame
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, see [Troubleshooting](#troubleshooting). Substitute your actual install path everywhere this guide shows `C:\NGAME\` in the auto-start batch file.

### What the FRP uses (not this file)

| Deliverable | File / URL |
|-------------|------------|
| Daily operations (print/PDF) | **[FRP_OPERATIONS_GUIDE.html](FRP_OPERATIONS_GUIDE.html)** |
| Browser bookmark | `http://localhost:5001/dashboard` |

The FRP does **not** use Terminal, `git`, or `pip` for daily work.

### Updating NGAME on the surveillance PC later

```powershell
cd C:\path\to\ngame
git pull origin main
.venv\Scripts\Activate.ps1
```

Restart the dashboard (sign out/in if Task Scheduler starts it, or run `app-simple.py` once to test). Do **not** follow archived CLI daily workflows in **docs/archive/**.

### Related docs (installer only)

| Need | Document |
|------|----------|
| Dashboard URLs / UI issues | [ngame_ui/README.md](ngame_ui/README.md), [ngame_ui/TROUBLESHOOTING.md](ngame_ui/TROUBLESHOOTING.md) |
| Wave API setup | [NGAME_WAVE_GRAPHQL_README.md](NGAME_WAVE_GRAPHQL_README.md) |
| Architecture / developers | [README.md](README.md) |

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

- [Windows surveillance PC — trial install (start here)](#windows-surveillance-pc--trial-install-start-here)
- [Surveillance computer architecture](#surveillance-computer-architecture)
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

### 6 — Ollama (before Phase II / fraud analysis)

Ollama runs **locally** on the surveillance computer. It powers the **LLM step** in fraud analysis (mapping anomalies to the misappropriation taxonomy in `Asset_Misappropriation.ttl`). Data stays on the machine — nothing is sent to a cloud LLM.

| Phase | Ollama required? |
|-------|------------------|
| **Training** (Days 1–30, `run_training_flow.py` or dashboard **Run Training Day**) | **No** — you can install Ollama after training works |
| **Fraud / surveillance** (Day 31+, `run_fraud_analysis.py` or dashboard **Run Churn Analysis**) | **Yes** — without Ollama, churn/z-scores may still run but management warnings lack LLM narrative |

**NGAME defaults** (in `ngame_llm_analysis_agent.py`): service `http://localhost:11434`, model name **`llama3.1:8b`**. The name you `ollama pull` must **exactly match** the `self.model_name = "..."` line in that file.

#### 6.1 — Install the Ollama application

1. In a browser, open [ollama.com/download](https://ollama.com/download).
2. Download **Ollama for macOS** and install (drag to Applications is typical).
3. Launch **Ollama** once. Confirm the **menu bar icon** (llama) appears — the app runs in the background.
4. You do **not** need a separate `ollama serve` command when the macOS app is running.

#### 6.2 — Verify the Ollama CLI

Open **Terminal** (venv not required for these commands):

```bash
ollama --version
ollama list
```

`ollama list` may be empty until you pull a model in § 6.4.

#### 6.3 — Choose a model (RAM and disk)

Pick **one** model for this machine. Use `ollama list` on the Mac after pull to see the exact tag.

| Model tag (`ollama pull …`) | Approx. disk | RAM guidance | Notes |
|-----------------------------|--------------|--------------|--------|
| **`llama3.1:8b`** | ~4–5 GB | **16 GB+** system RAM recommended | Matches NGAME code default |
| **`llama2:7b`** | ~3.8 GB | **8 GB+** RAM; close other apps | Good trial on smaller Macs |
| **`gemma2:2b`** | ~1.6 GB | **8 GB** tight but often workable | Lighter; shorter LLM answers |

If the Mac already has a custom model (e.g. `fraud-analyzer:latest` from `ollama list`), you may use it — set `model_name` to that **exact** tag in § 6.5.

#### 6.4 — Download the model

Replace `<model>` with your choice (example uses `llama2:7b`):

```bash
ollama pull llama2:7b
```

Wait until the download completes. Verify:

```bash
ollama list
```

#### 6.5 — Align NGAME with the model name

1. Open the repo root in Cursor or an editor.
2. Edit **`ngame_llm_analysis_agent.py`** near the top of `NGameLLMAnalysisAgent.__init__`:

```python
self.model_name = "llama2:7b"   # must match `ollama list` exactly
```

3. Save the file. On the surveillance PC, this same line must match **that** machine’s pulled model (copy the file or repeat this edit after `git pull`).

#### 6.6 — Smoke-test Ollama (not NGAME yet)

```bash
ollama run llama2:7b "Reply with the single word OK."
```

Exit the chat with `/bye` or **Ctrl+D**. If this fails, fix Ollama before running fraud analysis.

Optional API check:

```bash
curl -s http://localhost:11434/api/tags
```

#### 6.7 — Before the first fraud run (consultant only)

| Prerequisite | Check |
|--------------|--------|
| **30 training days** in `NGAME_Training_Matrix.xlsx` | Fraud launcher refuses fewer than 30 day columns — complete training or copy a 30-day matrix from another machine |
| **`Asset_Misappropriation.ttl`** in repo root | Required for LLM taxonomy |
| **Ollama running** | Menu bar icon visible |
| **Model pulled and `model_name` aligned** | § 6.4–6.5 |

Test fraud analysis (repo root, venv active) when ready:

```bash
python3 run_fraud_analysis.py
```

Answer **`y`** when prompted. Expect several minutes (QBO extract → CPI → churn → Ollama → warning JSON).

**FRP:** Does not install Ollama or edit `model_name`. The FRP only presses dashboard buttons; the technical contact completes this section.

### 7 — Quick smoke test (optional)

```bash
python3 run_training_flow.py
```

No errors → core pipeline is reachable. Full verification is in [Verify installation](#verify-installation) after the dashboard is running.

---

## Windows installation

Tested on Windows 10 (1909+) and Windows 11. Use **PowerShell** unless you prefer Git Bash. Even if you are familiar with "raw" Terminal CLI editing, use **PowerShell** or Git Bash instead. The script below will not work with "raw" CLI.

### 1 — Python 3.10+

[python.org/downloads](https://python.org/downloads) — check **Add Python to PATH** during install.

```powershell
python --version
```

### 2 — Git

In your browser (not PowerShell), open
[git-scm.com/download/win](https://git-scm.com/download/win) — This takes you directly to the Git Install page. The defaults are fine.

```powershell
git --version
```

### 3 — Clone

Run these in **PowerShell** (not Command Prompt). Quote the path — without quotes, `\D` in `\Documents` is parsed as an escape and `cd` fails.

```powershell
cd "$env:USERPROFILE\Documents"
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

With the venv active (`(.venv)` in the prompt), use **`python -m pip`** — not bare `pip`. On many Windows installs, `pip install` alone fails with *not a valid application for this OS platform*; `python -m pip` uses the correct interpreter.

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If install fails with **compiler** errors, install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and retry.

### 5 — Credentials

See [Credentials and configuration](#credentials-and-configuration).

### 6 — Ollama (before Phase II / fraud analysis)

Ollama runs **locally** on the surveillance computer. It powers the **LLM step** in fraud analysis (mapping anomalies to the misappropriation taxonomy in `Asset_Misappropriation.ttl`). Data stays on the machine — nothing is sent to a cloud LLM.

| Phase | Ollama required? |
|-------|------------------|
| **Training** (Days 1–30, `run_training_flow.py` or dashboard **Run Training Day**) | **No** — install Ollama after training works |
| **Fraud / surveillance** (Day 31+, `run_fraud_analysis.py` or dashboard **Run Churn Analysis**) | **Yes** — without Ollama, churn/z-scores may still run but management warnings lack LLM narrative |

**NGAME defaults** (in `ngame_llm_analysis_agent.py`): service `http://localhost:11434`, model name **`llama3.1:8b`**. The name you `ollama pull` must **exactly match** the `self.model_name = "..."` line in that file.

#### 6.1 — Install the Ollama application

1. In a browser on the surveillance PC, open [ollama.com/download](https://ollama.com/download).
2. Download **Ollama for Windows** and run the installer (defaults are fine).
3. After install, Ollama usually runs as a **background service** with a **tray icon** (system tray). Leave it running.
4. Do **not** run `ollama pull` in the browser — only in **PowerShell** (below).

#### 6.2 — Verify the Ollama CLI

Open **PowerShell** (NGAME venv **not** required for these commands):

```powershell
ollama --version
ollama list
```

`ollama list` may be empty until you pull a model in § 6.4.

#### 6.3 — Choose a model (RAM and disk)

Pick **one** model for this PC. Limited-RAM machines should **not** default to `llama3.1:8b` unless you have roughly **16 GB+** RAM.

| Model tag (`ollama pull …`) | Approx. disk | RAM guidance | Notes |
|-----------------------------|--------------|--------------|--------|
| **`llama3.1:8b`** | ~4–5 GB | **16 GB+** system RAM recommended | Matches NGAME code default |
| **`llama2:7b`** | ~3.8 GB | **8 GB+** RAM; close other apps | **Recommended** starting point for constrained PCs |
| **`gemma2:2b`** | ~1.6 GB | **8 GB** tight but often workable | Lighter; adequate for taxonomy-style prompts |

#### 6.4 — Download the model

Replace `<model>` with your choice (example uses `llama2:7b`):

```powershell
ollama pull llama2:7b
```

Wait until the download completes (may take several minutes). Verify:

```powershell
ollama list
```

You should see the model name in the **NAME** column. Copy that string exactly for § 6.5.

#### 6.5 — Align NGAME with the model name

1. Open the repo folder in Cursor or Notepad (e.g. `Documents\ngame`).
2. Edit **`ngame_llm_analysis_agent.py`** in the **repository root** — find `NGameLLMAnalysisAgent.__init__`:

```python
self.model_name = "llama2:7b"   # must match `ollama list` exactly
```

3. Save the file. If you `git pull` later from GitHub, re-check this line — the repo default may differ from what you pulled on this PC.

**Do not** change the model name only in INSTALL.md; NGAME reads **`ngame_llm_analysis_agent.py`**.

#### 6.6 — Smoke-test Ollama (not NGAME yet)

```powershell
ollama run llama2:7b "Reply with the single word OK."
```

Exit with `/bye` or **Ctrl+D**. If this hangs or errors, fix Ollama before fraud analysis (RAM, tray icon, re-pull model).

Optional check that the API responds:

```powershell
Invoke-WebRequest -Uri http://localhost:11434/api/tags -UseBasicParsing | Select-Object -ExpandProperty Content
```

#### 6.7 — Before the first fraud run (consultant only)

| Prerequisite | Check |
|--------------|--------|
| **30 training days** in `NGAME_Training_Matrix.xlsx` | `run_fraud_analysis.py` blocks if fewer than 30 day columns — add training days with **`y`**, or copy a 30-day matrix from the Mac |
| **`Asset_Misappropriation.ttl`** in repo root | Ships with the repo; confirm present |
| **Ollama service running** | Tray icon visible |
| **Model pulled and `model_name` aligned** | § 6.4–6.5 |

Test fraud analysis (repo root, `(.venv)` active) when ready:

```powershell
python run_fraud_analysis.py
```

Answer **`y`** when prompted. Or use the dashboard with **`app-simple.py`** running → **Run Churn Analysis**.

Outputs to confirm in repo root: `management_dashboard.json`, `NGAME_Fraud_Analysis_readable*.json`; refresh **http://localhost:5001/dashboard**.

**FRP:** Does not install Ollama, run `ollama pull`, or edit `model_name`. The FRP uses dashboard buttons only.

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
| 4 | Ollama (before Day 31) | `ollama list` shows your model; `model_name` aligned in `ngame_llm_analysis_agent.py`; when 30 training days complete, test `python run_training_flow.py` / `python3 run_fraud_analysis.py` or dashboard **Run Churn Analysis** |
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
| `cd $env:USERPROFILE\Documents` — “filename, directory name, or volume label syntax is incorrect” | Use **PowerShell** and quote the path: `cd "$env:USERPROFILE\Documents"` (or `cd "$env:USERPROFILE/Documents"`) |
| `python3` / `python` not found | Reinstall Python; on Windows enable **Add to PATH** |
| `pip install` → *not a valid application for this OS platform* (Windows) | Use `python -m pip install ...` with venv active; see [§ 4 — Virtual environment](#4--virtual-environment) |
| `pip install` compiler error (Windows) | Install Microsoft C++ Build Tools; retry |
| PowerShell blocks venv activation | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Dashboard empty | Run one training or churn day from dashboard |
| FRP cannot connect | Check LaunchAgent / Task Scheduler; read `logs/dashboard.err.log` |
| `Ollama is not running or not accessible` | Start Ollama (macOS: menu bar app; Windows: tray icon); `ollama list` |
| `model not found` / LLM error in Phase II | `ollama list` tag must match `self.model_name` in `ngame_llm_analysis_agent.py`; run `ollama pull` for that tag |
| Ollama very slow or PC freezes | Use a smaller model (`gemma2:2b`); close browsers; see [§ 6 — Ollama](#6--ollama-before-phase-ii--fraud-analysis) |
| Fraud blocked: training incomplete | Need **30** day columns in `NGAME_Training_Matrix.xlsx` |
| `No module named 'quickbooks'` (Windows) | `python -m pip install python-quickbooks intuit-oauth` or re-run `python -m pip install -r requirements.txt` |
| QBO / Wave auth error | Refresh tokens in config JSON or `.env` |
| Terminal flooded with `GET /api/...` | Normal — dashboard auto-refresh; stop server with Ctrl+C when testing |

UI details: **[ngame_ui/TROUBLESHOOTING.md](ngame_ui/TROUBLESHOOTING.md)**.

---

*NGAME · Apache 2.0 · Copyright 2026 Ron Turner*
