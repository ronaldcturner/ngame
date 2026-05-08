#!/usr/bin/env python3
"""
NGAME Fraud Analysis Launcher
Ensures correct Python environment and runs the fraud analysis flow
"""

import sys
import os
import subprocess

def check_environment():
    """Check if we're in the correct environment."""
    print("🔍 Checking Python environment...")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Check if required modules are available
    required_modules = ['openpyxl', 'numpy', 'rdflib', 'requests']
    all_available = True
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: available")
        except ImportError as e:
            print(f"❌ {module}: not available - {e}")
            all_available = False
    
    return all_available

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    dependencies = ['openpyxl', 'numpy', 'rdflib', 'requests']
    
    for dep in dependencies:
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ {dep} installed successfully")
            else:
                print(f"❌ Failed to install {dep}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error installing {dep}: {e}")
            return False
    
    return True

def run_fraud_analysis():
    """Run the fraud analysis flow manager."""
    print("🚀 Starting NGAME Fraud Analysis...")
    
    try:
        from ngame_fraud_analysis_flow_manager import NGameFraudAnalysisFlowManager
        
        # Initialize fraud analysis manager
        fraud_manager = NGameFraudAnalysisFlowManager()
        
        # Validate prerequisites
        print(f"\n🔍 Validating prerequisites...")
        if not fraud_manager.validate_prerequisites():
            print(f"\n❌ Prerequisites not met. Please complete training period first.")
            return False
        
        # Ask user if they want to proceed
        print(f"\n❓ Do you want to run the fraud analysis? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes']:
            print(f"\n🔍 Starting fraud analysis...")
            
            # Initialize agents
            fraud_manager.initialize_agents()
            
            # Execute daily fraud analysis
            result = fraud_manager.execute_daily_fraud_analysis()
            
            # Show summary
            fraud_manager.show_fraud_analysis_summary(result)
            
            if result['success']:
                print(f"\n🎉 Fraud analysis completed successfully!")
                return True
            else:
                print(f"\n❌ Fraud analysis failed")
                return False
        else:
            print(f"\n⏹️  Fraud analysis cancelled by user")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error running fraud analysis: {e}")
        return False

def main():
    """Main function."""
    print("🚀 NGAME Fraud Analysis Launcher")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n🔧 Attempting to fix environment...")
        if not install_dependencies():
            print("\n❌ Could not fix environment. Please check your Python setup.")
            return False
    
    # Run fraud analysis
    success = run_fraud_analysis()
    
    if success:
        print(f"\n✅ Launcher completed successfully!")
    else:
        print(f"\n❌ Launcher failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
