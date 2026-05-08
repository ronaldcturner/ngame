# NGAME + WAVE Accounting (GraphQL API)

This document describes how to run NGAME with **WAVE** as the accounting data source using the **Wave GraphQL API** (often used via GraphiQL or the API Playground).

## Overview

- **Data source**: WAVE accounting product  
- **API**: Wave GraphQL API at `https://gql.waveapps.com/graphql/public`  
- **Auth**: Bearer token (no OAuth flow in this implementation)

The same Phase I pipeline is used: extract data → build ontology → write `wave_ontology_Today.ttl`. Downstream Phase II (CPI analysis, fraud detection) uses that TTL as before.

## Setup

### 1. Wave API access

- Create an application in the [Wave Developer Portal](https://developer.waveapps.com/) and obtain an **access token**.
- Determine your **Business ID** (e.g. from the API Playground or `businesses` query).

### 2. Config file

Copy the example and fill in your values:

```bash
cp wave_config.example.json wave_config.json
```

Edit `wave_config.json`:

```json
{
  "wave_graphql": {
    "endpoint": "https://gql.waveapps.com/graphql/public",
    "access_token": "YOUR_WAVE_ACCESS_TOKEN",
    "business_id": "YOUR_BUSINESS_ID"
  }
}
```

- **Do not** commit `wave_config.json` if it contains real tokens; keep it in `.gitignore` if needed.

### 3. Curated transaction types

The same `Curated Transaction Types.ttl` file is used. WAVE currently fills:

- **Customers** – from `business.customers`
- **Invoices** – from `business.invoices`
- **Vendors** – from `business.vendors`
- **ChartOfAccounts** – from `business.accounts`
- **Products** / **Products_and_Services** – from `business.products`

Other types (e.g. Bills, Bill_Payments, Expenses) are left as empty lists until Wave supports them or we add more queries.

## Running extraction (WAVE)

Use the data extraction agent with `source="wave"`:

```python
from ngame_data_extraction_agent import NGameDataExtractionAgent, SOURCE_WAVE

agent = NGameDataExtractionAgent(source=SOURCE_WAVE)
result = agent.extract_daily_data()

if result["success"]:
    print("TTL file:", result["ttl_file"])  # wave_ontology_Today.ttl
    print("Records:", result["extraction_stats"]["total_records"])
else:
    print("Error:", result["error"])
```

From the command line you can run a small script that uses `SOURCE_WAVE` and calls `extract_daily_data()`.

## Output files (WAVE)

- `wave_ontology_Today.ttl` – current snapshot (same Turtle/ontology shape as QuickBooks run).
- `wave_ontology_Yesterday.ttl` – previous run (after the next extraction).

QuickBooks files (`quickbooks_ontology_*.ttl`) are unchanged when using the WAVE source.

## GraphQL (GraphiQL) usage

Wave’s API is GraphQL. You can:

- Use the [Wave API Playground](https://developer.waveapps.com/hc/en-us/articles/360018937431-API-Playground) or any GraphiQL client.
- Point the client at `https://gql.waveapps.com/graphql/public` and send a `Bearer <access_token>` in the `Authorization` header.

The NGAME WAVE client in `ngame_wave_graphql_client.py` runs a single business-scoped query that requests `business(id) { customers, invoices, vendors, accounts, products }` with pagination and normalizes the result for the ontology builder.

## Dependencies

- `requests` (for HTTP to the GraphQL endpoint)

No QuickBooks or Intuit libraries are required when using `source=SOURCE_WAVE`.
