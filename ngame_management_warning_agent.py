#!/usr/bin/env python3
"""
NGAME Management Warning Agent
Generates management-level warnings based on LLM misappropriation matches
"""

import os
import json
import smtplib
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NGameManagementWarningAgent:
    """
    NGAME Management Warning Agent for fraud analysis flow.
    Generates management-level warnings based on LLM matches.
    """
    
    def __init__(self):
        self.name = "NGameManagementWarningAgent"
        self.warning_config = {
            'email_enabled': False,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': '',
            'sender_password': '',
            'recipient_emails': [],
            'dashboard_enabled': True,
            'dashboard_file': 'management_dashboard.json'
        }
        
        logger.info(f"🤖 {self.name} initialized")
    
    def generate_management_warnings(self, llm_matches: List[Dict[str, Any]], risk_assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate management-level warnings based on LLM matches.
        Implements Requirement 7 from Chart 2.
        """
        logger.info(f"⚠️  {self.name}: Generating management warnings")
        
        try:
            # Analyze LLM matches and risk assessments
            warning_analysis = self._analyze_warning_requirements(llm_matches, risk_assessments)
            
            # Generate warnings
            warnings = self._generate_warnings(warning_analysis)
            
            # Calculate overall risk level
            overall_risk_level = self._calculate_overall_risk_level(warnings)
            
            # Create management summary
            management_summary = self._create_management_summary(warnings, overall_risk_level)
            
            # Deliver warnings
            delivery_result = self._deliver_warnings(warnings, management_summary)
            
            result = {
                'success': True,
                'warnings': warnings,
                'overall_risk_level': overall_risk_level,
                'management_summary': management_summary,
                'delivery_result': delivery_result,
                'warning_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ {self.name}: Generated {len(warnings)} management warnings")
            logger.info(f"🎯 Overall risk level: {overall_risk_level}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Error generating management warnings: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_warning_requirements(self, llm_matches: List[Dict[str, Any]], risk_assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze LLM matches and risk assessments to determine warning requirements."""
        logger.info(f"📊 {self.name}: Analyzing warning requirements")
        
        # Group matches by risk level
        high_risk_matches = [match for match in llm_matches if match.get('confidence', 0) > 0.7]
        medium_risk_matches = [match for match in llm_matches if 0.4 <= match.get('confidence', 0) <= 0.7]
        low_risk_matches = [match for match in llm_matches if match.get('confidence', 0) < 0.4]
        
        # Group by misappropriation type
        misappropriation_groups = {}
        for match in llm_matches:
            misapp_type = match.get('misappropriation_type', 'Unknown')
            if misapp_type not in misappropriation_groups:
                misappropriation_groups[misapp_type] = []
            misappropriation_groups[misapp_type].append(match)
        
        # Group by account
        account_groups = {}
        for match in llm_matches:
            account_name = match.get('account_name', 'Unknown')
            if account_name not in account_groups:
                account_groups[account_name] = []
            account_groups[account_name].append(match)
        
        analysis = {
            'total_matches': len(llm_matches),
            'high_risk_matches': high_risk_matches,
            'medium_risk_matches': medium_risk_matches,
            'low_risk_matches': low_risk_matches,
            'misappropriation_groups': misappropriation_groups,
            'account_groups': account_groups,
            'risk_assessments': risk_assessments
        }
        
        logger.info(f"✅ {self.name}: Warning requirements analyzed")
        logger.info(f"📊 High risk matches: {len(high_risk_matches)}")
        logger.info(f"📊 Medium risk matches: {len(medium_risk_matches)}")
        logger.info(f"📊 Low risk matches: {len(low_risk_matches)}")
        
        return analysis
    
    def _generate_warnings(self, warning_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific warnings based on analysis."""
        logger.info(f"⚠️  {self.name}: Generating specific warnings")
        
        warnings = []
        
        # Generate high-risk warnings
        for match in warning_analysis['high_risk_matches']:
            warning = self._create_high_risk_warning(match)
            warnings.append(warning)
        
        # Generate medium-risk warnings
        for match in warning_analysis['medium_risk_matches']:
            warning = self._create_medium_risk_warning(match)
            warnings.append(warning)
        
        # Generate misappropriation type warnings
        for misapp_type, matches in warning_analysis['misappropriation_groups'].items():
            if len(matches) > 1:  # Multiple matches for same type
                warning = self._create_misappropriation_type_warning(misapp_type, matches)
                warnings.append(warning)
        
        # Generate account-specific warnings
        for account_name, matches in warning_analysis['account_groups'].items():
            if len(matches) > 1:  # Multiple matches for same account
                warning = self._create_account_warning(account_name, matches)
                warnings.append(warning)
        
        logger.info(f"✅ {self.name}: Generated {len(warnings)} warnings")
        return warnings
    
    def _create_high_risk_warning(self, match: Dict[str, Any]) -> Dict[str, Any]:
        """Create high-risk warning for a specific match."""
        return {
            'warning_type': 'HIGH_RISK_ACCOUNT',
            'risk_level': 'HIGH',
            'priority': 'IMMEDIATE',
            'account_name': match.get('account_name', 'Unknown'),
            'misappropriation_type': match.get('misappropriation_type', 'Unknown'),
            'confidence': match.get('confidence', 0.0),
            'title': f'HIGH RISK: {match.get("account_name", "Unknown Account")}',
            'message': f'High-risk misappropriation detected in {match.get("account_name", "Unknown Account")}. '
                      f'Type: {match.get("misappropriation_type", "Unknown")}. '
                      f'Confidence: {match.get("confidence", 0.0):.2f}. '
                      f'Immediate investigation required.',
            'recommendations': [
                'Immediately review account transactions',
                'Verify account balances and reconciliations',
                'Check for unauthorized access or changes',
                'Consider temporary account restrictions',
                'Notify internal audit team'
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_medium_risk_warning(self, match: Dict[str, Any]) -> Dict[str, Any]:
        """Create medium-risk warning for a specific match."""
        return {
            'warning_type': 'MEDIUM_RISK_ACCOUNT',
            'risk_level': 'MEDIUM',
            'priority': 'HIGH',
            'account_name': match.get('account_name', 'Unknown'),
            'misappropriation_type': match.get('misappropriation_type', 'Unknown'),
            'confidence': match.get('confidence', 0.0),
            'title': f'MEDIUM RISK: {match.get("account_name", "Unknown Account")}',
            'message': f'Medium-risk misappropriation detected in {match.get("account_name", "Unknown Account")}. '
                      f'Type: {match.get("misappropriation_type", "Unknown")}. '
                      f'Confidence: {match.get("confidence", 0.0):.2f}. '
                      f'Enhanced monitoring recommended.',
            'recommendations': [
                'Review recent account activity',
                'Verify transaction documentation',
                'Increase monitoring frequency',
                'Check for unusual patterns',
                'Schedule follow-up review'
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_misappropriation_type_warning(self, misapp_type: str, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create warning for multiple matches of same misappropriation type."""
        return {
            'warning_type': 'MULTIPLE_MISAPPROPRIATION_MATCHES',
            'risk_level': 'HIGH',
            'priority': 'HIGH',
            'misappropriation_type': misapp_type,
            'match_count': len(matches),
            'title': f'MULTIPLE MATCHES: {misapp_type}',
            'message': f'Multiple accounts ({len(matches)}) show potential {misapp_type} misappropriation. '
                      f'This pattern suggests systematic risk requiring investigation.',
            'recommendations': [
                'Investigate all affected accounts',
                'Look for common patterns or perpetrators',
                'Review access controls and segregation of duties',
                'Consider broader system review',
                'Document findings for audit trail'
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_account_warning(self, account_name: str, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create warning for multiple matches for same account."""
        return {
            'warning_type': 'MULTIPLE_ACCOUNT_MATCHES',
            'risk_level': 'HIGH',
            'priority': 'HIGH',
            'account_name': account_name,
            'match_count': len(matches),
            'title': f'MULTIPLE RISKS: {account_name}',
            'message': f'Account {account_name} shows multiple misappropriation risks ({len(matches)} types). '
                      f'This account requires immediate attention.',
            'recommendations': [
                'Immediately review account in detail',
                'Check all recent transactions',
                'Verify account ownership and access',
                'Consider account freeze if necessary',
                'Escalate to senior management'
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_overall_risk_level(self, warnings: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level from warnings."""
        if not warnings:
            return 'LOW'
        
        high_risk_count = sum(1 for warning in warnings if warning['risk_level'] == 'HIGH')
        medium_risk_count = sum(1 for warning in warnings if warning['risk_level'] == 'MEDIUM')
        
        if high_risk_count > 0:
            return 'HIGH'
        elif medium_risk_count > 0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _create_management_summary(self, warnings: List[Dict[str, Any]], overall_risk_level: str) -> Dict[str, Any]:
        """Create management summary of warnings."""
        logger.info(f"📊 {self.name}: Creating management summary")
        
        # Count warnings by type
        warning_counts = {}
        for warning in warnings:
            warning_type = warning['warning_type']
            warning_counts[warning_type] = warning_counts.get(warning_type, 0) + 1
        
        # Get unique accounts and misappropriation types
        unique_accounts = set(warning.get('account_name', 'Unknown') for warning in warnings if warning.get('account_name'))
        unique_misapp_types = set(warning.get('misappropriation_type', 'Unknown') for warning in warnings if warning.get('misappropriation_type'))
        
        summary = {
            'overall_risk_level': overall_risk_level,
            'total_warnings': len(warnings),
            'warning_counts': warning_counts,
            'unique_accounts_affected': len(unique_accounts),
            'unique_misappropriation_types': len(unique_misapp_types),
            'accounts_affected': list(unique_accounts),
            'misappropriation_types': list(unique_misapp_types),
            'summary_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ {self.name}: Management summary created")
        return summary
    
    def _deliver_warnings(self, warnings: List[Dict[str, Any]], management_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver warnings via configured channels."""
        logger.info(f"📤 {self.name}: Delivering warnings")
        
        delivery_result = {
            'email_delivered': False,
            'dashboard_updated': False,
            'delivery_errors': []
        }
        
        # Update dashboard
        if self.warning_config['dashboard_enabled']:
            try:
                self._update_dashboard(warnings, management_summary)
                delivery_result['dashboard_updated'] = True
                logger.info(f"✅ {self.name}: Dashboard updated successfully")
            except Exception as e:
                delivery_result['delivery_errors'].append(f'Dashboard update failed: {str(e)}')
                logger.error(f"❌ {self.name}: Dashboard update failed: {e}")
        
        # Send email
        if self.warning_config['email_enabled'] and warnings:
            try:
                self._send_email_warnings(warnings, management_summary)
                delivery_result['email_delivered'] = True
                logger.info(f"✅ {self.name}: Email warnings sent successfully")
            except Exception as e:
                delivery_result['delivery_errors'].append(f'Email delivery failed: {str(e)}')
                logger.error(f"❌ {self.name}: Email delivery failed: {e}")
        
        return delivery_result
    
    def _update_dashboard(self, warnings: List[Dict[str, Any]], management_summary: Dict[str, Any]):
        """Update management dashboard with warnings."""
        dashboard_data = {
            'last_updated': datetime.now().isoformat(),
            'management_summary': management_summary,
            'warnings': warnings,
            'dashboard_status': 'ACTIVE'
        }
        
        with open(self.warning_config['dashboard_file'], 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
    
    def _send_email_warnings(self, warnings: List[Dict[str, Any]], management_summary: Dict[str, Any]):
        """Send email warnings to management."""
        if not self.warning_config['recipient_emails']:
            logger.warning(f"⚠️  {self.name}: No recipient emails configured")
            return
        
        # Create email content
        subject = f"NGAME Fraud Detection Alert - {management_summary['overall_risk_level']} Risk"
        
        # Create HTML email body
        html_body = self._create_email_html(warnings, management_summary)
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.warning_config['sender_email']
        msg['To'] = ', '.join(self.warning_config['recipient_emails'])
        
        # Attach HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(self.warning_config['smtp_server'], self.warning_config['smtp_port']) as server:
            server.starttls()
            server.login(self.warning_config['sender_email'], self.warning_config['sender_password'])
            server.send_message(msg)
    
    def _create_email_html(self, warnings: List[Dict[str, Any]], management_summary: Dict[str, Any]) -> str:
        """Create HTML email content for warnings."""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .high-risk {{ background-color: #f8d7da; border-color: #f5c6cb; }}
                .medium-risk {{ background-color: #fff3cd; border-color: #ffeaa7; }}
                .summary {{ background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>NGAME Fraud Detection Alert</h1>
                <p><strong>Overall Risk Level:</strong> {management_summary['overall_risk_level']}</p>
                <p><strong>Total Warnings:</strong> {management_summary['total_warnings']}</p>
                <p><strong>Accounts Affected:</strong> {management_summary['unique_accounts_affected']}</p>
                <p><strong>Timestamp:</strong> {management_summary['summary_timestamp']}</p>
            </div>
            
            <div class="summary">
                <h2>Management Summary</h2>
                <p>NGAME has detected potential asset misappropriation risks requiring management attention.</p>
                <ul>
                    <li>Total warnings generated: {management_summary['total_warnings']}</li>
                    <li>Accounts affected: {', '.join(management_summary['accounts_affected'])}</li>
                    <li>Misappropriation types: {', '.join(management_summary['misappropriation_types'])}</li>
                </ul>
            </div>
            
            <h2>Detailed Warnings</h2>
        """
        
        for warning in warnings:
            risk_class = 'high-risk' if warning['risk_level'] == 'HIGH' else 'medium-risk'
            html += f"""
            <div class="warning {risk_class}">
                <h3>{warning['title']}</h3>
                <p><strong>Risk Level:</strong> {warning['risk_level']}</p>
                <p><strong>Priority:</strong> {warning['priority']}</p>
                <p>{warning['message']}</p>
                <h4>Recommendations:</h4>
                <ul>
            """
            
            for recommendation in warning['recommendations']:
                html += f"<li>{recommendation}</li>"
            
            html += """
                </ul>
            </div>
            """
        
        html += """
            <div class="summary">
                <h2>Next Steps</h2>
                <p>Please review these warnings and take appropriate action based on the risk levels and recommendations provided.</p>
                <p>For questions or additional information, please contact the NGAME system administrator.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def save_warning_results(self, warning_result: Dict[str, Any], output_file: str = "management_warning_results.json"):
        """Save management warning results to file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(warning_result, f, indent=2, default=str)
            
            logger.info(f"💾 Management warning results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save management warning results: {str(e)}")

def main():
    """Main function for testing the management warning agent."""
    print("🚀 NGAME Management Warning Agent Test")
    print("=" * 50)
    
    # Initialize agent
    agent = NGameManagementWarningAgent()
    
    # Create test LLM matches
    test_llm_matches = [
        {
            'account_name': 'Accounts Receivable',
            'account_type': 'Accounts Receivable',
            'misappropriation_type': 'Cash_Theft',
            'confidence': 0.85,
            'risk_indicators': ['High balance', 'Frequent transactions'],
            'explanation': 'High-risk cash theft potential detected'
        },
        {
            'account_name': 'Petty Cash',
            'account_type': 'Cash',
            'misappropriation_type': 'Cash_Theft',
            'confidence': 0.75,
            'risk_indicators': ['Unreconciled transactions'],
            'explanation': 'Medium-risk cash theft potential detected'
        }
    ]
    
    # Create test risk assessments
    test_risk_assessments = [
        {
            'account_name': 'Accounts Receivable',
            'risk_level': 'HIGH',
            'confidence': 0.85,
            'matches_count': 1,
            'explanation': 'High-risk account with multiple indicators'
        }
    ]
    
    # Generate management warnings
    result = agent.generate_management_warnings(test_llm_matches, test_risk_assessments)
    
    if result['success']:
        print(f"\n✅ Management warnings generated successfully!")
        print(f"⚠️  Total warnings: {len(result['warnings'])}")
        print(f"🎯 Overall risk level: {result['overall_risk_level']}")
        print(f"📊 Accounts affected: {result['management_summary']['unique_accounts_affected']}")
        
        # Show warning summary
        for i, warning in enumerate(result['warnings'], 1):
            print(f"\n{i}. {warning['title']}")
            print(f"   Risk Level: {warning['risk_level']}")
            print(f"   Priority: {warning['priority']}")
        
        # Save results
        agent.save_warning_results(result)
        
        return True
    else:
        print(f"\n❌ Management warning generation failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    main()
