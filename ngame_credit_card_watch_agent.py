#!/usr/bin/env python3
"""
NGAME Credit Card Watch Agent

Detects company credit-card misuse by comparing the *actual* vendor type
(classified from the vendor name preserved in the ontology) against the
*intended* use reflected in the GL account code.

Core detection principle (from NGAME CC Misuse Analysis canvas, May 2026):
    The vendor name is ground truth — it cannot be rewritten without also
    falsifying the bank statement.  A vendor coded to "Travel" that is
    actually a cruise line is a structural anomaly regardless of the memo.

Detection dimensions implemented
---------------------------------
1. Vendor-Category Mismatch  (primary — highest signal)
2. Structuring / Threshold Evasion  (multiple charges below approval limit)
3. Temporal Pattern Anomalies  (weekend / holiday charges to personal vendors)
4. High-Dollar Personal-Category Charges  (dollar alarm on personal vendors)

Limitations (per canvas)
--------------------------
- QBO does not import MCC codes; vendor classification relies on name patterns.
- Some card processors truncate names ("SQ *", "TST *") — those are flagged
  as UNKNOWN and surfaced for human review rather than silently skipped.
- No cardholder identity in transaction; card-to-employee mapping is external.
"""

import json
import os
import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# ── Vendor Taxonomy ──────────────────────────────────────────────────────────
#
# Format: lowercase_keyword → (actual_category, risk_level)
#
# Risk levels: CRITICAL | HIGH | MEDIUM | LOW
# CRITICAL = personal use virtually certain; HIGH = strong personal-use signal;
# MEDIUM = personal use plausible; LOW = context-dependent.
#
# Listed longest/most-specific patterns first inside each group so that
# prefix-match scanning finds the most specific hit.
#
VENDOR_TAXONOMY: List[Tuple[str, str, str]] = [
    # ── Casinos / Gambling (CRITICAL) ──────────────────────────────────────
    ('draftkings',         'Online Gambling',        'CRITICAL'),
    ('fanduel',            'Online Gambling',        'CRITICAL'),
    ('betmgm',             'Online Gambling',        'CRITICAL'),
    ('caesars',            'Casino / Gambling',      'CRITICAL'),
    ('mgm grand',          'Casino / Gambling',      'CRITICAL'),
    ('borgata',            'Casino / Gambling',      'CRITICAL'),
    ('hard rock casino',   'Casino / Gambling',      'CRITICAL'),
    ('foxwoods',           'Casino / Gambling',      'CRITICAL'),
    ('mohegan sun',        'Casino / Gambling',      'CRITICAL'),
    ('bellagio',           'Casino / Gambling',      'CRITICAL'),
    ('venetian',           'Casino / Gambling',      'CRITICAL'),
    ('wynn las vegas',     'Casino / Gambling',      'CRITICAL'),
    ('harrahs',            'Casino / Gambling',      'CRITICAL'),
    ('casino',             'Casino / Gambling',      'CRITICAL'),

    # ── Personal Auto (CRITICAL) ────────────────────────────────────────────
    ('ally financial',     'Personal Auto Loan',     'CRITICAL'),
    ('carmax',             'Personal Auto Purchase', 'CRITICAL'),
    ('carvana',            'Personal Auto Purchase', 'CRITICAL'),
    ('vroom',              'Personal Auto Purchase', 'CRITICAL'),
    ('auto loan',          'Personal Auto Loan',     'CRITICAL'),

    # ── Cruise Lines (HIGH) ─────────────────────────────────────────────────
    ('royal caribbean',    'Cruise Line',            'HIGH'),
    ('carnival cruise',    'Cruise Line',            'HIGH'),
    ('norwegian cruise',   'Cruise Line',            'HIGH'),
    ('celebrity cruises',  'Cruise Line',            'HIGH'),
    ('disney cruise',      'Cruise Line',            'HIGH'),
    ('princess cruises',   'Cruise Line',            'HIGH'),
    ('holland america',    'Cruise Line',            'HIGH'),
    ('msc cruises',        'Cruise Line',            'HIGH'),

    # ── Personal Streaming / Subscriptions (HIGH) ──────────────────────────
    ('netflix',            'Personal Streaming',     'HIGH'),
    ('hulu',               'Personal Streaming',     'HIGH'),
    ('spotify',            'Personal Streaming',     'HIGH'),
    ('apple tv',           'Personal Streaming',     'HIGH'),
    ('disney plus',        'Personal Streaming',     'HIGH'),
    ('disney+',            'Personal Streaming',     'HIGH'),
    ('paramount plus',     'Personal Streaming',     'HIGH'),
    ('paramount+',         'Personal Streaming',     'HIGH'),
    ('peacock',            'Personal Streaming',     'HIGH'),
    ('hbo max',            'Personal Streaming',     'HIGH'),
    ('max.com',            'Personal Streaming',     'HIGH'),
    ('amazon prime',       'Personal Streaming',     'HIGH'),
    ('pandora',            'Personal Streaming',     'HIGH'),
    ('audible',            'Personal Streaming',     'HIGH'),

    # ── Personal Luxury Retail (HIGH) ──────────────────────────────────────
    ('neiman marcus',      'Personal Luxury Retail', 'HIGH'),
    ('saks fifth',         'Personal Luxury Retail', 'HIGH'),
    ('nordstrom',          'Personal Luxury Retail', 'HIGH'),
    ('bloomingdale',       'Personal Luxury Retail', 'HIGH'),
    ('bergdorf',           'Personal Luxury Retail', 'HIGH'),
    ('barneys',            'Personal Luxury Retail', 'HIGH'),
    ('louis vuitton',      'Personal Luxury Retail', 'HIGH'),
    ('gucci',              'Personal Luxury Retail', 'HIGH'),
    ('hermes',             'Personal Luxury Retail', 'HIGH'),
    ('tiffany',            'Personal Luxury Retail', 'HIGH'),

    # ── Home Improvement (HIGH personal, MEDIUM if Contractors flagged) ─────
    ('home depot',         'Home Improvement',       'HIGH'),
    ('lowes',              'Home Improvement',       'HIGH'),
    ("lowe's",             'Home Improvement',       'HIGH'),

    # ── Personal Wellness / Fitness (MEDIUM–HIGH) ──────────────────────────
    ('equinox',            'Personal Gym',           'HIGH'),
    ('soulcycle',          'Personal Gym',           'HIGH'),
    ('planet fitness',     'Personal Gym',           'MEDIUM'),
    ('la fitness',         'Personal Gym',           'MEDIUM'),
    ('24 hour fitness',    'Personal Gym',           'MEDIUM'),
    ('crunch fitness',     'Personal Gym',           'MEDIUM'),
    ('massage envy',       'Personal Wellness',      'MEDIUM'),
    ('hand and stone',     'Personal Wellness',      'MEDIUM'),

    # ── Personal Food Delivery (MEDIUM) ────────────────────────────────────
    ('doordash',           'Personal Food Delivery', 'MEDIUM'),
    ('grubhub',            'Personal Food Delivery', 'MEDIUM'),
    ('uber eats',          'Personal Food Delivery', 'MEDIUM'),
    ('instacart',          'Personal Grocery Delivery', 'MEDIUM'),
    ('shipt',              'Personal Grocery Delivery', 'MEDIUM'),

    # ── Personal Pet (MEDIUM) ───────────────────────────────────────────────
    ('petsmart',           'Personal Pet Expense',   'MEDIUM'),
    ('petco',              'Personal Pet Expense',   'MEDIUM'),
    ('chewy',              'Personal Pet Expense',   'MEDIUM'),

    # ── Personal Lodging (MEDIUM — can be business) ────────────────────────
    ('airbnb',             'Personal Lodging',       'MEDIUM'),
    ('vrbo',               'Personal Lodging',       'MEDIUM'),
]

