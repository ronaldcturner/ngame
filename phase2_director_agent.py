#!/usr/bin/env python3
"""
Director Agent for NGAME Agent-Driven Pipeline
Orchestrates Phase 2: Ontology Construction, Fraud Detection, and Report Generation
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import sys

# Add the current directory to the path to import the advanced CPI analysis
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectorAgent:
    """
    Director Agent that orchestrates the agent-driven pipeline for Phase 2.
    Manages Ontology Construction, Fraud Detection, and Report Generation agents.
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
        self.input_files = {
            'yesterday': 'quickbooks_ontology_Yesterday.ttl',
            'today': 'quickbooks_ontology_Today.ttl'
        }
        self.output_files = {
            'fraud_analysis': 'agent_driven_fraud_analysis.json',
            'report': 'agent_driven_report.json'
        }
        
    def initialize_agents(self):
        """Initialize all agents for Phase 2."""
        logger.info("🤖 Initializing Phase 2 Agents...")
        
        # Initialize Ontology Construction Agent
        self.agents['ontology_agent'] = OntologyConstructionAgent()
        
        # Initialize Fraud Detection Agent
        self.agents['fraud_agent'] = FraudDetectionAgent()
        
        # Initialize Report Generation Agent
        self.agents['report_agent'] = ReportGenerationAgent()
        
        logger.info("✅ All Phase 2 agents initialized successfully")
        
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
        """Execute the complete agent-driven pipeline."""
        logger.info("🚀 Starting Agent-Driven Pipeline Execution")
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
            
            # Step 3: Ontology Construction
            self.pipeline_state['current_step'] = 'ontology_construction'
            ontology_results = self.agents['ontology_agent'].process_ontologies(
                self.input_files['yesterday'],
                self.input_files['today']
            )
            self.pipeline_state['results']['ontology'] = ontology_results
            
            # Step 4: Fraud Detection Analysis
            self.pipeline_state['current_step'] = 'fraud_detection'
            fraud_results = self.agents['fraud_agent'].analyze_fraud_risks(
                ontology_results
            )
            self.pipeline_state['results']['fraud_analysis'] = fraud_results
            
            # Step 5: Report Generation
            self.pipeline_state['current_step'] = 'report_generation'
            report_results = self.agents['report_agent'].generate_comprehensive_report(
                ontology_results,
                fraud_results
            )
            self.pipeline_state['results']['report'] = report_results
            
            # Step 6: Save outputs
            self.pipeline_state['current_step'] = 'saving_outputs'
            self._save_outputs()
            
            self.pipeline_state['status'] = 'completed'
            self.pipeline_state['end_time'] = datetime.now()
            
            logger.info("✅ Agent-Driven Pipeline completed successfully")
            return self.pipeline_state
            
        except Exception as e:
            logger.error(f"❌ Pipeline execution failed: {str(e)}")
            self.pipeline_state['status'] = 'failed'
            self.pipeline_state['errors'].append(str(e))
            self.pipeline_state['end_time'] = datetime.now()
            return self.pipeline_state
    
    def _save_outputs(self):
        """Save all outputs from the pipeline."""
        logger.info("💾 Saving pipeline outputs...")
        
        # Save fraud analysis results
        with open(self.output_files['fraud_analysis'], 'w') as f:
            json.dump(self.pipeline_state['results']['fraud_analysis'], f, indent=2)
        
        # Save comprehensive report
        with open(self.output_files['report'], 'w') as f:
            json.dump(self.pipeline_state['results']['report'], f, indent=2)
        
        logger.info(f"✅ Outputs saved to {self.output_files}")
    
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


