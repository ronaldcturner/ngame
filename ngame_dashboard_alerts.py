#!/usr/bin/env python3
"""Helpers for consolidating fraud-analysis alerts for the NGAME dashboard."""

from typing import Any, Dict, List

from ngame_transaction_types import (
    STANDARD_TRANSACTION_TYPES,
    dollar_signal_duplicates_count,
    is_actionable_anomaly,
    transaction_type_for_index,
)


def _tx_type_name(index: int) -> str:
    return transaction_type_for_index(index)


def _comparison_differences(fraud: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Prefer comparison_result.differences; fall back to ranking_result."""
    comparison = fraud.get("comparison_result") or {}
    diffs = comparison.get("differences") or []
    if diffs:
        return diffs
    ranking = fraud.get("ranking_result") or {}
    return ranking.get("ranked_differences") or []


def format_cc_flags_for_display(cc_flags: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize credit-card watch flags for the dashboard panel."""
    rows: List[Dict[str, Any]] = []
    for flag in cc_flags:
        alerts = flag.get("alerts") or []
        detail = alerts[0].get("detail", "") if alerts else ""
        vendor = (flag.get("vendor_name") or "").strip()
        gl_account = (flag.get("gl_account") or "").strip()
        amount = float(flag.get("amount") or 0.0)
        if vendor:
            desc = f"{vendor} — {gl_account} — ${amount:,.2f}".strip(" —")
        else:
            desc = f"{gl_account} — ${amount:,.2f}".strip(" —")
        if detail:
            desc = f"{desc}: {detail}" if desc else detail
        rows.append(
            {
                "risk_level": flag.get("overall_risk", "FLAGGED"),
                "vendor_name": vendor,
                "description": desc or "Credit card item",
                "pattern": detail,
            }
        )
    return rows


def filter_top_anomalies_for_display(
    anomalies: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Drop baseline-noise rows from Top Anomalies (e.g. quiet-day ChartOfAccounts)."""
    return [row for row in anomalies if is_actionable_anomaly(row)]


def build_dollar_alarm_alerts(fraud: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return dollar-weighted alerts sorted by |dollar z-score| (highest first)."""
    diffs = _comparison_differences(fraud)
    alerts: List[Dict[str, Any]] = []

    for diff in diffs:
        if not diff.get("dollar_alarm"):
            continue
        idx = int(diff.get("index") or 0)
        tx_type = _tx_type_name(idx)
        if dollar_signal_duplicates_count(diff, tx_type):
            continue
        alerts.append(
            {
                "index": idx,
                "phi_index": f"φ{idx}",
                "transaction_type": tx_type,
                "deviation_level": diff.get("deviation_level", "LOW"),
                "dollar_alarm_level": diff.get("dollar_alarm_level", "LOW"),
                "dollar_z_score": diff.get("dollar_z_score", 0.0),
                "dollar_abs_z_score": diff.get("dollar_abs_z_score", 0.0),
                "z_score": diff.get("z_score", 0.0),
                "abs_z_score": diff.get("abs_z_score", 0.0),
                "composite_alarm": bool(diff.get("composite_alarm")),
                "weighted_cpi": diff.get("weighted_cpi"),
                "today_value": diff.get("today_value"),
                "average_value": diff.get("average_value"),
            }
        )

    alerts.sort(
        key=lambda row: float(row.get("dollar_abs_z_score") or 0.0),
        reverse=True,
    )
    return alerts


def needs_full_comparison(fraud: Dict[str, Any]) -> bool:
    """True when the loaded artifact lacks dollar-weighted comparison fields."""
    diffs = (fraud.get("comparison_result") or {}).get("differences") or []
    if not diffs:
        return True
    return not any(
        d.get("dollar_alarm") is not None or d.get("dollar_alarm_level")
        for d in diffs
    )


def merge_full_fraud_comparison(
    fraud: Dict[str, Any],
    load_json,
    root,
    fallbacks,
) -> Dict[str, Any]:
    """
    Overlay fields that are sometimes stripped from the readable dashboard JSON.

    We primarily need the full `comparison_result` (dollar-weighted fields), but we
    also opportunistically restore other sections (e.g., `cc_watch_result`) when
    they are absent in the readable artifact.
    """
    wants_comparison = needs_full_comparison(fraud)
    wants_cc_watch = not bool(fraud.get("cc_watch_result"))
    if not wants_comparison and not wants_cc_watch:
        return fraud
    for p in (
        root / "NGAME_Fraud_Analysis.json",
        fallbacks / "NGAME_Fraud_Analysis.json",
    ):
        full_fraud, _ = load_json(p)
        if not full_fraud:
            continue
        merged = {**fraud}
        changed = False
        if wants_comparison and (full_fraud.get("comparison_result") or {}).get("differences"):
            merged["comparison_result"] = full_fraud["comparison_result"]
            changed = True
            if full_fraud.get("ranking_result"):
                merged["ranking_result"] = full_fraud["ranking_result"]
            if full_fraud.get("anomaly_result"):
                merged["anomaly_result"] = full_fraud["anomaly_result"]
        if wants_cc_watch and full_fraud.get("cc_watch_result"):
            merged["cc_watch_result"] = full_fraud["cc_watch_result"]
            changed = True
        if changed:
            return merged
    return fraud
