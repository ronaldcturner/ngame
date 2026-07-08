#!/usr/bin/env python3
"""
Split QBO extraction for φ14 Contractors vs φ18 Vendors.

Vendors (φ18): all Vendor master records — entity churn / new-vendor fraud.
Contractors (φ14): payment transactions (Purchases, Bill Payments, Bills) paid to
vendors flagged Vendor1099 in QuickBooks — 1099 contractor payment activity.
"""

from typing import Any, Dict, List, Optional, Set


def ref_id(ref: Optional[Dict[str, Any]]) -> Optional[str]:
    """Return the QBO Ref.value as a string, or None."""
    if not ref:
        return None
    val = ref.get("value")
    return str(val) if val is not None else None


def contractor_vendor_ids(vendors: List[Dict[str, Any]]) -> Set[str]:
    """Vendor IDs marked for 1099 tracking in QuickBooks."""
    ids: Set[str] = set()
    for vendor in vendors:
        flag = vendor.get("Vendor1099")
        if flag in (True, "true", "True", 1, "1"):
            ids.add(str(vendor.get("Id")))
    return ids


def _payment_record(
    source: str,
    record_id: Any,
    total_amt: Any,
    txn_date: Any,
    vendor_ref: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "Id": f"{source}-{record_id}",
        "TotalAmt": total_amt,
        "TxnDate": txn_date,
        "VendorRef": vendor_ref,
        "_contractor_source": source,
    }


def build_contractor_payment_records(
    contractor_ids: Set[str],
    purchases: Optional[List[Dict[str, Any]]] = None,
    bill_payments: Optional[List[Dict[str, Any]]] = None,
    bills: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Build contractor CPI records from payment transactions to 1099 vendors.
    URIs use prefixed IDs so Purchases and BillPayments never collide.
    """
    if not contractor_ids:
        return []

    records: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    def _add(source: str, record_id: Any, payload: Dict[str, Any]) -> None:
        key = f"{source}-{record_id}"
        if key in seen:
            return
        seen.add(key)
        records.append(
            _payment_record(
                source,
                record_id,
                payload.get("TotalAmt"),
                payload.get("TxnDate"),
                payload.get("VendorRef") or payload.get("EntityRef"),
            )
        )

    for purchase in purchases or []:
        vendor_id = ref_id(purchase.get("EntityRef"))
        if vendor_id and vendor_id in contractor_ids and purchase.get("Id") is not None:
            _add("purchase", purchase["Id"], purchase)

    for bill_payment in bill_payments or []:
        vendor_id = ref_id(bill_payment.get("VendorRef"))
        if vendor_id and vendor_id in contractor_ids and bill_payment.get("Id") is not None:
            _add("billpayment", bill_payment["Id"], bill_payment)

    for bill in bills or []:
        vendor_id = ref_id(bill.get("VendorRef"))
        if vendor_id and vendor_id in contractor_ids and bill.get("Id") is not None:
            _add("bill", bill["Id"], bill)

    return records