# GL account keywords → list of intended business categories.
# If a vendor's actual category does NOT appear in the GL account's
# intended list, a mismatch is recorded.
GL_INTENDED_CATEGORIES: Dict[str, List[str]] = {
    'travel':               ['Air Travel', 'Hotel', 'Car Rental', 'Business Travel',
                             'Taxi / Rideshare'],
    'meals':                ['Business Meals', 'Client Entertainment'],
    'entertainment':        ['Client Entertainment', 'Business Event'],
    'office':               ['Office Supplies', 'Business Software', 'Printer / Toner'],
    'vehicle':              ['Business Vehicle', 'Fuel', 'Vehicle Maintenance'],
    'repairs':              ['Facility Repair', 'Equipment Maintenance'],
    'utilities':            ['Business Utility', 'Internet', 'Phone'],
    'advertising':          ['Business Advertising', 'Marketing', 'Promotions'],
    'professional':         ['Consulting', 'Legal', 'Accounting', 'IT Services'],
    'benefits':             ['Business Benefits', 'Health Insurance', 'Retirement Plan'],
    'supplies':             ['Office Supplies', 'Business Supplies', 'Cleaning Supplies'],
    'uniforms':             ['Staff Uniforms', 'Branded Clothing'],
    'dues':                 ['Professional Dues', 'Trade Association'],
    'insurance':            ['Business Insurance'],
    'contractor':           ['Contractor Labor', 'Subcontractor'],
}

