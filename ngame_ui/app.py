#!/usr/bin/env python3
"""
NGAME Web Application
Modern, attractive user interface for the NGAME ontology-based anomaly detection system.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit
import json
import os
import logging
from datetime import datetime, timedelta
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List

# Import NGAME components
import sys
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
sys.path.append('..')
from ngame_env import load_ngame_dotenv

load_ngame_dotenv()

from quickbooks_chart_of_accounts_extractor import ChartOfAccountsExtractor, OntologyConverter
from quickbooks_chart_of_accounts_creator import OntologyChartExtractor, ChartOfAccountsCreator
from ngame_ontology_workflow import NGAMEOntologyWorkflow
from ngame_dashboard_alerts import (
    build_dollar_alarm_alerts,
    filter_top_anomalies_for_display,
    merge_full_fraud_comparison,
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ngame-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Consolidated dashboard artifact loading ----

def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent

def _try_load_json(path: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        if not path.exists():
            return None, None
        with path.open('r', encoding='utf-8') as f:
            return json.load(f), None
    except Exception as e:
        return None, f"{path}: {e}"

def _load_latest_artifacts() -> Dict[str, Any]:
    """
    Consolidate key NGAME run artifacts for the UI.

    Priority is root-level artifacts, then GENERATED_FILES fallbacks.
    """
    root = _repo_root()
    fallbacks = root / "GENERATED_FILES"

    candidates: Dict[str, List[Path]] = {
        "management_dashboard": [
            root / "management_dashboard.json",
            fallbacks / "management_dashboard.json",
        ],
        "fraud_analysis": [
            root / "NGAME_Fraud_Analysis_readable_truly_clean.json",
            root / "NGAME_Fraud_Analysis_readable_clean.json",
            root / "NGAME_Fraud_Analysis_readable.json",
            root / "NGAME_Fraud_Analysis.json",
            fallbacks / "NGAME_Fraud_Analysis_readable_truly_clean.json",
            fallbacks / "NGAME_Fraud_Analysis_readable_clean.json",
            fallbacks / "NGAME_Fraud_Analysis_readable.json",
            fallbacks / "NGAME_Fraud_Analysis.json",
        ],
    }

    errors: List[str] = []
    loaded: Dict[str, Any] = {}
    sources: Dict[str, str] = {}

    for key, paths in candidates.items():
        for p in paths:
            data, err = _try_load_json(p)
            if err:
                errors.append(err)
            if data is not None:
                loaded[key] = data
                sources[key] = str(p)
                break

    management_dashboard = loaded.get("management_dashboard") or {}
    fraud = loaded.get("fraud_analysis") or {}

    fraud = merge_full_fraud_comparison(
        loaded.get("fraud_analysis") or {},
        _try_load_json,
        root,
        fallbacks,
    )

    management_summary = (management_dashboard.get("management_summary") or
                          fraud.get("warning_result", {}).get("management_summary") or {})
    warnings = management_dashboard.get("warnings") or fraud.get("warning_result", {}).get("warnings") or []
    overall_risk = (management_summary.get("overall_risk_level") or
                    fraud.get("summary", {}).get("overall_risk_level") or
                    fraud.get("warning_result", {}).get("overall_risk_level") or
                    "UNKNOWN")
    top_anomalies = filter_top_anomalies_for_display(
        (fraud.get("anomaly_result", {}) or {}).get("top_anomalies") or []
    )
    dollar_alarm_alerts = build_dollar_alarm_alerts(fraud)

    last_updated = management_dashboard.get("last_updated") or management_dashboard.get("management_summary", {}).get("summary_timestamp")
    execution_time = fraud.get("execution_time")

    return {
        "success": True,
        "sources": sources,
        "errors": errors[-10:],
        "summary": {
            "overall_risk_level": overall_risk,
            "warnings_count": len(warnings),
            "top_anomalies_count": len(top_anomalies),
            "dollar_alarm_count": len(dollar_alarm_alerts),
            "dollar_alarm_high_count": sum(
                1 for a in dollar_alarm_alerts
                if (a.get("dollar_alarm_level") or "").upper() == "HIGH"
            ),
            "last_updated": last_updated,
            "execution_time": execution_time,
        },
        "management_dashboard": {
            "management_summary": management_summary,
            "warnings": warnings[:50],
            "dashboard_status": management_dashboard.get("dashboard_status", "UNKNOWN"),
            "last_updated": last_updated,
        },
        "fraud_analysis": {
            "execution_time": execution_time,
            "anomaly_result": {"top_anomalies": top_anomalies[:10]},
            "dollar_alarm_alerts": dollar_alarm_alerts[:10],
            "llm_result": fraud.get("llm_result", {}),
            "summary": fraud.get("summary", {}),
        },
    }

# Global state
ngame_workflow = None
current_analysis = None
analysis_history = []

class NGAMEState:
    """Global state management for NGAME application."""
    
    def __init__(self):
        self.workflow = None
        self.current_analysis = None
        self.analysis_history = []
        self.quickbooks_connected = False
        self.ontology_loaded = False
        self.active_alerts = []
        
    def initialize_workflow(self):
        """Initialize the NGAME ontology workflow."""
        try:
            self.workflow = NGAMEOntologyWorkflow()
            return True
        except Exception as e:
            logger.error(f"Error initializing workflow: {e}")
            return False
    
    def add_analysis(self, analysis_data):
        """Add analysis to history."""
        analysis_data['timestamp'] = datetime.now().isoformat()
        analysis_data['id'] = len(self.analysis_history) + 1
        self.analysis_history.append(analysis_data)
        
        # Keep only last 50 analyses
        if len(self.analysis_history) > 50:
            self.analysis_history = self.analysis_history[-50:]
    
    def get_dashboard_stats(self):
        """Get dashboard statistics."""
        return {
            'total_analyses': len(self.analysis_history),
            'active_alerts': len(self.active_alerts),
            'quickbooks_connected': self.quickbooks_connected,
            'ontology_loaded': self.ontology_loaded,
            'recent_analyses': self.analysis_history[-5:] if self.analysis_history else []
        }

# Initialize global state
ngame_state = NGAMEState()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html', stats=ngame_state.get_dashboard_stats())

@app.route('/dashboard')
def dashboard():
    """Dashboard with real-time updates."""
    return render_template('dashboard.html', stats=ngame_state.get_dashboard_stats())

@app.route('/dashboard-debug')
def dashboard_debug():
    """Debug dashboard showing raw consolidated payload."""
    return render_template('dashboard-debug.html')

@app.route('/analysis')
def analysis():
    """Analysis page for running anomaly detection."""
    return render_template('analysis.html')

@app.route('/ontology')
def ontology():
    """Ontology management page."""
    return render_template('ontology.html')

@app.route('/quickbooks')
def quickbooks():
    """QuickBooks integration page."""
    return render_template('quickbooks.html')

@app.route('/alerts')
def alerts():
    """Alerts and notifications page."""
    return render_template('alerts.html', alerts=ngame_state.active_alerts)

@app.route('/reports')
def reports():
    """Reports and analytics page."""
    return render_template('reports.html', history=ngame_state.analysis_history)

@app.route('/settings')
def settings():
    """Settings and configuration page."""
    return render_template('settings.html')

# API Routes

@app.route('/api/initialize', methods=['POST'])
def api_initialize():
    """Initialize NGAME system."""
    try:
        success = ngame_state.initialize_workflow()
        if success:
            return jsonify({'success': True, 'message': 'NGAME system initialized successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to initialize NGAME system'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/load-ontology', methods=['POST'])
def api_load_ontology():
    """Load ontology file."""
    try:
        data = request.get_json()
        ontology_path = data.get('ontology_path')
        
        if not ontology_path or not os.path.exists(ontology_path):
            return jsonify({'success': False, 'message': 'Ontology file not found'})
        
        # Load ontology using NGAME workflow
        if ngame_state.workflow:
            ngame_state.workflow.load_ontology(ontology_path)
            ngame_state.ontology_loaded = True
            return jsonify({'success': True, 'message': 'Ontology loaded successfully'})
        else:
            return jsonify({'success': False, 'message': 'NGAME workflow not initialized'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/run-analysis', methods=['POST'])
def api_run_analysis():
    """Run anomaly detection analysis."""
    try:
        data = request.get_json()
        analysis_type = data.get('type', 'comprehensive')
        
        # Start analysis in background
        def run_analysis():
            try:
                if ngame_state.workflow:
                    results = ngame_state.workflow.run_ontology_analysis(data)
                    ngame_state.current_analysis = results
                    ngame_state.add_analysis(results)
                    
                    # Emit results via WebSocket
                    socketio.emit('analysis_complete', {
                        'success': True,
                        'results': results,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    socketio.emit('analysis_complete', {
                        'success': False,
                        'message': 'NGAME workflow not initialized'
                    })
            except Exception as e:
                socketio.emit('analysis_complete', {
                    'success': False,
                    'message': str(e)
                })
        
        # Run analysis in background thread
        thread = threading.Thread(target=run_analysis)
        thread.start()
        
        return jsonify({'success': True, 'message': 'Analysis started'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/extract-chart-of-accounts', methods=['POST'])
def api_extract_chart_of_accounts():
    """Extract chart of accounts from QuickBooks."""
    try:
        data = request.get_json()
        
        # Extract chart of accounts
        extractor = ChartOfAccountsExtractor(None)  # Will need API client
        chart_of_accounts = extractor.extract_chart_of_accounts()
        
        # Convert to ontology
        converter = OntologyConverter()
        ontology_graph = converter.convert_to_ontology(chart_of_accounts)
        
        # Save ontology
        output_path = f"output/chart_of_accounts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ttl"
        converter.save_ontology(output_path)
        
        return jsonify({
            'success': True,
            'message': 'Chart of accounts extracted successfully',
            'output_path': output_path,
            'account_count': len(chart_of_accounts.accounts)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/create-chart-of-accounts', methods=['POST'])
def api_create_chart_of_accounts():
    """Create chart of accounts in QuickBooks from ontology."""
    try:
        data = request.get_json()
        ontology_path = data.get('ontology_path')
        
        # Extract from ontology
        extractor = OntologyChartExtractor()
        extractor.load_ontology(ontology_path)
        template = extractor.extract_chart_of_accounts()
        
        # Create in QuickBooks (dry run for safety)
        creator = ChartOfAccountsCreator(None)  # Will need API client
        result = creator.create_chart_of_accounts(template, dry_run=True)
        
        return jsonify({
            'success': True,
            'message': 'Chart of accounts creation preview',
            'result': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/dashboard-stats')
def api_dashboard_stats():
    """Get dashboard statistics."""
    return jsonify(ngame_state.get_dashboard_stats())

@app.route('/api/consolidated-dashboard')
def api_consolidated_dashboard():
    """Get consolidated dashboard data from NGAME run artifacts."""
    return jsonify(_load_latest_artifacts())

@app.route('/api/socketio-enabled')
def api_socketio_enabled():
    """Whether this server supports Socket.IO endpoints."""
    return jsonify({"enabled": True})

@app.route('/api/analysis-history')
def api_analysis_history():
    """Get analysis history."""
    return jsonify(ngame_state.analysis_history)

@app.route('/api/active-alerts')
def api_active_alerts():
    """Get active alerts."""
    return jsonify(ngame_state.active_alerts)

# WebSocket Events

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('connected', {'message': 'Connected to NGAME system'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

@socketio.on('start_analysis')
def handle_start_analysis(data):
    """Handle analysis start request."""
    analysis_type = data.get('type', 'comprehensive')
    emit('analysis_status', {'status': 'started', 'type': analysis_type})

@socketio.on('stop_analysis')
def handle_stop_analysis():
    """Handle analysis stop request."""
    emit('analysis_status', {'status': 'stopped'})

# Error Handlers

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    
    # Initialize NGAME state
    ngame_state.initialize_workflow()
    
    # Run the application
    socketio.run(app, debug=True, host='0.0.0.0', port=5001) 