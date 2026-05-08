#!/usr/bin/env python3
"""
Phase 1 Director Agent for NGAME Agent-Driven Pipeline
Orchestrates Data Extraction, Authentication, and Ontology Construction
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from ngame_quickbooks_oauth import (
    QuickBooksOAuthError,
    default_quickbooks_config_path,
    ensure_quickbooks_auth,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase1DirectorAgent:
    """
    Phase 1 Director Agent that orchestrates the data extraction and ontology construction pipeline.
    Manages Authentication, Data Extraction, and Ontology Construction agents.
    """
    
    def __init__(self):
        self.agents = {}
        self.pipeline_state = {
            'status': 'initialized',
            'start_time': None,
            'end_time': None,
            'current_step': None,
            'errors': [],
            'results': {}
        }
        self.quickbooks_config_path = default_quickbooks_config_path()
        self.input_files = {
            'curated_types': 'Curated Transaction Types.ttl',
            'config': self.quickbooks_config_path,
        }
        self.output_files = {
            'ontology': 'quickbooks_final_clean_ontology_with_user_transaction_types.ttl',
            'summary': 'phase1_extraction_summary.json'
        }
        
    def initialize_agents(self):
        """Initialize all agents for Phase 1."""
        logger.info("🤖 Initializing Phase 1 Agents...")
        
        # Initialize Authentication & API Management Agent
        self.agents['auth_agent'] = AuthenticationAgent()
        
        # Initialize Data Extraction Agent
        self.agents['extraction_agent'] = DataExtractionAgent()
        
        # Initialize Ontology Construction Agent
        self.agents['ontology_agent'] = OntologyConstructionAgent()
        
        # Initialize Summary Generation Agent
        self.agents['summary_agent'] = SummaryGenerationAgent()
        
        logger.info("✅ All Phase 1 agents initialized successfully")
        
    def validate_inputs(self) -> bool:
        """Validate that required input files exist."""
        logger.info("🔍 Validating input files...")
        
        missing_files = []
        for name, filepath in self.input_files.items():
            if not os.path.exists(filepath):
                missing_files.append(f"{name}: {filepath}")
        
        if missing_files:
            logger.error(f"❌ Missing input files: {missing_files}")
            return False
        
        logger.info("✅ All input files validated")
        return True
        
    def execute_pipeline(self) -> Dict[str, Any]:
        """Execute the complete Phase 1 agent-driven pipeline."""
        logger.info("🚀 Starting Phase 1 Agent-Driven Pipeline Execution")
        self.pipeline_state['start_time'] = datetime.now()
        self.pipeline_state['status'] = 'running'
        
        try:
            # Step 1: Initialize agents
            self.pipeline_state['current_step'] = 'initializing_agents'
            self.initialize_agents()
            
            # Step 2: Validate inputs
            self.pipeline_state['current_step'] = 'validating_inputs'
            if not self.validate_inputs():
                raise Exception("Input validation failed")
            
            # Step 3: Load curated transaction types
            self.pipeline_state['current_step'] = 'loading_transaction_types'
            transaction_types = self.agents['ontology_agent'].load_curated_transaction_types()
            if not transaction_types:
                raise Exception("Failed to load curated transaction types")
            self.pipeline_state['results']['transaction_types'] = transaction_types
            
            # Step 4: Authentication & API setup
            self.pipeline_state['current_step'] = 'authentication'
            auth_result = self.agents['auth_agent'].setup_authentication()
            if not auth_result['success']:
                raise Exception(f"Authentication failed: {auth_result['error']}")
            self.pipeline_state['results']['auth'] = auth_result
            
            # Step 5: Data extraction
            self.pipeline_state['current_step'] = 'data_extraction'
            extraction_result = self.agents['extraction_agent'].extract_all_data(
                transaction_types, 
                auth_result['client']
            )
            if not extraction_result['success']:
                raise Exception(f"Data extraction failed: {extraction_result['error']}")
            self.pipeline_state['results']['extraction'] = extraction_result
            
            # Step 6: Ontology construction
            self.pipeline_state['current_step'] = 'ontology_construction'
            ontology_result = self.agents['ontology_agent'].construct_ontology(
                extraction_result['data'],
                transaction_types,
                self.output_files['ontology']
            )
            if not ontology_result['success']:
                raise Exception(f"Ontology construction failed: {ontology_result['error']}")
            self.pipeline_state['results']['ontology'] = ontology_result
            
            # Step 7: Summary generation
            self.pipeline_state['current_step'] = 'summary_generation'
            summary_result = self.agents['summary_agent'].generate_summary(
                transaction_types,
                extraction_result['data'],
                self.output_files['summary']
            )
            self.pipeline_state['results']['summary'] = summary_result
            
            self.pipeline_state['status'] = 'completed'
            self.pipeline_state['end_time'] = datetime.now()
            
            logger.info("✅ Phase 1 Agent-Driven Pipeline completed successfully")
            return self.pipeline_state
            
        except Exception as e:
            logger.error(f"❌ Pipeline execution failed: {str(e)}")
            self.pipeline_state['status'] = 'failed'
            self.pipeline_state['errors'].append(str(e))
            self.pipeline_state['end_time'] = datetime.now()
            return self.pipeline_state
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            'status': self.pipeline_state['status'],
            'current_step': self.pipeline_state['current_step'],
            'start_time': self.pipeline_state['start_time'],
            'end_time': self.pipeline_state['end_time'],
            'errors': self.pipeline_state['errors'],
            'agents_initialized': len(self.agents),
            'results_available': list(self.pipeline_state['results'].keys())
        }


class AuthenticationAgent:
    """
    Agent responsible for QuickBooks API authentication and token management.
    """
    
    def __init__(self):
        self.name = "AuthenticationAgent"
        logger.info(f"🤖 {self.name} initialized")
    
    def setup_authentication(self) -> Dict[str, Any]:
        """Set up QuickBooks API authentication."""
        logger.info(f"🔐 {self.name}: Setting up authentication...")
        
        try:
            from quickbooks import QuickBooks

            bundle = ensure_quickbooks_auth(
                default_quickbooks_config_path(),
                interactive_on_invalid_grant=True,
            )
            auth_client = bundle.auth_client
            
            # Create QuickBooks client
            client = QuickBooks(
                auth_client=auth_client,
                refresh_token=auth_client.refresh_token,
                company_id=bundle.realm_id,
            )
            
            logger.info(f"✅ {self.name}: Authentication successful")
            return {
                'success': True,
                'client': client,
                'auth_client': auth_client,
                'realm_id': bundle.realm_id
            }
            
        except QuickBooksOAuthError as e:
            logger.error(f"❌ {self.name}: Authentication failed - {e}")
            return {
                'success': False,
                'error': str(e),
                'client': None
            }
        except Exception as e:
            logger.error(f"❌ {self.name}: Authentication failed - {e}")
            return {
                'success': False,
                'error': str(e),
                'client': None
            }


class DataExtractionAgent:
    """
    Agent responsible for extracting data from QuickBooks API for all transaction types.
    """
    
    def __init__(self):
        self.name = "DataExtractionAgent"
        logger.info(f"🤖 {self.name} initialized")
    
    def extract_all_data(self, transaction_types: Dict[str, Any], client) -> Dict[str, Any]:
        """Extract data for all transaction types using CDC approach."""
        logger.info(f"📊 {self.name}: Extracting data for {len(transaction_types)} transaction types...")
        
        try:
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
                        objects = api_class.all(qb=client)
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
                'stats': extraction_stats
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Data extraction failed - {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {},
                'stats': {}
            }


class OntologyConstructionAgent:
    """
    Agent responsible for constructing semantic ontologies from extracted data.
    """
    
    def __init__(self):
        self.name = "OntologyConstructionAgent"
        logger.info(f"🤖 {self.name} initialized")
    
    def load_curated_transaction_types(self) -> Dict[str, Any]:
        """Load curated transaction types from TTL file."""
        logger.info(f"📚 {self.name}: Loading curated transaction types...")
        
        curated_file = "Curated Transaction Types.ttl"
        if not os.path.exists(curated_file):
            logger.error(f"❌ {curated_file} not found!")
            return {}
        
        try:
            from rdflib import Graph, Namespace
            from rdflib.namespace import RDF, RDFS, OWL
            
            g = Graph()
            g.parse(curated_file, format="turtle")
            
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
    
    def construct_ontology(self, data: Dict[str, Any], transaction_types: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Construct clean Turtle ontology file."""
        logger.info(f"🏗️  {self.name}: Constructing ontology...")
        
        try:
            with open(output_file, 'w') as f:
                # Write header with proper prefixes
                f.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n")
                f.write("@prefix qb: <http://www.semanticweb.org/quickbooks/ontology#> .\n")
                f.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
                f.write("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n")
                f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n\n")
                
                # Write class definitions
                f.write("# Class Definitions\n")
                
                # Define UserTransactionType as base class
                f.write("qb:UserTransactionType a owl:Class ;\n")
                f.write("    rdfs:subClassOf owl:Thing ;\n")
                f.write("    rdfs:label \"User Transaction Type\" ;\n")
                f.write("    rdfs:comment \"Base class for all QuickBooks transaction types\" .\n\n")
                
                # Define all transaction types as subclasses
                for tx_type, info in transaction_types.items():
                    label = info['label'] or tx_type
                    comment = info['comment'] or f"A {tx_type.lower()} transaction in QuickBooks"
                    class_name = tx_type.replace('_', '')
                    
                    f.write(f"qb:{class_name} a owl:Class ;\n")
                    f.write(f"    rdfs:subClassOf qb:UserTransactionType ;\n")
                    f.write(f"    rdfs:label \"{label}\" ;\n")
                    f.write(f"    rdfs:comment \"{comment}\" .\n\n")
                
                # Write property definitions
                f.write("# Property Definitions\n")
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
                    f.write(f"{prop} a owl:DatatypeProperty ;\n")
                    f.write(f"    rdfs:label \"{label}\" ;\n")
                    f.write(f"    rdfs:comment \"{comment}\" .\n\n")
                
                # Write individuals for all transaction types
                for tx_type, info in transaction_types.items():
                    data_key = tx_type.lower()
                    class_name = tx_type.replace('_', '')
                    
                    if data.get(data_key):
                        f.write(f"# {tx_type} Individuals\n")
                        
                        for i, item in enumerate(data[data_key]):
                            item_id = item.get('Id', f'unknown_{i}')
                            f.write(f"<http://www.semanticweb.org/quickbooks/{data_key}/{item_id}> a qb:{class_name}")
                            
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
                                f.write(" ;\n")
                                f.write(" ;\n".join(properties))
                            f.write(" .\n\n")
            
            logger.info(f"✅ {self.name}: Ontology construction completed - {output_file}")
            return {
                'success': True,
                'output_file': output_file,
                'transaction_types_count': len(transaction_types),
                'total_records': sum(len(data.get(tx_type.lower(), [])) for tx_type in transaction_types)
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Ontology construction failed - {e}")
            return {
                'success': False,
                'error': str(e)
            }


class SummaryGenerationAgent:
    """
    Agent responsible for generating comprehensive extraction summaries.
    """
    
    def __init__(self):
        self.name = "SummaryGenerationAgent"
        logger.info(f"🤖 {self.name} initialized")
    
    def generate_summary(self, transaction_types: Dict[str, Any], data: Dict[str, Any], output_file: str) -> Dict[str, Any]:
        """Generate comprehensive extraction summary."""
        logger.info(f"📊 {self.name}: Generating extraction summary...")
        
        try:
            total_records = 0
            extraction_summary = {
                'extraction_timestamp': datetime.now().isoformat(),
                'transaction_types': {},
                'risk_analysis': {},
                'total_records': 0,
                'total_types': len(transaction_types)
            }
            
            # Analyze each transaction type
            for tx_type, info in transaction_types.items():
                data_key = tx_type.lower()
                count = len(data.get(data_key, []))
                total_records += count
                
                risk_level = info.get('risk_level', 'Unknown')
                frequency = info.get('transaction_frequency', 0)
                
                extraction_summary['transaction_types'][tx_type] = {
                    'record_count': count,
                    'risk_level': risk_level,
                    'transaction_frequency': frequency,
                    'label': info.get('label', tx_type),
                    'comment': info.get('comment', '')
                }
            
            extraction_summary['total_records'] = total_records
            
            # Risk analysis summary
            risk_counts = {}
            for tx_type, info in transaction_types.items():
                risk = info.get('risk_level', 'Unknown')
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            
            extraction_summary['risk_analysis'] = {
                'risk_distribution': risk_counts,
                'high_risk_types': [tx for tx, info in transaction_types.items() 
                                   if info.get('risk_level') == 'High'],
                'medium_risk_types': [tx for tx, info in transaction_types.items() 
                                    if info.get('risk_level') == 'Medium'],
                'low_risk_types': [tx for tx, info in transaction_types.items() 
                                  if info.get('risk_level') == 'Low']
            }
            
            # Save summary to file
            with open(output_file, 'w') as f:
                json.dump(extraction_summary, f, indent=2)
            
            logger.info(f"✅ {self.name}: Summary generated - {total_records} total records")
            return {
                'success': True,
                'output_file': output_file,
                'summary': extraction_summary
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Summary generation failed - {e}")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """Main function to run the Phase 1 director agent."""
    _repo = os.path.dirname(os.path.abspath(__file__))
    if os.getcwd() != _repo:
        os.chdir(_repo)
    from ngame_env import load_ngame_dotenv

    load_ngame_dotenv()

    print("🚀 NGAME Phase 1 Agent-Driven Pipeline")
    print("Data Extraction → Authentication → Ontology Construction")
    print("=" * 70)
    
    # Initialize director agent
    director = Phase1DirectorAgent()
    
    # Execute pipeline
    results = director.execute_pipeline()
    
    # Display results
    print("\n📊 PHASE 1 PIPELINE EXECUTION RESULTS")
    print("=" * 70)
    print(f"Status: {results['status']}")
    print(f"Start Time: {results['start_time']}")
    print(f"End Time: {results['end_time']}")
    print(f"Current Step: {results['current_step']}")
    
    if results['errors']:
        print(f"Errors: {results['errors']}")
    else:
        print("✅ No errors detected")
    
    if results['results']:
        print(f"Results Generated: {list(results['results'].keys())}")
        
        # Display extraction summary
        if 'extraction' in results['results']:
            extraction = results['results']['extraction']
            if extraction['success']:
                stats = extraction['stats']
                print(f"\n📊 DATA EXTRACTION SUMMARY")
                print(f"Total Records: {stats['total_records']}")
                print(f"Successful Extractions: {stats['successful_extractions']}")
                print(f"Failed Extractions: {stats['failed_extractions']}")
        
        # Display ontology summary
        if 'ontology' in results['results']:
            ontology = results['results']['ontology']
            if ontology['success']:
                print(f"\n🏗️  ONTOLOGY CONSTRUCTION SUMMARY")
                print(f"Output File: {ontology['output_file']}")
                print(f"Transaction Types: {ontology['transaction_types_count']}")
                print(f"Total Records: {ontology['total_records']}")
    
    print(f"\n📁 Output Files:")
    for name, filepath in director.output_files.items():
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✅ {name}: {filepath} ({file_size} bytes)")
        else:
            print(f"  ❌ {name}: {filepath} (not found)")


if __name__ == "__main__":
    main()
