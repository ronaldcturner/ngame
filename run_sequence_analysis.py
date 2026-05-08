#!/usr/bin/env python3
"""
run_sequence_analysis.py  —  Standalone SCPI / Slow-Burn Analysis Runner

Reads the rolling CPI buffer built up by daily fraud analysis runs and
computes the Sequence Churn Proximity Index (SCPI) for the last L days.
Compares SCPI against the Training Matrix baseline using a sequence-scaled
z-score (σ / √L) to surface slow-burn fraud that no single day would catch.

Usage
-----
    python3 run_sequence_analysis.py                  # default window = 5
    python3 run_sequence_analysis.py --window 7       # 7-day window
    python3 run_sequence_analysis.py --window 3 --verbose

Options
-------
    --window  L     Number of days in the rolling window (default: 5)
    --verbose       Print per-position z-scores for all 18 types
    --buffer  PATH  Path to the rolling buffer JSON (default: NGAME_CPI_Rolling_Buffer.json)
    --matrix  PATH  Path to the Training Matrix XLSX (default: NGAME_Training_Matrix.xlsx)

Interpreting the output
-----------------------
    HIGH   (|z_seq| > 3σ)  —  Sustained anomaly.  Escalate immediately.
    MEDIUM (|z_seq| > 2σ)  —  Elevated pattern.   Increase monitoring.
    LOW                    —  No sustained deviation.

The key statistic: a transaction type scoring MEDIUM (-2σ) every single day
will reach HIGH by day 3 (z_seq ≈ 3.46σ) and keeps rising.  This is the
"slow-burn" detection capability that the single-day path cannot provide.
"""

import argparse
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if os.getcwd() != _REPO_ROOT:
    os.chdir(_REPO_ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="NGAME Sequence CPI (slow-burn fraud) analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--window", "-w", type=int, default=5, metavar="L",
        help="Rolling window length in days (default: 5)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print z-scores for all 18 transaction types",
    )
    parser.add_argument(
        "--buffer", type=str, default="NGAME_CPI_Rolling_Buffer.json",
        help="Path to rolling CPI buffer JSON",
    )
    parser.add_argument(
        "--matrix", type=str, default="NGAME_Training_Matrix.xlsx",
        help="Path to Training Matrix XLSX",
    )
    args = parser.parse_args()

    print("🔁 NGAME Sequence CPI Analysis  (Slow-Burn Fraud Detection)")
    print("=" * 60)

    # ── Buffer status ────────────────────────────────────────────────────────
    from ngame_sequence_cpi_agent import NGameSequenceCpiAgent, STANDARD_TRANSACTION_TYPES
    agent = NGameSequenceCpiAgent(buffer_file=args.buffer)

    buf = agent.get_buffer_summary()
    print(f"\n📦 Rolling buffer:  {buf['days_stored']} day(s) stored")
    if buf['oldest_date']:
        print(f"   Range: {buf['oldest_date']}  →  {buf['newest_date']}")
    else:
        print("   Buffer is empty — run daily fraud analysis first to populate it.")
        return 1

    # ── Compute SCPI ─────────────────────────────────────────────────────────
    print(f"\n🔍 Computing SCPI for window = {args.window} day(s) …")
    result = agent.compute_scpi(window=args.window)

    if not result.get('success'):
        print(f"\n❌ SCPI computation failed: {result.get('error')}")
        return 1

    if not result.get('ready'):
        days_avail = result.get('days_available', 0)
        print(
            f"\n⏳ Not enough data yet: {days_avail}/{args.window} days in buffer.\n"
            f"   Run 'python3 run_fraud_analysis.py' for {args.window - days_avail} "
            f"more day(s) to activate sequence detection."
        )
        return 0

    # ── SCPI is ready — compare against Training Matrix ─────────────────────
    from ngame_churn_comparison_agent import NGameChurnComparisonAgent
    cmp_agent = NGameChurnComparisonAgent()
    comparison = cmp_agent.compare_sequence_profiles(
        result['scpi_array'],
        args.matrix,
        result['window_size'],
        weighted_scpi_array=result.get('weighted_scpi_array'),
    )

    # ── Print results ────────────────────────────────────────────────────────
    window   = result['window_size']
    dates    = result.get('dates', [])
    high_n   = result['high_count']
    medium_n = result['medium_count']
    summary  = result['scpi_summary']

    print(f"\n✅ SCPI computed over {window} days")
    print(f"   Dates: {', '.join(dates)}")
    print(f"\n📊 SCPI Array Summary:")
    print(f"   Mean:  {summary['mean']:.6f}")
    print(f"   Std:   {summary['std']:.6f}")
    print(f"   Min:   {summary['min']:.6f}  Max: {summary['max']:.6f}")

    print(f"\n⚡ Sequence Z-Score Results  (|z_seq| = |SCPI − μ| / (σ / √{window}))")
    print(f"   HIGH   positions (|z_seq| > 3σ): {high_n}")
    print(f"   MEDIUM positions (|z_seq| > 2σ): {medium_n}")

    if high_n > 0 or medium_n > 0:
        print(f"\n{'':=<60}")
        if high_n > 0:
            print("🚨 SLOW-BURN HIGH ALERT — Sustained anomaly across window:")
        elif medium_n > 0:
            print("⚠️  SLOW-BURN MEDIUM ALERT — Elevated pattern across window:")
        print(f"{'':=<60}")

        for i, diff in enumerate(result.get('scpi_z_scores', [])):
            lvl = result['deviation_levels'][i]
            if lvl != 'LOW':
                tx = STANDARD_TRANSACTION_TYPES[i]
                scpi_v = result['scpi_array'][i]
                print(
                    f"   φ{i+1:2d} {tx:<30s}  "
                    f"SCPI={scpi_v:.6f}  z_seq={diff:+.3f}  {lvl}"
                )

    # ── Verbose: print all 18 positions ─────────────────────────────────────
    if args.verbose:
        print(f"\n{'':─<60}")
        print(f"{'φ':>4}  {'Transaction Type':<30}  {'SCPI':>10}  {'z_seq':>8}  Level")
        print(f"{'':─<60}")
        for i, tx in enumerate(STANDARD_TRANSACTION_TYPES):
            scpi_v = result['scpi_array'][i]
            z      = result['scpi_z_scores'][i] if i < len(result.get('scpi_z_scores', [])) else 0.0
            lvl    = result['deviation_levels'][i] if i < len(result.get('deviation_levels', [])) else 'LOW'
            marker = "  ◄" if lvl != 'LOW' else ""
            print(
                f"  {i+1:2d}  {tx:<30s}  {scpi_v:10.6f}  {z:+8.3f}  {lvl}{marker}"
            )

    # ── Final verdict ────────────────────────────────────────────────────────
    print()
    if high_n > 0:
        print("🚨 VERDICT: SLOW-BURN HIGH — immediate investigation recommended.")
        return 2   # non-zero exit so shell scripts / CI can react
    elif medium_n > 0:
        print("⚠️  VERDICT: SLOW-BURN MEDIUM — enhanced monitoring recommended.")
        return 0
    else:
        print("✅ VERDICT: No slow-burn anomaly detected over this window.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
