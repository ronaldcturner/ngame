#!/usr/bin/env python3
"""
Training Agent Script - Append New Day Column
This script is run by the Training Agent to append new CPI data.
"""

import sys
import os
from training_agent_excel_manager import TrainingAgentExcelManager

def main():
    """Main function for Training Agent to append new day."""
    print("🤖 Training Agent - Appending New Day")
    print("=" * 50)
    
    # Initialize Excel manager
    excel_manager = TrainingAgentExcelManager()
    
    # Check if Excel file exists
    if not os.path.exists(excel_manager.excel_file):
        print("❌ Excel file not found. Creating initial file...")
        excel_manager.create_initial_excel()
    
    # Append new day (assumes new CPI data is in Today_Churn_Matrix_Ready.json)
    new_day = excel_manager.append_new_day()
    
    # Get matrix summary
    summary = excel_manager.get_matrix_summary()
    
    if summary:
        print(f"\n📊 MATRIX SUMMARY:")
        print(f"   Transaction types: {summary['total_transaction_types']}")
        print(f"   Total days: {summary['total_days']}")
        print(f"   Mean average CPI: {summary['mean_average_cpi']:.6f}")
        print(f"   Std average CPI: {summary['std_average_cpi']:.6f}")
        
        print(f"\n✅ Training Agent completed successfully!")
        print(f"📁 Excel file: {summary['excel_file']}")
        print(f"📈 New day added: Day {new_day}")
        
        return True
    else:
        print("❌ Failed to get matrix summary")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
