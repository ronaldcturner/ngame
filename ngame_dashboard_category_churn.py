#!/usr/bin/env python3
"""Day-over-day category activity for the NGAME dashboard (Yesterday.ttl vs Today.ttl)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ngame_transaction_types import (
    CPI_ONTOLOGY_ALIASES,
    STANDARD_TRANSACTION_TYPES,
    resolve_cpi_coefficient,
)

YESTERDAY_TTL = "quickbooks_ontology_Yesterday.ttl"
TODAY_TTL = "quickbooks_ontology_Today.ttl"

# Ontology/rdf class name → matrix row (first match wins when aggregating).
ONTOLOGY_CLASS_TO_MATRIX: Dict[str, str] = {}
for _row in STANDARD_TRANSACTION_TYPES:
    ONTOLOGY_CLASS_TO_MATRIX[_row.replace("_", "")] = _row
    ONTOLOGY_CLASS_TO_MATRIX[_row] = _row
for _row, _aliases in CPI_ONTOLOGY_ALIASES.items():
    for _alias in _aliases:
        ONTOLOGY_CLASS_TO_MATRIX[_alias] = _row


def _ontology_class_to_matrix(class_name: str) -> Optional[str]:
    if class_name in ONTOLOGY_CLASS_TO_MATRIX:
        return ONTOLOGY_CLASS_TO_MATRIX[class_name]
    stripped = class_name.replace("_", "")
    return ONTOLOGY_CLASS_TO_MATRIX.get(stripped)


def _load_type_uri_sets(ttl_path: Path) -> Dict[str, Set[str]]:
    """Return matrix-row → set of individual URIs in one snapshot."""
    from rdflib import Graph, Namespace, RDF

    g = Graph()
    g.parse(str(ttl_path), format="turtle")
    qbo = Namespace("http://www.semanticweb.org/quickbooks/ontology#")

    by_matrix: Dict[str, Set[str]] = {}
    for subject, _pred, obj in g.triples((None, RDF.type, None)):
        type_str = str(obj)
        if not type_str.startswith(str(qbo)):
            continue
        class_name = type_str.split("#")[-1]
        matrix_row = _ontology_class_to_matrix(class_name)
        if not matrix_row:
            continue
        by_matrix.setdefault(matrix_row, set()).add(str(subject))
    return by_matrix


def build_category_day_activity(
    root: Path,
    fraud: Optional[Dict[str, Any]] = None,
    yesterday_filename: str = YESTERDAY_TTL,
    today_filename: str = TODAY_TTL,
) -> List[Dict[str, Any]]:
    """
    Per φ category: records added/removed overnight and today's CPI (if available).

    Helps FRPs see which QBO transaction *types* actually changed — e.g. Bills vs
    Bill_Payments are separate rows and are never merged in this view.
    """
    yesterday_path = root / yesterday_filename
    today_path = root / today_filename
    if not yesterday_path.is_file() or not today_path.is_file():
        return []

    yesterday_sets = _load_type_uri_sets(yesterday_path)
    today_sets = _load_type_uri_sets(today_path)

    cpi_by_row: Dict[str, float] = {}
    if fraud:
        comp = fraud.get("comparison_result") or {}
        diffs = comp.get("differences") or []
        for diff in diffs:
            idx = int(diff.get("index") or 0)
            if 1 <= idx <= len(STANDARD_TRANSACTION_TYPES):
                cpi_by_row[STANDARD_TRANSACTION_TYPES[idx - 1]] = float(
                    diff.get("today_value") or 1.0
                )

    rows: List[Dict[str, Any]] = []
    for idx, matrix_row in enumerate(STANDARD_TRANSACTION_TYPES, start=1):
        y_uris = yesterday_sets.get(matrix_row, set())
        t_uris = today_sets.get(matrix_row, set())
        added = len(t_uris - y_uris)
        removed = len(y_uris - t_uris)
        retained = len(y_uris & t_uris)
        total = added + removed + retained
        if total == 0 and added == 0 and removed == 0:
            cpi = 1.0
        elif total == 0:
            cpi = 1.0
        else:
            cpi = retained / total

        if added == 0 and removed == 0 and abs(cpi - 1.0) < 1e-9:
            continue

        rows.append(
            {
                "index": idx,
                "phi_index": f"φ{idx}",
                "transaction_type": matrix_row,
                "added": added,
                "removed": removed,
                "retained": retained,
                "cpi": round(cpi_by_row.get(matrix_row, cpi), 6),
                "churn": round(max(0.0, 1.0 - cpi), 6),
            }
        )

    rows.sort(
        key=lambda r: (r["added"] + r["removed"], r["churn"]),
        reverse=True,
    )
    return rows
