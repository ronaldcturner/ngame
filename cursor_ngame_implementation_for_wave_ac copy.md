# NGAME implementation for WAVE accounting
_Exported on 2/27/2026 at 17:25:47 PST from Cursor (2.4.37)_

---

**User**

Can you support a new implementation of NGAME for the WAVE accounting product using the GraphiQL API?

---

**Cursor**

Exploring the codebase to understand the NGAME implementation and how we can add WAVE accounting support via GraphQL.


Exploring the project structure and how NGAME integrates with data sources/APIs:


Reading the data extraction agent and config to determine the data contract and how we can add a WAVE GraphQL path.


Checking the curated transaction types and phase1 director usage so we can add a WAVE/GraphQL data source.


Implementing WAVE GraphQL support: adding a WAVE GraphQL client and integrating it into the data extraction flow.


Creating the WAVE GraphQL client and config, then integrating it into the data extraction agent.


Refactoring the data extraction agent to support `source=quickbooks` and `source=wave`, and ensuring the WAVE client's result is merged with all curated transaction-type keys.


Fixing the Wave client: the GraphQL query uses variables for page but the query string embeds page size. Checking the query and fixing pagination.


Removing dead code from the Wave client and adding a short README for the WAVE integration.


Adding a CLI script to run WAVE extraction and syncing ESSENTIAL_FILES.


Updating ESSENTIAL_FILES to match the refactored data extraction agent.


Summary of what’s in place for **NGAME with WAVE accounting using the GraphQL (GraphiQL) API**:

## 1. **WAVE GraphQL client** (`ngame_wave_graphql_client.py`)
- Calls Wave at `https://gql.waveapps.com/graphql/public` with a Bearer token.
- Single business-scoped query with pagination for:
  - **Customers**, **Invoices**, **Vendors**, **Accounts** (chart of accounts), **Products**
- Normalizes Wave responses into the same shape the rest of NGAME expects (e.g. `Id`, `Name`, `CompanyName`, `TxnDate`, `TotalAmt`, `Balance`, `DocNumber`, etc.) so the existing ontology and TTL logic can be reused.

## 2. **Config** (`wave_config.example.json`)
- Example config with `wave_graphql.endpoint`, `access_token`, and `business_id`.
- Copy to `wave_config.json` and set your token and business ID.

## 3. **Data extraction agent** (QuickBooks + WAVE)
- **`ngame_data_extraction_agent.py`** (root and `ESSENTIAL_FILES/`):
  - `NGameDataExtractionAgent(source="quickbooks")` — default, unchanged behavior.
  - `NGameDataExtractionAgent(source="wave")` — uses WAVE GraphQL only (no QuickBooks auth).
- For **WAVE**, the agent:
  - Reads `wave_config.json`
  - Uses `NGameWaveGraphQLClient` to fetch and normalize data
  - Builds the same ontology and writes **`wave_ontology_Today.ttl`** (and rotates to `wave_ontology_Yesterday.ttl` on the next run).

## 4. **Runner script** (`run_wave_extraction.py`)
- Runs Phase I with WAVE only:
  - `python run_wave_extraction.py`
- Requires `wave_config.json` and `Curated Transaction Types.ttl`.

## 5. **Docs** (`NGAME_WAVE_GRAPHQL_README.md`)
- Setup (Wave app, token, business ID, config).
- Which curated types are filled from Wave (Customers, Invoices, Vendors, ChartOfAccounts, Products).
- How to use the agent with `SOURCE_WAVE` and how to use GraphiQL/Playground.

**Usage (WAVE):**
1. Copy `wave_config.example.json` to `wave_config.json` and set `access_token` and `business_id`.
2. Run:
   - **CLI:** `python run_wave_extraction.py`
   - **Code:**  
     `agent = NGameDataExtractionAgent(source=SOURCE_WAVE)`  
     `result = agent.extract_daily_data()`
3. Use `wave_ontology_Today.ttl` (and `Yesterday`) in your existing Phase II / phi / fraud analysis as before.

**Dependency:** `requests` (for the GraphQL HTTP calls). No QuickBooks/Intuit libraries are required when using `source="wave"`.

