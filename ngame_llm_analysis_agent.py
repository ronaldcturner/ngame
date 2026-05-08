#!/usr/bin/env python3
"""
NGAME LLM Analysis Agent
Uses RAG/Ollama LLM to match accounts with Misappropriated Assets taxonomy
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NGameLLMAnalysisAgent:
    """
    NGAME LLM Analysis Agent for fraud analysis flow.
    Uses RAG/Ollama LLM to analyze misappropriation risks.
    """
    
    def __init__(self):
        self.name = "NGameLLMAnalysisAgent"
        self.ollama_base_url = "http://localhost:11434"
        self.model_name = "llama3.1:8b"  # Default model, can be configured
        
        logger.info(f"🤖 {self.name} initialized")
    
    def analyze_misappropriation_risks(self, account_mappings: List[Dict[str, Any]], taxonomy_file: str) -> Dict[str, Any]:
        """
        Analyze misappropriation risks using RAG/Ollama LLM.
        Implements Requirement 6 from Chart 2.
        """
        logger.info(f"🤖 {self.name}: Analyzing misappropriation risks with LLM")
        
        try:
            # Load asset misappropriation taxonomy
            taxonomy = self._load_misappropriation_taxonomy(taxonomy_file)
            
            if not taxonomy:
                return {
                    'success': False,
                    'error': f'Failed to load misappropriation taxonomy from {taxonomy_file}'
                }
            
            # Analyze each account mapping
            matches = []
            risk_assessments = []
            
            for mapping in account_mappings:
                transaction_type = mapping['transaction_type']
                accounts = mapping['accounts']
                
                logger.info(f"🔍 Analyzing {len(accounts)} accounts for {transaction_type}")
                
                for account in accounts:
                    # Analyze account with LLM
                    analysis_result = self._analyze_account_with_llm(account, taxonomy, transaction_type)
                    
                    if analysis_result['success']:
                        matches.extend(analysis_result['matches'])
                        risk_assessments.append(analysis_result['risk_assessment'])
            
            # Calculate overall risk assessment
            overall_risk = self._calculate_overall_risk(risk_assessments)
            
            result = {
                'success': True,
                'matches': matches,
                'risk_assessments': risk_assessments,
                'overall_risk': overall_risk,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ {self.name}: LLM analysis completed successfully")
            logger.info(f"📊 Found {len(matches)} potential misappropriation matches")
            logger.info(f"🎯 Overall risk level: {overall_risk['risk_level']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {self.name}: LLM analysis failed - {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_misappropriation_taxonomy(self, taxonomy_file: str) -> Dict[str, Any]:
        """Load asset misappropriation taxonomy from TTL file."""
        logger.info(f"📚 {self.name}: Loading misappropriation taxonomy from {taxonomy_file}")
        
        try:
            from rdflib import Graph, Namespace
            from rdflib.namespace import RDF, RDFS, OWL
            
            g = Graph()
            g.parse(taxonomy_file, format="turtle")
            
            taxonomy = {
                'misappropriation_types': {},
                'risk_indicators': {},
                'total_types': 0
            }
            
            # Define namespace for misappropriation taxonomy
            misapp = Namespace("http://www.semanticweb.org/misappropriation/ontology#")
            
            # Extract misappropriation types and their properties
            for s, p, o in g.triples((None, RDF.type, None)):
                if str(o).startswith("http://www.semanticweb.org/misappropriation/ontology#"):
                    class_name = str(o).split("#")[-1]
                    individual_uri = str(s)
                    
                    # Extract properties for this misappropriation type
                    misapp_props = {}
                    for prop_s, prop_p, prop_o in g.triples((s, None, None)):
                        if str(prop_p).startswith("http://www.semanticweb.org/misappropriation/ontology#"):
                            prop_name = str(prop_p).split("#")[-1]
                            misapp_props[prop_name] = str(prop_o)
                    
                    taxonomy['misappropriation_types'][class_name] = {
                        'uri': individual_uri,
                        'properties': misapp_props
                    }
            
            taxonomy['total_types'] = len(taxonomy['misappropriation_types'])
            
            logger.info(f"✅ {self.name}: Loaded {taxonomy['total_types']} misappropriation types")
            return taxonomy
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error loading misappropriation taxonomy: {e}")
            return {}
    
    def _analyze_account_with_llm(self, account: Dict[str, Any], taxonomy: Dict[str, Any], transaction_type: str) -> Dict[str, Any]:
        """Analyze a single account with LLM against misappropriation taxonomy."""
        logger.info(f"🤖 {self.name}: Analyzing account {account['name']} with LLM")
        
        try:
            # Prepare account information for LLM analysis
            account_info = self._prepare_account_info(account, transaction_type)
            
            # Prepare taxonomy information for LLM
            taxonomy_info = self._prepare_taxonomy_info(taxonomy)
            
            # Create LLM prompt
            prompt = self._create_analysis_prompt(account_info, taxonomy_info)
            
            # Query LLM
            llm_response = self._query_ollama_llm(prompt)
            
            if not llm_response['success']:
                return {
                    'success': False,
                    'error': llm_response['error'],
                    'matches': [],
                    'risk_assessment': None
                }
            
            # Parse LLM response
            analysis_result = self._parse_llm_response(llm_response['response'], account, taxonomy)
            
            return {
                'success': True,
                'matches': analysis_result['matches'],
                'risk_assessment': analysis_result['risk_assessment']
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error analyzing account {account['name']}: {e}")
            return {
                'success': False,
                'error': str(e),
                'matches': [],
                'risk_assessment': None
            }
    
    def _prepare_account_info(self, account: Dict[str, Any], transaction_type: str) -> str:
        """Prepare account information for LLM analysis."""
        account_info = f"Account: {account['name']}\n"
        account_info += f"Type: {account['type']}\n"
        account_info += f"Transaction Type: {transaction_type}\n"
        
        # Add relevant properties
        properties = account['properties']
        if properties.get('AccountSubType'):
            account_info += f"Subtype: {properties['AccountSubType']}\n"
        if properties.get('Description'):
            account_info += f"Description: {properties['Description']}\n"
        if properties.get('Balance'):
            account_info += f"Balance: {properties['Balance']}\n"
        
        return account_info
    
    def _prepare_taxonomy_info(self, taxonomy: Dict[str, Any]) -> str:
        """Prepare taxonomy information for LLM analysis."""
        taxonomy_info = "Asset Misappropriation Types:\n"
        
        for misapp_type, data in taxonomy['misappropriation_types'].items():
            taxonomy_info += f"- {misapp_type}\n"
            
            # Add relevant properties
            properties = data['properties']
            if properties.get('description'):
                taxonomy_info += f"  Description: {properties['description']}\n"
            if properties.get('riskLevel'):
                taxonomy_info += f"  Risk Level: {properties['riskLevel']}\n"
            if properties.get('indicators'):
                taxonomy_info += f"  Indicators: {properties['indicators']}\n"
        
        return taxonomy_info
    
    def _create_analysis_prompt(self, account_info: str, taxonomy_info: str) -> str:
        """Create LLM prompt for misappropriation analysis."""
        prompt = f"""
