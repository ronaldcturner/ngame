# NGAME User Interface (`ngame_ui`)

Web UI for the **NGAME-POC** project. This folder ships two Flask apps; only one matches what this repository actually contains today.

## Which app to run

| File | Purpose | Parent-directory Python modules? |
|------|---------|----------------------------------|
| **`app-simple.py`** | **Recommended.** Dashboard + consolidated NGAME run data from JSON artifacts. Works without optional imports. | **No** (optional try/except only) |
| **`app.py`** | Full demo: Socket.IO + optional `NGAMEOntologyWorkflow` and QuickBooks helpers. | **Yes** — those modules are **not** in the NGAME-POC repo root (see below). |

Run from **`ngame_ui`** so Flask finds `templates/` and the parent directory is **`NGAME-POC`** (for artifact paths).

## Prerequisites (accurate for this repo)

### Always

- **Python 3.10+** (match the main NGAME README).
- Install dependencies (minimal UI):

  ```bash
  cd ngame_ui
  pip install -r requirements-minimal.txt
  ```

  For `app.py` (Socket.IO stack):

  ```bash
  pip install -r requirements.txt
  ```

### For `app-simple.py` consolidated dashboard / debug

The UI reads NGAME outputs from the **repository root** (`..` relative to `ngame_ui`), with fallbacks under `../GENERATED_FILES/` when present.

**Files used (first match wins per category):**

- `management_dashboard.json`
- Fraud analysis (one of): `NGAME_Fraud_Analysis_readable_truly_clean.json`, `NGAME_Fraud_Analysis_readable_clean.json`, `NGAME_Fraud_Analysis_readable.json`, `NGAME_Fraud_Analysis.json`

These are **produced by the NGAME pipeline** (e.g. `run_fraud_analysis.py` / `ngame_fraud_analysis_flow_manager.py`), not shipped as static prerequisites. If they are missing, the dashboard shows empty or default content; `/dashboard-debug` shows what loaded.

**You do not need** `ngame_ontology_workflow.py` or QuickBooks extractor modules in the parent directory for `app-simple.py`.

### Optional / legacy (`app.py` only)

The older README listed these in the **parent** directory:

- `ngame_ontology_workflow.py`
- `quickbooks_chart_of_accounts_extractor.py`
- `quickbooks_chart_of_accounts_creator.py`
- `ontology_based_anomaly_agents.py`

In **NGAME-POC** they are **not** in the project root. Similar names may appear under `SCRAP/` or `Recovered SCRAP/` for reference only. **`app.py` will not import successfully** unless you add compatible modules next to `ngame_ui` or adjust `sys.path` and code. Use **`app-simple.py`** unless you are restoring that stack.

Config files that **do** exist at repo root (for the main pipeline, not strictly for `app-simple.py`) include e.g. `quickbooks_config.json`, `ngame_ontology_config.json` — see the main project README.

## Quick start (`app-simple.py`)

```bash
cd ngame_ui
python3 app-simple.py
```

- **Dashboard:** http://localhost:5001/dashboard  
- **Debug (raw JSON + artifact sources):** http://localhost:5001/dashboard-debug  
- **API:** `GET /api/consolidated-dashboard`, `GET /api/dashboard-stats`, `GET /api/socketio-enabled`  

Open the UI via these URLs (not by opening `.html` files directly), or browser fetches to `/api/*` will fail.

## Quick start (`app.py`, optional)

Requires `requirements.txt` and the optional parent modules if you use workflow/QuickBooks routes.

```bash
cd ngame_ui
python3 app.py
```

Default listen is **port 5001** in this project’s `app.py` (check the file if yours differs).

## Features (current POC)

- **Dashboard:** Overall risk, management warnings, top anomalies — from consolidated JSON when available.
- **Dashboard debug:** Raw `/api/consolidated-dashboard` payload, artifact paths, loader errors.
- **Analysis / QuickBooks pages:** Presentational / demo; full backend wiring depends on optional modules not in repo root.
- **Socket.IO:** Used by `app.py`. `app-simple.py` exposes `/api/socketio-enabled` as `false` so the templates do not spam missing `/socket.io` routes.

## Theming

Primary accent is **`#2CA01C`** (see `:root --primary-color` and body gradient in `templates/dashboard.html`, `analysis.html`, `quickbooks.html`).

## API (subset)

| Method | Path | Notes |
|--------|------|--------|
| GET | `/api/consolidated-dashboard` | Merged view + `sources` for files read |
| GET | `/api/dashboard-stats` | In-memory UI stats |
| GET | `/api/socketio-enabled` | `{ "enabled": true|false }` |
| POST | `/api/initialize` | Depends on app mode |

## Troubleshooting

- **Import errors when running `app.py`:** Use `app-simple.py`, or copy/restore the optional modules into the parent directory and fix imports.
- **Debug page blank:** Use `http://localhost:5001/dashboard-debug`, not a `file://` path.
- **Port in use:** Change the port in `app-simple.py` / `app.py` `app.run(...)` / `socketio.run(...)`, or stop the other process.

## License

See the main project or repository license file if present.
