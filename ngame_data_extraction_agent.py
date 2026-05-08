#!/usr/bin/env python3
"""
NGAME Data Extraction Agent
Handles data extraction and ontology construction for both training and fraud analysis.
Supports QuickBooks API and WAVE accounting via GraphQL (GraphiQL) API.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from ngame_quickbooks_oauth import default_quickbooks_config_path
from ngame_wave_graphql_client import default_wave_config_path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Supported data sources
SOURCE_QUICKBOOKS = "quickbooks"
SOURCE_WAVE = "wave"


class NGameDataExtractionAgent:
    """
    NGAME Data Extraction Agent for both training and fraud analysis flows.
    Supports QuickBooks API or WAVE accounting GraphQL API; builds same ontology output.
    """
    
    def __init__(self, source: str = SOURCE_QUICKBOOKS):
        from ngame_env import load_ngame_dotenv

        load_ngame_dotenv()

        self.source = source.lower() if source else SOURCE_QUICKBOOKS
        if self.source not in (SOURCE_QUICKBOOKS, SOURCE_WAVE):
            raise ValueError(f"source must be '{SOURCE_QUICKBOOKS}' or '{SOURCE_WAVE}', got '{source}'")
        self.name = "NGameDataExtractionAgent"
        self.config_file = (
            default_quickbooks_config_path()
            if self.source == SOURCE_QUICKBOOKS
            else default_wave_config_path()
        )
        self.curated_types_file = "Curated Transaction Types.ttl"
        prefix = "quickbooks" if self.source == SOURCE_QUICKBOOKS else "wave"
        self.yesterday_file = f"{prefix}_ontology_Yesterday.ttl"
        self.today_file = f"{prefix}_ontology_Today.ttl"
        
        # QuickBooks API configuration (used only when source=quickbooks)
        self.client = None
        self.auth_client = None
        
        logger.info(f"🤖 {self.name} initialized (source={self.source})")
    
    def extract_daily_data(self) -> Dict[str, Any]:
        """
        Extract daily data and generate Today.ttl.
        Uses QuickBooks API or WAVE GraphQL API depending on source.
        Implements Phase I of both training and fraud analysis flows.
        """
        logger.info(f"📊 {self.name}: Starting daily data extraction (source={self.source})")
        
        try:
            # Step 1: File Management - Shift Today.ttl to Yesterday.ttl
            self.manage_ttl_files()
            
            if self.source == SOURCE_WAVE:
                # WAVE: no OAuth; extract via GraphQL
                extraction_result = self.extract_wave_data()
            else:
                # Step 2: Authentication (QuickBooks only)
                auth_result = self.setup_authentication()
                if not auth_result['success']:
                    return auth_result
                # Step 3: Data Extraction (QuickBooks)
                extraction_result = self.extract_quickbooks_data()
            
            if not extraction_result['success']:
                return extraction_result
            
            # Step 4: Ontology Construction
            ontology_result = self.construct_ontology(extraction_result['data'])
            if not ontology_result['success']:
                return ontology_result
            
            # Step 5: Generate Today.ttl
            ttl_result = self.generate_today_ttl(ontology_result['ontology'])
            if not ttl_result['success']:
                return ttl_result
            
            result = {
                'success': True,
                'source': self.source,
                'extraction_stats': extraction_result['stats'],
                'ontology_stats': ontology_result['stats'],
                'ttl_file': self.today_file,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ {self.name}: Daily data extraction completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Daily data extraction failed - {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'source': self.source,
                'timestamp': datetime.now().isoformat()
            }
    
    def extract_wave_data(self) -> Dict[str, Any]:
        """Extract data from WAVE accounting via GraphQL API and normalize for ontology."""
        logger.info(f"📊 {self.name}: Extracting WAVE data (GraphQL)")
        
        try:
            from ngame_wave_graphql_client import NGameWaveGraphQLClient, load_wave_config
            
            transaction_types = self.load_curated_transaction_types()
            if not transaction_types:
                return {
                    'success': False,
                    'error': 'Failed to load curated transaction types'
                }
            
            config = load_wave_config(self.config_file)
            wave_cfg = config.get('wave_graphql') or config
            endpoint = (
                (os.getenv("WAVE_GRAPHQL_ENDPOINT") or "").strip()
                or wave_cfg.get('endpoint', 'https://gql.waveapps.com/graphql/public')
            )
            access_token = (os.getenv("WAVE_ACCESS_TOKEN") or "").strip() or wave_cfg.get('access_token')
            business_id = (os.getenv("WAVE_BUSINESS_ID") or "").strip() or wave_cfg.get('business_id')
            if not access_token or not business_id:
                return {
                    'success': False,
                    'error': (
                        'WAVE needs access_token and business_id: set wave_graphql in wave_config.json '
                        'or environment variables WAVE_ACCESS_TOKEN and WAVE_BUSINESS_ID '
                        '(optional WAVE_GRAPHQL_ENDPOINT, WAVE_CONFIG_PATH).'
                    ),
                }
            
            client = NGameWaveGraphQLClient(
                endpoint=endpoint,
                access_token=access_token,
                business_id=business_id,
            )
            wave_data = client.fetch_all_business_data()
            
            # Merge with all curated transaction type keys (missing = [])
            data = {}
            for tx_type in transaction_types:
                key = tx_type.lower()
                data[key] = wave_data.get(key, wave_data.get(tx_type.replace('_', '').lower(), []))
            
            total_records = sum(len(v) for v in data.values())
            extraction_stats = {
                'total_types': len(transaction_types),
                'successful_extractions': sum(1 for k, v in data.items() if len(v) > 0),
                'failed_extractions': 0,
                'total_records': total_records,
                'extraction_details': {tx: {'success': True, 'record_count': len(data.get(tx.lower(), [])), 'error': None} for tx in transaction_types}
            }
            
            logger.info(f"✅ {self.name}: WAVE extraction completed - {total_records} total records")
            return {
                'success': True,
                'data': data,
                'stats': extraction_stats,
                'transaction_types': transaction_types
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: WAVE extraction failed - {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {},
                'stats': {}
            }
    
    def manage_ttl_files(self):
        """Manage TTL files - shift Today.ttl to Yesterday.ttl."""
        logger.info(f"📁 {self.name}: Managing TTL files")
        
        if os.path.exists(self.today_file):
            if os.path.exists(self.yesterday_file):
                os.remove(self.yesterday_file)
            
            os.rename(self.today_file, self.yesterday_file)
            logger.info(f"✅ Shifted {self.today_file} → {self.yesterday_file}")
        else:
            logger.info(f"ℹ️  No {self.today_file} found (first run)")
    
    def setup_authentication(self) -> Dict[str, Any]:
        """Set up QuickBooks API authentication."""
        logger.info(f"🔐 {self.name}: Setting up authentication")
        
        try:
            # Import required modules
            from quickbooks import QuickBooks
            from ngame_quickbooks_oauth import ensure_quickbooks_auth, QuickBooksOAuthError

            bundle = ensure_quickbooks_auth(self.config_file, interactive_on_invalid_grant=True)
            self.auth_client = bundle.auth_client
            
            # Create QuickBooks client
            self.client = QuickBooks(
                auth_client=self.auth_client,
                refresh_token=self.auth_client.refresh_token,
                company_id=bundle.realm_id,
            )
            
            logger.info(f"✅ {self.name}: Authentication successful")
            return {
                'success': True,
                'client': self.client,
                'auth_client': self.auth_client
            }
            
        except QuickBooksOAuthError as e:
            logger.error(f"❌ {self.name}: Authentication failed - {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"❌ {self.name}: Authentication failed - {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _refresh_access_token(self) -> bool:
        """Refresh the access token."""
        try:
            logger.info("🔄 Attempting to refresh token...")
            self.auth_client.refresh()
            logger.info("✅ Token refreshed successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Error refreshing token: {e}")
            return False
    
    def extract_quickbooks_data(self) -> Dict[str, Any]:
        """Extract data from QuickBooks API for all transaction types."""
        logger.info(f"📊 {self.name}: Extracting QuickBooks data")
        
        try:
            # Load curated transaction types
            transaction_types = self.load_curated_transaction_types()
            if not transaction_types:
                return {
                    'success': False,
                    'error': 'Failed to load curated transaction types'
                }
            
            # API mappings for transaction types
            api_mappings = {
                'Vendors': ('quickbooks.objects.vendor', 'Vendor'),
                'Customers': ('quickbooks.objects.customer', 'Customer'),
                'Invoices': ('quickbooks.objects.invoice', 'Invoice'),
                'Payments': ('quickbooks.objects.payment', 'Payment'),
                'Time_Activities': ('quickbooks.objects.timeactivity', 'TimeActivity'),
                'Bills': ('quickbooks.objects.bill', 'Bill'),
                'Bill_Payments': ('quickbooks.objects.billpayment', 'BillPayment'),
                'Expenses': ('quickbooks.objects.purchase', 'Purchase'),
                'ExpenseTransaction': ('quickbooks.objects.purchase', 'Purchase'),
                'Bank_Transactions': ('quickbooks.objects.deposit', 'Deposit'),
                'BankDeposits': ('quickbooks.objects.deposit', 'Deposit'),
                'BankTransfers': ('quickbooks.objects.transfer', 'Transfer'),
                'BankReconciliation': ('quickbooks.objects.bankaccount', 'BankAccount'),
                'CustomerPayments': ('quickbooks.objects.payment', 'Payment'),
                'Sales_transactions': ('quickbooks.objects.salesreceipt', 'SalesReceipt'),
                'SalesReceipts': ('quickbooks.objects.salesreceipt', 'SalesReceipt'),
                'Estimates': ('quickbooks.objects.estimate', 'Estimate'),
                'Refunds': ('quickbooks.objects.creditmemo', 'CreditMemo'),
                'Products': ('quickbooks.objects.item', 'Item'),
                'Products_and_Services': ('quickbooks.objects.item', 'Item'),
                'Inventory': ('quickbooks.objects.item', 'Item'),
                'InventoryAdjustments': ('quickbooks.objects.item', 'Item'),
                'PurchaseOrders': ('quickbooks.objects.purchaseorder', 'PurchaseOrder'),
                'Receipts': ('quickbooks.objects.receipt', 'Receipt'),
                'Recurring_Transactions': ('quickbooks.objects.recurringtransaction', 'RecurringTransaction'),
                'Contractors': ('quickbooks.objects.vendor', 'Vendor'),
                'Mileage': ('quickbooks.objects.vehicle', 'Vehicle'),
                'ChartOfAccounts': ('quickbooks.objects.account', 'Account'),
                'CreditCardTransactions': ('quickbooks.objects.creditcardpayment', 'CreditCardPayment'),
                'EmployeePayroll': ('quickbooks.objects.employee', 'Employee'),
                'EmployeeBenefits': ('quickbooks.objects.employee', 'Employee'),
                'PayrollTaxes': ('quickbooks.objects.taxrate', 'TaxRate'),
                'Payroll': ('quickbooks.objects.employee', 'Employee')
            }
            
            data = {}
            extraction_stats = {
                'total_types': len(transaction_types),
                'successful_extractions': 0,
                'failed_extractions': 0,
                'total_records': 0,
                'extraction_details': {}
            }
            
            # Retrieve data for each transaction type
            for tx_type, info in transaction_types.items():
                if tx_type in api_mappings:
                    module_name, class_name = api_mappings[tx_type]
                    try:
                        logger.info(f"🔍 Retrieving {tx_type}...")
                        module = __import__(module_name, fromlist=[class_name])
                        api_class = getattr(module, class_name)
                        objects = api_class.all(qb=self.client)
                        data[tx_type.lower()] = [obj.to_dict() for obj in objects]
                        
                        record_count = len(objects)
                        extraction_stats['successful_extractions'] += 1
                        extraction_stats['total_records'] += record_count
                        extraction_stats['extraction_details'][tx_type] = {
                            'success': True,
                            'record_count': record_count,
                            'error': None
                        }
                        
                        logger.info(f"✅ Retrieved {record_count} {tx_type.lower()}")
                        
                    except Exception as e:
                        logger.error(f"❌ Error retrieving {tx_type}: {e}")
                        data[tx_type.lower()] = []
                        extraction_stats['failed_extractions'] += 1
                        extraction_stats['extraction_details'][tx_type] = {
                            'success': False,
                            'record_count': 0,
                            'error': str(e)
                        }
                else:
                    logger.warning(f"⚠️  No API mapping for {tx_type} - skipping")
                    data[tx_type.lower()] = []
                    extraction_stats['extraction_details'][tx_type] = {
                        'success': False,
                        'record_count': 0,
                        'error': 'No API mapping available'
                    }
            
            logger.info(f"✅ {self.name}: Data extraction completed - {extraction_stats['total_records']} total records")
            return {
                'success': True,
                'data': data,
                'stats': extraction_stats,
                'transaction_types': transaction_types
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Data extraction failed - {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {},
                'stats': {}
            }
    
    def load_curated_transaction_types(self) -> Dict[str, Any]:
        """Load curated transaction types from TTL file."""
        logger.info(f"📚 {self.name}: Loading curated transaction types")
        
        if not os.path.exists(self.curated_types_file):
            logger.error(f"❌ {self.curated_types_file} not found!")
            return {}
        
        try:
            from rdflib import Graph, Namespace
            from rdflib.namespace import RDF, RDFS, OWL
            
            g = Graph()
            g.parse(self.curated_types_file, format="turtle")
            
            # Extract all subclasses and their properties
            transaction_types = {}
            qbo = Namespace("http://www.semanticweb.org/quickbooks/ontology#")
            
            # Get all subclasses
            for s, p, o in g.triples((None, RDFS.subClassOf, None)):
                if str(o).startswith("http://www.semanticweb.org/quickbooks/ontology#") or \
                   str(o).startswith("http://www.co-ode.org/ontologies/ont.owl#"):
                    class_name = str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1]
                    parent_name = str(o).split("#")[-1] if "#" in str(o) else str(o).split("/")[-1]
                    
                    if class_name not in transaction_types:
                        transaction_types[class_name] = {
                            'parent': parent_name,
                            'risk_level': None,
                            'transaction_frequency': None,
                            'label': None,
                            'comment': None
                        }
            
            # Get risk levels and frequencies from individuals
            for s, p, o in g.triples((None, qbo.riskLevel, None)):
                individual_name = str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1]
                if individual_name in transaction_types:
                    transaction_types[individual_name]['risk_level'] = str(o)
            
            for s, p, o in g.triples((None, qbo.transactionFrequency, None)):
                individual_name = str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1]
                if individual_name in transaction_types:
                    transaction_types[individual_name]['transaction_frequency'] = int(str(o))
            
            # Get labels and comments
            for s, p, o in g.triples((None, RDFS.label, None)):
                individual_name = str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1]
                if individual_name in transaction_types:
                    transaction_types[individual_name]['label'] = str(o)
            
            for s, p, o in g.triples((None, RDFS.comment, None)):
                individual_name = str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1]
                if individual_name in transaction_types:
                    transaction_types[individual_name]['comment'] = str(o)
            
            logger.info(f"✅ {self.name}: Loaded {len(transaction_types)} transaction types")
            return transaction_types
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error loading curated transaction types: {e}")
            return {}
    
    def construct_ontology(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Construct semantic ontology from extracted data."""
        logger.info(f"🏗️  {self.name}: Constructing ontology")
        
        try:
            # Load transaction types
            transaction_types = self.load_curated_transaction_types()
            
            ontology_content = self._generate_ontology_content(data, transaction_types)
            
            ontology_stats = {
                'transaction_types_count': len(transaction_types),
                'total_records': sum(len(data.get(tx_type.lower(), [])) for tx_type in transaction_types),
                'ontology_size': len(ontology_content)
            }
            
            logger.info(f"✅ {self.name}: Ontology construction completed")
            return {
                'success': True,
                'ontology': ontology_content,
                'stats': ontology_stats
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Ontology construction failed - {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_ontology_content(self, data: Dict[str, Any], transaction_types: Dict[str, Any]) -> str:
        """Generate ontology content in Turtle format."""
        ontology_lines = []
        
        # Write header with proper prefixes
        ontology_lines.extend([
            "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
            "@prefix qb: <http://www.semanticweb.org/quickbooks/ontology#> .",
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
            "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
            ""
        ])
        
        # Write class definitions
        ontology_lines.extend([
            "# Class Definitions",
            "",
            "qb:UserTransactionType a owl:Class ;",
            "    rdfs:subClassOf owl:Thing ;",
            "    rdfs:label \"User Transaction Type\" ;",
            "    rdfs:comment \"Base class for all QuickBooks transaction types\" .",
            ""
        ])
        
        # Define all transaction types as subclasses
        for tx_type, info in transaction_types.items():
            label = info['label'] or tx_type
            comment = info['comment'] or f"A {tx_type.lower()} transaction in QuickBooks"
            class_name = tx_type.replace('_', '')
            
            ontology_lines.extend([
                f"qb:{class_name} a owl:Class ;",
                f"    rdfs:subClassOf qb:UserTransactionType ;",
                f"    rdfs:label \"{label}\" ;",
                f"    rdfs:comment \"{comment}\" .",
                ""
            ])
        
        # Write property definitions
        ontology_lines.extend([
            "# Property Definitions",
            ""
        ])
        
        properties = [
            ("qb:hasName", "Name", "Name of the entity"),
            ("qb:hasCompanyName", "CompanyName", "Company name"),
            ("qb:hasEmail", "Email", "Email address"),
            ("qb:hasPhone", "Phone", "Phone number"),
            ("qb:isActive", "Active", "Active status"),
            ("qb:hasDocNumber", "DocNumber", "Document number"),
            ("qb:hasTotalAmount", "TotalAmount", "Total amount"),
            ("qb:hasBalance", "Balance", "Balance amount"),
            ("qb:hasTransactionDate", "TransactionDate", "Transaction date"),
            ("qb:hasVendorType", "VendorType", "Type of vendor"),
            ("qb:hasGivenName", "GivenName", "First name"),
            ("qb:hasFamilyName", "FamilyName", "Last name"),
            ("qb:hasPaymentMethod", "PaymentMethod", "Payment method"),
            ("qb:hasUnappliedAmount", "UnappliedAmount", "Unapplied amount"),
            ("qb:hasHours", "Hours", "Hours worked"),
            ("qb:hasMinutes", "Minutes", "Minutes worked"),
            ("qb:hasHourlyRate", "HourlyRate", "Hourly rate"),
            ("qb:hasBillableStatus", "BillableStatus", "Billable status"),
            ("qb:hasDescription", "Description", "Activity description"),
            ("qb:riskLevel", "RiskLevel", "Risk level for fraud detection"),
            ("qb:transactionFrequency", "TransactionFrequency", "Typical frequency of this transaction type")
        ]
        
        for prop, label, comment in properties:
            ontology_lines.extend([
                f"{prop} a owl:DatatypeProperty ;",
                f"    rdfs:label \"{label}\" ;",
                f"    rdfs:comment \"{comment}\" .",
                ""
            ])
        
        # Write individuals for all transaction types
        for tx_type, info in transaction_types.items():
            data_key = tx_type.lower()
            class_name = tx_type.replace('_', '')
            
            if data.get(data_key):
                ontology_lines.extend([
                    f"# {tx_type} Individuals",
                    ""
                ])
                
                for i, item in enumerate(data[data_key]):
                    item_id = item.get('Id', f'unknown_{i}')
                    ontology_lines.append(f"<http://www.semanticweb.org/quickbooks/{data_key}/{item_id}> a qb:{class_name}")
                    
                    properties = []
                    
                    # Common properties
                    if item.get('Name'):
                        properties.append(f"    qb:hasName \"{item['Name']}\"")
                    if item.get('CompanyName'):
                        properties.append(f"    qb:hasCompanyName \"{item['CompanyName']}\"")
                    if item.get('PrimaryEmailAddr'):
                        properties.append(f"    qb:hasEmail \"{item['PrimaryEmailAddr']}\"")
                    if item.get('PrimaryPhone'):
                        properties.append(f"    qb:hasPhone \"{item['PrimaryPhone']}\"")
                    if item.get('Active'):
                        properties.append(f"    qb:isActive {str(item['Active']).lower()}")
                    
                    # Transaction-specific properties
                    if item.get('DocNumber'):
                        properties.append(f"    qb:hasDocNumber \"{item['DocNumber']}\"")
                    if item.get('TotalAmt'):
                        properties.append(f"    qb:hasTotalAmount {item['TotalAmt']}")
                    if item.get('Balance'):
                        properties.append(f"    qb:hasBalance {item['Balance']}")
                    if item.get('TxnDate'):
                        properties.append(f"    qb:hasTransactionDate \"{item['TxnDate']}\"^^xsd:date")
                    if item.get('UnappliedAmt'):
                        properties.append(f"    qb:hasUnappliedAmount {item['UnappliedAmt']}")
                    if item.get('PaymentMethodRef'):
                        properties.append(f"    qb:hasPaymentMethod \"{item['PaymentMethodRef']}\"")
                    if item.get('Hours'):
                        properties.append(f"    qb:hasHours {item['Hours']}")
                    if item.get('Minutes'):
                        properties.append(f"    qb:hasMinutes {item['Minutes']}")
                    if item.get('HourlyRate'):
                        properties.append(f"    qb:hasHourlyRate {item['HourlyRate']}")
                    if item.get('BillableStatus'):
                        properties.append(f"    qb:hasBillableStatus \"{item['BillableStatus']}\"")
                    if item.get('Description'):
                        properties.append(f"    qb:hasDescription \"{item['Description']}\"")
                    if item.get('GivenName'):
                        properties.append(f"    qb:hasGivenName \"{item['GivenName']}\"")
                    if item.get('FamilyName'):
                        properties.append(f"    qb:hasFamilyName \"{item['FamilyName']}\"")
                    if item.get('VendorType'):
                        properties.append(f"    qb:hasVendorType \"{item['VendorType']}\"")
                    
                    # Add risk level and frequency
                    risk_level = info.get('risk_level', 'Medium')
                    frequency = info.get('transaction_frequency', 0)
                    
                    if risk_level is not None:
                        properties.append(f"    qb:riskLevel \"{risk_level}\"")
                    if frequency is not None:
                        properties.append(f"    qb:transactionFrequency {frequency}")
                    
                    if properties:
                        ontology_lines.append(" ;")
                        ontology_lines.append(" ;\n".join(properties))
                    ontology_lines.append(" .")
                    ontology_lines.append("")
        
        return "\n".join(ontology_lines)
    
    def generate_today_ttl(self, ontology_content: str) -> Dict[str, Any]:
        """Generate Today.ttl file from ontology content."""
        logger.info(f"📄 {self.name}: Generating Today.ttl")
        
        try:
            with open(self.today_file, 'w') as f:
                f.write(ontology_content)
            
            file_size = os.path.getsize(self.today_file)
            
            logger.info(f"✅ {self.name}: Today.ttl generated successfully ({file_size} bytes)")
            return {
                'success': True,
                'file': self.today_file,
                'file_size': file_size
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Failed to generate Today.ttl - {e}")
            return {
                'success': False,
                'error': str(e)
            }

def main():
    """Main function for testing the data extraction agent."""
    print("🚀 NGAME Data Extraction Agent Test")
    print("=" * 50)
    
    # Initialize agent
    agent = NGameDataExtractionAgent()
    
    # Execute daily data extraction
    result = agent.extract_daily_data()
    
    if result['success']:
        print(f"\n✅ Data extraction completed successfully!")
        print(f"📁 TTL file: {result['ttl_file']}")
        print(f"📊 Records extracted: {result['extraction_stats']['total_records']}")
        print(f"📊 Transaction types: {result['extraction_stats']['total_types']}")
        return True
    else:
        print(f"\n❌ Data extraction failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    main()