# GL accounts that are inherently suspicious for CC charges (should almost
# never appear as a credit card expense account).
SUSPICIOUS_GL_ACCOUNTS: List[str] = [
    'loan', 'mortgage', 'personal', 'owner draw', 'distribution',
    'shareholder', 'dividend', 'capital',
]

# Structuring: charges just below these dollar thresholds trigger extra scrutiny.
STRUCTURING_THRESHOLDS: List[float] = [25.0, 50.0, 100.0, 250.0, 500.0, 1000.0]
STRUCTURING_BAND: float = 2.0   # flag if amount is within $2 below threshold

# QBO credit card class names (try multiple to handle variant TTL schemas)
CC_CHARGE_CLASSES = [
    'CreditCardCharge', 'Credit_Card_Charge', 'CreditCard_Charge',
    'CreditCardExpense', 'Credit_Card_Expense',
]
CC_CREDIT_CLASSES = [
    'CreditCardCredit', 'Credit_Card_Credit', 'CreditCard_Credit',
]
# NGAME TTL stores QBO Purchases as Expenses / ExpenseTransaction (PaymentType=CreditCard).
EXPENSE_LIKE_CLASSES = [
    'Expenses', 'ExpenseTransaction', 'CreditCardTransactions',
]
PAYMENT_TYPE_PROPS = ['hasPaymentType', 'hasPaymentMethod', 'PaymentType']
CC_PAYMENT_HINTS = ('creditcard', 'credit card', 'credit_card')
CC_ACCOUNT_HINTS = (
    'visa', 'mastercard', 'amex', 'american express', 'discover',
    'credit card', 'company card', 'corp card', 'chase card', 'capital one',
)

# Property name variants tried in order
VENDOR_PROPS    = ['hasVendorName', 'hasPayeeName', 'hasVendor', 'hasPayee',
                   'EntityRef', 'hasName']
ACCOUNT_PROPS   = ['hasAccountType', 'hasAccount', 'hasAccountRef',
                   'AccountRef', 'hasGLAccount']
AMOUNT_PROPS    = ['hasTotalAmount', 'hasAmount', 'TotalAmt', 'hasTotal']
DATE_PROPS      = ['hasTransactionDate', 'hasDate', 'TxnDate', 'hasDocDate']
MEMO_PROPS      = ['hasPrivateNote', 'hasMemo', 'PrivateNote', 'Memo',
                   'hasDescription', 'hasNarrative']


