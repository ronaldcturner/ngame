#!/usr/bin/env python3
"""
NGAME CPI Analysis Agent
Handles churn persistence index calculation and analysis for both training and fraud analysis flows
"""

import os
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NGameCpiAnalysisAgent:
    """
    NGAME CPI Analysis Agent for both training and fraud analysis flows.
    Handles churn persistence index calculation and analysis.
    """
    
    def __init__(self):
        self.name = "NGameCpiAnalysisAgent"
        self.yesterday_file = "quickbooks_ontology_Yesterday.ttl"
        self.today_file = "quickbooks_ontology_Today.ttl"
        self.cpi_array_size = 18  # 18 transaction types (incl. Vendors φ18)
        
        logger.info(f"🤖 {self.name} initialized")
    
    def analyze_cpi_coefficients(self) -> Dict[str, Any]:
        """
        Analyze churn persistence indexs between Yesterday.ttl and Today.ttl.
        Returns 17-element CPI array for both training and fraud analysis flows.
        """
        logger.info(f"🔍 {self.name}: Starting churn persistence index analysis")
        
        try:
            # Check if both TTL files exist
            if not os.path.exists(self.yesterday_file):
                logger.info(f"ℹ️  No {self.yesterday_file} found (first run)")
                return {
                    'success': False,
                    'error': 'No Yesterday.ttl file found (first run)',
                    'cpi_array': None
                }
            
            if not os.path.exists(self.today_file):
                logger.error(f"❌ {self.today_file} not found")
                return {
                    'success': False,
                    'error': f'{self.today_file} not found',
                    'cpi_array': None
                }
            
            # Load and analyze ontologies
            yesterday_analysis = self._analyze_ontology_file(self.yesterday_file)
            today_analysis = self._analyze_ontology_file(self.today_file)
            
            if not yesterday_analysis['success'] or not today_analysis['success']:
                return {
                    'success': False,
                    'error': 'Failed to analyze ontology files',
                    'cpi_array': None
                }
            
            # Calculate CPI coefficients
            cpi_result = self._calculate_cpi_coefficients(
                yesterday_analysis['ontology_data'],
                today_analysis['ontology_data']
            )

            if not cpi_result['success']:
                return cpi_result

            # Generate all CPI arrays (unweighted + dollar-weighted)
            cpi_arrays = self._generate_cpi_arrays(
                cpi_result['cpi_coefficients'],
                cpi_result.get('weighted_cpi_coefficients')
            )

            # Analyze property mutations
            property_mutations = self._calculate_property_mutations(
                yesterday_analysis['ontology_data'],
                today_analysis['ontology_data']
            )

            property_mutation_summary = self._summarize_property_mutations(property_mutations)

            result = {
                'success': True,
                # Unweighted Jaccard persistence score ∈ [0, 1]
                'cpi_array':             cpi_arrays['cpi_array'],
                # Dollar-weighted Jaccard persistence score ∈ [0, 1]
                # A large divergence from cpi_array signals dollar-disproportionate activity.
                'weighted_cpi_array':    cpi_arrays['weighted_cpi_array'],
                # Directional decomposition (unweighted)
                'addition_rate_array':   cpi_arrays['addition_rate_array'],
                'deletion_rate_array':   cpi_arrays['deletion_rate_array'],
                'cpi_coefficients':          cpi_result['cpi_coefficients'],
                'weighted_cpi_coefficients': cpi_result.get('weighted_cpi_coefficients', {}),
                'yesterday_stats':     yesterday_analysis['stats'],
                'today_stats':         today_analysis['stats'],
                'property_mutations':        property_mutations,
                'property_mutation_summary': property_mutation_summary,
                'analysis_timestamp':  datetime.now().isoformat()
            }

            logger.info(f"✅ {self.name}: CPI analysis completed successfully")
            logger.info(f"📊 Generated CPI arrays with {len(cpi_arrays['cpi_array'])} elements each")
            logger.info(f"💵 Dollar-weighted CPI array also computed")
            logger.info(f"🔄 Detected {len(property_mutations)} individuals with property mutations")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {self.name}: CPI analysis failed - {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'cpi_array': None
            }
    
    def _analyze_ontology_file(self, filepath: str) -> Dict[str, Any]:
        """Analyze a single ontology file."""
        logger.info(f"📊 {self.name}: Analyzing {filepath}")
        
        try:
            from rdflib import Graph, Namespace
            from rdflib.namespace import RDF, RDFS, OWL
            
            g = Graph()
            g.parse(filepath, format="turtle")
            
            # Extract ontology data
            ontology_data = {
                'transaction_types': {},
                'individuals': {},
                'properties': {}
            }
            
            qbo = Namespace("http://www.semanticweb.org/quickbooks/ontology#")
            
            # Extract transaction types and their individuals
            for s, p, o in g.triples((None, RDF.type, None)):
                if str(o).startswith("http://www.semanticweb.org/quickbooks/ontology#"):
                    class_name = str(o).split("#")[-1]
                    individual_uri = str(s)
                    
                    if class_name not in ontology_data['transaction_types']:
                        ontology_data['transaction_types'][class_name] = []
                    
                    # Extract properties for this individual
                    individual_props = {}
                    for prop_s, prop_p, prop_o in g.triples((s, None, None)):
                        if str(prop_p).startswith("http://www.semanticweb.org/quickbooks/ontology#"):
                            prop_name = str(prop_p).split("#")[-1]
                            individual_props[prop_name] = str(prop_o)
                    
                    ontology_data['transaction_types'][class_name].append({
                        'uri': individual_uri,
                        'properties': individual_props
                    })
            
            # Calculate statistics
            stats = {
                'file_size': os.path.getsize(filepath),
                'transaction_types_count': len(ontology_data['transaction_types']),
                'total_individuals': sum(len(individuals) for individuals in ontology_data['transaction_types'].values()),
                'transaction_type_breakdown': {
                    tx_type: len(individuals) 
                    for tx_type, individuals in ontology_data['transaction_types'].items()
                }
            }
            
            logger.info(f"✅ {self.name}: Analyzed {filepath} - {stats['total_individuals']} individuals across {stats['transaction_types_count']} types")
            
            return {
                'success': True,
                'ontology_data': ontology_data,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error analyzing {filepath}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_cpi_coefficients(self, yesterday_data: Dict[str, Any], today_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate both unweighted and dollar-weighted CPI coefficients for every
        transaction type found across both ontology snapshots.
        """
        logger.info(f"🔍 {self.name}: Calculating CPI coefficients (unweighted + dollar-weighted)")

        try:
            cpi_coefficients          = {}
            weighted_cpi_coefficients = {}

            all_types = set(yesterday_data['transaction_types'].keys()) | set(today_data['transaction_types'].keys())

            for tx_type in all_types:
                yesterday_individuals = yesterday_data['transaction_types'].get(tx_type, [])
                today_individuals     = today_data['transaction_types'].get(tx_type, [])

                cpi_coefficients[tx_type] = self._calculate_cpi_for_transaction_type(
                    yesterday_individuals, today_individuals, tx_type
                )
                weighted_cpi_coefficients[tx_type] = self._calculate_weighted_cpi_for_transaction_type(
                    yesterday_individuals, today_individuals, tx_type
                )

            logger.info(
                f"✅ {self.name}: Calculated CPI + wCPI coefficients "
                f"for {len(cpi_coefficients)} transaction types"
            )

            return {
                'success':                   True,
                'cpi_coefficients':          cpi_coefficients,
                'weighted_cpi_coefficients': weighted_cpi_coefficients,
            }

        except Exception as e:
            logger.error(f"❌ {self.name}: Error calculating CPI coefficients: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_cpi_for_transaction_type(
        self, yesterday_individuals: List[Dict], today_individuals: List[Dict], tx_type: str
    ) -> Dict[str, Any]:
        """
        Calculate the Churn Persistence Index (CPI) for a specific transaction type.

        Uses Jaccard similarity between yesterday's and today's transaction URI sets.

        Contingency counts (d is formally excluded — the universe of non-occurring
        transactions is undefined for financial data, not a workaround):
            a  =  |Y ∩ T|  — URIs present in both snapshots (retained)
            b  =  |Y \\ T|  — URIs in yesterday only (removed)
            c  =  |T \\ Y|  — URIs in today only (new additions)
            n  =  a + b + c — total unique URIs seen across both days

        Formula:
            CPI           = a / n          ∈ [0, 1]
            AdditionRate  = c / n          ∈ [0, 1]
            DeletionRate  = b / n          ∈ [0, 1]
            CPI + AdditionRate + DeletionRate = 1.0  (always)

        Edge case: when n == 0 (no transactions of this type in either snapshot),
        CPI is 1.0 by convention — absence is stable.
        """
        try:
            yesterday_uris = {ind['uri'] for ind in yesterday_individuals}
            today_uris     = {ind['uri'] for ind in today_individuals}

            a = len(yesterday_uris & today_uris)   # retained
            b = len(yesterday_uris - today_uris)   # removed
            c = len(today_uris - yesterday_uris)   # added
            n = a + b + c                          # total unique

            if n == 0:
                cpi           = 1.0
                addition_rate = 0.0
                deletion_rate = 0.0
            else:
                cpi           = a / n
                addition_rate = c / n
                deletion_rate = b / n

            logger.debug(
                f"📊 {tx_type}: retained={a}, added={c}, removed={b}, "
                f"CPI={cpi:.6f}, AddRate={addition_rate:.6f}, DelRate={deletion_rate:.6f}"
            )

            return {
                'cpi':           cpi,
                'addition_rate': addition_rate,
                'deletion_rate': deletion_rate,
                'retained':      a,
                'added':         c,
                'removed':       b,
            }

        except Exception as e:
            logger.error(f"❌ {self.name}: Error calculating CPI for {tx_type}: {e}")
            return {'cpi': 1.0, 'addition_rate': 0.0, 'deletion_rate': 0.0,
                    'retained': 0, 'added': 0, 'removed': 0}
    
    def _calculate_weighted_cpi_for_transaction_type(
        self, yesterday_individuals: List[Dict], today_individuals: List[Dict], tx_type: str
    ) -> Dict[str, Any]:
        """
        Calculate the Dollar-Weighted Churn Persistence Index (wCPI) for a transaction type.

        Replaces URI cardinality with dollar value (qb:hasTotalAmount) as the weight,
        making a single $50,000 payment as visible as 1,000 ordinary $50 transactions.

        Formula (Weighted Jaccard):
            w_i          =  qb:hasTotalAmount for transaction i
                            (falls back to 1.0 for entity records that carry no dollar value,
                             so wCPI degrades gracefully to unweighted CPI for those types)
            W_retained   =  Σ w_i  for i in Y ∩ T   (dollar value of retained transactions)
            W_added      =  Σ w_i  for i in T \\ Y   (dollar value of new additions)
            W_removed    =  Σ w_i  for i in Y \\ T   (dollar value of removed transactions)
            W_union      =  W_retained + W_added + W_removed

            wCPI           = W_retained / W_union  ∈ [0, 1]
            wAdditionRate  = W_added    / W_union  ∈ [0, 1]
            wDeletionRate  = W_removed  / W_union  ∈ [0, 1]
            wCPI + wAdditionRate + wDeletionRate = 1.0  (always)

        Fraud interpretation:
            wCPI << unweighted CPI  →  new additions carry outsized dollar value  (alarm)
            wCPI >> unweighted CPI  →  retained transactions dominate in dollars   (normal)

        Edge case: W_union == 0 → wCPI = 1.0 by convention (stable absence).
        """
        def _get_amount(ind: Dict) -> float:
            raw = ind.get('properties', {}).get('hasTotalAmount', None)
            if raw is None:
                return 1.0          # entity record with no monetary value; treat as $1
            try:
                v = float(str(raw).strip())
                return max(v, 0.0)  # guard against negative amounts in source data
            except (ValueError, TypeError):
                return 1.0

        try:
            yesterday_map = {ind['uri']: _get_amount(ind) for ind in yesterday_individuals}
            today_map     = {ind['uri']: _get_amount(ind) for ind in today_individuals}

            yesterday_uris = set(yesterday_map.keys())
            today_uris     = set(today_map.keys())

            retained_uris = yesterday_uris & today_uris
            added_uris    = today_uris     - yesterday_uris
            removed_uris  = yesterday_uris - today_uris

            # Use today's amount for retained (most recent value); yesterday's for removed
            W_retained = sum(today_map[u]     for u in retained_uris)
            W_added    = sum(today_map[u]     for u in added_uris)
            W_removed  = sum(yesterday_map[u] for u in removed_uris)
            W_union    = W_retained + W_added + W_removed

            if W_union == 0:
                w_cpi           = 1.0
                w_addition_rate = 0.0
                w_deletion_rate = 0.0
            else:
                w_cpi           = W_retained / W_union
                w_addition_rate = W_added    / W_union
                w_deletion_rate = W_removed  / W_union

            logger.debug(
                f"📊 {tx_type} (weighted): W_retained=${W_retained:,.2f}, "
                f"W_added=${W_added:,.2f}, W_removed=${W_removed:,.2f}, wCPI={w_cpi:.6f}"
            )

            return {
                'w_cpi':           w_cpi,
                'w_addition_rate': w_addition_rate,
                'w_deletion_rate': w_deletion_rate,
                'W_retained':      W_retained,
                'W_added':         W_added,
                'W_removed':       W_removed,
                'W_union':         W_union,
            }

        except Exception as e:
            logger.error(f"❌ {self.name}: Error calculating weighted CPI for {tx_type}: {e}")
            return {'w_cpi': 1.0, 'w_addition_rate': 0.0, 'w_deletion_rate': 0.0,
                    'W_retained': 0.0, 'W_added': 0.0, 'W_removed': 0.0, 'W_union': 0.0}

    def _generate_cpi_arrays(self, cpi_coefficients: Dict[str, Dict],
                             weighted_cpi_coefficients: Optional[Dict[str, Dict]] = None) -> Dict[str, List[float]]:
        """
        Generate standardized 17-element arrays from the CPI coefficients dicts.

        Returns:
            cpi_array            — Unweighted Jaccard persistence score ∈ [0, 1]
            addition_rate_array  — Fraction of today's population that is new ∈ [0, 1]
            deletion_rate_array  — Fraction of yesterday's population removed ∈ [0, 1]
            weighted_cpi_array   — Dollar-weighted Jaccard persistence score ∈ [0, 1]
                                   (equals cpi_array for entity types with no TotalAmt)

        All arrays are positionally aligned: index 0 = Customers, …, index 17 = Vendors.
        Default for a type absent from both snapshots: CPI=1.0, rates=0.0.
        """
        logger.info(f"📊 {self.name}: Generating CPI arrays")

        standard_transaction_types = [
            'Customers', 'Recurring_payments', 'Invoices', 'Payments', 'Time_Activities',
            'Bills', 'Bill_Payments', 'Expenses', 'Bank_Transactions', 'Sales_transactions',
            'Products', 'PurchaseOrders', 'Recurring_Transactions', 'Contractors',
            'Mileage', 'ChartOfAccounts', 'EmployeePayroll',
            'Vendors',          # φ18 — high-risk fraud hot-spot
        ]

        _absent          = {'cpi': 1.0, 'addition_rate': 0.0, 'deletion_rate': 0.0}
        _absent_weighted = {'w_cpi': 1.0}

        cpi_array           = []
        addition_rate_array = []
        deletion_rate_array = []
        weighted_cpi_array  = []

        for tx_type in standard_transaction_types:
            coeff = cpi_coefficients.get(tx_type, _absent)
            cpi_array.append(coeff['cpi'])
            addition_rate_array.append(coeff['addition_rate'])
            deletion_rate_array.append(coeff['deletion_rate'])

            if weighted_cpi_coefficients is not None:
                wcoeff = weighted_cpi_coefficients.get(tx_type, _absent_weighted)
                weighted_cpi_array.append(wcoeff['w_cpi'])
            else:
                weighted_cpi_array.append(coeff['cpi'])   # fall back to unweighted

        logger.info(f"✅ {self.name}: Generated CPI arrays with {len(cpi_array)} elements each")

        return {
            'cpi_array':           cpi_array,
            'addition_rate_array': addition_rate_array,
            'deletion_rate_array': deletion_rate_array,
            'weighted_cpi_array':  weighted_cpi_array,
        }
    
    def _calculate_property_mutations(self, yesterday_data: Dict[str, Any], today_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare property mutations for individuals present in both ontologies.
        Detects property changes (additions, removals, modifications) for common URIs.
        Returns dictionary mapping URIs to their property mutations by transaction type.
        """
        logger.info(f"🔄 {self.name}: Analyzing property mutations for common individuals")
        
        try:
            property_mutations = {}
            total_checked = 0
            total_mutations = 0
            
            # Iterate through transaction types
            for tx_type in yesterday_data['transaction_types'].keys():
                yesterday_individuals = yesterday_data['transaction_types'].get(tx_type, [])
                today_individuals = today_data['transaction_types'].get(tx_type, [])
                
                # Create URI→properties lookup dictionaries
                yesterday_props = {ind['uri']: ind['properties'] for ind in yesterday_individuals}
                today_props = {ind['uri']: ind['properties'] for ind in today_individuals}
                
                # Find common URIs (individuals present in both yesterday and today)
                common_uris = set(yesterday_props.keys()) & set(today_props.keys())
                total_checked += len(common_uris)
                
                # Compare properties for each common URI
                for uri in common_uris:
                    mutations = self._detect_property_changes(
                        yesterday_props[uri],
                        today_props[uri],
                        uri,
                        tx_type
                    )
                    
                    if mutations and any(mutations.values()):
                        property_mutations[uri] = {
                            'transaction_type': tx_type,
                            'mutations': mutations
                        }
                        total_mutations += 1
            
            logger.info(f"✅ {self.name}: Property mutation analysis completed")
            logger.info(f"📊 Checked {total_checked} common individuals, found {total_mutations} with mutations")
            
            return property_mutations
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error analyzing property mutations: {e}")
            return {}
    
    def _detect_property_changes(self, yesterday_props: Dict[str, str], today_props: Dict[str, str], 
                                 uri: str, tx_type: str) -> Dict[str, Any]:
        """
        Detect which properties changed for a given URI.
        Tracks additions, removals, and modifications.
        """
        try:
            changes = {
                'added': {},        # New properties in Today
                'removed': {},      # Properties removed in Today
                'modified': {}      # Properties with different values
            }
            
            # Check for modified or removed properties
            for prop_name, prop_value in yesterday_props.items():
                if prop_name not in today_props:
                    changes['removed'][prop_name] = prop_value
                elif today_props[prop_name] != prop_value:
                    changes['modified'][prop_name] = {
                        'yesterday_value': prop_value,
                        'today_value': today_props[prop_name]
                    }
            
            # Check for added properties
            for prop_name, prop_value in today_props.items():
                if prop_name not in yesterday_props:
                    changes['added'][prop_name] = prop_value
            
            # Return changes only if something actually changed
            return changes if any(changes.values()) else None
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error detecting property changes for {uri}: {e}")
            return None
    
    def _summarize_property_mutations(self, property_mutations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary statistics for property mutations.
        Aggregates mutation data for reporting and analysis.
        """
        logger.info(f"📊 {self.name}: Summarizing property mutations")
        
        try:
            summary = {
                'total_individuals_mutated': len(property_mutations),
                'mutation_categories': {
                    'added_properties': 0,
                    'removed_properties': 0,
                    'modified_properties': 0
                },
                'property_change_counts': {},
                'most_mutated_properties': {},
                'transaction_types_with_mutations': {}
            }
            
            # Count mutations by category
            for uri, mutation_data in property_mutations.items():
                mutations = mutation_data['mutations']
                tx_type = mutation_data['transaction_type']
                
                # Count by category
                summary['mutation_categories']['added_properties'] += len(mutations.get('added', {}))
                summary['mutation_categories']['removed_properties'] += len(mutations.get('removed', {}))
                summary['mutation_categories']['modified_properties'] += len(mutations.get('modified', {}))
                
                # Track by transaction type
                if tx_type not in summary['transaction_types_with_mutations']:
                    summary['transaction_types_with_mutations'][tx_type] = 0
                summary['transaction_types_with_mutations'][tx_type] += 1
                
                # Count property changes
                for prop_name in mutations.get('added', {}).keys():
                    key = f"added_{prop_name}"
                    summary['property_change_counts'][key] = summary['property_change_counts'].get(key, 0) + 1
                
                for prop_name in mutations.get('removed', {}).keys():
                    key = f"removed_{prop_name}"
                    summary['property_change_counts'][key] = summary['property_change_counts'].get(key, 0) + 1
                
                for prop_name in mutations.get('modified', {}).keys():
                    key = f"modified_{prop_name}"
                    summary['property_change_counts'][key] = summary['property_change_counts'].get(key, 0) + 1
            
            # Identify most frequently changed properties
            if summary['property_change_counts']:
                sorted_props = sorted(summary['property_change_counts'].items(), 
                                     key=lambda x: x[1], reverse=True)
                summary['most_mutated_properties'] = dict(sorted_props[:10])
            
            logger.info(f"✅ {self.name}: Property mutation summary generated")
            logger.info(f"📊 Total individuals with mutations: {summary['total_individuals_mutated']}")
            logger.info(f"📊 Added properties: {summary['mutation_categories']['added_properties']}")
            logger.info(f"📊 Removed properties: {summary['mutation_categories']['removed_properties']}")
            logger.info(f"📊 Modified properties: {summary['mutation_categories']['modified_properties']}")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error summarizing property mutations: {e}")
            return {}
    
    def get_cpi_array_summary(self, cpi_array: List[float]) -> Dict[str, Any]:
        """
        Get summary statistics for a CPI array.

        All values are in [0, 1].  A mean close to 1.0 indicates a very stable day;
        a mean close to 0.0 indicates high churn across all transaction types.
        """
        if not cpi_array:
            return {'mean': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0,
                    'range': 0.0, 'count': 0}

        arr = np.array(cpi_array)

        return {
            'mean':  float(np.mean(arr)),
            'std':   float(np.std(arr)),
            'min':   float(np.min(arr)),
            'max':   float(np.max(arr)),
            'range': float(np.max(arr) - np.min(arr)),
            'count': len(cpi_array)
        }

    
    def save_cpi_analysis_results(self, cpi_result: Dict[str, Any], output_file: str = "cpi_analysis_results.json"):
        """Save CPI analysis results to file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(cpi_result, f, indent=2, default=str)
            
            logger.info(f"💾 CPI analysis results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save CPI analysis results: {str(e)}")

    # ── Rolling Buffer (Phase 1 of SCPI / slow-burn upgrade) ────────────────

    def append_to_rolling_buffer(
        self,
        cpi_result: Dict[str, Any],
        buffer_file: str = "NGAME_CPI_Rolling_Buffer.json",
        max_days: int = 30,
    ) -> bool:
        """
        Append today's CPI arrays to the rolling buffer file and prune to max_days.

        Each buffer record:
            {
                "date":                 "YYYY-MM-DD",
                "timestamp":            "<ISO-8601>",
                "cpi_array":            [18 floats],   # unweighted Jaccard persistence
                "weighted_cpi_array":   [18 floats],   # dollar-weighted variant
                "addition_rate_array":  [18 floats],
                "deletion_rate_array":  [18 floats],
            }

        Called automatically by NGameFraudAnalysisFlowManager after each
        successful CPI analysis so that NGameSequenceCpiAgent can read the
        most recent L days on demand.

        Returns True on success, False on any error (non-fatal to the daily run).
        """
        if not cpi_result.get('success'):
            logger.warning(f"⚠️  {self.name}: Skipping buffer append — cpi_result has success=False")
            return False

        try:
            buffer: List[Dict] = []
            if os.path.exists(buffer_file):
                with open(buffer_file, 'r') as fh:
                    buffer = json.load(fh)
                if not isinstance(buffer, list):
                    logger.warning(f"⚠️  {self.name}: Buffer file malformed — resetting")
                    buffer = []

            timestamp = cpi_result.get('analysis_timestamp', datetime.now().isoformat())
            date_str = timestamp[:10]  # "YYYY-MM-DD"

            record = {
                'date':                date_str,
                'timestamp':           timestamp,
                'cpi_array':           cpi_result.get('cpi_array',           []),
                'weighted_cpi_array':  cpi_result.get('weighted_cpi_array',  []),
                'addition_rate_array': cpi_result.get('addition_rate_array', []),
                'deletion_rate_array': cpi_result.get('deletion_rate_array', []),
            }

            # Replace existing record for the same date (idempotent re-runs)
            buffer = [r for r in buffer if r.get('date') != date_str]
            buffer.append(record)

            # Keep only the most recent max_days records
            buffer = buffer[-max_days:]

            with open(buffer_file, 'w') as fh:
                json.dump(buffer, fh, indent=2, default=str)

            logger.info(
                f"💾 {self.name}: Rolling buffer updated — "
                f"{len(buffer)} day(s) stored in {buffer_file}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ {self.name}: Failed to update rolling buffer: {e}")
            return False

    def load_rolling_buffer(
        self,
        buffer_file: str = "NGAME_CPI_Rolling_Buffer.json",
    ) -> List[Dict]:
        """Return the rolling buffer as a list of daily records (oldest first)."""
        if not os.path.exists(buffer_file):
            return []
        try:
            with open(buffer_file, 'r') as fh:
                data = json.load(fh)
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"❌ {self.name}: Failed to load rolling buffer: {e}")
            return []

def main():
    """Main function for testing the CPI analysis agent."""
    print("🚀 NGAME CPI Analysis Agent Test")
    print("=" * 50)

    agent = NGameCpiAnalysisAgent()
    result = agent.analyze_cpi_coefficients()

    if result['success']:
        print(f"\n✅ CPI analysis completed successfully!")
        print(f"📊 CPI array length: {len(result['cpi_array'])}")

        # CPI array summary (persistence scores)
        cpi_summary = agent.get_cpi_array_summary(result['cpi_array'])
        print(f"\n📊 CPI array summary (persistence, range [0,1]):")
        print(f"   Mean:  {cpi_summary['mean']:.6f}")
        print(f"   Std:   {cpi_summary['std']:.6f}")
        print(f"   Min:   {cpi_summary['min']:.6f}")
        print(f"   Max:   {cpi_summary['max']:.6f}")
        print(f"   Range: {cpi_summary['range']:.6f}")

        # Directional decomposition summaries
        add_summary = agent.get_cpi_array_summary(result['addition_rate_array'])
        del_summary = agent.get_cpi_array_summary(result['deletion_rate_array'])
        print(f"\n📊 Addition rate summary (new transactions, range [0,1]):")
        print(f"   Mean: {add_summary['mean']:.6f}   Max: {add_summary['max']:.6f}")
        print(f"\n📊 Deletion rate summary (removed transactions, range [0,1]):")
        print(f"   Mean: {del_summary['mean']:.6f}   Max: {del_summary['max']:.6f}")

        # Property mutation analysis
        print(f"\n🔄 Property Mutation Analysis:")
        mutation_summary = result.get('property_mutation_summary', {})
        if mutation_summary:
            print(f"   Total individuals with mutations: {mutation_summary.get('total_individuals_mutated', 0)}")
            print(f"   Added properties:    {mutation_summary.get('mutation_categories', {}).get('added_properties', 0)}")
            print(f"   Removed properties:  {mutation_summary.get('mutation_categories', {}).get('removed_properties', 0)}")
            print(f"   Modified properties: {mutation_summary.get('mutation_categories', {}).get('modified_properties', 0)}")

            if mutation_summary.get('most_mutated_properties'):
                print(f"\n   Top 10 most mutated properties:")
                for prop, count in list(mutation_summary['most_mutated_properties'].items())[:10]:
                    print(f"      • {prop}: {count} occurrences")

            if mutation_summary.get('transaction_types_with_mutations'):
                print(f"\n   Mutations by transaction type:")
                for tx_type, count in mutation_summary['transaction_types_with_mutations'].items():
                    print(f"      • {tx_type}: {count} individuals")
        else:
            print("   No property mutations detected")

        agent.save_cpi_analysis_results(result)
        return True
    else:
        print(f"\n❌ CPI analysis failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    main()
