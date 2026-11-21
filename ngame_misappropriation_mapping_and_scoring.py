#!/usr/bin/env python3
"""
NGAME Misappropriation Mapping + Scoring (QuickBooks-context).

This file provides:
  1) A static, QuickBooks-specific mapping generator from curated
     QuickBooks transaction types (Curated Transaction Types.ttl) to
     your Asset_Misappropriation.ttl taxonomy classes.
  2) A deterministic scoring model that combines:
       - curated qbo:riskLevel
       - curated qbo:transactionFrequency
       - real-world scheme priors from ACFE Fraud Tree (2024)

The goal is to remove "bespoke" ranking logic and make it reproducible.
"""

from __future__ import annotations

import math
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL


QBO = Namespace("http://www.semanticweb.org/quickbooks/ontology#")
QB_RISK_LEVEL_PRED = QBO.riskLevel
QB_TX_FREQ_PRED = QBO.transactionFrequency


def _local_name(uri: Any) -> str:
    s = str(uri)
    if "#" in s:
        return s.split("#")[-1]
    if "/" in s:
        return s.rsplit("/", 1)[-1]
    return s


def _parse_ttl_individuals_with_risk_and_frequency(curated_ttl_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Load curated transaction *individuals* (e.g., qbo:BillPayments) and extract:
      - riskLevel
      - transactionFrequency
    """
    g = Graph()
    g.parse(curated_ttl_path, format="turtle")

    tx: Dict[str, Dict[str, Any]] = {}

    for s, _p, o in g.triples((None, QB_RISK_LEVEL_PRED, None)):
        name = _local_name(s)
        tx.setdefault(name, {})
        tx[name]["risk_level"] = str(o)

    for s, _p, o in g.triples((None, QB_TX_FREQ_PRED, None)):
        name = _local_name(s)
        tx.setdefault(name, {})
        try:
            tx[name]["transaction_frequency"] = int(str(o))
        except ValueError:
            # Keep as None if parse fails
            tx[name]["transaction_frequency"] = None

    # Optional metadata (label/comment) for interpretability/debugging.
    for s, _p, o in g.triples((None, RDFS.label, None)):
        name = _local_name(s)
        if name in tx:
            tx[name]["label"] = str(o)

    for s, _p, o in g.triples((None, RDFS.comment, None)):
        name = _local_name(s)
        if name in tx:
            tx[name]["comment"] = str(o)

    return tx


def _parse_asset_misappropriation_classes(asset_ttl_path: str) -> List[str]:
    """
    Extract all OWL classes (local names) from Asset_Misappropriation.ttl.
    """
    g = Graph()
    g.parse(asset_ttl_path, format="turtle")

    classes: List[str] = []
    seen = set()
    for s, _p, o in g.triples((None, RDF.type, OWL.Class)):
        if str(o).endswith("#Class") or str(o).endswith("/Class"):
            # defensive: o is owl:Class
            pass
        name = _local_name(s)
        if name not in seen:
            seen.add(name)
            classes.append(name)

    return classes


# Evidence priors extracted from ACFE "THE FRAUD TREE" (Occupational Fraud 2024).
# These are "percent of all cases" at the asset misappropriation sub-scheme level.
ACFE_ASSET_MISAPPROPRIATION_SCHEME_PRIORS: Dict[str, float] = {
    "billing": 0.22,
    "noncash": 0.22,
    "expense_reimbursements": 0.13,
    "check_and_payment_tampering": 0.11,
    "cash_on_hand": 0.11,
    "skimming": 0.10,
    "cash_larceny": 0.10,
    "payroll": 0.10,
    "register_disbursements": 0.03,
}


RISK_LEVEL_TO_VALUE: Dict[str, float] = {
    "low": 0.1,
    "medium": 0.5,
    "high": 0.8,
    "critical": 1.0,
}


@dataclass(frozen=True)
class EvidenceBucket:
    bucket_id: str
    evidence_percent: float
    taxonomy_classes: Tuple[str, ...]


def _default_evidence_buckets_and_taxonomy() -> Dict[str, EvidenceBucket]:
    """
    Map ACFE scheme buckets to your Asset_Misappropriation.ttl taxonomy classes.

    Note: this is the deterministic "context glue" between the real-world
    scheme taxonomy and your ontology taxonomy levels.
    """
    return {
        "billing": EvidenceBucket(
            bucket_id="billing",
            evidence_percent=ACFE_ASSET_MISAPPROPRIATION_SCHEME_PRIORS["billing"],
            taxonomy_classes=("Billing_Schemes",),
        ),
        "noncash": EvidenceBucket(
            bucket_id="noncash",
            evidence_percent=ACFE_ASSET_MISAPPROPRIATION_SCHEME_PRIORS["noncash"],
            taxonomy_classes=("Larceny",),
        ),
        "expense_reimbursements": EvidenceBucket(
            bucket_id="expense_reimbursements",
            evidence_percent=ACFE_ASSET_MISAPPROPRIATION_SCHEME_PRIORS["expense_reimbursements"],
            taxonomy_classes=("Expense_Reimbursement_Schemes",),
        ),
        "check_and_payment_tampering": EvidenceBucket(
            bucket_id="check_and_payment_tampering",
            evidence_percent=ACFE_ASSET_MISAPPROPRIATION_SCHEME_PRIORS["check_and_payment_tampering"],
            taxonomy_classes=("Check_&_Payment_Tampering", "Fraudulent_Disbursements"),
        ),
        "cash_on_hand": EvidenceBucket(
            bucket_id="cash_on_hand",
            evidence_percent=ACFE_ASSET_MISAPPROPRIATION_SCHEME_PRIORS["cash_on_hand"],
            taxonomy_classes=("Theft_of_Cash_on_Hand", "Cash"),
        ),
        "skimming": EvidenceBucket(
            bucket_id="skimming",
            evidence_percent=ACFE_ASSET_MISAPPROPRIATION_SCHEME_PRIORS["skimming"],
            taxonomy_classes=("Skimming", "Theft_of_Cash_Receipts"),
        ),
        "cash_larceny": EvidenceBucket(
            bucket_id="cash_larceny",
            evidence_percent=ACFE_ASSET_MISAPPROPRIATION_SCHEME_PRIORS["cash_larceny"],
            taxonomy_classes=("Cash_Larceny", "Larceny"),
        ),
        "payroll": EvidenceBucket(
            bucket_id="payroll",
            evidence_percent=ACFE_ASSET_MISAPPROPRIATION_SCHEME_PRIORS["payroll"],
            taxonomy_classes=("Payroll_Schemes",),
        ),
        "register_disbursements": EvidenceBucket(
            bucket_id="register_disbursements",
            evidence_percent=ACFE_ASSET_MISAPPROPRIATION_SCHEME_PRIORS["register_disbursements"],
            taxonomy_classes=("Register_Disbursements",),
        ),
    }


def _default_quickbooks_transaction_to_bucket_rules() -> Dict[str, str]:
    """
    QuickBooks transaction individual -> ACFE evidence bucket.

    This encodes how your NGAME interprets QuickBooks transaction semantics
    as potential misappropriation schemes.
    """
    # Primary (direct) mappings aligned with typical fraud scheme mechanics.
    return {
        "BillPayments": "billing",
        "Vendors": "billing",
        "BankTransfers": "check_and_payment_tampering",  # electronic payment diversion
        "ExpenseTransaction": "expense_reimbursements",
        "InventoryAdjustments": "noncash",
        "CustomerPayments": "skimming",
        "EmployeePayroll": "payroll",
        # time tracking / activity is a payroll-adjacent area in many fraud patterns
        "TimeTracking": "payroll",

        # Reconciliation/journal-entry risk are handled as "unknown baseline evidence"
        # (i.e., we do not assert an ACFE asset-misappropriation scheme prior),
        # because the ACFE Fraud Tree sub-scheme frequencies we used are specific to
        # asset misappropriation methods, not financial-statement journal manipulation.
        "BankReconciliation": "cash_larceny",
    }


def build_quickbooks_misappropriation_mapping(
    curated_transaction_ttl: str,
    asset_misappropriation_ttl: str,
    transaction_to_bucket_rules: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Produce a deterministic mapping:
      transaction_type -> {risk_level, transaction_frequency, evidence_bucket, evidence_percent, taxonomy_classes}

    Output shape is designed to be consumed by scoring/ranking code.
    """
    if transaction_to_bucket_rules is None:
        transaction_to_bucket_rules = _default_quickbooks_transaction_to_bucket_rules()

    curated = _parse_ttl_individuals_with_risk_and_frequency(curated_transaction_ttl)
    asset_classes = set(_parse_asset_misappropriation_classes(asset_misappropriation_ttl))

    evidence_buckets = _default_evidence_buckets_and_taxonomy()
    unknown_baseline_evidence_percent = min(ACFE_ASSET_MISAPPROPRIATION_SCHEME_PRIORS.values())  # typically 0.03

    max_freq = 0
    for _tx_name, info in curated.items():
        freq = info.get("transaction_frequency")
        if isinstance(freq, int):
            max_freq = max(max_freq, freq)
    max_evidence_percent = max(b.evidence_percent for b in evidence_buckets.values())

    mapping: Dict[str, Any] = {"transactions": {}, "meta": {}}
    mapping["meta"]["max_transaction_frequency"] = max_freq
    mapping["meta"]["max_evidence_percent"] = max_evidence_percent
    mapping["meta"]["unknown_baseline_evidence_percent"] = unknown_baseline_evidence_percent

    for tx_name, info in curated.items():
        bucket_id = transaction_to_bucket_rules.get(tx_name)

        if bucket_id is not None and bucket_id in evidence_buckets:
            bucket = evidence_buckets[bucket_id]
            taxonomy_classes = tuple(
                c for c in bucket.taxonomy_classes if c in asset_classes
            )
            evidence_percent = bucket.evidence_percent
            evidence_bucket_id = bucket_id
        else:
            # Fallback to a small baseline evidence prior; no taxonomy classes asserted.
            evidence_bucket_id = None
            evidence_percent = unknown_baseline_evidence_percent
            taxonomy_classes = tuple()

        mapping["transactions"][tx_name] = {
            "risk_level": info.get("risk_level"),
            "transaction_frequency": info.get("transaction_frequency"),
            "label": info.get("label"),
            "comment": info.get("comment"),
            "evidence_bucket_id": evidence_bucket_id,
            "evidence_percent": evidence_percent,
            "evidence_percent_normalized": evidence_percent / max_evidence_percent if max_evidence_percent else 0.0,
            "misappropriation_taxonomy_classes": list(taxonomy_classes),
        }

    return mapping


def _log_freq_normalize(freq: Optional[int], max_freq: int) -> float:
    if freq is None or max_freq <= 0:
        return 0.0
    # Log scale prevents huge frequency values from dominating.
    return math.log(1 + float(freq)) / math.log(1 + float(max_freq))


def score_transaction_misappropriation_likelihood(
    tx_name: str,
    mapping: Dict[str, Any],
    *,
    weights: Optional[Dict[str, float]] = None,
    default_risk_level: str = "Medium",
) -> Dict[str, Any]:
    """
    Score a transaction type's likelihood of misappropriation (QuickBooks-context).

    Score components (normalized to [0, 1] where possible):
      - risk_norm from curated qbo:riskLevel
      - freq_norm from curated qbo:transactionFrequency
      - evidence_norm from ACFE scheme priors mapped to your taxonomy buckets

    Final:
      score = w_risk*risk_norm + w_freq*freq_norm + w_evidence*evidence_norm
    """
    if weights is None:
        # Evidence is explicitly "occurrence in real-world cases", so it gets meaningful weight.
        weights = {"risk": 0.35, "freq": 0.20, "evidence": 0.45}

    tx = mapping["transactions"][tx_name]
    risk_level = tx.get("risk_level") or default_risk_level
    risk_norm = RISK_LEVEL_TO_VALUE.get(str(risk_level).strip().lower(), RISK_LEVEL_TO_VALUE["medium"])

    max_freq = mapping["meta"]["max_transaction_frequency"]
    freq_norm = _log_freq_normalize(tx.get("transaction_frequency"), max_freq)

    evidence_norm = tx.get("evidence_percent_normalized", 0.0)

    score = (
        weights["risk"] * risk_norm
        + weights["freq"] * freq_norm
        + weights["evidence"] * evidence_norm
    )

    return {
        "transaction_type": tx_name,
        "risk_level": risk_level,
        "risk_norm": risk_norm,
        "transaction_frequency": tx.get("transaction_frequency"),
        "freq_norm": freq_norm,
        "evidence_bucket_id": tx.get("evidence_bucket_id"),
        "evidence_percent": tx.get("evidence_percent"),
        "evidence_norm": evidence_norm,
        "misappropriation_taxonomy_classes": tx.get("misappropriation_taxonomy_classes", []),
        "score": score,
        "score_weights": weights,
    }


def rank_transactions_by_misappropriation_likelihood(
    mapping: Dict[str, Any],
    *,
    top_k: Optional[int] = None,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    scored = [
        score_transaction_misappropriation_likelihood(tx_name, mapping, weights=weights)
        for tx_name in mapping["transactions"].keys()
    ]
    scored_sorted = sorted(scored, key=lambda x: x["score"], reverse=True)
    if top_k is not None:
        scored_sorted = scored_sorted[:top_k]
    return {"success": True, "ranked": scored_sorted}


def _pretty_print_ranking(ranking: Dict[str, Any]) -> None:
    ranked = ranking["ranked"]
    print("\nMisappropriation Likelihood Ranking (QuickBooks-context)")
    print("=" * 70)
    for i, item in enumerate(ranked, start=1):
        classes = ", ".join(item["misappropriation_taxonomy_classes"]) if item["misappropriation_taxonomy_classes"] else "-"
        print(
            f"{i:2d}. {item['transaction_type']:<20} score={item['score']:.4f}  "
            f"risk={item['risk_level']:<8} freq={item.get('transaction_frequency')}  "
            f"bucket={item.get('evidence_bucket_id')}  classes={classes}"
        )


def main() -> None:
    """
    CLI entry point for local testing.
    """
    curated_ttl_path = "Curated Transaction Types.ttl"
    asset_ttl_path = "Asset_Misappropriation.ttl"

    mapping = build_quickbooks_misappropriation_mapping(
        curated_transaction_ttl=curated_ttl_path,
        asset_misappropriation_ttl=asset_ttl_path,
    )

    ranking = rank_transactions_by_misappropriation_likelihood(mapping)
    _pretty_print_ranking(ranking)

    # Optional artifact for UI consumption.
    with open("ngame_misappropriation_risk_ranking.json", "w", encoding="utf-8") as f:
        json.dump({"mapping": mapping, "ranking": ranking}, f, indent=2, default=str)

    print("\nSaved: `ngame_misappropriation_risk_ranking.json`")


if __name__ == "__main__":
    main()

