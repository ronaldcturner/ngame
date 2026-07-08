#!/usr/bin/env python3
"""
NGAME Anomaly Identification Agent
Identifies top anomalies from ranked differences for fraud analysis
"""

import os
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from ngame_transaction_types import (
    dollar_signal_duplicates_count,
    is_actionable_anomaly,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NGameAnomalyIdentificationAgent:
    """
    NGAME Anomaly Identification Agent for fraud analysis flow.
    Identifies top anomalies from ranked differences.
    """
    
    def __init__(self):
        self.name = "NGameAnomalyIdentificationAgent"
        
        # 1-based mapping — aligns with 'index': i+1 emitted by NGameChurnComparisonAgent
        self.transaction_type_mappings = {
            1:  'Customers',
            2:  'Recurring_payments',
            3:  'Invoices',
            4:  'Payments',
            5:  'Time_Activities',
            6:  'Bills',
            7:  'Bill_Payments',
            8:  'Expenses',
            9:  'Bank_Transactions',
            10: 'Sales_transactions',
            11: 'Products',
            12: 'PurchaseOrders',
            13: 'Recurring_Transactions',
            14: 'Contractors',
            15: 'Mileage',
            16: 'ChartOfAccounts',
            17: 'EmployeePayroll',
            18: 'Vendors',          # φ18 — high-risk fraud hot-spot
        }
        
        logger.info(f"🤖 {self.name} initialized")
    
    def identify_top_anomalies(self, ranked_differences: List[Dict[str, Any]], top_n: int = 3) -> Dict[str, Any]:
        """
        Identify top N anomalies from ranked differences.
        Implements part of Requirement 5 from Chart 2.
        """
        logger.info(f"🔍 {self.name}: Identifying top {top_n} anomalies")
        
        try:
            def _composite_rank_key(diff: Dict[str, Any]) -> float:
                count_z = abs(float(diff.get('abs_z_score') or 0.0))
                dollar_z = abs(float(diff.get('dollar_abs_z_score') or 0.0))
                index = int(diff.get('index') or 0)
                tx_type = self.transaction_type_mappings.get(index, '')
                if dollar_signal_duplicates_count(diff, tx_type):
                    return count_z
                return max(count_z, dollar_z)

            # Only surface categories with elevated count or dollar signal — not
            # quiet-day statistical noise (e.g. ChartOfAccounts with CPI=1.0).
            eligible = [d for d in ranked_differences if is_actionable_anomaly(d)]
            sorted_differences = sorted(
                eligible,
                key=_composite_rank_key,
                reverse=True,
            )
            top_anomalies = sorted_differences[:top_n]
            
            # Enrich anomalies with transaction type information
            enriched_anomalies = []
            
            for anomaly in top_anomalies:
                index = anomaly['index']
                transaction_type = self.transaction_type_mappings.get(index, f'Unknown_{index}')
                
                enriched_anomaly = {
                    'index': index,
                    'phi_index': f'φ{index}',
                    'transaction_type': transaction_type,
                    'today_value': anomaly['today_value'],
                    'average_value': anomaly['average_value'],
                    'absolute_difference': anomaly['absolute_difference'],
                    'percent_deviation': anomaly['percent_deviation'],
                    'deviation_level': anomaly['deviation_level'],
                    'z_score': anomaly.get('z_score', 0.0),
                    'abs_z_score': anomaly.get('abs_z_score', 0.0),
                    'dollar_alarm_level': anomaly.get('dollar_alarm_level', 'LOW'),
                    'dollar_alarm': bool(anomaly.get('dollar_alarm')),
                    'dollar_z_score': anomaly.get('dollar_z_score', 0.0),
                    'dollar_abs_z_score': anomaly.get('dollar_abs_z_score', 0.0),
                    'composite_alarm': bool(anomaly.get('composite_alarm')),
                    'rank': anomaly['rank'],
                }
                
                enriched_anomalies.append(enriched_anomaly)
            
            # Calculate anomaly statistics
            anomaly_stats = self._calculate_anomaly_statistics(enriched_anomalies)
            
            result = {
                'success': True,
                'top_anomalies': enriched_anomalies,
                'anomaly_stats': anomaly_stats,
                'identification_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ {self.name}: Identified {len(enriched_anomalies)} top anomalies")
            
            # Log top anomalies
            for i, anomaly in enumerate(enriched_anomalies, 1):
                logger.info(f"  {i}. {anomaly['transaction_type']}: {anomaly['percent_deviation']:.2f}% deviation")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error identifying top anomalies: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_anomaly_statistics(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for identified anomalies."""
        logger.info(f"📊 {self.name}: Calculating anomaly statistics")
        
        if not anomalies:
            return {
                'count': 0,
                'mean_deviation': 0.0,
                'max_deviation': 0.0,
                'min_deviation': 0.0,
                'deviation_levels': {}
            }
        
        percent_deviations = [anomaly['percent_deviation'] for anomaly in anomalies]
        deviation_levels = [anomaly['deviation_level'] for anomaly in anomalies]
        
        # Count deviation levels
        level_counts = {}
        for level in deviation_levels:
            level_counts[level] = level_counts.get(level, 0) + 1
        
        stats = {
            'count': len(anomalies),
            'mean_deviation': float(np.mean(percent_deviations)),
            'std_deviation': float(np.std(percent_deviations)),
            'max_deviation': float(np.max(percent_deviations)),
            'min_deviation': float(np.min(percent_deviations)),
            'deviation_levels': level_counts
        }
        
        logger.info(f"✅ {self.name}: Anomaly statistics calculated")
        return stats
    
    def get_anomaly_summary(self, anomalies: List[Dict[str, Any]]) -> str:
        """Get human-readable summary of anomalies."""
        if not anomalies:
            return "No anomalies identified"
        
        summary_lines = [f"Top {len(anomalies)} Anomalies Identified:"]
        
        for i, anomaly in enumerate(anomalies, 1):
            z = anomaly.get('z_score', 0.0)
            summary_lines.append(
                f"  {i}. {anomaly['transaction_type']}: "
                f"z={z:.3f}  ({anomaly['deviation_level']} risk)"
            )
        
        return "\n".join(summary_lines)
    
    def save_anomaly_results(self, anomaly_result: Dict[str, Any], output_file: str = "anomaly_identification_results.json"):
        """Save anomaly identification results to file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(anomaly_result, f, indent=2, default=str)
            
            logger.info(f"💾 Anomaly identification results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save anomaly identification results: {str(e)}")

def main():
    """Main function for testing the anomaly identification agent."""
    print("🚀 NGAME Anomaly Identification Agent Test")
    print("=" * 50)
    
    # Initialize agent
    agent = NGameAnomalyIdentificationAgent()
    
    # Test data uses 1-based indices (matching NGameChurnComparisonAgent output)
    test_ranked_differences = [
        {'index': 1,  'today_value': 0.8, 'average_value': 0.3, 'std_value': 0.05, 'absolute_difference': 0.5, 'z_score': 10.0, 'abs_z_score': 10.0, 'percent_deviation': 166.67, 'deviation_level': 'HIGH', 'rank': 1},
        {'index': 6,  'today_value': 0.6, 'average_value': 0.4, 'std_value': 0.05, 'absolute_difference': 0.2, 'z_score':  4.0, 'abs_z_score':  4.0, 'percent_deviation': 50.0,   'deviation_level': 'HIGH', 'rank': 2},
        {'index': 11, 'today_value': 0.3, 'average_value': 0.2, 'std_value': 0.05, 'absolute_difference': 0.1, 'z_score':  2.0, 'abs_z_score':  2.0, 'percent_deviation': 50.0,   'deviation_level': 'MEDIUM', 'rank': 3},
    ]
    
    # Identify top anomalies
    result = agent.identify_top_anomalies(test_ranked_differences, top_n=3)
    
    if result['success']:
        print(f"\n✅ Anomaly identification completed successfully!")
        print(f"📊 Identified {len(result['top_anomalies'])} top anomalies")
        
        # Show summary
        summary = agent.get_anomaly_summary(result['top_anomalies'])
        print(f"\n{summary}")
        
        # Show statistics
        stats = result['anomaly_stats']
        print(f"\n📊 Anomaly Statistics:")
        print(f"   Mean deviation: {stats['mean_deviation']:.2f}%")
        print(f"   Max deviation: {stats['max_deviation']:.2f}%")
        print(f"   Min deviation: {stats['min_deviation']:.2f}%")
        print(f"   Deviation levels: {stats['deviation_levels']}")
        
        # Save results
        agent.save_anomaly_results(result)
        
        return True
    else:
        print(f"\n❌ Anomaly identification failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    main()
