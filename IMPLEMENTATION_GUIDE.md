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
  - [Switch from Track A to Track B](#switch-from-track-a-to-track-b)
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
| 7 | Startup folder auto-start at sign-in | [Windows — auto-start at login](#windows--auto-start-at-login) |
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

```powershell
cd "$($env:USERPROFILE)\Documents"
git clone https://github.com/ronaldcturner/ngame.git
cd ngame
```

After `cd`, the prompt should end in `\Documents`.

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

Configure **one** accounting source (Wave and/or QuickBooks). For QuickBooks, follow **only** the numbered **Do this** steps. Short **Background** notes sit under the step they belong to — skip them if you already know why.

### Wave (simplest)

**Do this**

```bash
# macOS
cp wave_config.example.json wave_config.json

# Windows PowerShell
Copy-Item wave_config.example.json wave_config.json
```

Edit `wave_config.json` — set `access_token` and `business_id` from [developer.waveapps.com](https://developer.waveapps.com).

Optional check (repo root, venv active): `python3 run_wave_extraction.py` (Windows: `python run_wave_extraction.py`).

### Choose your QuickBooks track

| Track | Use when | Then open |
|-------|----------|-----------|
| **A — Development / sandbox** | Practice, lab, or validate the PC before live books | [Track A cookbook](#quickbooks-online--track-a-development--sandbox) |
| **B — Customer Go-Live** | Customer’s live QBO ledger | [Track B cookbook](#quickbooks-online--track-b-customer-go-live) |

Software install (Python, clone, `.venv`, dashboard) is the same for both. Only Intuit keys, `environment`, company, and redirect URI change.

**Recommended at a customer site:** complete **Track A** to prove the PC works, then switch with [Switch from Track A to Track B](#switch-from-track-a-to-track-b) — no re-clone.

---

### QuickBooks Online — Track A (Development / sandbox)

<a id="quickbooks-online--track-a-development--sandbox"></a>

**Practice / sandbox only.** For the customer’s live ledger use **Track B**.

#### Track A — checklist before you start

- [ ] Intuit **Developer** access to the app (not only a bookkeeper QBO login)
- [ ] A **sandbox** company; you can sign in as **Company Admin** or **Master Admin**
- [ ] Current directory is the NGAME clone (path ends in `\ngame` or `/ngame`; `quickbooks_config.example.json` is present — check with `Get-Location` / `pwd` and `Get-Item` / `ls`)
- [ ] You can activate the venv when you reach **A4** (`.venv\Scripts\Activate.ps1` or `source .venv/bin/activate`) — not required until then

#### A1 — Create `quickbooks_config.json`

**Do this** (repo root):

```bash
# macOS
cp quickbooks_config.example.json quickbooks_config.json

# Windows PowerShell
Copy-Item quickbooks_config.example.json quickbooks_config.json
```

<details>
<summary><strong>Background — why this file exists</strong></summary>

NGAME does not store the bookkeeper’s QBO password. It uses OAuth 2.0 and saves **access** and **refresh** tokens in `quickbooks_config.json` on the surveillance PC. The dashboard can open without OAuth; **Run Training Day** / live QBO pulls cannot.

</details>

#### A2 — Register the Development redirect URI

**Do this**

1. Sign in at [developer.intuit.com](https://developer.intuit.com).
2. Open your app (e.g. Safe Landing).
3. Stay in **Development** (not Production).
4. Go to **Settings → Redirect URIs → Development** (or **Development → Keys & OAuth**).
5. **Add URI** exactly: `http://localhost:8000/callback`
6. Click **Save** on that row (often to the **right** of the field — scroll/widen if you only see the trash icon).
7. Refresh the page and confirm the URI is still listed.

Official reference: [Set app redirect URIs](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/set-redirect-uri).

<details>
<summary><strong>Background — two URLs (do not confuse them)</strong></summary>

| URL | Port | Role | Register in Intuit? |
|-----|------|------|---------------------|
| **http://localhost:5001/dashboard** | 5001 | NGAME web UI. FRP bookmark. | **No** |
| **http://localhost:8000/callback** | 8000 | OAuth callback after **Connect** | **Yes** (Development) |

Intuit only returns the browser to URIs you register. Mismatch → often *“Sorry, but [app] didn’t connect”*. Do **not** put localhost in the OAuth Playground-only URL field. Portal and config must agree on port **8000** (not 8080 unless you change both).

| Portal field | Use for NGAME? |
|--------------|----------------|
| **Redirect URIs → Development** | **Yes** — `http://localhost:8000/callback` |
| **Keys & credentials → Development** | **Yes** — Client ID / Secret |
| **Launch URL / Host Domain** | **No** |
| Playground RedirectUrl | **No** — leave unchanged |

</details>

#### A3 — Fill Development keys in the config

**Do this**

1. Open the file **`quickbooks_config.json`** in the repo root (Notepad, Cursor, etc.).  
   There is **no** separate file named `quickbooks_api`.
2. Inside that JSON file, find the block that starts with `"quickbooks_api": { ... }`.
3. Set these fields **inside** that block:

| Field | Value |
|-------|--------|
| `client_id` | **Development** Client ID |
| `client_secret` | **Development** Client Secret |
| `redirect_uri` | `http://localhost:8000/callback` (exact match to portal) |
| `environment` | `sandbox` |
| `realm_id`, `access_token`, `refresh_token` | Leave empty until OAuth |

4. Save the file (gitignored — stays on this PC only).

#### A4 — Complete OAuth once

**Do this** (repo root, venv active). Keep the session open until the browser shows success (listener on port **8000**, ~3 minutes).

```bash
# macOS
source .venv/bin/activate
python3 run_data_extraction.py

# Windows PowerShell
.venv\Scripts\Activate.ps1
python run_data_extraction.py
```

In the browser: sign in at the **sandbox** host, select the **sandbox** company, **Connect** / **Authorize** as Company/Master Admin.

**Success:** page shows **“NGAME: OAuth complete. You can close this tab.”** Config now has `access_token`, `refresh_token`, and `realm_id`.

<details>
<summary><strong>Background — sandbox login rules</strong></summary>

| Requirement | Detail |
|-------------|--------|
| Login host | [sandbox.qbo.intuit.com](https://sandbox.qbo.intuit.com) — not live qbo.intuit.com |
| Role | Company Admin or Master Admin (Standard users cannot finish app OAuth) |
| Bookkeepers / students | May use QBO UI; they do **not** run NGAME OAuth |
| Developer portal password | Do not give to students / FRP |

**Alternative:** with the dashboard running, **Run Training Day** can trigger the same OAuth flow if tokens are missing.

</details>

#### A5 — Verify Track A

**Do this**

| # | Check |
|---|--------|
| 1 | `quickbooks_config.json` has non-empty `access_token`, `refresh_token`, `realm_id` |
| 2 | `"environment": "sandbox"` |
| 3 | Start the dashboard (below), then open **http://localhost:5001/dashboard** |
| 4 | **Run Today's Training Day** (or **Run Training Day**) completes without Intuit “didn’t connect” |
| 5 | `NGAME_Training_Matrix.xlsx` appears or updates in repo root |

**Step 3 — start the dashboard** (repo root, venv active). Leave this window open:

```bash
# macOS
cd ngame_ui
python3 app-simple.py

# Windows PowerShell
cd ngame_ui
python app-simple.py
```

Then in a browser open **http://localhost:5001/dashboard**. Stop later with **Ctrl+C** in that Terminal/PowerShell window (Windows Startup-folder auto-start is a later cookbook step).

<details>
<summary><strong>Background — Track A troubleshooting</strong></summary>

| Symptom | Action |
|---------|--------|
| “[App] didn’t connect” | Portal Development URI = `http://localhost:8000/callback`; matches config; Save + refresh portal |
| “unique valid redirect URI” | URI already listed, or fix `8080` → `8000`; no trailing spaces |
| Only Playground URL visible | Wrong tab — use Redirect URIs → Development |
| Save button missing | Scroll right / widen window |
| URI reverts | You did not click Save |
| OAuth OK, training fails | Re-run extraction; confirm `realm_id` is the intended sandbox company |
| Callback timeout | Free port 8000; keep Terminal/PowerShell open |
| `invalid_grant` | Re-run A4 OAuth |

Diagram (dashboard → OAuth → API): see [How QBO fits the dashboard](#how-qbo-fits-the-dashboard).

</details>

**Track A done.**  
**Return to cookbook:** [← macOS Steps 1–9](#macos-cookbook) · [← Windows Steps 1–9](#windows-cookbook)  
**Next:** [Step 4 — macOS Ollama](#macos-ollama) or [Step 4 — Windows Ollama](#windows-ollama) (or [Step 6 — Dashboard](#start-manually-testing) if Ollama is already done).  
Later: [Switch from Track A to Track B](#switch-from-track-a-to-track-b).

---

### QuickBooks Online — Track B (Customer Go-Live)

<a id="quickbooks-online--track-b-customer-go-live"></a>

**Live customer ledger.** Do **not** use Development keys, `"sandbox"`, or a sandbox company here.

#### Track B — checklist before you start

- [ ] Customer approved read-only API access to live QBO
- [ ] Intuit **Developer** access; **Production** Client ID / Secret available
- [ ] **Company Admin** or **Master Admin** of the **live** company will click Connect
- [ ] Current directory is the NGAME clone (same checks as Track A checklist)
- [ ] OS install §§ 1–4 done; internet OK
- [ ] You will use a temporary **https** tunnel for OAuth (B3) — localhost is not allowed for Production

#### B1 — Create or reset `quickbooks_config.json` for Production

**Do this** (repo root):

```bash
# macOS
cp quickbooks_config.example.json quickbooks_config.json

# Windows PowerShell
Copy-Item quickbooks_config.example.json quickbooks_config.json
```

If switching from Track A, you may edit the existing file instead of copying — clear tokens (B1 table) and replace keys/`environment`/`redirect_uri`.

#### B2 — Fill Production keys (leave redirect for B3)

**Do this**

1. Open **`quickbooks_config.json`** in the repo root.  
   There is **no** separate file named `quickbooks_api`.
2. Find the `"quickbooks_api": { ... }` block inside that file.
3. Set these fields **inside** that block:

| Field | Value |
|-------|--------|
| `client_id` | **Production** Client ID |
| `client_secret` | **Production** Client Secret |
| `environment` | `production` |
| `redirect_uri` | Set in **B3** (https URI) |
| `realm_id`, `access_token`, `refresh_token` | Empty until OAuth |

4. Save the file.

#### B3 — Production https redirect + tunnel

**Do this**

1. Start a tunnel to local port **8000** (example: [ngrok](https://ngrok.com/) — `ngrok http 8000`).
2. Copy the tunnel **https** base URL (e.g. `https://<random>.ngrok-free.app`).
3. Intuit portal → app → **Settings → Redirect URIs → Production** → **Add URI** exactly: `https://<random>.ngrok-free.app/callback` → **Save** → refresh and confirm.
4. Open `quickbooks_config.json` → inside `"quickbooks_api"` set `redirect_uri` to that **same** https `…/callback` string.
5. Leave the tunnel **running** until B4 finishes.

<details>
<summary><strong>Background — why Production needs a tunnel</strong></summary>

Intuit Production redirect URIs must be **`https://`**, not localhost, and not a raw IP ([docs](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/set-redirect-uri)). NGAME listens on **`127.0.0.1:8000`**; the tunnel forwards public https → that port. After tokens exist, daily use is refresh-only — stop the tunnel. Do not paste Production URIs into Development-only fields or use the Playground URL as NGAME’s runtime `redirect_uri`.

</details>

#### B4 — Complete OAuth against the live company

**Do this** (tunnel still up; repo root; venv active):

```bash
# macOS
source .venv/bin/activate
python3 run_data_extraction.py

# Windows PowerShell
.venv\Scripts\Activate.ps1
python run_data_extraction.py
```

Browser: sign in at [qbo.intuit.com](https://qbo.intuit.com), select the **customer’s live company**, **Connect** as Company/Master Admin.

**Success:** “NGAME: OAuth complete…” and tokens/`realm_id` filled. Then **stop the tunnel**.

#### B5 — Verify Track B

**Do this**

| # | Check |
|---|--------|
| 1 | `"environment": "production"` and Production client id/secret |
| 2 | `realm_id` is the live company |
| 3 | Start the dashboard (same commands as [A5 step 3](#a5--verify-track-a)), then open **http://localhost:5001/dashboard** |
| 4 | **Run Today's Training Day** succeeds; matrix updates |
| 5 | Spot-check counts vs what the FRP/bookkeeper expects for **live** books |

<details>
<summary><strong>Background — go-live rules & re-auth</strong></summary>

| Requirement | Detail |
|-------------|--------|
| Login | Live QBO, not sandbox |
| Role | Company/Master Admin on the live company |
| Bookkeeper | Normal QBO use; no NGAME OAuth |
| FRP | Dashboard only after you finish OAuth + auto-start |
| Secrets | Stay on the surveillance PC |

If `invalid_grant` or the app is revoked: start tunnel again → match Production redirect in portal + config → re-run `run_data_extraction.py` → stop tunnel.

Sandbox training days are **not** the customer baseline — plan a fresh matrix for the live company after switching.

</details>

**Track B done.**  
**Return to cookbook:** [← macOS Steps 1–9](#macos-cookbook) · [← Windows Steps 1–9](#windows-cookbook)  
**Next:** [Step 6 — Dashboard](#start-manually-testing) (or [Step 7 — macOS LaunchAgent](#macos--auto-start-at-login) / [Step 7 — Windows Startup auto-start](#windows--auto-start-at-login) if the dashboard already runs).

---

### Switch from Track A to Track B

No re-clone or new `.venv`. After Track A proves the PC:

1. Follow **Track B** from [B1](#quickbooks-online--track-b-customer-go-live) (Production keys, https redirect, live OAuth).
2. Replace sandbox tokens; confirm `"environment": "production"`.
3. Verify with **B5** (live company).
4. Do **not** hand off the FRP while still on sandbox.

---

### How QBO fits the dashboard

<a id="how-qbo-fits-the-dashboard"></a>

```
FRP browser  →  http://localhost:5001/dashboard  (app-simple.py)
                      │
                      ├─ UI only: no Intuit redirect URI required
                      │
                      └─ Run Training Day / Run Churn Analysis
                             │
                             └─ ensure_quickbooks_auth()
                                    ├─ refresh token OR
                                    └─ browser OAuth → callback URI
                                           └─ tokens → QBO API (sandbox or production)
```

**Fast demo without live QBO:** `python3 run_training_flow.py --demo` (Windows: `python …`) replays saved matrix data — does not replace OAuth for live pulls.

Implementation: `ngame_quickbooks_oauth.py`, `quickbooks_config.example.json`.

### Environment variables

Optional: copy `.env.example` to `.env` and set variables listed there (`QBO_CLIENT_ID`, `QBO_CLIENT_SECRET`, `QBO_REDIRECT_URI`, `QBO_ENVIRONMENT`, etc.).

> **Security:** `wave_config.json`, `quickbooks_config.json`, and `.env` are in `.gitignore`. Keep them only on the surveillance machine.

---
**Return to cookbook:** [← macOS Steps 1–9](#macos-cookbook) · [← Windows Steps 1–9](#windows-cookbook)  
**Next:** [Step 4 — macOS Ollama](#macos-ollama) or [Step 4 — Windows Ollama](#windows-ollama)

## Dashboard service (required for FRP)

The FRP never uses Terminal for daily work. They use a **browser bookmark** to the dashboard, which you install and keep running.

**Your responsibilities:**

1. Run `app-simple.py` and confirm **http://localhost:5001/dashboard**
2. Auto-start at login (LaunchAgent / Windows Startup folder)
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
**Next:** [Step 7 — macOS LaunchAgent](#macos--auto-start-at-login) or [Step 7 — Windows Startup auto-start](#windows--auto-start-at-login)

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

**Goal:** After the FRP signs in to the surveillance PC, the dashboard starts by itself — no PowerShell window for the FRP to manage each morning.

**Primary method (use this):** Windows **Startup folder** + shipped launcher files at repository root.

| Item | Value |
|------|--------|
| **Batch file** | `start-dashboard.bat` (repo root) — starts the dashboard |
| **Silent launcher** | `start-dashboard-silent.vbs` (repo root) — runs the bat **without** a flashing console (recommended for Startup) |
| **Startup folder** | Press Win+R → type `shell:startup` → Enter |
| **Example install path** | `C:\Users\you\Documents\ngame\` |

Do **not** use Task Scheduler for a normal NGAME install (easy to confuse with other Soft Landing / Custom Handler tasks; path errors are common). Task Scheduler is optional/advanced only — see the end of this section.

**Before you start**

- [Start manually (testing)](#start-manually-testing) succeeded — **http://localhost:5001/dashboard** loads.
- You are in the **NGAME clone** on this PC (folder with `.venv`, `ngame_ui`, `start-dashboard.bat`) — not an iCloud/OneDrive **copy** of an old development tree.

#### Step 1 — Confirm launchers at repo root

In **PowerShell**:

```powershell
cd "$($env:USERPROFILE)\Documents\ngame"    # or your real clone path
Get-Location
Get-Item .\start-dashboard.bat
Get-Item .\start-dashboard-silent.vbs
New-Item -ItemType Directory -Force -Path ".\logs" | Out-Null
```

If either file is missing, run `git pull origin main` from this folder, or recreate them from the copies in this guide / the GitHub repo.

**What `start-dashboard.bat` does** (do **not** paste this into PowerShell — it already lives in the file):

```bat
@echo off
REM NGAME dashboard auto-start — place at repository root (ships with the repo).
REM Double-click to test; for login auto-start prefer start-dashboard-silent.vbs in shell:startup.
cd /d "%~dp0"
if not exist "logs" mkdir logs
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0ngame_ui"
"%~dp0.venv\Scripts\pythonw.exe" app-simple.py >> "%~dp0logs\dashboard.log" 2>> "%~dp0logs\dashboard.err.log"
```

**What `start-dashboard-silent.vbs` does:** runs that bat with a **hidden** window so the FRP does not see a console flash at sign-in.

#### Step 2 — Quick test the bat (once)

1. In File Explorer, open your NGAME folder.
2. Double-click **`start-dashboard.bat`**.
3. Wait ~10–15 seconds → open **http://localhost:5001/dashboard**.
4. If it loads, stop this test dashboard: **Ctrl+Shift+Esc** (Task Manager) → end **pythonw.exe** / **python.exe** if listed (they are processes, not files in a folder).

If the page does not load, read `logs\dashboard.err.log` before continuing.

#### Step 3 — Add the silent launcher to Startup (Do this)

1. Press **Win+R**, type `shell:startup`, press **Enter**.  
   This opens **your** Startup folder (not Task Scheduler).
2. Open a second Explorer window to your NGAME repo root (`Documents\ngame`).
3. **Right-click** `start-dashboard-silent.vbs` → **Show more options** (Windows 11) if needed → **Create shortcut**.
4. **Move** that shortcut into the Startup folder from step 1.
5. (Optional) Rename the shortcut to **`NGAME Dashboard`** (right-click → Rename). Do **not** rename the real `.vbs` / `.bat` files in the repo unless you know what you are doing.

**Alternate (console may flash):** put a shortcut to `start-dashboard.bat` in Startup instead of the `.vbs`. Prefer the `.vbs` for FRP machines.

#### Step 4 — Disable any NGAME Task Scheduler task

If you previously created a Task Scheduler task (e.g. **NGAME Dashboard**):

1. Open **Task Scheduler**.
2. Select that task → right-click → **Disable**.

Leave Soft Landing / other vendors’ tasks alone. NGAME auto-start should be **only** the Startup shortcut.

#### Step 5 — Verify at sign-in

1. Do **not** double-click the bat and do **not** click Run in Task Scheduler.
2. Sign **out** and sign **back in** (or reboot).
3. Wait **30–45 seconds** after the desktop appears (first sign-in can be slow).
4. Open **http://localhost:5001/dashboard** — it should load with no PowerShell and no manual start.

**If it fails**

| Check | How |
|--------|-----|
| Shortcut target | In `shell:startup`, right-click the shortcut → **Properties** → **Target** must be the **local** `…\Documents\ngame\start-dashboard-silent.vbs` (not an iCloud/dev copy) |
| Bat still works | Double-click `start-dashboard.bat` once |
| Logs | `Documents\ngame\logs\dashboard.err.log` |
| Processes | After sign-in, Task Manager may show **pythonw.exe** when the dashboard is up |

**Consultant fallback:** double-click `start-dashboard.bat` until Startup is fixed — do not leave that as the FRP’s daily workflow.

> Do **not** also run `ngame_dual_mode.py` on a schedule on the same machine if the FRP uses the dashboard — that can double-run the pipeline.

#### Optional — Task Scheduler (advanced; not recommended)

Prefer Startup (above). Use Task Scheduler only if site policy blocks Startup folders.

Requirements if you try it anyway:

- Task name: **`NGAME Dashboard`** (easy to find later)
- Trigger: **At log on** of the FRP’s Windows user (not **Daily**) — in Edit Trigger, field **Begin the task:**
- Action: **Start a program** only — **not** Custom Handler
- Program: `C:\Windows\System32\cmd.exe`
- Arguments: `/c ""C:\Users\you\Documents\ngame\start-dashboard.bat""` (exact real path; Browse to confirm)
- Start in: `C:\Users\you\Documents\ngame`
- General: **Run only when user is logged on**
- Delay 30 seconds on the logon trigger helps
- Do **not** edit Soft Landing / SoftLandingCreativeManagementTask tasks

`LastTaskResult` **2147942402** (`0x80070002`) means **file not found** — wrong path (often OneDrive/iCloud vs local Documents).

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
3. [ ] Auto-start configured (LaunchAgent or Windows Startup folder)
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
| `cd …` fails with path **`C:\Documents`** does not exist | Use `cd "$($env:USERPROFILE)\Documents"` (see [§ 3 — Clone](#3--clone)) — not `"$env:USERPROFILE\Documents"` |
| `destination path 'ngame' already exists…` | Rename or remove `Documents\ngame`, then `git clone` again (see [§ 3 — Clone](#3--clone)) |
| `cd $env:USERPROFILE\Documents` — “filename, directory name, or volume label syntax is incorrect” | Use **PowerShell** and: `cd "$($env:USERPROFILE)\Documents"` |
| `python3` / `python` not found | Reinstall Python; on Windows enable **Add to PATH** |
| `pip install` → *not a valid application for this OS platform* (Windows) | Use `python -m pip install ...` with venv active; see [§ 4 — Virtual environment](#4--virtual-environment) |
| `pip install` compiler error (Windows) | Install Microsoft C++ Build Tools; retry |
| PowerShell blocks venv activation | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Dashboard empty | Run one training or churn day from dashboard |
| FRP cannot connect | Check LaunchAgent / Windows Startup shortcut; read `logs/dashboard.err.log` |
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
