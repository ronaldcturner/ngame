#!/usr/bin/env python3
"""
NGAME Account Mapping Agent
Maps top anomalies to Chart of Accounts for fraud analysis
"""

import os
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NGameAccountMappingAgent:
    """
    NGAME Account Mapping Agent for fraud analysis flow.
    Maps top anomalies to Chart of Accounts.
    """
    
    def __init__(self):
        self.name = "NGameAccountMappingAgent"
        self.today_file = "quickbooks_ontology_Today.ttl"
        
        logger.info(f"🤖 {self.name} initialized")
    
    def map_to_chart_of_accounts(self, top_anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Map top anomalies to Chart of Accounts.
        Implements Requirement 5 from Chart 2.
        """
        logger.info(f"📊 {self.name}: Mapping top anomalies to Chart of Accounts")
        
        try:
            # Load Chart of Accounts from Today.ttl
            chart_of_accounts = self._load_chart_of_accounts()
            
            if not chart_of_accounts:
                return {
                    'success': False,
                    'error': 'Failed to load Chart of Accounts from Today.ttl'
                }
            
            # Map each anomaly to relevant accounts
            account_mappings = []
            
            for anomaly in top_anomalies:
                transaction_type = anomaly['transaction_type']
                accounts = self._find_accounts_for_transaction_type(
                    transaction_type, chart_of_accounts
                )
                
                mapping = {
                    'anomaly': anomaly,
                    'transaction_type': transaction_type,
                    'accounts': accounts,
                    'account_count': len(accounts)
                }
                
                account_mappings.append(mapping)
            
            # Calculate mapping statistics
            mapping_stats = self._calculate_mapping_statistics(account_mappings)
            
            result = {
                'success': True,
                'account_mappings': account_mappings,
                'mapping_stats': mapping_stats,
                'mapping_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ {self.name}: Mapped {len(account_mappings)} anomalies to accounts")
            
            # Log mapping summary
            for mapping in account_mappings:
                logger.info(f"  {mapping['transaction_type']}: {mapping['account_count']} accounts")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error mapping to Chart of Accounts: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_chart_of_accounts(self) -> Dict[str, Any]:
        """Load Chart of Accounts from Today.ttl file."""
        logger.info(f"📊 {self.name}: Loading Chart of Accounts from {self.today_file}")
        
        try:
            from rdflib import Graph, Namespace
            from rdflib.namespace import RDF, RDFS, OWL
            
            g = Graph()
            g.parse(self.today_file, format="turtle")
            
            chart_of_accounts = {
                'accounts': {},
                'account_types': {},
                'total_accounts': 0
            }
            
            qbo = Namespace("http://www.semanticweb.org/quickbooks/ontology#")
            
            # Extract Chart of Accounts individuals
            for s, p, o in g.triples((None, RDF.type, qbo.ChartOfAccounts)):
                account_uri = str(s)
                account_name = account_uri.split("/")[-1] if "/" in account_uri else account_uri.split("#")[-1]
                
                # Extract account properties
                account_props = {}
                for prop_s, prop_p, prop_o in g.triples((s, None, None)):
                    if str(prop_p).startswith("http://www.semanticweb.org/quickbooks/ontology#"):
                        prop_name = str(prop_p).split("#")[-1]
                        account_props[prop_name] = str(prop_o)
                
                chart_of_accounts['accounts'][account_name] = {
                    'uri': account_uri,
                    'properties': account_props
                }
                
                # Track account types
                account_type = account_props.get('AccountType', 'Unknown')
                if account_type not in chart_of_accounts['account_types']:
                    chart_of_accounts['account_types'][account_type] = []
                chart_of_accounts['account_types'][account_type].append(account_name)
            
            chart_of_accounts['total_accounts'] = len(chart_of_accounts['accounts'])
            
            logger.info(f"✅ {self.name}: Loaded {chart_of_accounts['total_accounts']} accounts")
            return chart_of_accounts
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error loading Chart of Accounts: {e}")
            return {}
    
    def _find_accounts_for_transaction_type(self, transaction_type: str, chart_of_accounts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find accounts associated with a specific transaction type."""
        logger.info(f"🔍 {self.name}: Finding accounts for {transaction_type}")
        
        relevant_accounts = []
        
        # Define transaction type to account type mappings
        transaction_to_account_mappings = {
            'Customers': ['Accounts Receivable', 'Sales', 'Service Revenue'],
            'Recurring_payments': ['Accounts Receivable', 'Sales', 'Service Revenue'],
            'Invoices': ['Accounts Receivable', 'Sales', 'Service Revenue'],
            'Payments': ['Cash', 'Bank', 'Accounts Receivable'],
            'Time_Activities': ['Service Revenue', 'Labor', 'Overhead'],
            'Bills': ['Accounts Payable', 'Expenses', 'Cost of Goods Sold'],
            'Bill_Payments': ['Accounts Payable', 'Cash', 'Bank'],
            'Expenses': ['Expenses', 'Cost of Goods Sold', 'Overhead'],
            'Bank_Transactions': ['Cash', 'Bank', 'Accounts Receivable', 'Accounts Payable'],
            'Sales_transactions': ['Sales', 'Service Revenue', 'Product Revenue'],
            'Products': ['Inventory', 'Cost of Goods Sold', 'Product Revenue'],
            'PurchaseOrders': ['Accounts Payable', 'Inventory', 'Expenses'],
            'Recurring_Transactions': ['Accounts Receivable', 'Sales', 'Service Revenue'],
            'Contractors': ['Accounts Payable', 'Contractor Expenses', 'Labor'],
            'Mileage': ['Travel Expenses', 'Vehicle Expenses', 'Mileage'],
            'ChartOfAccounts': ['All Account Types'],
            'EmployeePayroll': ['Payroll Expenses', 'Employee Benefits', 'Payroll Taxes'],
            'Vendors':         ['Accounts Payable', 'Expenses', 'Cost of Goods Sold'],  # φ18
        }
        
        # Get relevant account types for this transaction type
        relevant_account_types = transaction_to_account_mappings.get(transaction_type, ['All Account Types'])
        
        # Find accounts matching these types
        for account_name, account_data in chart_of_accounts['accounts'].items():
            account_type = account_data['properties'].get('AccountType', 'Unknown')
            
            if 'All Account Types' in relevant_account_types or account_type in relevant_account_types:
                relevant_accounts.append({
                    'name': account_name,
                    'type': account_type,
                    'properties': account_data['properties'],
                    'uri': account_data['uri']
                })
        
        logger.info(f"✅ {self.name}: Found {len(relevant_accounts)} accounts for {transaction_type}")
        return relevant_accounts
    
    def _calculate_mapping_statistics(self, account_mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for account mappings."""
        logger.info(f"📊 {self.name}: Calculating mapping statistics")
        
        if not account_mappings:
            return {
                'total_mappings': 0,
                'total_accounts': 0,
                'average_accounts_per_mapping': 0.0,
                'account_type_distribution': {}
            }
        
        total_accounts = sum(mapping['account_count'] for mapping in account_mappings)
        account_type_distribution = {}
        
        # Count account types across all mappings
        for mapping in account_mappings:
            for account in mapping['accounts']:
                account_type = account['type']
                account_type_distribution[account_type] = account_type_distribution.get(account_type, 0) + 1
        
        stats = {
            'total_mappings': len(account_mappings),
            'total_accounts': total_accounts,
            'average_accounts_per_mapping': total_accounts / len(account_mappings) if account_mappings else 0.0,
            'account_type_distribution': account_type_distribution
        }
        
        logger.info(f"✅ {self.name}: Mapping statistics calculated")
        return stats
    
    def get_mapping_summary(self, account_mappings: List[Dict[str, Any]]) -> str:
        """Get human-readable summary of account mappings."""
        if not account_mappings:
            return "No account mappings found"
        
        summary_lines = [f"Account Mappings for {len(account_mappings)} Anomalies:"]
        
        for mapping in account_mappings:
            summary_lines.append(
                f"  {mapping['transaction_type']}: {mapping['account_count']} accounts"
            )
        
        return "\n".join(summary_lines)
    
    def save_mapping_results(self, mapping_result: Dict[str, Any], output_file: str = "account_mapping_results.json"):
        """Save account mapping results to file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(mapping_result, f, indent=2, default=str)
            
            logger.info(f"💾 Account mapping results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save account mapping results: {str(e)}")

def main():
    """Main function for testing the account mapping agent."""
    print("🚀 NGAME Account Mapping Agent Test")
    print("=" * 50)
    
    # Initialize agent
    agent = NGameAccountMappingAgent()
    
    # Create test top anomalies
    test_top_anomalies = [
        {
            'index': 0,
            'transaction_type': 'Customers',
            'today_value': 0.8,
            'average_value': 0.3,
            'absolute_difference': 0.5,
            'percent_deviation': 166.67,
            'deviation_level': 'HIGH',
            'rank': 1
        },
        {
            'index': 5,
            'transaction_type': 'Bills',
            'today_value': 0.6,
            'average_value': 0.4,
            'absolute_difference': 0.2,
            'percent_deviation': 50.0,
            'deviation_level': 'HIGH',
            'rank': 2
        }
    ]
    
    # Map to Chart of Accounts
    result = agent.map_to_chart_of_accounts(test_top_anomalies)
    
    if result['success']:
        print(f"\n✅ Account mapping completed successfully!")
        print(f"📊 Mapped {len(result['account_mappings'])} anomalies to accounts")
        
        # Show summary
        summary = agent.get_mapping_summary(result['account_mappings'])
        print(f"\n{summary}")
        
        # Show statistics
        stats = result['mapping_stats']
        print(f"\n📊 Mapping Statistics:")
        print(f"   Total mappings: {stats['total_mappings']}")
        print(f"   Total accounts: {stats['total_accounts']}")
        print(f"   Average accounts per mapping: {stats['average_accounts_per_mapping']:.1f}")
        print(f"   Account type distribution: {stats['account_type_distribution']}")
        
        # Save results
        agent.save_mapping_results(result)
        
        return True
    else:
        print(f"\n❌ Account mapping failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    main()
