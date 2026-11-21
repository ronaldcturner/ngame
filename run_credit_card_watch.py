#!/usr/bin/env python3
"""
run_credit_card_watch.py — Standalone NGAME Credit Card Watch Runner

Scans today's QuickBooks ontology snapshot for company credit card misuse
without running the full fraud analysis pipeline.  Use this to:

  • Run a targeted CC-only scan on demand
  • Inspect individual flag details and structuring patterns
  • Test the CC watch agent against a custom TTL file

Usage
-----
  python run_credit_card_watch.py
  python run_credit_card_watch.py --ttl path/to/custom_snapshot.ttl
  python run_credit_card_watch.py --verbose
  python run_credit_card_watch.py --output cc_flags_today.json
"""

import argparse
import json
import os
import sys
from datetime import datetime


def _risk_colour(level: str) -> str:
    """Return ANSI-coloured risk badge for terminal output."""
    colours = {
        'CRITICAL': '\033[91m',  # bright red
        'HIGH':     '\033[93m',  # yellow
        'MEDIUM':   '\033[94m',  # blue
        'LOW':      '\033[96m',  # cyan
        'CLEAR':    '\033[92m',  # green
        'UNKNOWN':  '\033[90m',  # grey
    }
    reset = '\033[0m'
    c = colours.get(level, '\033[0m')
    return f"{c}{level:8s}{reset}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="NGAME Credit Card Watch — standalone scan of today's ontology",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_credit_card_watch.py
  python run_credit_card_watch.py --ttl quickbooks_ontology_Today.ttl
  python run_credit_card_watch.py --verbose --output cc_flags.json
        """,
    )
    parser.add_argument(
        '--ttl',
        default='quickbooks_ontology_Today.ttl',
        help='Path to QuickBooks ontology TTL file (default: quickbooks_ontology_Today.ttl)',
    )
    parser.add_argument(
        '--output',
        default='cc_watch_results.json',
        help='Output JSON file for full results (default: cc_watch_results.json)',
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show all alerts for every flagged transaction',
    )
    parser.add_argument(
        '--structuring-only',
        action='store_true',
        help='Show only structuring / threshold-evasion patterns',
    )
    parser.add_argument(
        '--min-risk',
        choices=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        default='LOW',
        help='Minimum risk level to display (default: LOW)',
    )
    args = parser.parse_args()

    print("💳 NGAME Credit Card Watch — Standalone Runner")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📄 TTL file : {args.ttl}")
    print()

    if not os.path.exists(args.ttl):
        print(f"❌ TTL file not found: {args.ttl}")
        print("   Ensure a QuickBooks ontology snapshot exists at the specified path.")
        return 1

    # ── Run the scan ──────────────────────────────────────────────────────────
    from ngame_credit_card_watch_agent import NGameCreditCardWatchAgent

    agent = NGameCreditCardWatchAgent(today_file=args.ttl)
    result = agent.scan_today_transactions()

    if not result['success']:
        print(f"❌ CC watch scan failed: {result.get('error', 'unknown error')}")
        return 1

    summary = result['summary']

    # ── Summary block ─────────────────────────────────────────────────────────
    print("📊 Scan Summary")
    print("-" * 40)
    print(f"   CC transactions scanned  : {summary['total_cc_transactions']}")
    print(f"   Total flagged            : {summary['total_flagged']}")
    print(f"   CRITICAL                 : {summary['critical_count']}")
    print(f"   HIGH                     : {summary['high_count']}")
    print(f"   MEDIUM                   : {summary['medium_count']}")
    print(f"   LOW                      : {summary['low_count']}")
    print(f"   Structuring patterns     : {summary['structuring_flags']}")
    print(f"   Highest risk level       : {summary['highest_risk_level']}")
    print(f"   Total at-risk dollars    : ${summary['total_at_risk_dollars']:,.2f}")

    # ── Top-level alert banner ────────────────────────────────────────────────
    if summary['critical_count'] > 0:
        print(
            f"\n🚨 CRITICAL ALERT — {summary['critical_count']} transaction(s) with "
            f"virtually-certain personal misuse on company card(s)"
        )
    elif summary['high_count'] > 0:
        print(
            f"\n⚠️  HIGH RISK — {summary['high_count']} transaction(s) with "
            f"strong personal-use signal on company card(s)"
        )
    elif summary['medium_count'] > 0:
        print(f"\n📎 MEDIUM RISK — {summary['medium_count']} transaction(s) warrant review")
    else:
        print(f"\n✅ No high-risk CC transactions detected in today's snapshot")

    # ── Risk filter ────────────────────────────────────────────────────────────
    risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'CLEAR': 4}
    min_order  = risk_order.get(args.min_risk, 3)

    # ── Individual flags ───────────────────────────────────────────────────────
    if not args.structuring_only:
        visible_flags = [
            f for f in result['cc_flags']
            if risk_order.get(f['overall_risk'], 4) <= min_order
        ]

        if visible_flags:
            print(f"\n⚠️  Flagged CC Transactions (≥ {args.min_risk})")
            print("-" * 70)
            for flag in visible_flags:
                print(
                    f"  [{_risk_colour(flag['overall_risk'])}]  "
                    f"${flag['amount']:>10,.2f}  "
                    f"{flag['vendor_name'][:35]:<35s}  "
                    f"GL: {flag['gl_account'][:28]}"
                )
                if flag['date']:
                    print(f"              Date: {flag['date'][:10]}")
                if flag.get('vendor_class', {}).get('matched'):
                    vc = flag['vendor_class']
                    print(f"              Actual type: {vc['actual_category']} "
                          f"(taxonomy risk: {vc['risk_level']})")
                if args.verbose:
                    for alert in flag['alerts']:
                        print(f"              → [{alert['risk']:8s}] {alert['detail']}")
                elif flag['alerts']:
                    # Show only the top alert when not verbose
                    top = flag['alerts'][0]
                    print(f"              → {top['detail']}")
                print()
        elif result['cc_flags']:
            print(
                f"\n   (All {len(result['cc_flags'])} flag(s) below "
                f"--min-risk {args.min_risk} threshold; use --min-risk MEDIUM to see more)"
            )

    # ── Structuring patterns ───────────────────────────────────────────────────
    if result['structuring_flags']:
        print(f"\n🔀 Structuring / Threshold-Evasion Patterns")
        print("-" * 70)
        for sf in result['structuring_flags']:
            print(f"  [{_risk_colour(sf['risk'])}]  {sf['detail']}")
            if sf['pattern'] == 'threshold_banding':
                print(
                    f"              Amounts: "
                    f"{[f'${a:,.2f}' for a in sf.get('amounts', [])]}"
                )
            print()
    elif args.structuring_only:
        print("\n   No structuring patterns detected.")

    # ── Top flagged vendors (if any) ───────────────────────────────────────────
    if summary['top_flagged_vendors']:
        print("\n🏪 Top Flagged Vendors")
        print("-" * 40)
        for entry in summary['top_flagged_vendors']:
            print(
                f"  [{_risk_colour(entry['risk'])}]  {entry['vendor']}"
            )

    # ── Save results ───────────────────────────────────────────────────────────
    agent.save_results(result, output_file=args.output)
    print(f"\n💾 Full results saved to: {args.output}")

    # ── Exit code reflects highest risk ────────────────────────────────────────
    if summary['critical_count'] > 0:
        return 2     # CRITICAL — escalate
    if summary['high_count'] > 0:
        return 1     # HIGH — warrants review
    return 0         # CLEAR / LOW / MEDIUM


if __name__ == "__main__":
    sys.exit(main())