class NGameCreditCardWatchAgent:
    """
    Scans today's QBO ontology snapshot for credit card transactions and
    scores each one for potential personal misuse using:

      1. Vendor-Category Mismatch  — vendor name vs. GL account coding
      2. Structuring Detection     — amounts clustered just below thresholds
      3. Temporal Anomalies        — weekend / holiday charges to personal vendors
      4. Dollar Alarm              — large amounts to personal-category vendors
    """

    def __init__(self, today_file: str = "quickbooks_ontology_Today.ttl"):
        self.name = "NGameCreditCardWatchAgent"
        self.today_file = today_file
        logger.info(f"🤖 {self.name} initialized  (TTL: {self.today_file})")

    # ── Public API ───────────────────────────────────────────────────────────

    def scan_today_transactions(self) -> Dict[str, Any]:
        """
        Full credit card watch scan of Today.ttl.

        Returns:
            success         bool
            cc_flags        list  — scored CC transactions (sorted HIGH→LOW)
            structuring_flags list — groupings that suggest threshold evasion
            summary         dict  — counts by risk level, top vendors
            scan_timestamp  str
        """
        logger.info(f"💳 {self.name}: Starting CC watch scan")

        try:
            if not os.path.exists(self.today_file):
                return {
                    'success': False,
                    'error': f'{self.today_file} not found',
                    'cc_flags': [],
                    'structuring_flags': [],
                    'summary': self._empty_summary(),
                }

            transactions = self._extract_cc_transactions()

            if not transactions:
                logger.info(f"ℹ️  {self.name}: No CC transactions found in {self.today_file}")
                return {
                    'success': True,
                    'cc_flags': [],
                    'structuring_flags': [],
                    'summary': self._empty_summary(),
                    'scan_timestamp': datetime.now().isoformat(),
                }

            # Score each transaction
            cc_flags: List[Dict] = []
            for tx in transactions:
                flag = self._score_transaction(tx)
                if flag['overall_risk'] != 'CLEAR':
                    cc_flags.append(flag)

            # Sort: CRITICAL → HIGH → MEDIUM → LOW
            risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
            cc_flags.sort(key=lambda f: risk_order.get(f['overall_risk'], 99))

            # Structuring analysis across all CC transactions
            structuring_flags = self._detect_structuring(transactions)

            summary = self._build_summary(cc_flags, transactions, structuring_flags)

            logger.info(
                f"✅ {self.name}: CC scan complete — "
                f"{len(transactions)} CC txns, {len(cc_flags)} flagged, "
                f"{len(structuring_flags)} structuring pattern(s)"
            )

            return {
                'success':           True,
                'cc_flags':          cc_flags,
                'structuring_flags': structuring_flags,
                'summary':           summary,
                'scan_timestamp':    datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ {self.name}: CC scan failed — {e}")
            return {
                'success': False,
                'error': str(e),
                'cc_flags': [],
                'structuring_flags': [],
                'summary': self._empty_summary(),
            }

    # ── Transaction Extraction ────────────────────────────────────────────────

    def _extract_cc_transactions(self) -> List[Dict]:
        """
        Load credit-card transactions from Today.ttl.

        Supports dedicated CC classes and QBO Purchase rows stored as Expenses
        with qb:hasPaymentType \"CreditCard\".
        """
        logger.info(f"📖 {self.name}: Parsing CC transactions from {self.today_file}")

        try:
            from rdflib import Graph, Namespace
            from rdflib.namespace import RDF

            g = Graph()
            g.parse(self.today_file, format="turtle")
            qbo = Namespace("http://www.semanticweb.org/quickbooks/ontology#")

            transactions: List[Dict] = []
            seen_uris: set = set()
            dedicated_classes = CC_CHARGE_CLASSES + CC_CREDIT_CLASSES

            def _add_tx(subject, class_name: str, props: Dict[str, str]) -> None:
                uri = str(subject)
                if uri in seen_uris:
                    return
                if class_name in EXPENSE_LIKE_CLASSES and not self._looks_like_credit_card(props):
                    return
                seen_uris.add(uri)
                transactions.append(
                    self._transaction_from_props(
                        uri, class_name, props,
                        is_credit=class_name in CC_CREDIT_CLASSES,
                    )
                )

            for class_name in dedicated_classes + EXPENSE_LIKE_CLASSES:
                class_uri = qbo[class_name]
                for subject, _, _ in g.triples((None, RDF.type, class_uri)):
                    props: Dict[str, str] = {}
                    for _, prop_p, prop_o in g.triples((subject, None, None)):
                        pname = str(prop_p).split('#')[-1]
                        props[pname] = str(prop_o)
                    _add_tx(subject, class_name, props)

            logger.info(
                f"✅ {self.name}: Extracted {len(transactions)} CC transaction(s)"
            )
            return transactions

        except Exception as e:
            logger.error(f"❌ {self.name}: Error parsing TTL for CC transactions: {e}")
            return []

    @staticmethod
    def _transaction_from_props(
        uri: str,
        class_name: str,
        props: Dict[str, str],
        is_credit: bool = False,
    ) -> Dict[str, Any]:
        return {
            'uri': uri,
            'tx_class': class_name,
            'is_credit': is_credit,
            'vendor_name': NGameCreditCardWatchAgent._pick(props, VENDOR_PROPS, ''),
            'gl_account': NGameCreditCardWatchAgent._pick(props, ACCOUNT_PROPS, ''),
            'amount': NGameCreditCardWatchAgent._to_float(
                NGameCreditCardWatchAgent._pick(props, AMOUNT_PROPS, '0')
            ),
            'date': NGameCreditCardWatchAgent._pick(props, DATE_PROPS, ''),
            'memo': NGameCreditCardWatchAgent._pick(props, MEMO_PROPS, ''),
            'payment_type': NGameCreditCardWatchAgent._pick(props, PAYMENT_TYPE_PROPS, ''),
            'raw_props': props,
        }

    @staticmethod
    def _looks_like_credit_card(props: Dict[str, str]) -> bool:
        payment = NGameCreditCardWatchAgent._pick(props, PAYMENT_TYPE_PROPS, '').lower()
        if any(hint in payment.replace('_', '').replace(' ', '') for hint in CC_PAYMENT_HINTS):
            return True
        gl_account = NGameCreditCardWatchAgent._pick(props, ACCOUNT_PROPS, '').lower()
        return any(hint in gl_account for hint in CC_ACCOUNT_HINTS)

    # ── Vendor Classification ─────────────────────────────────────────────────

    def _classify_vendor(self, vendor_name: str) -> Dict[str, Any]:
        """
        Match vendor_name against VENDOR_TAXONOMY using case-insensitive substring
        search.  Returns the best (most specific) match found, or UNKNOWN.
        """
        needle = vendor_name.lower().strip()

        best_keyword = ''
        best_result: Optional[Tuple[str, str, str]] = None

        for keyword, actual_category, risk_level in VENDOR_TAXONOMY:
            if keyword in needle:
                # Prefer longer (more specific) keyword matches
                if len(keyword) > len(best_keyword):
                    best_keyword  = keyword
                    best_result   = (keyword, actual_category, risk_level)

        if best_result is None:
            return {
                'matched':          False,
                'keyword':          '',
                'actual_category':  'Unknown',
                'risk_level':       'UNKNOWN',
                'confidence':       0.0,
            }

        return {
            'matched':         True,
            'keyword':         best_result[0],
            'actual_category': best_result[1],
            'risk_level':      best_result[2],
            'confidence':      min(1.0, len(best_result[0]) / max(len(needle), 1) + 0.5),
        }

    def _check_gl_mismatch(
        self, vendor_class: Dict[str, Any], gl_account: str
    ) -> Dict[str, Any]:
        """
        Determine whether the vendor's actual category is consistent with
        the GL account's intended use category.

        A mismatch does not guarantee misuse — it is a signal that warrants
        investigation.  The scoring weight depends on the vendor risk level.
        """
        if not vendor_class['matched']:
            return {'mismatch': False, 'reason': 'vendor not in taxonomy'}

        gl_lower = gl_account.lower()
        actual   = vendor_class['actual_category'].lower()

        # Check suspicious GL accounts first
        for sus in SUSPICIOUS_GL_ACCOUNTS:
            if sus in gl_lower:
                return {
                    'mismatch':         True,
                    'reason':           f'GL account contains "{sus}" — inherently suspicious for CC expense',
                    'severity':         'HIGH',
                    'gl_intended':      gl_account,
                    'vendor_actual':    vendor_class['actual_category'],
                }

        # Check whether the actual vendor category is plausible for this GL account
        matched_gl_bucket: Optional[str] = None
        for gl_keyword, intended_list in GL_INTENDED_CATEGORIES.items():
            if gl_keyword in gl_lower:
                matched_gl_bucket = gl_keyword
                # If the vendor's actual category matches any intended use → no mismatch
                for intended in intended_list:
                    if intended.lower() in actual or actual in intended.lower():
                        return {
                            'mismatch':  False,
                            'reason':    f'Vendor consistent with GL "{gl_account}"',
                        }
                # GL bucket found but actual category not in intended list → mismatch
                return {
                    'mismatch':      True,
                    'reason':        (
                        f'Vendor actual type "{vendor_class["actual_category"]}" '
                        f'is inconsistent with GL account "{gl_account}" '
                        f'(expected: {", ".join(intended_list[:3])}…)'
                    ),
                    'severity':      vendor_class['risk_level'],
                    'gl_intended':   gl_account,
                    'vendor_actual': vendor_class['actual_category'],
                }

        # GL account not in our mapping — flag as unclassified-GL mismatch only
        # when the vendor has HIGH/CRITICAL risk
        if vendor_class['risk_level'] in ('HIGH', 'CRITICAL'):
            return {
                'mismatch':      True,
                'reason':        (
                    f'High-risk personal vendor "{vendor_class["actual_category"]}" '
                    f'charged to unclassified GL account "{gl_account}"'
                ),
                'severity':      vendor_class['risk_level'],
                'gl_intended':   gl_account,
                'vendor_actual': vendor_class['actual_category'],
            }

        return {'mismatch': False, 'reason': 'GL account not classified; low-risk vendor'}

    # ── Transaction Scoring ───────────────────────────────────────────────────

    def _score_transaction(self, tx: Dict) -> Dict[str, Any]:
        """
        Compute a composite risk score for a single CC transaction using all
        four detection dimensions.  Returns a flag dict.
        """
        alerts: List[Dict] = []
        vendor_class = self._classify_vendor(tx['vendor_name'])

        # ── Dimension 1: Vendor-Category Mismatch ──────────────────────────
        if vendor_class['matched']:
            mismatch = self._check_gl_mismatch(vendor_class, tx['gl_account'])
            if mismatch['mismatch']:
                alerts.append({
                    'dimension': 'vendor_category_mismatch',
                    'risk':      mismatch.get('severity', vendor_class['risk_level']),
                    'detail':    mismatch['reason'],
                })
            elif vendor_class['risk_level'] in ('HIGH', 'CRITICAL'):
                # Even when GL coding "matches", a CRITICAL vendor warrants a flag
                alerts.append({
                    'dimension': 'high_risk_vendor',
                    'risk':      vendor_class['risk_level'],
                    'detail': (
                        f'High-risk personal vendor "{vendor_class["actual_category"]}" '
                        f'regardless of GL coding'
                    ),
                })
        elif not tx['vendor_name']:
            alerts.append({
                'dimension': 'missing_vendor_name',
                'risk':      'MEDIUM',
                'detail':    'CC charge has no vendor name — cannot classify actual use',
            })
        # Truncated / ambiguous vendor names from some card processors
        elif any(tx['vendor_name'].lower().startswith(p)
                 for p in ('sq *', 'tst *', 'amzn', 'pp*', 'paypal')):
            alerts.append({
                'dimension': 'ambiguous_vendor_name',
                'risk':      'LOW',
                'detail':    f'Vendor name "{tx["vendor_name"]}" is processor-truncated — flag for human review',
            })

        # ── Dimension 2: Temporal Anomalies ────────────────────────────────
        if tx['date']:
            temporal = self._check_temporal(tx['date'], vendor_class)
            if temporal:
                alerts.append(temporal)

        # ── Dimension 3: Dollar Alarm ───────────────────────────────────────
        if tx['amount'] > 0 and vendor_class.get('risk_level') in ('HIGH', 'CRITICAL'):
            if tx['amount'] >= 500:
                alerts.append({
                    'dimension': 'large_personal_vendor_charge',
                    'risk':      'HIGH' if tx['amount'] >= 1000 else 'MEDIUM',
                    'detail': (
                        f'${tx["amount"]:,.2f} charged to personal-category vendor '
                        f'"{vendor_class["actual_category"]}"'
                    ),
                })

        # ── Dimension 4: Missing Audit Trail ───────────────────────────────
        if not tx['memo'] or tx['memo'].lower() in ('', 'misc', 'miscellaneous',
                                                      'supplies', 'expense', 'other'):
            if vendor_class.get('risk_level') in ('HIGH', 'CRITICAL'):
                alerts.append({
                    'dimension': 'missing_or_generic_memo',
                    'risk':      'MEDIUM',
                    'detail':    'No specific memo on a high-risk personal-category vendor charge',
                })

        # ── Composite risk level ─────────────────────────────────────────────
        risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'CLEAR': 4}
        overall_risk = 'CLEAR' if not alerts else min(
            alerts, key=lambda a: risk_order.get(a['risk'], 99)
        )['risk']

        return {
            'uri':             tx['uri'],
            'tx_class':        tx['tx_class'],
            'is_credit':       tx['is_credit'],
            'vendor_name':     tx['vendor_name'],
            'gl_account':      tx['gl_account'],
            'amount':          tx['amount'],
            'date':            tx['date'],
            'memo':            tx['memo'],
            'vendor_class':    vendor_class,
            'alerts':          alerts,
            'overall_risk':    overall_risk,
            'alert_count':     len(alerts),
        }

    # ── Structuring Detection ─────────────────────────────────────────────────

    def _detect_structuring(self, transactions: List[Dict]) -> List[Dict]:
        """
        Flag patterns consistent with threshold evasion:
          - Multiple charges to the same vendor within STRUCTURING_BAND below
            a STRUCTURING_THRESHOLD (suggests intentional split to stay under
            an approval limit).
          - Two or more charges to the same high-risk vendor on the same day.
        """
        flags: List[Dict] = []

        # Group by vendor name (normalised)
        by_vendor: Dict[str, List[Dict]] = {}
        for tx in transactions:
            key = tx['vendor_name'].lower().strip()
            by_vendor.setdefault(key, []).append(tx)

        for vendor_norm, txns in by_vendor.items():
            vendor_class = self._classify_vendor(txns[0]['vendor_name'])
            is_personal   = vendor_class['risk_level'] in ('HIGH', 'CRITICAL')

            # Same-day duplicate to personal vendor
            by_date: Dict[str, List[Dict]] = {}
            for t in txns:
                by_date.setdefault(t['date'], []).append(t)
            for day, day_txns in by_date.items():
                if len(day_txns) >= 2 and is_personal:
                    flags.append({
                        'pattern':       'same_day_duplicate',
                        'risk':          'HIGH',
                        'vendor_name':   txns[0]['vendor_name'],
                        'actual_category': vendor_class.get('actual_category', 'Unknown'),
                        'date':          day,
                        'charge_count':  len(day_txns),
                        'total_amount':  sum(t['amount'] for t in day_txns),
                        'detail': (
                            f'{len(day_txns)} charges to "{txns[0]["vendor_name"]}" '
                            f'on {day} (personal vendor — possible split to avoid threshold)'
                        ),
                    })

            # Threshold-banding
            for threshold in STRUCTURING_THRESHOLDS:
                near_threshold = [
                    t for t in txns
                    if threshold - STRUCTURING_BAND <= t['amount'] < threshold
                ]
                if len(near_threshold) >= 2:
                    flags.append({
                        'pattern':       'threshold_banding',
                        'risk':          'HIGH',
                        'vendor_name':   txns[0]['vendor_name'],
                        'actual_category': vendor_class.get('actual_category', 'Unknown'),
                        'threshold':     threshold,
                        'charge_count':  len(near_threshold),
                        'amounts':       [t['amount'] for t in near_threshold],
                        'total_amount':  sum(t['amount'] for t in near_threshold),
                        'detail': (
                            f'{len(near_threshold)} charges to '
                            f'"{txns[0]["vendor_name"]}" '
                            f'just below ${threshold:,.0f} threshold '
                            f'({[f"${a:,.2f}" for a in [t["amount"] for t in near_threshold]]})'
                        ),
                    })

        return flags

    # ── Temporal Check ────────────────────────────────────────────────────────

    def _check_temporal(
        self, date_str: str, vendor_class: Dict[str, Any]
    ) -> Optional[Dict]:
        """
        Flag weekend / holiday charges to personal-category vendors.
        Only generates an alert when the vendor is already classified as
        personal-use (HIGH/CRITICAL) to avoid noise on legitimate weekend
        business travel.
        """
        if vendor_class.get('risk_level') not in ('HIGH', 'CRITICAL'):
            return None
        try:
            dt = datetime.fromisoformat(date_str[:10])
            if dt.weekday() >= 5:   # Saturday = 5, Sunday = 6
                return {
                    'dimension': 'weekend_personal_vendor',
                    'risk':      'MEDIUM',
                    'detail': (
                        f'Charge to personal-category vendor '
                        f'"{vendor_class["actual_category"]}" on a weekend '
                        f'({date_str[:10]})'
                    ),
                }
        except (ValueError, TypeError):
            pass
        return None

    # ── Summary ───────────────────────────────────────────────────────────────

    def _build_summary(
        self,
        cc_flags: List[Dict],
        all_transactions: List[Dict],
        structuring_flags: List[Dict],
    ) -> Dict[str, Any]:
        counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'CLEAR': 0}
        for f in cc_flags:
            counts[f['overall_risk']] = counts.get(f['overall_risk'], 0) + 1

        top_vendors = sorted(
            {f['vendor_name']: f['overall_risk'] for f in cc_flags if f['vendor_name']}.items(),
            key=lambda x: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}.get(x[1], 99),
        )[:5]

        total_flagged_amount = sum(
            f['amount'] for f in cc_flags if f['overall_risk'] in ('CRITICAL', 'HIGH')
        )

        return {
            'total_cc_transactions':  len(all_transactions),
            'total_flagged':          len(cc_flags),
            'critical_count':         counts.get('CRITICAL', 0),
            'high_count':             counts.get('HIGH',     0),
            'medium_count':           counts.get('MEDIUM',   0),
            'low_count':              counts.get('LOW',       0),
            'structuring_flags':      len(structuring_flags),
            'top_flagged_vendors':    [{'vendor': v, 'risk': r} for v, r in top_vendors],
            'total_at_risk_dollars':  total_flagged_amount,
            'highest_risk_level':     (
                'CRITICAL' if counts.get('CRITICAL', 0)
                else 'HIGH' if counts.get('HIGH', 0)
                else 'MEDIUM' if counts.get('MEDIUM', 0)
                else 'LOW' if counts.get('LOW', 0)
                else 'CLEAR'
            ),
        }

    @staticmethod
    def _empty_summary() -> Dict[str, Any]:
        return {
            'total_cc_transactions': 0, 'total_flagged': 0,
            'critical_count': 0, 'high_count': 0, 'medium_count': 0,
            'low_count': 0, 'structuring_flags': 0,
            'top_flagged_vendors': [], 'total_at_risk_dollars': 0.0,
            'highest_risk_level': 'CLEAR',
        }

    # ── Utility helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _pick(props: Dict[str, str], candidates: List[str], default: str) -> str:
        """Return the first non-empty value from a list of candidate property names."""
        for key in candidates:
            val = props.get(key, '').strip()
            if val:
                return val
        return default

    @staticmethod
    def _to_float(s: str) -> float:
        try:
            return max(float(re.sub(r'[^\d.]', '', s)), 0.0)
        except (ValueError, TypeError):
            return 0.0

    def save_results(
        self, result: Dict[str, Any],
        output_file: str = "cc_watch_results.json",
    ) -> None:
        try:
            with open(output_file, 'w') as fh:
                json.dump(result, fh, indent=2, default=str)
            logger.info(f"💾 {self.name}: CC watch results saved to {output_file}")
        except Exception as e:
            logger.error(f"❌ {self.name}: Failed to save CC watch results: {e}")


