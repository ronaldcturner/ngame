#!/usr/bin/env python3
"""
Canonical NGAME transaction-type names for the 18-element CPI / training matrix.

Matrix rows use underscore names (e.g. Bill_Payments).  Ontology classes and
QBO extraction often use camelCase without underscores (e.g. BillPayments).
resolve_cpi_coefficient() bridges the two when building matrix columns.
"""

from typing import Any, Dict, List, Optional

# 18-element ordering — must stay aligned across matrix, CPI, and sequence agents.
STANDARD_TRANSACTION_TYPES: List[str] = [
    'Customers', 'Recurring_payments', 'Invoices', 'Payments', 'Time_Activities',
    'Bills', 'Bill_Payments', 'Expenses', 'Bank_Transactions', 'Sales_transactions',
    'Products', 'PurchaseOrders', 'Recurring_Transactions', 'Contractors',
    'Mileage', 'ChartOfAccounts', 'EmployeePayroll',
    'Vendors',          # φ18 — high-risk fraud hot-spot
]

CPI_ARRAY_SIZE = len(STANDARD_TRANSACTION_TYPES)

# Master-data dimensions: dollar wCPI often mirrors count CPI ($1/entity placeholder).
# Dollar-weighted ranking/alerts are misleading for these unless wCPI diverges from CPI.
MASTER_DATA_TRANSACTION_TYPES = frozenset({
    'Customers',
    'Vendors',
    'Products',
    'ChartOfAccounts',
    'Contractors',
    'Mileage',
    'EmployeePayroll',
})

# Matrix row → ontology CPI coefficient keys (first match wins).
CPI_ONTOLOGY_ALIASES: Dict[str, List[str]] = {
    'Bank_Transactions': ['BankTransactions', 'BankDeposits', 'Bank_Transactions'],
    'Bill_Payments': ['BillPayments', 'Bill_Payments'],
    'Payments': ['CustomerPayments', 'Payments'],
    'Recurring_payments': ['RecurringPayments', 'Recurring_payments'],
    'Time_Activities': ['TimeActivities', 'TimeTracking', 'Time_Activities'],
    'Sales_transactions': [
        'SalesReceipts', 'Salestransactions', 'Sales_transactions',
    ],
    'Recurring_Transactions': ['RecurringTransactions', 'Recurring_Transactions'],
    'Expenses': ['Expenses', 'ExpenseTransaction'],
}


def ontology_lookup_keys(matrix_row: str) -> List[str]:
    """Candidate ontology keys for a matrix row, in priority order."""
    stripped = matrix_row.replace('_', '')
    keys = CPI_ONTOLOGY_ALIASES.get(matrix_row, [matrix_row, stripped])
    # Always try exact row name and de-underscored variant as fallbacks.
    extras = [matrix_row, stripped]
    seen = set()
    ordered: List[str] = []
    for k in keys + extras:
        if k not in seen:
            seen.add(k)
            ordered.append(k)
    return ordered


def resolve_cpi_coefficient(
    coefficients: Dict[str, Dict[str, Any]],
    matrix_row: str,
    default: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return CPI stats for a matrix row, resolving ontology name aliases."""
    fallback = default or {'cpi': 1.0, 'addition_rate': 0.0, 'deletion_rate': 0.0}
    for key in ontology_lookup_keys(matrix_row):
        if key in coefficients:
            return coefficients[key]
    return fallback


def resolve_weighted_cpi_coefficient(
    coefficients: Optional[Dict[str, Dict[str, Any]]],
    matrix_row: str,
    default: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return dollar-weighted CPI stats for a matrix row."""
    fallback = default or {'w_cpi': 1.0}
    if not coefficients:
        return fallback
    for key in ontology_lookup_keys(matrix_row):
        if key in coefficients:
            return coefficients[key]
    return fallback


def transaction_type_for_index(index: int) -> str:
    """1-based φ index → canonical matrix row name."""
    if 1 <= index <= len(STANDARD_TRANSACTION_TYPES):
        return STANDARD_TRANSACTION_TYPES[index - 1]
    return f"Unknown_{index}"


def is_actionable_anomaly(diff: Dict[str, Any]) -> bool:
    """True when a comparison row warrants FRP attention (not baseline noise)."""
    if diff.get("composite_alarm"):
        return True
    if (diff.get("deviation_level") or "").upper() in ("HIGH", "MEDIUM"):
        return True
    if (diff.get("dollar_alarm_level") or "").upper() in ("HIGH", "MEDIUM"):
        return True
    return False


def dollar_signal_duplicates_count(diff: Dict[str, Any], tx_type: str) -> bool:
    """True when dollar z-score adds no information beyond count churn."""
    if tx_type not in MASTER_DATA_TRANSACTION_TYPES:
        return False
    weighted = diff.get("weighted_cpi")
    today = diff.get("today_value")
    if weighted is None or today is None:
        return True
    return abs(float(weighted) - float(today)) < 1e-6