class OntologyConstructionAgent:
    """
    Agent responsible for ontology construction and validation.
    """
    
    def __init__(self):
        self.name = "OntologyConstructionAgent"
        logger.info(f"🤖 {self.name} initialized")
    
    def process_ontologies(self, yesterday_file: str, today_file: str) -> Dict[str, Any]:
        """Process and validate ontology files."""
        logger.info(f"🔧 {self.name}: Processing ontologies...")
        
        results = {
            'yesterday_file': yesterday_file,
            'today_file': today_file,
            'yesterday_stats': self._analyze_ontology_file(yesterday_file),
            'today_stats': self._analyze_ontology_file(today_file),
            'comparison': self._compare_ontologies(yesterday_file, today_file),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ {self.name}: Ontology processing completed")
        return results
    
    def _analyze_ontology_file(self, filepath: str) -> Dict[str, Any]:
        """Analyze a single ontology file."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Basic file analysis
            lines = content.split('\n')
            triples = [line for line in lines if line.strip() and not line.startswith('#') and not line.startswith('@')]
            
            return {
                'file_size': len(content),
                'line_count': len(lines),
                'triple_count': len(triples),
                'exists': True
            }
        except Exception as e:
            logger.error(f"❌ Error analyzing {filepath}: {e}")
            return {
                'file_size': 0,
                'line_count': 0,
                'triple_count': 0,
                'exists': False,
                'error': str(e)
            }
    
    def _compare_ontologies(self, yesterday_file: str, today_file: str) -> Dict[str, Any]:
        """Compare two ontology files."""
        yesterday_stats = self._analyze_ontology_file(yesterday_file)
        today_stats = self._analyze_ontology_file(today_file)
        
        return {
            'size_change': today_stats['file_size'] - yesterday_stats['file_size'],
            'line_change': today_stats['line_count'] - yesterday_stats['line_count'],
            'triple_change': today_stats['triple_count'] - yesterday_stats['triple_count'],
            'size_change_percent': ((today_stats['file_size'] - yesterday_stats['file_size']) / yesterday_stats['file_size'] * 100) if yesterday_stats['file_size'] > 0 else 0
        }


class FraudDetectionAgent:
    """
    Agent responsible for fraud detection analysis using churn persistence index analysis.
    """
    
    def __init__(self):
        self.name = "FraudDetectionAgent"
        logger.info(f"🤖 {self.name} initialized")
    
    def analyze_fraud_risks(self, ontology_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fraud risks using both basic metrics and advanced CPI analysis."""
        logger.info(f"🔍 {self.name}: Analyzing fraud risks...")
        
        comparison = ontology_results['comparison']
        
        # Basic fraud risk indicators
        risk_indicators = {
            'high_volume_change': abs(comparison['size_change_percent']) > 50,
            'significant_triple_change': abs(comparison['triple_change']) > 100,
            'rapid_growth': comparison['size_change_percent'] > 25,
            'rapid_decline': comparison['size_change_percent'] < -25
        }
        
        # Try to run advanced CPI analysis if files exist
        advanced_analysis = self._run_advanced_cpi_analysis(ontology_results)
        
        # Calculate overall risk score
        risk_score = 0
        if risk_indicators['high_volume_change']:
            risk_score += 30
        if risk_indicators['significant_triple_change']:
            risk_score += 25
        if risk_indicators['rapid_growth']:
            risk_score += 20
        if risk_indicators['rapid_decline']:
            risk_score += 15
        
        # Add advanced analysis risk score if available
        if advanced_analysis and 'risk_score' in advanced_analysis:
            risk_score += advanced_analysis['risk_score']
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = "HIGH"
        elif risk_score >= 25:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        results = {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_indicators': risk_indicators,
            'change_metrics': comparison,
            'advanced_analysis': advanced_analysis,
            'recommendations': self._generate_recommendations(risk_level, risk_indicators, advanced_analysis),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ {self.name}: Fraud analysis completed - Risk Level: {risk_level}")
        return results
    
    def _run_advanced_cpi_analysis(self, ontology_results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run advanced churn persistence index analysis if possible."""
        try:
            # Check if the advanced CPI analysis file exists
            cpi_analysis_file = "advanced_cpi_analysis Onto II.py"
            if not os.path.exists(cpi_analysis_file):
                logger.warning("Advanced CPI analysis file not found, using basic analysis only")
                return None
            
            # Import and run the advanced analyzer
            # The file name has spaces, so we need to handle it differently
            import importlib.util
            spec = importlib.util.spec_from_file_location("advanced_cpi_analysis", cpi_analysis_file)
            advanced_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(advanced_module)
            AdvancedPhiAnalyzer = advanced_module.AdvancedPhiAnalyzer
            
            analyzer = AdvancedPhiAnalyzer()
            
            # Load the ontologies
            yesterday_file = ontology_results['yesterday_file']
            today_file = ontology_results['today_file']
            
            if analyzer.load_ontology('Yesterday', yesterday_file) and analyzer.load_ontology('Today', today_file):
                # Run similarity analysis
                similarity_results = analyzer.analyze_ontology_similarity()
                
                # Run business entity analysis
                business_results = analyzer.analyze_business_entities()
                
                # Calculate overall risk from churn persistence indexs
                risk_score = 0
                if similarity_results:
                    for feature_type, correlations in similarity_results.items():
                        if correlations:
                            cpi_values = [corr['cpi'] for corr in correlations.values()]
                            avg_cpi = sum(cpi_values) / len(cpi_values) if cpi_values else 0
                            # Lower CPI values indicate higher risk
                            risk_score += (1 - abs(avg_cpi)) * 20
                
                return {
                    'similarity_results': similarity_results,
                    'business_results': business_results,
                    'risk_score': min(risk_score, 50),  # Cap at 50
                    'analysis_type': 'advanced_cpi'
                }
            
        except Exception as e:
            logger.warning(f"Advanced CPI analysis failed: {e}")
            return None
        
        return None
    
    def _generate_recommendations(self, risk_level: str, indicators: Dict[str, bool], advanced_analysis: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate fraud detection recommendations."""
        recommendations = []
        
        if risk_level == "HIGH":
            recommendations.append("🔴 IMMEDIATE INVESTIGATION REQUIRED: High risk indicators detected")
            recommendations.append("🔍 Review all recent transactions for anomalies")
            recommendations.append("📊 Conduct detailed forensic analysis")
        elif risk_level == "MEDIUM":
            recommendations.append("🟡 MONITOR CLOSELY: Medium risk indicators present")
            recommendations.append("📈 Increase monitoring frequency")
            recommendations.append("🔍 Investigate specific high-risk areas")
        else:
            recommendations.append("🟢 NORMAL OPERATIONS: Low risk level")
            recommendations.append("📊 Continue regular monitoring")
        
        if indicators['high_volume_change']:
            recommendations.append("⚠️ Large volume changes detected - investigate data integrity")
        if indicators['significant_triple_change']:
            recommendations.append("⚠️ Significant structural changes - review ontology modifications")
        
        # Add advanced analysis recommendations if available
        if advanced_analysis and advanced_analysis.get('analysis_type') == 'advanced_cpi':
            recommendations.append("🔬 Advanced churn persistence index analysis completed")
            if advanced_analysis.get('risk_score', 0) > 20:
                recommendations.append("⚠️ Advanced analysis indicates elevated risk")
            else:
                recommendations.append("✅ Advanced analysis shows normal patterns")
        
        return recommendations


class ReportGenerationAgent:
    """
    Agent responsible for generating comprehensive reports.
    """
    
    def __init__(self):
        self.name = "ReportGenerationAgent"
        logger.info(f"🤖 {self.name} initialized")
    
    def generate_comprehensive_report(self, ontology_results: Dict[str, Any], fraud_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive report combining all analysis results."""
        logger.info(f"📊 {self.name}: Generating comprehensive report...")
        
        report = {
            'executive_summary': self._create_executive_summary(fraud_results),
            'ontology_analysis': ontology_results,
            'fraud_analysis': fraud_results,
            'recommendations': fraud_results['recommendations'],
            'metadata': {
                'generated_by': 'NGAME Agent-Driven Pipeline',
                'generation_time': datetime.now().isoformat(),
                'pipeline_version': '1.0.0',
                'agents_used': ['OntologyConstructionAgent', 'FraudDetectionAgent', 'ReportGenerationAgent']
            }
        }
        
        logger.info(f"✅ {self.name}: Comprehensive report generated")
        return report
    
    def _create_executive_summary(self, fraud_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary of the analysis."""
        return {
            'risk_level': fraud_results['risk_level'],
            'risk_score': fraud_results['risk_score'],
            'key_findings': [
                f"Risk Level: {fraud_results['risk_level']}",
                f"Risk Score: {fraud_results['risk_score']}/100",
                f"High Volume Change: {'Yes' if fraud_results['risk_indicators']['high_volume_change'] else 'No'}",
                f"Significant Triple Change: {'Yes' if fraud_results['risk_indicators']['significant_triple_change'] else 'No'}"
            ],
            'immediate_actions': [rec for rec in fraud_results['recommendations'] if '🔴' in rec or 'IMMEDIATE' in rec],
            'monitoring_actions': [rec for rec in fraud_results['recommendations'] if '🟡' in rec or 'MONITOR' in rec]
        }


def main():
    """Main function to run the director agent."""
    print("🚀 NGAME Agent-Driven Pipeline - Phase 2 Demo")
    print("=" * 60)
    
    # Initialize director agent
    director = DirectorAgent()
    
    # Execute pipeline
    results = director.execute_pipeline()
    
    # Display results
    print("\n📊 PIPELINE EXECUTION RESULTS")
    print("=" * 60)
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
        
        # Display fraud analysis summary
        if 'fraud_analysis' in results['results']:
            fraud = results['results']['fraud_analysis']
            print(f"\n🔍 FRAUD ANALYSIS SUMMARY")
            print(f"Risk Level: {fraud['risk_level']}")
            print(f"Risk Score: {fraud['risk_score']}/100")
            print("Recommendations:")
            for rec in fraud['recommendations']:
                print(f"  - {rec}")
    
    print(f"\n📁 Output Files:")
    for name, filepath in director.output_files.items():
        if os.path.exists(filepath):
            print(f"  ✅ {name}: {filepath}")
        else:
            print(f"  ❌ {name}: {filepath} (not found)")


if __name__ == "__main__":
    main()
