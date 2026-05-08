#!/usr/bin/env python3
"""
Run NGAME Phase I data extraction using WAVE accounting (GraphQL API).
Produces wave_ontology_Today.ttl for use by downstream CPI/fraud analysis.
"""

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if os.getcwd() != _REPO_ROOT:
    os.chdir(_REPO_ROOT)

from ngame_data_extraction_agent import NGameDataExtractionAgent, SOURCE_WAVE


def main():
    print("NGAME Phase I – WAVE (GraphQL) data extraction")
    print("=" * 50)
    agent = NGameDataExtractionAgent(source=SOURCE_WAVE)
    result = agent.extract_daily_data()
    if result.get("success"):
        print(f"\nOK  TTL file: {result['ttl_file']}")
        stats = result.get("extraction_stats", {})
        print(f"    Total records: {stats.get('total_records', 0)}")
        print(f"    Transaction types: {stats.get('total_types', 0)}")
        return 0
    print(f"\nFAIL {result.get('error', 'Unknown error')}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
