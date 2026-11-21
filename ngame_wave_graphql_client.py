#!/usr/bin/env python3
"""
NGAME WAVE GraphQL Client
Fetches accounting data from the WAVE product via its GraphQL API (GraphiQL)
and normalizes responses to the same shape expected by NGAME ontology construction.
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Default page size for paginated Wave API
DEFAULT_PAGE_SIZE = 100


# GraphQL query to fetch business-scoped data (customers, invoices, vendors, accounts, products)
BUSINESS_DATA_QUERY = """
query WaveBusinessData($businessId: ID!, $customersPage: Int, $invoicesPage: Int, $vendorsPage: Int, $accountsPage: Int, $productsPage: Int) {
  business(id: $businessId) {
    id
    name
    customers(page: $customersPage, pageSize: %d) {
      edges { node {
        id name email firstName lastName displayId phone mobile
        address { addressLine1 addressLine2 city postalCode }
        outstandingAmount { value } overdueAmount { value }
        isArchived createdAt modifiedAt
      }}
      pageInfo { currentPage totalPages totalCount }
    }
    invoices(page: $invoicesPage, pageSize: %d) {
      edges { node {
        id invoiceNumber title status invoiceDate dueDate
        total { value } amountDue { value } amountPaid { value }
        customer { id name }
        createdAt modifiedAt
      }}
      pageInfo { currentPage totalPages totalCount }
    }
    vendors(page: $vendorsPage, pageSize: %d) {
      edges { node {
        id name email address { addressLine1 city postalCode }
        isArchived createdAt modifiedAt
      }}
      pageInfo { currentPage totalPages totalCount }
    }
    accounts(page: $accountsPage, pageSize: %d) {
      edges { node {
        id name description displayId type { value } subtype { value }
        balance { value } balanceInBusinessCurrency { value }
        isArchived
      }}
      pageInfo { currentPage totalPages totalCount }
    }
    products(page: $productsPage, pageSize: %d) {
      edges { node {
        id name description unitPrice { value } defaultSalesTaxes { id }
        isSold isBought isArchived
      }}
      pageInfo { currentPage totalPages totalCount }
    }
  }
}
""" % (
    DEFAULT_PAGE_SIZE,
    DEFAULT_PAGE_SIZE,
    DEFAULT_PAGE_SIZE,
    DEFAULT_PAGE_SIZE,
    DEFAULT_PAGE_SIZE,
)


def _money_value(m: Optional[Dict]) -> Optional[float]:
    if m is None:
        return None
    v = m.get("value")
    return float(v) if v is not None else None


def _date_str(d: Optional[str]) -> Optional[str]:
    return d[:10] if d and len(d) >= 10 else d


def normalize_customer(node: Dict) -> Dict:
    """Map Wave Customer to NGAME/QuickBooks-shaped dict."""
    name = node.get("name") or ""
    if not name and (node.get("firstName") or node.get("lastName")):
        name = " ".join(filter(None, [node.get("firstName"), node.get("lastName")]))
    return {
        "Id": node.get("id"),
        "Name": name or "Unknown",
        "CompanyName": node.get("name") or name,
        "PrimaryEmailAddr": node.get("email"),
        "PrimaryPhone": node.get("phone") or node.get("mobile"),
        "Balance": _money_value(node.get("outstandingAmount")),
        "Active": not node.get("isArchived", False),
    }


def normalize_invoice(node: Dict) -> Dict:
    """Map Wave Invoice to NGAME/QuickBooks-shaped dict."""
    return {
        "Id": node.get("id"),
        "DocNumber": node.get("invoiceNumber"),
        "Name": node.get("title"),
        "TxnDate": _date_str(node.get("invoiceDate")),
        "TotalAmt": _money_value(node.get("total")),
        "Balance": _money_value(node.get("amountDue")),
        "AmountPaid": _money_value(node.get("amountPaid")),
    }


def normalize_vendor(node: Dict) -> Dict:
    """Map Wave Vendor to NGAME/QuickBooks-shaped dict."""
    return {
        "Id": node.get("id"),
        "Name": node.get("name") or "Unknown",
        "CompanyName": node.get("name"),
        "PrimaryEmailAddr": node.get("email"),
        "Active": not node.get("isArchived", False),
    }


def normalize_account(node: Dict) -> Dict:
    """Map Wave Account (Chart of Accounts) to NGAME-shaped dict."""
    return {
        "Id": node.get("id"),
        "Name": node.get("name"),
        "Description": node.get("description"),
        "DocNumber": node.get("displayId"),
        "Balance": _money_value(node.get("balance")) or _money_value(node.get("balanceInBusinessCurrency")),
        "Active": not node.get("isArchived", False),
    }


def normalize_product(node: Dict) -> Dict:
    """Map Wave Product to NGAME/QuickBooks-shaped dict."""
    return {
        "Id": node.get("id"),
        "Name": node.get("name") or "Unknown",
        "Description": node.get("description"),
        "UnitPrice": _money_value(node.get("unitPrice")),
        "Active": not node.get("isArchived", False),
    }


class NGameWaveGraphQLClient:
    """
    Client for WAVE accounting GraphQL API.
    Fetches business data and returns it normalized for NGAME ontology construction.
    """

    def __init__(self, endpoint: str, access_token: str, business_id: str):
        self.endpoint = endpoint.rstrip("/")
        self.access_token = access_token
        self.business_id = business_id
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        })

    def _execute(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        resp = self.session.post(self.endpoint, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data and data["errors"]:
            raise RuntimeError("GraphQL errors: " + json.dumps(data["errors"], indent=2))
        return data.get("data") or {}

    def fetch_all_business_data(self) -> Dict[str, List[Dict]]:
        """
        Fetch customers, invoices, vendors, accounts, and products (all pages)
        and return normalized dict keyed by NGAME transaction type (lowercase).
        """
        result = {}
        # Single-query fetch for first page to get structure; then we paginate per entity
        variables = {
            "businessId": self.business_id,
            "customersPage": 1,
            "invoicesPage": 1,
            "vendorsPage": 1,
            "accountsPage": 1,
            "productsPage": 1,
        }
        try:
            data = self._execute(BUSINESS_DATA_QUERY, variables)
        except Exception as e:
            logger.exception("Wave GraphQL request failed")
            raise

        business = data.get("business") or {}
        if not business:
            logger.warning("No business returned; check business_id and token scope")

        # Customers
        customers_conn = business.get("customers") or {}
        customers_raw = [e.get("node") for e in (customers_conn.get("edges") or []) if e.get("node")]
        page_info = customers_conn.get("pageInfo") or {}
        total_pages = page_info.get("totalPages") or 1
        for p in range(2, total_pages + 1):
            v = {"businessId": self.business_id, "customersPage": p, "invoicesPage": 1, "vendorsPage": 1, "accountsPage": 1, "productsPage": 1}
            d = self._execute(BUSINESS_DATA_QUERY, v)
            b = d.get("business") or {}
            c = b.get("customers") or {}
            for e in c.get("edges") or []:
                if e.get("node"):
                    customers_raw.append(e["node"])
        result["customers"] = [normalize_customer(n) for n in customers_raw]

        # Invoices
        invoices_conn = business.get("invoices") or {}
        invoices_raw = [e.get("node") for e in (invoices_conn.get("edges") or []) if e.get("node")]
        page_info = invoices_conn.get("pageInfo") or {}
        total_pages = page_info.get("totalPages") or 1
        for p in range(2, total_pages + 1):
            v = {"businessId": self.business_id, "customersPage": 1, "invoicesPage": p, "vendorsPage": 1, "accountsPage": 1, "productsPage": 1}
            d = self._execute(BUSINESS_DATA_QUERY, v)
            b = d.get("business") or {}
            inv = b.get("invoices") or {}
            for e in inv.get("edges") or []:
                if e.get("node"):
                    invoices_raw.append(e["node"])
        result["invoices"] = [normalize_invoice(n) for n in invoices_raw]

        # Vendors
        vendors_conn = business.get("vendors") or {}
        vendors_raw = [e.get("node") for e in (vendors_conn.get("edges") or []) if e.get("node")]
        page_info = vendors_conn.get("pageInfo") or {}
        total_pages = page_info.get("totalPages") or 1
        for p in range(2, total_pages + 1):
            v = {"businessId": self.business_id, "customersPage": 1, "invoicesPage": 1, "vendorsPage": p, "accountsPage": 1, "productsPage": 1}
            d = self._execute(BUSINESS_DATA_QUERY, v)
            b = d.get("business") or {}
            vconn = b.get("vendors") or {}
            for e in vconn.get("edges") or []:
                if e.get("node"):
                    vendors_raw.append(e["node"])
        result["vendors"] = [normalize_vendor(n) for n in vendors_raw]

        # Accounts (Chart of Accounts)
        accounts_conn = business.get("accounts") or {}
        accounts_raw = [e.get("node") for e in (accounts_conn.get("edges") or []) if e.get("node")]
        page_info = accounts_conn.get("pageInfo") or {}
        total_pages = page_info.get("totalPages") or 1
        for p in range(2, total_pages + 1):
            v = {"businessId": self.business_id, "customersPage": 1, "invoicesPage": 1, "vendorsPage": 1, "accountsPage": p, "productsPage": 1}
            d = self._execute(BUSINESS_DATA_QUERY, v)
            b = d.get("business") or {}
            a = b.get("accounts") or {}
            for e in a.get("edges") or []:
                if e.get("node"):
                    accounts_raw.append(e["node"])
        result["chartofaccounts"] = [normalize_account(n) for n in accounts_raw]

        # Products
        products_conn = business.get("products") or {}
        products_raw = [e.get("node") for e in (products_conn.get("edges") or []) if e.get("node")]
        page_info = products_conn.get("pageInfo") or {}
        total_pages = page_info.get("totalPages") or 1
        for p in range(2, total_pages + 1):
            v = {"businessId": self.business_id, "customersPage": 1, "invoicesPage": 1, "vendorsPage": 1, "accountsPage": 1, "productsPage": p}
            d = self._execute(BUSINESS_DATA_QUERY, v)
            b = d.get("business") or {}
            pr = b.get("products") or {}
            for e in pr.get("edges") or []:
                if e.get("node"):
                    products_raw.append(e["node"])
        result["products"] = [normalize_product(n) for n in products_raw]
        result["products_and_services"] = result["products"]

        logger.info(
            "Wave data fetched: %d customers, %d invoices, %d vendors, %d accounts, %d products",
            len(result["customers"]),
            len(result["invoices"]),
            len(result["vendors"]),
            len(result["chartofaccounts"]),
            len(result["products"]),
        )
        return result


def default_wave_config_path() -> str:
    """Path to WAVE JSON config; override with WAVE_CONFIG_PATH or NGAME_WAVE_CONFIG."""
    p = (os.getenv("WAVE_CONFIG_PATH") or os.getenv("NGAME_WAVE_CONFIG") or "wave_config.json").strip()
    return p or "wave_config.json"


def load_wave_config(config_path: str = "wave_config.json") -> Dict[str, Any]:
    """Load WAVE GraphQL config from JSON file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"WAVE config not found: {config_path!r}. Copy wave_config.example.json to wave_config.json "
            "or set WAVE_CONFIG_PATH / NGAME_WAVE_CONFIG."
        ) from e
