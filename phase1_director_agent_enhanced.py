#!/usr/bin/env python3
"""
Enhanced Phase 1 Director Agent with File Management
Includes automatic shifting of Today.ttl to Yesterday.ttl before generating new Today.ttl
"""

import os
import json
from datetime import datetime
from phase1_director_agent import Phase1DirectorAgent

class EnhancedPhase1DirectorAgent(Phase1DirectorAgent):
    """Enhanced Phase 1 Director Agent with file management capabilities."""
    
    def __init__(self):
        super().__init__()
        self.yesterday_file = 'quickbooks_ontology_Yesterday.ttl'
        self.today_file = 'quickbooks_ontology_Today.ttl'
    
    def shift_ttl_files(self):
        """Shift Today.ttl to Yesterday.ttl before generating new Today.ttl."""
        print("🔄 Shifting TTL Files")
        print("=" * 30)
        
        if os.path.exists(self.today_file):
            # Shift Today.ttl to Yesterday.ttl
            os.rename(self.today_file, self.yesterday_file)
            print(f"✅ Shifted {self.today_file} → {self.yesterday_file}")
            
            # Verify the shift
            if os.path.exists(self.yesterday_file):
                print(f"✅ {self.yesterday_file} confirmed")
            else:
                print(f"❌ Error: {self.yesterday_file} not found after shift")
                return False
        else:
            print(f"ℹ️  No existing {self.today_file} found (first run)")
        
        return True
    
    def run_enhanced_phase1(self):
        """Run enhanced Phase 1 with file management."""
        print("🚀 Enhanced Phase 1 - Data Extraction with File Management")
        print("=" * 70)
        
        # Step 1: Shift existing Today.ttl to Yesterday.ttl
        print("\n📁 Step 1: File Management")
        if not self.shift_ttl_files():
            print("❌ File management failed")
            return False
        
        # Step 2: Run Phase 1 to generate new Today.ttl
        print("\n📊 Step 2: Data Extraction")
        try:
            # Run the original Phase 1 workflow
            result = self.run()
            
            if result and os.path.exists(self.today_file):
                print(f"✅ Enhanced Phase 1 completed successfully")
                print(f"📁 Generated: {self.today_file}")
                print(f"📁 Previous: {self.yesterday_file}")
                return True
            else:
                print(f"❌ Enhanced Phase 1 failed")
                return False
                
        except Exception as e:
            print(f"❌ Error in Phase 1 execution: {e}")
            return False
    
    def get_file_status(self):
        """Get status of TTL files."""
        print("📁 TTL File Status")
        print("=" * 30)
        
        yesterday_exists = os.path.exists(self.yesterday_file)
        today_exists = os.path.exists(self.today_file)
        
        print(f"Yesterday.ttl: {'✅ Exists' if yesterday_exists else '❌ Missing'}")
        print(f"Today.ttl: {'✅ Exists' if today_exists else '❌ Missing'}")
        
        if yesterday_exists:
            yesterday_size = os.path.getsize(self.yesterday_file)
            print(f"Yesterday.ttl size: {yesterday_size:,} bytes")
        
        if today_exists:
            today_size = os.path.getsize(self.today_file)
            print(f"Today.ttl size: {today_size:,} bytes")
        
        return yesterday_exists, today_exists

def main():
    """Main function to demonstrate enhanced Phase 1."""
    print("🚀 Enhanced Phase 1 Director Agent")
    print("=" * 60)
    
    # Initialize enhanced Phase 1 agent
    enhanced_phase1 = EnhancedPhase1DirectorAgent()
    
    # Check initial file status
    print("\n📁 Initial File Status:")
    enhanced_phase1.get_file_status()
    
    # Run enhanced Phase 1
    print("\n🔄 Running Enhanced Phase 1:")
    success = enhanced_phase1.run_enhanced_phase1()
    
    if success:
        print("\n📁 Final File Status:")
        enhanced_phase1.get_file_status()
        
        print(f"\n🎉 Enhanced Phase 1 completed successfully!")
        print(f"📁 Ready for Phase 2 analysis")
        print(f"📁 Yesterday.ttl: Previous day ontology")
        print(f"📁 Today.ttl: Current day ontology")
        
        return True
    else:
        print(f"\n❌ Enhanced Phase 1 failed")
        return False

if __name__ == "__main__":
    main()