You are a fraud detection expert analyzing QuickBooks accounts for potential asset misappropriation risks.

Account Information:
{account_info}

Asset Misappropriation Taxonomy:
{taxonomy_info}

Please analyze this account for potential misappropriation risks. Consider:
1. Does this account type typically involve cash or assets that could be misappropriated?
2. Are there any red flags in the account properties?
3. How does this account relate to the transaction type being analyzed?
4. What misappropriation types from the taxonomy might apply?

Provide your analysis in the following JSON format:
{{
    "risk_level": "HIGH|MEDIUM|LOW",
    "confidence": 0.0-1.0,
    "misappropriation_types": ["type1", "type2"],
    "risk_indicators": ["indicator1", "indicator2"],
    "explanation": "Detailed explanation of the risk assessment"
}}

Focus on identifying specific misappropriation types from the taxonomy that could apply to this account.
"""
        return prompt
    
    def _query_ollama_llm(self, prompt: str) -> Dict[str, Any]:
        """Query Ollama LLM for analysis."""
        logger.info(f"🤖 {self.name}: Querying Ollama LLM")
        
        try:
            # Check if Ollama is running
            if not self._check_ollama_status():
                return {
                    'success': False,
                    'error': 'Ollama is not running or not accessible'
                }
            
            # Prepare request
            url = f"{self.ollama_base_url}/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            # Make request
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            llm_response = result.get('response', '')
            
            logger.info(f"✅ {self.name}: LLM query completed successfully")
            
            return {
                'success': True,
                'response': llm_response
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error querying Ollama LLM: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_ollama_status(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _parse_llm_response(self, response: str, account: Dict[str, Any], taxonomy: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response and extract matches and risk assessment."""
        logger.info(f"📊 {self.name}: Parsing LLM response")
        
        try:
            # Try to extract JSON from response
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                try:
                    analysis_data = json.loads(json_str)
                except json.JSONDecodeError:
                    # Fallback to text parsing
                    analysis_data = self._parse_text_response(response)
            else:
                analysis_data = self._parse_text_response(response)
            
            # Extract matches
            matches = []
            misappropriation_types = analysis_data.get('misappropriation_types', [])
            
            for misapp_type in misappropriation_types:
                if misapp_type in taxonomy['misappropriation_types']:
                    match = {
                        'account_name': account['name'],
                        'account_type': account['type'],
                        'misappropriation_type': misapp_type,
                        'confidence': analysis_data.get('confidence', 0.5),
                        'risk_indicators': analysis_data.get('risk_indicators', []),
                        'explanation': analysis_data.get('explanation', '')
                    }
                    matches.append(match)
            
            # Create risk assessment
            risk_assessment = {
                'account_name': account['name'],
                'risk_level': analysis_data.get('risk_level', 'LOW'),
                'confidence': analysis_data.get('confidence', 0.5),
                'matches_count': len(matches),
                'explanation': analysis_data.get('explanation', '')
            }
            
            return {
                'matches': matches,
                'risk_assessment': risk_assessment
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error parsing LLM response: {e}")
            return {
                'matches': [],
                'risk_assessment': {
                    'account_name': account['name'],
                    'risk_level': 'UNKNOWN',
                    'confidence': 0.0,
                    'matches_count': 0,
                    'explanation': f'Error parsing response: {str(e)}'
                }
            }
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails."""
        # Simple text parsing fallback
        risk_level = 'LOW'
        confidence = 0.5
        misappropriation_types = []
        risk_indicators = []
        explanation = response
        
        # Look for risk level indicators
        if 'HIGH' in response.upper():
            risk_level = 'HIGH'
        elif 'MEDIUM' in response.upper():
            risk_level = 'MEDIUM'
        
        # Look for confidence indicators
        confidence_match = re.search(r'confidence[:\s]*(\d+\.?\d*)', response, re.IGNORECASE)
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
            except ValueError:
                pass
        
        return {
            'risk_level': risk_level,
            'confidence': confidence,
            'misappropriation_types': misappropriation_types,
            'risk_indicators': risk_indicators,
            'explanation': explanation
        }
    
    def _calculate_overall_risk(self, risk_assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall risk assessment from individual assessments."""
        if not risk_assessments:
            return {
                'risk_level': 'LOW',
                'confidence': 0.0,
                'total_assessments': 0,
                'high_risk_count': 0,
                'medium_risk_count': 0,
                'low_risk_count': 0
            }
        
        high_count = sum(1 for assessment in risk_assessments if assessment['risk_level'] == 'HIGH')
        medium_count = sum(1 for assessment in risk_assessments if assessment['risk_level'] == 'MEDIUM')
        low_count = sum(1 for assessment in risk_assessments if assessment['risk_level'] == 'LOW')
        
        # Determine overall risk level
        if high_count > 0:
            overall_risk = 'HIGH'
        elif medium_count > 0:
            overall_risk = 'MEDIUM'
        else:
            overall_risk = 'LOW'
        
        # Calculate average confidence
        avg_confidence = sum(assessment['confidence'] for assessment in risk_assessments) / len(risk_assessments)
        
        return {
            'risk_level': overall_risk,
            'confidence': avg_confidence,
            'total_assessments': len(risk_assessments),
            'high_risk_count': high_count,
            'medium_risk_count': medium_count,
            'low_risk_count': low_count
        }
    
    def save_llm_analysis_results(self, llm_result: Dict[str, Any], output_file: str = "llm_analysis_results.json"):
        """Save LLM analysis results to file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(llm_result, f, indent=2, default=str)
            
            logger.info(f"💾 LLM analysis results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save LLM analysis results: {str(e)}")

def main():
    """Main function for testing the LLM analysis agent."""
    print("🚀 NGAME LLM Analysis Agent Test")
    print("=" * 50)
    
    # Initialize agent
    agent = NGameLLMAnalysisAgent()
    
    # Create test account mappings
    test_account_mappings = [
        {
            'anomaly': {'transaction_type': 'Customers', 'percent_deviation': 166.67},
            'transaction_type': 'Customers',
            'accounts': [
                {
                    'name': 'Accounts Receivable',
                    'type': 'Accounts Receivable',
                    'properties': {'AccountSubType': 'AccountsReceivable', 'Balance': 50000}
                }
            ],
            'account_count': 1
        }
    ]
    
    # Analyze misappropriation risks
    result = agent.analyze_misappropriation_risks(test_account_mappings, "Asset_Misappropriation.ttl")
    
    if result['success']:
        print(f"\n✅ LLM analysis completed successfully!")
        print(f"📊 Found {len(result['matches'])} potential matches")
        print(f"🎯 Overall risk level: {result['overall_risk']['risk_level']}")
        print(f"📊 Confidence: {result['overall_risk']['confidence']:.2f}")
        
        # Save results
        agent.save_llm_analysis_results(result)
        
        return True
    else:
        print(f"\n❌ LLM analysis failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    main()
