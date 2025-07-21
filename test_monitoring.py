#!/usr/bin/env python3
"""
Test script for continuous email monitoring.
"""

import time
import logging
from datetime import datetime
from main import JobAIAgent
from utils.helpers import FileUtils

def test_continuous_monitoring():
    """Test the continuous monitoring functionality."""
    print("🧪 Testing Continuous Email Monitoring")
    print("=" * 50)
    
    # Setup logging
    FileUtils.setup_logging("DEBUG")
    logger = logging.getLogger(__name__)
    
    # Create agent
    agent = JobAIAgent()
    
    # Test configuration first
    print("\n1. Testing configuration...")
    if not agent.test_configuration():
        print("❌ Configuration test failed. Please fix issues first.")
        return False
    
    print("✅ Configuration test passed!")
    
    # Test email processing
    print("\n2. Testing email processing...")
    start_time = datetime.now()
    
    success = agent.run(days_back=1)  # Check last 1 day
    
    duration = (datetime.now() - start_time).total_seconds()
    
    if success:
        print(f"✅ Email processing test passed! (took {duration:.2f}s)")
    else:
        print(f"⚠️ Email processing completed with some issues (took {duration:.2f}s)")
    
    # Show statistics
    print("\n3. Processing Statistics:")
    tracker_stats = agent.email_tracker.get_stats()
    print(f"   📧 Emails checked: {agent.stats['emails_checked']}")
    print(f"   🆕 New emails processed: {agent.stats['emails_processed']}")
    print(f"   ⏭️ Duplicates skipped: {agent.stats['duplicates_skipped']}")
    print(f"   📝 New applications: {agent.stats['new_applications']}")
    print(f"   🔄 Status updates: {agent.stats['status_updates']}")
    print(f"   📨 Notifications sent: {agent.stats['notifications_sent']}")
    print(f"   💾 Total emails in tracking DB: {tracker_stats['total_processed']}")
    
    print("\n4. System is ready for continuous monitoring!")
    print("   Run: python scheduler.py")
    print(f"   Will check every 15 minutes for latest 15 emails")
    
    return True

def simulate_monitoring_run():
    """Simulate what happens during a monitoring run."""
    print("\n🔄 Simulating monitoring run...")
    
    agent = JobAIAgent()
    
    print("   - Checking Gmail for latest 15 emails")
    print("   - Filtering out already processed emails")
    print("   - Processing only new emails with Gemini")
    print("   - Updating Google Sheets if needed")
    print("   - Sending notifications for interviews/assessments")
    print("   - Saving processed email IDs to avoid duplicates")
    
    # Run actual check
    success = agent.run(days_back=1)
    
    if success:
        print("   ✅ Monitoring run completed successfully")
    else:
        print("   ⚠️ Monitoring run completed with some issues")

if __name__ == "__main__":
    try:
        if test_continuous_monitoring():
            response = input("\n🚀 Run a simulation of the monitoring process? (y/N): ")
            if response.lower() == 'y':
                simulate_monitoring_run()
        
        print("\n📖 Next steps:")
        print("1. Fix your EMAIL_PASSWORD in .env (use Gmail App Password)")
        print("2. Run: python scheduler.py")
        print("3. The system will check for new emails every 15 minutes")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.error(f"Test failed: {e}")
