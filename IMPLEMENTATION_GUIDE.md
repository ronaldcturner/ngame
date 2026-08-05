# NGAME — Implementation Guide

**Audience:** Systems administrator or **technical consultant** (NGAME implementation lead) — comfortable with Python, Terminal or PowerShell, and secure handling of API credentials.

**Not for:** The **Financially Responsible Person (FRP)**. The FRP uses only the web dashboard. Give them **[FRP_OPERATIONS_GUIDE.html](FRP_OPERATIONS_GUIDE.html)** (print/PDF) or **[FRP_OPERATIONS_GUIDE.md](FRP_OPERATIONS_GUIDE.md)** — not this file.

---

## Documentation map

| Document | Who reads it | What it covers |
|----------|--------------|----------------|
| **This file (`README.md` / `IMPLEMENTATION_GUIDE.md`)** | Technical consultant | Clone, Python env, credentials, Ollama, dashboard service, verification, FRP handoff — **same content in both filenames** |
| **[FRP_OPERATIONS_GUIDE.md](FRP_OPERATIONS_GUIDE.md)** / **[.html](FRP_OPERATIONS_GUIDE.html)** | FRP | Bookmark, daily training/fraud checks, warnings, QuickBooks Audit Log |
| **[ngame_ui/README.md](ngame_ui/README.md)** | Consultants | Dashboard URLs, API endpoints, UI troubleshooting |
| **[ngame_ui/TROUBLESHOOTING.md](ngame_ui/TROUBLESHOOTING.md)** | Consultants | Dashboard failures and common fixes |
| **[ANOMALY_INJECTION_AGENT_README.md](ANOMALY_INJECTION_AGENT_README.md)** | Technical validator | Optional injection harness (not for daily FRP use) |

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

## Contents