def main():
    """Standalone test / demo run."""
    print("💳 NGAME Credit Card Watch Agent Test")
    print("=" * 55)

    agent = NGameCreditCardWatchAgent()
    result = agent.scan_today_transactions()

    if not result['success']:
        print(f"\n❌ Scan failed: {result.get('error')}")
        return False

    summary = result['summary']
    print(f"\n📊 Scan Summary")
    print(f"   CC transactions found : {summary['total_cc_transactions']}")
    print(f"   Flagged               : {summary['total_flagged']}")
    print(f"   CRITICAL              : {summary['critical_count']}")
    print(f"   HIGH                  : {summary['high_count']}")
    print(f"   MEDIUM                : {summary['medium_count']}")
    print(f"   Structuring patterns  : {summary['structuring_flags']}")
    print(f"   Total at-risk $       : ${summary['total_at_risk_dollars']:,.2f}")
    print(f"   Highest risk level    : {summary['highest_risk_level']}")

    if result['cc_flags']:
        print(f"\n⚠️  Flagged Transactions:")
        for flag in result['cc_flags'][:10]:
            print(
                f"   [{flag['overall_risk']:8s}] "
                f"${flag['amount']:9,.2f}  "
                f"{flag['vendor_name'][:35]:<35s}  "
                f"GL: {flag['gl_account'][:30]}"
            )
            for alert in flag['alerts']:
                print(f"              → {alert['detail']}")

    if result['structuring_flags']:
        print(f"\n🔀 Structuring Patterns:")
        for sf in result['structuring_flags']:
            print(f"   [{sf['risk']:8s}] {sf['detail']}")

    agent.save_results(result)
    return True


if __name__ == "__main__":
    main()