- [Choose your platform](#choose-your-platform)
- [macOS cookbook](#macos-cookbook)
- [Windows cookbook](#windows-cookbook)
- [Prerequisites](#prerequisites)
- [macOS installation (detail)](#macos-installation-detail)
- [Windows installation (detail)](#windows-installation-detail)
- [Credentials and configuration](#credentials-and-configuration)
  - [Choose your QuickBooks track](#choose-your-quickbooks-track)
  - [Track A — Development / sandbox](#quickbooks-online--track-a-development--sandbox)
  - [Track B — Customer Go-Live](#quickbooks-online--track-b-customer-go-live)
- [Dashboard service](#dashboard-service-required-for-frp)
  - [Start manually](#start-manually-testing)
  - [macOS — auto-start at login](#macos--auto-start-at-login)
  - [Windows — auto-start at login](#windows--auto-start-at-login)
- [Verify installation](#verify-installation)
- [Hand off to the FRP](#hand-off-to-the-frp)
- [Leave-site checklist](#leave-site-checklist)
- [Appendix: Developer — publish before remote clone](#appendix-developer--publish-before-remote-clone)
- [Appendix: Where to run commands](#appendix-where-to-run-commands)
- [Appendix: Updating NGAME later](#appendix-updating-ngame-later)
- [Optional: CLI and scheduled runs](#optional-cli-and-scheduled-runs)
- [Troubleshooting](#troubleshooting)

---

## Choose your platform

This guide has **two** top-level cookbooks — one per OS. Pick the surveillance computer’s OS and follow **only** that cookbook’s Steps 1–9.

| Surveillance PC OS | Open this cookbook |
|--------------------|--------------------|
| macOS | [macOS cookbook](#macos-cookbook) |
| Windows 10 / 11 | [Windows cookbook](#windows-cookbook) |

Detail sections farther down are shared or OS-specific. Each detail block ends with **← Back** links so you return to Steps 1–9 without scrolling.

---

## macOS cookbook

**Audience:** Technical consultant installing NGAME on a **macOS** surveillance computer. Use **Terminal**.

Follow Steps 1–9 in order. Open each **Detail** link, finish that section, then use **← Back to macOS cookbook** at the bottom of the detail to return here for the next step. Do not rely on scrolling.

| Step | What to do | Detail |
|------|------------|--------|
| 1 | Confirm Python 3.10+, Git, internet, accounting access | [Prerequisites](#prerequisites) |
| 2 | Clone repo, create `.venv`, install requirements | [macOS installation — §§ 1–4](#macos-installation-detail) |
| 3 | Credentials; QBO [Track A](#quickbooks-online--track-a-development--sandbox) or [Track B](#quickbooks-online--track-b-customer-go-live) | [Credentials](#credentials-and-configuration) |
| 4 | Ollama (before Phase II / Day 31) | [macOS installation — § 6](#macos-ollama) |
| 5 | Optional smoke test | [macOS installation — § 7](#macos-smoke-test) |
| 6 | Start dashboard; open http://localhost:5001/dashboard | [Start manually](#start-manually-testing) |
| 7 | LaunchAgent auto-start at login | [macOS — auto-start at login](#macos--auto-start-at-login) |
| 8 | One Run Training Day; confirm matrix file | [Verify installation](#verify-installation) |
| 9 | FRP guide, bookmark, supervised handoff | [Hand off to the FRP](#hand-off-to-the-frp) |

When Step 9 is done, use the [Leave-site checklist](#leave-site-checklist).

---

## Windows cookbook

**Audience:** Technical consultant installing NGAME on a **Windows** surveillance computer. Use **PowerShell** (not Command Prompt).

Follow Steps 1–9 in order. Open each **Detail** link, finish that section, then use **← Back to Windows cookbook** at the bottom of the detail to return here for the next step. Do not rely on scrolling.

| Step | What to do | Detail |
|------|------------|--------|
| 1 | Confirm Python 3.10+, Git, internet, accounting access | [Prerequisites](#prerequisites) |
| 2 | Clone repo, create `.venv`, install requirements | [Windows installation — §§ 1–4](#windows-installation-detail) |
| 3 | Credentials; QBO [Track A](#quickbooks-online--track-a-development--sandbox) or [Track B](#quickbooks-online--track-b-customer-go-live) | [Credentials](#credentials-and-configuration) |
| 4 | Ollama (before Phase II / Day 31) | [Windows installation — § 6](#windows-ollama) |
| 5 | Optional smoke test | [Windows installation — § 7](#windows-smoke-test) |
| 6 | Start dashboard; open http://localhost:5001/dashboard | [Start manually](#start-manually-testing) |
| 7 | Task Scheduler auto-start at logon | [Windows — auto-start at login](#windows--auto-start-at-login) |
| 8 | One Run Training Day; confirm matrix file | [Verify installation](#verify-installation) |
| 9 | FRP guide, bookmark, supervised handoff | [Hand off to the FRP](#hand-off-to-the-frp) |

When Step 9 is done, use the [Leave-site checklist](#leave-site-checklist).

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
**Return to cookbook:** [← macOS Steps 1–9](#macos-cookbook) · [← Windows Steps 1–9](#windows-cookbook)  
**Next:** [Step 2 — macOS install detail](#macos-installation-detail) or [Step 2 — Windows install detail](#windows-installation-detail)

---

## macOS installation (detail)

<a id="macos-installation-detail"></a>


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
pip install -r ngame_ui/requirements.txt
```

Allow 2–5 minutes on first install. Root `requirements.txt` includes Flask for the dashboard; `ngame_ui/requirements.txt` pins the full UI set — install both.


---
**macOS cookbook:** [← Back to Steps 1–9](#macos-cookbook) · **Next:** [Step 3 — Credentials](#credentials-and-configuration)

### 5 — Credentials

See [Credentials and configuration](#credentials-and-configuration).

<a id="macos-ollama"></a>

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


---
**macOS cookbook:** [← Back to Steps 1–9](#macos-cookbook) · **Next:** [Step 5 — Smoke test](#macos-smoke-test)

<a id="macos-smoke-test"></a>

### 7 — Quick smoke test (optional)

```bash
python3 run_training_flow.py
```

No errors → core pipeline is reachable. Full verification is in [Verify installation](#verify-installation) after the dashboard is running.

---

---
**macOS cookbook:** [← Back to Steps 1–9](#macos-cookbook) · **Next:** [Step 6 — Dashboard](#start-manually-testing)


## Windows installation (detail)

<a id="windows-installation-detail"></a>


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

Run these in **PowerShell** (not Command Prompt).

PowerShell treated `"$env:USERPROFILE\Documents"` as an empty name, so it tried `C:\Documents`. Use this instead:

```powershell
$env:USERPROFILE
cd "$($env:USERPROFILE)\Documents"
git clone https://github.com/ronaldcturner/ngame.git
cd ngame
```

`$env:USERPROFILE` should print something like `C:\Users\YourName` (not blank). After `cd`, the prompt should end in `\Documents`.

**If `cd` still fails**, use:

```powershell
cd (Join-Path $env:USERPROFILE 'Documents')
```

**If clone says** `destination path 'ngame' already exists and is not an empty directory`, that folder is already present under Documents. Rename or remove it, then run `git clone` again:

```powershell
Rename-Item ngame ngame-clone-old
# or: Remove-Item -Recurse -Force .\ngame
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
python -m pip install -r ngame_ui/requirements.txt
```

If install fails with **compiler** errors, install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and retry.


---
**Windows cookbook:** [← Back to Steps 1–9](#windows-cookbook) · **Next:** [Step 3 — Credentials](#credentials-and-configuration)

### 5 — Credentials

See [Credentials and configuration](#credentials-and-configuration).

<a id="windows-ollama"></a>

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

**Do not** change the model name only in this guide; NGAME reads **`ngame_llm_analysis_agent.py`**.

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


---
**Windows cookbook:** [← Back to Steps 1–9](#windows-cookbook) · **Next:** [Step 5 — Smoke test](#windows-smoke-test)

<a id="windows-smoke-test"></a>

### 7 — Quick smoke test (optional)

```powershell
python run_training_flow.py
```

---

---
**Windows cookbook:** [← Back to Steps 1–9](#windows-cookbook) · **Next:** [Step 6 — Dashboard](#start-manually-testing)


## Credentials and configuration

Configure **one** accounting source (or both if you are testing).

### Wave (simplest)

```bash
# macOS
cp wave_config.example.json wave_config.json

# Windows
Copy-Item wave_config.example.json wave_config.json
```

Edit `wave_config.json` — set `access_token` and `business_id` from [developer.waveapps.com](https://developer.waveapps.com). Optional CLI: `python3 run_wave_extraction.py` (repo root, venv active).

### Choose your QuickBooks track

The **software install** (Python, Git, clone, `.venv`, dashboard, auto-start) is **identical** for practice and for customer go-live. Only the **QuickBooks Online** connection forks.

| Track | When to use | QBO company | Intuit keys | `environment` in `quickbooks_config.json` |
|-------|-------------|-------------|-------------|-------------------------------------------|
| **A — Development (practice / lab)** | Cold install; university lab; Safe Landing–style sandbox | Intuit **sandbox** company | **Development** Client ID / Secret | `sandbox` |
| **B — Customer Go-Live** | Customer’s surveillance PC for the FRP | Customer’s **live** QBO company | **Production** Client ID / Secret | `production` |

- Track A: [QuickBooks Online — Track A (Development / sandbox)](#quickbooks-online--track-a-development--sandbox)
- Track B: [QuickBooks Online — Track B (Customer Go-Live)](#quickbooks-online--track-b-customer-go-live) — do **not** reuse Development keys or a sandbox company on a go-live machine.

### QuickBooks Online — Track A (Development / sandbox)

**Practice / lab track.** For the customer’s live ledger, skip this section and use **Track B** instead.


The default deployment uses the **dashboard** (`app-simple.py` at **http://localhost:5001/dashboard**) to pull **live QuickBooks Online data** (sandbox for lab/POC; production when deployed). OAuth must succeed before **Run Training Day**, **Run Churn Analysis**, or any live QBO API pull will work. The dashboard can load without OAuth; live data cannot.

Create the config file at repository root:

```bash
cp quickbooks_config.example.json quickbooks_config.json   # macOS
Copy-Item quickbooks_config.example.json quickbooks_config.json   # Windows
```

#### Why OAuth and the redirect URI matter

NGAME does not store the bookkeeper’s QBO password. It uses **OAuth 2.0**: a one-time browser authorization on the surveillance machine, then **access and refresh tokens** in `quickbooks_config.json`. When tokens expire or are revoked, NGAME opens Intuit again and completes the same flow.

Intuit only redirects the browser back to **URIs you register** in the Developer Portal. If the registered URI does not **exactly** match what NGAME sends, authorization fails (often: *“Sorry, but [app name] didn’t connect”*).

This procedure is a **required prerequisite** for operating NGAME with real (or sandbox) QBO data—not for merely opening the dashboard in a browser.

#### Two URLs — do not confuse them

| URL | Port | Role | Register in Intuit? |
|-----|------|------|---------------------|
| **http://localhost:5001/dashboard** | 5001 | NGAME web UI (`app-simple.py`). FRP bookmark. | **No** |
| **http://localhost:8000/callback** | 8000 | OAuth callback. Intuit redirects here after **Connect**. NGAME’s local listener captures the code. | **Yes** (Development / sandbox) |

- The **dashboard** can start and display without OAuth.
- **Live QBO pulls** require valid OAuth tokens, which require the **callback URI** to be registered and to match `quickbooks_config.json`.

Default in repo: `quickbooks_config.example.json` → `"redirect_uri": "http://localhost:8000/callback"`. Older notes sometimes mention port **8080**; portal and config must agree on **one** value (NGAME standard: **8000**).

#### Before you start (QuickBooks)

- [ ] Intuit **Developer** account access to the NGAME app, not only a QBO bookkeeper login.
- [ ] `quickbooks_config.json` with **Development** Client ID and Client Secret.
- [ ] `"environment": "sandbox"` for lab/POC (`"production"` only with production keys and a live company).
- [ ] Sandbox company available; authorize as **Company Administrator** or **Master Administrator** (Standard users cannot complete app OAuth).
- [ ] Python venv active at repo root; `intuit-oauth` installed (`requirements.txt`).

#### Register the redirect URI (Intuit Developer Portal)

Official reference: [Set app redirect URIs](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/set-redirect-uri).

1. Sign in at [developer.intuit.com](https://developer.intuit.com).
2. Open your app (e.g. Safe Landing).
3. Work in **Development** (sandbox), not Production, unless you are configuring a live deployment.

| Screen / field | Purpose | Use for NGAME localhost OAuth? |
|----------------|---------|--------------------------------|
| **Settings → Redirect URIs → Development** | Allowed OAuth callback URLs | **Yes** — add `http://localhost:8000/callback` here |
| **Keys & credentials → Development** | Client ID, Client Secret | Copy into `quickbooks_config.json`; redirect list may also appear under **Keys & OAuth** on some portal versions |
| **Launch URL / Host Domain** | Where users start your product | **No** — not the OAuth callback |
| `https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl` | OAuth 2.0 Playground only | **No** — leave unchanged; do not replace with localhost |

**Add and save the URI:**

1. Go to **Settings** → **Redirect URIs** → **Development** (or **Development → Keys & OAuth** if **Redirect URIs** appears there).
2. Click **Add URI**.
3. Enter exactly: `http://localhost:8000/callback`
4. Click **Save** for that row.

**Save is easy to miss:** it is often to the **right** of the URI field (between the text box and the trash icon). Widen the window or scroll horizontally if you only see the trash can. Changes do **not** persist if you tab away without **Save**. Success may show: *“Changes saved here and in your settings.”*

5. **Refresh the page** and confirm `http://localhost:8000/callback` is still listed.

Do **not** paste localhost into the Playground-only URL field. Localhost is for Development/sandbox only (per Intuit); production callbacks require **https**.

#### Align `quickbooks_config.json`

Under `quickbooks_api`, confirm:

| Field | Sandbox / lab value |
|-------|---------------------|
| `client_id` | Development Client ID from portal |
| `client_secret` | Development Client Secret |
| `redirect_uri` | `http://localhost:8000/callback` (must match portal **exactly**) |
| `environment` | `sandbox` |
| `realm_id`, `access_token`, `refresh_token` | Filled by OAuth (may be empty before first run) |

Optional overrides via `.env`: `QBO_CLIENT_ID`, `QBO_CLIENT_SECRET`, `QBO_REDIRECT_URI`, `QBO_ENVIRONMENT` (see `.env.example`).

#### Complete OAuth once on the surveillance machine

Run from **repository root** with venv active. Either method refreshes tokens; use one after portal or config changes.

**Recommended — dedicated OAuth / extraction test:**

```bash
cd /path/to/NGAME-POC          # your INSTALL_PATH
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\Activate.ps1   # Windows
python3 run_data_extraction.py # Windows: python run_data_extraction.py
```

A browser opens to Intuit. Sign in, select the **sandbox company** (if `environment` is `sandbox`), click **Connect** / **Authorize**.

**Success:** browser shows **“NGAME: OAuth complete. You can close this tab.”** Terminal shows ✅ lines. `quickbooks_config.json` has updated `access_token`, `refresh_token`, and `realm_id`.

**Keep the Terminal session open** until the callback page appears (NGAME listens on port **8000** for up to ~3 minutes).

**Alternative — from the dashboard:**

1. `cd ngame_ui` → `python3 app-simple.py` (Windows: `python app-simple.py`)
2. Open **http://localhost:5001/dashboard**
3. Click **Run Training Day** (or the primary green training button)

If tokens are invalid, the same OAuth browser flow runs in the background. Stopping the dashboard with **Ctrl+C** does not invalidate saved tokens; restart the dashboard when finished.

#### Verify live QuickBooks connection (consultant)

| Step | Check |
|------|--------|
| 1 | `quickbooks_config.json` contains non-empty `access_token`, `refresh_token`, `realm_id` |
| 2 | Dashboard loads at **http://localhost:5001/dashboard** |
| 3 | **Run Training Day** completes without Intuit “didn’t connect” error |
| 4 | `NGAME_Training_Matrix.xlsx` appears or updates in repo root (after at least one successful training run) |

A **UI-only demo** (no live QBO) may show the dashboard without OAuth—that is not the default model in this guide.

#### Sandbox authorization rules

| Requirement | Detail |
|-------------|--------|
| Login target | [sandbox.qbo.intuit.com](https://sandbox.qbo.intuit.com) for sandbox apps—not [qbo.intuit.com](https://qbo.intuit.com) unless `environment` is `production` |
| Role | **Company Admin** or **Master Admin** on the company being connected |
| Students / bookkeepers | May post transactions in QBO UI; they do **not** run NGAME OAuth on the surveillance PC |
| Developer portal login | For app keys and redirect URIs only—do not give students the developer password |

For a university lab sandbox, authorize as Company Admin on the sandbox company; students may post QBO data but do not run OAuth on the surveillance PC.

#### QuickBooks OAuth troubleshooting

| Symptom | Likely cause | Action |
|---------|----------------|--------|
| “[App] didn’t connect” on Intuit | Redirect URI mismatch or wrong environment | Portal **Development** list includes `http://localhost:8000/callback`; matches `quickbooks_config.json`; Save and refresh portal |
| “Please enter a unique valid redirect URI” | Duplicate or invalid paste | URI already listed—use existing row; or edit `8080` → `8000`; no trailing spaces |
| Only Playground URL visible | Wrong settings tab | **Settings → Redirect URIs → Development**, not Playground-only field |
| No Save button | Save off-screen | Scroll right / widen window; save per row |
| URI reverts after refresh | Did not click Save | Save explicitly; look for confirmation message |
| OAuth completes but training fails | Wrong company or expired tokens | Re-run `run_data_extraction.py`; confirm `realm_id` matches intended sandbox company |
| Port / callback timeout | 8000 blocked or Terminal closed | Free port 8000; keep Terminal open until callback message |
| Dashboard works; QBO fails | OAuth never completed | Complete OAuth above; do not rely on simulated QuickBooks page in UI |

Token refresh failures (`invalid_grant`): re-run OAuth. In CI/unattended environments, interactive OAuth is disabled—complete authorization once on the surveillance machine.

#### How this fits the dashboard-first deployment

```
FRP browser  →  http://localhost:5001/dashboard  (app-simple.py)
                      │
                      ├─ UI only: no Intuit redirect URI required
                      │
                      └─ Run Training Day / Run Churn Analysis
                             │
                             └─ NGAME pipeline → ensure_quickbooks_auth()
                                    │
                                    ├─ refresh token OR
                                    └─ browser OAuth → Intuit → http://localhost:8000/callback
                                           │
                                           └─ tokens saved → live QBO API (sandbox or production)
```

**Consultant order (QuickBooks):** (1) `quickbooks_config.json` → (2) register redirect URI in portal → (3) complete OAuth once → (4) start dashboard and verify → (5) [Dashboard service](#dashboard-service-required-for-frp) auto-start and FRP bookmark → (6) build training baseline via **Run Training Day** (30 business days).

**Fast demo without live QBO posting:** `python3 run_training_flow.py --demo` replays from `NGAME_Training_Matrix_SAVED.xlsx`—does not replace OAuth for live pulls.

Implementation details: `ngame_quickbooks_oauth.py`, `quickbooks_config.example.json`.


### QuickBooks Online — Track B (Customer Go-Live)

**Goal:** On the **customer’s surveillance PC**, connect NGAME to the customer’s **own live QuickBooks Online company** (not a sandbox). The FRP then uses the local dashboard against that ledger.

**Do not use Track A values** (Development keys, `"environment": "sandbox"`, Safe Landing / other sandbox companies) on a go-live machine.

#### B.0 — What is the same as Track A

| Step | Same as Track A? |
|------|------------------|
| Install Python, Git, clone repo, `.venv`, `pip install` | **Yes** |
| Start dashboard / auto-start / FRP bookmark | **Yes** |
| OAuth concept (browser authorize once → tokens in `quickbooks_config.json`) | **Yes** |
| Intuit Developer Portal **Development** keys and sandbox company | **No — use Production** |
| `"environment": "sandbox"` | **No — use `production`** |
| `http://localhost:8000/callback` as Production redirect URI | **No — Intuit rejects localhost / http for Production** |

#### B.1 — Before you start (go-live checklist)

- [ ] Customer has approved NGAME read-only API access to their live QBO company.
- [ ] You have Intuit **Developer** access to the NGAME app (or the customer’s app) — not only a bookkeeper QBO login.
- [ ] You can open **Keys & credentials → Production** (Client ID and Client Secret).
- [ ] A **Company Administrator** or **Master Administrator** of the **live** company will complete the one-time Connect/Authorize click (Standard users cannot finish app OAuth).
- [ ] Surveillance PC has stable internet; Python venv already created (OS installation §§ 1–4 done).
- [ ] You understand Production OAuth needs a temporary **https** callback (see B.3) — not the Track A localhost URI alone.

#### B.2 — Create / align `quickbooks_config.json` for Production

From repository root:

```bash
# macOS
cp quickbooks_config.example.json quickbooks_config.json

# Windows PowerShell
Copy-Item quickbooks_config.example.json quickbooks_config.json
```

Edit `quickbooks_config.json` and set **`quickbooks_api`** fields:

| Field | Customer Go-Live value |
|-------|------------------------|
| `client_id` | **Production** Client ID from Intuit Developer Portal |
| `client_secret` | **Production** Client Secret |
| `environment` | `production` |
| `redirect_uri` | Your **https** Production redirect URI from B.3 (exact string) |
| `realm_id`, `access_token`, `refresh_token` | Leave empty until OAuth succeeds |

Save the file. Keep it only on the surveillance PC (it is gitignored).

#### B.3 — Production redirect URI (required by Intuit)

Intuit rules for **Production** (see [Set app redirect URIs](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/set-redirect-uri)):

- Redirect URI must start with **`https://`**
- **`localhost` is not allowed**
- IP addresses are not allowed

NGAME still needs a **one-time** (or re-auth) browser redirect that lands on a listener on the surveillance PC. After tokens exist, daily work uses **token refresh** — no redirect — until tokens are revoked or expire beyond refresh.

NGAME binds the OAuth callback listener on **`127.0.0.1:8000`** while Intuit redirects to your public **https** URI. A temporary tunnel bridges them.

**Consultant method (temporary HTTPS tunnel for the OAuth session only):**

1. On the surveillance PC, start a tunnel that forwards public HTTPS to local port **8000** (example: [ngrok](https://ngrok.com/) — `ngrok http 8000`).
2. Copy the tunnel’s **https** base URL (example shape: `https://<random>.ngrok-free.app`).
3. In Intuit Developer Portal → your app → **Settings → Redirect URIs → Production**:
   - **Add URI** exactly: `https://<random>.ngrok-free.app/callback`
   - Click **Save** on that row; refresh and confirm it remains listed.
4. Put the **same** string in `quickbooks_config.json` → `redirect_uri`.
5. Keep the tunnel **running** until OAuth completes (B.4). You may stop the tunnel afterward.

Do **not** paste a Production URI into Development-only fields, and do **not** use the OAuth Playground URL as NGAME’s runtime `redirect_uri` unless you are following a separate manual-token procedure (not the default dashboard flow).

#### B.4 — Complete OAuth once against the live company

1. Leave the HTTPS tunnel running (B.3).
2. From repository root with venv active:

```bash
# macOS
source .venv/bin/activate
python3 run_data_extraction.py

# Windows PowerShell
.venv\Scripts\Activate.ps1
python run_data_extraction.py
```

3. Browser opens to Intuit. Sign in to the **live** QBO company ([qbo.intuit.com](https://qbo.intuit.com) — not sandbox).
4. Select the **customer’s live company** (not a sandbox company).
5. Click **Connect** / **Authorize** as Company Admin / Master Admin.
6. **Success:** browser shows **“NGAME: OAuth complete. You can close this tab.”** Terminal shows success lines. `quickbooks_config.json` now has non-empty `access_token`, `refresh_token`, and `realm_id`.
7. Stop the tunnel. Daily dashboard use does not need it while refresh tokens remain valid.

**Alternative:** With the dashboard already running, **Run Training Day** will trigger the same OAuth flow if tokens are missing — still requires the tunnel and matching Production redirect URI for the interactive step.

#### B.5 — Verify live customer ledger (not sandbox)

| Step | Check |
|------|--------|
| 1 | `quickbooks_config.json` has `"environment": "production"` and Production client id/secret |
| 2 | `realm_id` matches the customer’s live company (confirm in Intuit / QBO company settings if unsure) |
| 3 | Dashboard at **http://localhost:5001/dashboard** |
| 4 | **Run Training Day** completes without “didn’t connect”; matrix updates |
| 5 | Spot-check extracted entity counts against what the FRP/bookkeeper expects for the **live** books |

#### B.6 — Go-live authorization rules

| Requirement | Detail |
|-------------|--------|
| Login target | Live QBO ([qbo.intuit.com](https://qbo.intuit.com)), not sandbox |
| Role | Company Admin or Master Admin on the **live** company |
| Bookkeeper | Continues normal QBO browser use; does **not** run NGAME OAuth |
| FRP | Dashboard only after consultant finishes OAuth and auto-start |
| Secrets | Production Client Secret and tokens stay on the surveillance PC only |

#### B.7 — Re-authorization later

If refresh fails (`invalid_grant`) or the customer revokes the app:

1. Start the HTTPS tunnel again (or register a new Production redirect URI if the tunnel URL changed).
2. Align `redirect_uri` in portal and `quickbooks_config.json`.
3. Re-run `run_data_extraction.py` (or trigger OAuth from the dashboard).
4. Stop the tunnel after success.

#### B.8 — Continue after QBO works

Continue with your OS cookbook from **Step 6** (dashboard) onward. Give the FRP only the operations guide and the dashboard bookmark — not Developer Portal access.

### Environment variables

Alternatively: copy `.env.example` to `.env` and set variables listed there.

> **Security:** `wave_config.json`, `quickbooks_config.json`, and `.env` are in `.gitignore`. Keep them only on the surveillance machine.

---

---
**Return to cookbook:** [← macOS Steps 1–9](#macos-cookbook) · [← Windows Steps 1–9](#windows-cookbook)  
**Next:** [Step 4 — macOS Ollama](#macos-ollama) or [Step 4 — Windows Ollama](#windows-ollama)


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


---
**Return to cookbook:** [← macOS Steps 1–9](#macos-cookbook) · [← Windows Steps 1–9](#windows-cookbook)  
**Next:** [Step 7 — macOS LaunchAgent](#macos--auto-start-at-login) or [Step 7 — Windows Task Scheduler](#windows--auto-start-at-login)

### macOS — auto-start at login

**Goal:** After the FRP signs in to the surveillance Mac, the dashboard starts by itself — no Terminal window and no daily double-click.

**What you are building:** macOS keeps a per-user folder of **LaunchAgents** — small XML **plist** files that tell the system what to start at login. You create **one file**:

| Item | Value |
|------|--------|
| **File name** | `com.ngame.dashboard.plist` |
| **Full path** | `~/Library/LaunchAgents/com.ngame.dashboard.plist` |
| **Expanded example** | `/Users/you/Library/LaunchAgents/com.ngame.dashboard.plist` |

The tilde (`~`) is shorthand for the signed-in user's home folder. This file lives in **macOS user settings**, not inside the NGAME repo.

**Before you start:**

- [Start manually (testing)](#start-manually-testing) succeeded — **http://localhost:5001/dashboard** loads.
- You know where you cloned NGAME: the **repository root** (folder containing `.venv`, `ngame_ui`, and `requirements.txt`).

#### Step 1 — Write down your install path

In **Terminal**, `cd` to your NGAME folder and print the full path:

```bash
cd /path/to/your/clone    # wherever you ran git clone
pwd
```

Example output: `/Users/you/Developer/Projects/NGAME-POC`

Use that string everywhere below as **INSTALL_PATH**. All paths in the plist must be **absolute** (start with `/Users/...`).

#### Step 2 — Create the logs folder

Replace the example with your **INSTALL_PATH**:

```bash
mkdir -p /Users/you/Developer/Projects/NGAME-POC/logs
```

#### Step 3 — Create the LaunchAgents folder

```bash
mkdir -p ~/Library/LaunchAgents
```

**Finder shortcut:** **Go → Go to Folder…** (⇧⌘G), paste `~/Library/LaunchAgents`, press Return. (`~/Library` is hidden by default — that is normal.)

#### Step 4 — Create `com.ngame.dashboard.plist`

You are creating a new text file named **`com.ngame.dashboard.plist`** in the folder from Step 3. Its entire contents are the XML block below — nothing else in the file.

**Terminal (recommended):**

```bash
nano ~/Library/LaunchAgents/com.ngame.dashboard.plist
```

Paste the XML. Replace **every** occurrence of `/Users/you/Developer/Projects/NGAME-POC` with your **INSTALL_PATH** from Step 1 (five paths total). Save: **Ctrl+O**, Enter, **Ctrl+X**.

**TextEdit (GUI alternative):**

1. Open **TextEdit** → **Format → Make Plain Text**.
2. Paste the XML (with your paths substituted).
3. **File → Save** → **Go to Folder…** → paste `~/Library/LaunchAgents`.
4. Save as **`com.ngame.dashboard.plist`** (not `.txt`).

**File contents** (substitute your **INSTALL_PATH** for the example path):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.ngame.dashboard</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/you/Developer/Projects/NGAME-POC/.venv/bin/python3</string>
    <string>/Users/you/Developer/Projects/NGAME-POC/ngame_ui/app-simple.py</string>
  </array>
  <key>WorkingDirectory</key>
  <string>/Users/you/Developer/Projects/NGAME-POC/ngame_ui</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/Users/you/Developer/Projects/NGAME-POC/logs/dashboard.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/you/Developer/Projects/NGAME-POC/logs/dashboard.err.log</string>
</dict>
</plist>
```

| Path in plist | Points to |
|---------------|-----------|
| `…/.venv/bin/python3` | Python from the venv you created at repo root |
| `…/ngame_ui/app-simple.py` | Dashboard script (same as [manual start](#start-manually-testing)) |
| `…/ngame_ui` | Working directory for the process |
| `…/logs/dashboard.log` | Normal output log |
| `…/logs/dashboard.err.log` | Error log |

The string `com.ngame.dashboard` under **Label** is the service name macOS uses internally; it should match the file name (without `.plist`).

#### Step 5 — Register the LaunchAgent

```bash
launchctl load ~/Library/LaunchAgents/com.ngame.dashboard.plist
```

#### Step 6 — Verify

1. Stop any dashboard you started manually for testing (**Ctrl+C** in that Terminal window).
2. Start the service now (optional quick check):

   ```bash
   launchctl start com.ngame.dashboard
   ```

3. Open **http://localhost:5001/dashboard** — the page should load.
4. **Reboot** (or sign out and back in) and confirm the dashboard still loads **without** opening Terminal.

**If it fails:** read `INSTALL_PATH/logs/dashboard.err.log` first. Common fixes: wrong **INSTALL_PATH** in the plist, `.venv` not created at repo root, or dashboard not yet tested manually.

**Consultant fallback:** double-click `launch_dashboard.command` in the repo root until the plist is fixed — do not leave that as the FRP's daily workflow.


---
**macOS cookbook:** [← Back to Steps 1–9](#macos-cookbook) · **Next:** [Step 8 — Verify](#verify-installation)

### Windows — auto-start at login

**Goal:** After the FRP signs in to the surveillance PC, the dashboard starts by itself — no PowerShell window the FRP must manage each morning.

**What you are building:** two pieces:

1. The **`start-dashboard.bat`** file that ships at repository root (relative paths — works after any `git clone` without editing).
2. A **Task Scheduler** job — a built-in Windows tool that runs that batch file at sign-in.

| Item | Value |
|------|--------|
| **Batch file name** | `start-dashboard.bat` (included in the repo) |
| **Example location** | `C:\Users\you\Documents\ngame\start-dashboard.bat` |
| **Task Scheduler task name** | `NGAME Dashboard` (you choose this in the wizard; use something recognizable) |

The batch file lives **inside your NGAME install folder** (repository root), next to `.venv` and `ngame_ui`. Task Scheduler is a Windows system app — you do not install anything extra.

**Before you start:**

- [Start manually (testing)](#start-manually-testing) succeeded — **http://localhost:5001/dashboard** loads.
- You know where you cloned NGAME: the **repository root** (folder containing `.venv`, `ngame_ui`, `start-dashboard.bat`, and `requirements.txt`).

#### Step 1 — Write down your install path

In **PowerShell**, `cd` to your NGAME folder and print the full path:

```powershell
cd "$($env:USERPROFILE)\Documents\ngame"    # or wherever you ran git clone
Get-Location
```

Example output: `C:\Users\you\Documents\ngame`

Use that string as **INSTALL_PATH** when pointing Task Scheduler at `start-dashboard.bat`.

#### Step 2 — Confirm `logs` and the shipped batch file

```powershell
New-Item -ItemType Directory -Force -Path ".\logs"
Get-Item .\start-dashboard.bat
```

**Shipped file contents** (relative paths — do not hard-code a user folder unless you have a special layout):

```bat
@echo off
REM NGAME dashboard auto-start — place at repository root (ships with the repo).
REM Double-click to test; Task Scheduler should run this file at logon.
cd /d "%~dp0"
if not exist "logs" mkdir logs
cd /d "%~dp0ngame_ui"
"%~dp0.venv\Scripts\pythonw.exe" app-simple.py >> "%~dp0logs\dashboard.log" 2>> "%~dp0logs\dashboard.err.log"
```

| Part of the batch file | Points to |
|------------------------|-----------|
| `%~dp0` | Folder containing the `.bat` (repository root) |
| `…\ngame_ui` | Dashboard working directory (same as [manual start](#start-manually-testing)) |
| `…\.venv\Scripts\pythonw.exe` | Python from the venv — **`pythonw.exe`** runs without a visible console window |
| `app-simple.py` | Dashboard script |
| `…\logs\dashboard.log` / `.err.log` | Output logs |

If `start-dashboard.bat` is missing (old clone), create it with the contents above.

**Quick test:** Double-click `start-dashboard.bat` in File Explorer once. Wait a few seconds, then open **http://localhost:5001/dashboard**. If it loads, stop the test (close any running dashboard from Task Manager or reboot) before continuing to Step 3.

#### Step 3 — Create the Task Scheduler job

1. Press the **Windows key**, type **Task Scheduler**, press **Enter**.
2. In the right **Actions** pane, click **Create Basic Task…**
3. **Name:** `NGAME Dashboard` → **Next**
4. **Trigger:** **When I log on** → **Next**
5. **Action:** **Start a program** → **Next**
6. **Program/script:** paste the full path to your batch file, for example:

   `C:\Users\you\Documents\ngame\start-dashboard.bat`

   (Use **Browse…** if you prefer to pick the file in a dialog.)
7. **Start in (optional):** leave blank — the batch file sets its own folder → **Next**
8. Check **Open the Properties dialog for this task when I click Finish** → **Finish**

In the **Properties** window that opens:

9. **General** tab: select **Run only when user is logged on** (the FRP uses a browser on this same PC).
10. **Conditions** tab: if this is a **laptop**, uncheck **Start the task only if the computer is on AC power** so the dashboard still starts on battery.
11. **Settings** tab: uncheck **Stop the task if it runs longer than** — the dashboard is meant to run all day.
12. Click **OK**. Enter your Windows password if prompted.

#### Step 4 — Verify

1. Stop any dashboard you started manually for testing (**Ctrl+C** in that PowerShell window).
2. Sign **out** and sign **back in** (or restart the PC).
3. Wait 10–15 seconds after the desktop appears.
4. Open **http://localhost:5001/dashboard** — the page should load **without** you opening PowerShell or double-clicking the batch file.

**If it fails:** read `INSTALL_PATH\logs\dashboard.err.log` first. Common fixes: `.venv` not created at repo root, Task Scheduler task points to the wrong file, or dashboard not yet tested manually.

**Consultant fallback:** double-click `start-dashboard.bat` in the repo root until Task Scheduler is fixed — do not leave that as the FRP's daily workflow.

> Do **not** schedule `ngame_dual_mode.py` on the same machine if the FRP runs from the dashboard — that can double-run the pipeline.

---

---
**Windows cookbook:** [← Back to Steps 1–9](#windows-cookbook) · **Next:** [Step 8 — Verify](#verify-installation)


## Verify installation

Complete **before** FRP handoff.

| # | Check | How |
|---|--------|-----|
| 1 | Dashboard loads | Open **http://localhost:5001/dashboard** (empty results OK until first run) |
| 2 | QuickBooks OAuth (if using QBO) | [QuickBooks Online](#quickbooks-online) complete; `quickbooks_config.json` has tokens; **Run Training Day** does not show Intuit “didn’t connect” |
| 3 | Training via UI | **NGAME Operations** → **Run Training Day** (or primary green **Run Today's Training Day**) → live output shows success / day recorded |
| 4 | Matrix file | `NGAME_Training_Matrix.xlsx` exists in repo root |
| 5 | Ollama (before Day 31) | `ollama list` shows your model; `model_name` aligned in `ngame_llm_analysis_agent.py`; when 30 training days complete, test `python run_training_flow.py` / `python3 run_fraud_analysis.py` or dashboard **Run Churn Analysis** |
| 6 | CLI fallback (optional) | `python3 run_training_flow.py` only if dashboard run failed — for debugging |

---

---
**Return to cookbook:** [← macOS Steps 1–9](#macos-cookbook) · [← Windows Steps 1–9](#windows-cookbook)  
**Next:** [Step 9 — Hand off](#hand-off-to-the-frp)


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

---
**Return to cookbook:** [← macOS Steps 1–9](#macos-cookbook) · [← Windows Steps 1–9](#windows-cookbook) · **Done** — use the [Leave-site checklist](#leave-site-checklist).


## Leave-site checklist

Complete after your OS cookbook Step 9. This is a **departure checklist**, not a second install cookbook.

1. [ ] OS cookbook Steps 1–9 done ([macOS](#macos-cookbook) or [Windows](#windows-cookbook))
2. [ ] Dashboard loads at http://localhost:5001/dashboard
3. [ ] Auto-start configured (LaunchAgent or Task Scheduler)
4. [ ] One training day recorded; `NGAME_Training_Matrix.xlsx` present
5. [ ] FRP guide printed/PDF; contacts filled; bookmark created
6. [ ] Supervised FRP Run Training Day completed
7. [ ] FRP has guide + bookmark only (no Terminal / PowerShell daily steps)

---

## Appendix: Developer — publish before remote clone

**Not part of the consultant install cookbook.** Use this on the **development** machine (for example your Mac) when you need GitHub to hold the latest code/docs before a surveillance PC runs `git clone` or `git pull`.

1. Commit changes.
2. `git push origin main`

The surveillance PC never pushes; it only clones/pulls.

---

## Appendix: Where to run commands

| Location | Use for |
|----------|---------|
| **Repository root** (`ngame/` or `NGAME-POC/`) | `git`, `pip install`, `run_training_flow.py`, config files, credentials |
| **`ngame_ui/`** subfolder | `python3 app-simple.py` / `python app-simple.py` (dashboard server only) |

After `cd` to the repo root, activate the virtual environment **once per Terminal / PowerShell session**:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Your prompt shows `(.venv)` when active. Dashboard logs (`GET /api/...`) in Terminal are normal — they mean the browser is refreshing, not an error.

---

## Appendix: Updating NGAME later

**macOS (Terminal, repo root):**

```bash
cd /path/to/ngame
git pull origin main
source .venv/bin/activate
```

**Windows (PowerShell, repo root):**

```powershell
cd C:\path\to\ngame
git pull origin main
.venv\Scripts\Activate.ps1
```

Restart the dashboard (sign out/in if auto-start runs it, or start `app-simple.py` from `ngame_ui/` once to test).

**Related docs (installer only)**

| Need | Document |
|------|----------|
| Dashboard URLs / UI issues | [ngame_ui/README.md](ngame_ui/README.md), [ngame_ui/TROUBLESHOOTING.md](ngame_ui/TROUBLESHOOTING.md) |
| Wave API (optional) | Copy `wave_config.example.json` → `wave_config.json`; token and business ID from [developer.waveapps.com](https://developer.waveapps.com) |
| FRP daily ops | [FRP_OPERATIONS_GUIDE.html](FRP_OPERATIONS_GUIDE.html) |

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
| `cd …` fails with path **`C:\Documents`** does not exist | PowerShell treated `"$env:USERPROFILE\Documents"` as an empty name. Use `$env:USERPROFILE` then `cd "$($env:USERPROFILE)\Documents"` (see [§ 3 — Clone](#3--clone)) |
| `destination path 'ngame' already exists…` | Rename or remove `Documents\ngame`, then `git clone` again (see [§ 3 — Clone](#3--clone)) |
| `cd $env:USERPROFILE\Documents` — “filename, directory name, or volume label syntax is incorrect” | Use **PowerShell** and: `cd "$($env:USERPROFILE)\Documents"` |
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
| QBO “didn’t connect” / auth error | [QuickBooks Online OAuth](#quickbooks-online): redirect URI `http://localhost:8000/callback`, sandbox admin login, re-run `run_data_extraction.py` |
| QBO / Wave token refresh (`invalid_grant`) | Re-run OAuth on surveillance PC ([Complete OAuth once](#complete-oauth-once-on-the-surveillance-machine)); refresh tokens in config JSON or `.env` |
| Terminal flooded with `GET /api/...` | Normal — dashboard auto-refresh; stop server with Ctrl+C when testing |

UI details: **[ngame_ui/TROUBLESHOOTING.md](ngame_ui/TROUBLESHOOTING.md)**.

---


---

*NGAME · Apache 2.0 · Copyright 2026 Ron Turner*
