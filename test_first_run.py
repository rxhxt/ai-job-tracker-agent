#!/usr/bin/env python3
"""
Test script to demonstrate first run vs ongoing monitoring behavior.
"""

import os
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_first_run_detection():
    """Test the first run detection logic."""
    from services.email_tracker import EmailTracker
    from config.settings import settings
    
    logger.info("=== Testing First Run Detection ===")
    
    # Initialize email tracker
    tracker = EmailTracker()
    
    # Check if this is first run
    is_first_run = tracker.is_first_run()
    logger.info(f"Is first run: {is_first_run}")
    
    # Show what email counts would be used
    first_run_count = settings.FIRST_RUN_EMAIL_COUNT
    ongoing_count = settings.ONGOING_EMAIL_COUNT
    
    logger.info(f"First run email count: {first_run_count}")
    logger.info(f"Ongoing monitoring email count: {ongoing_count}")
    
    if is_first_run:
        logger.info(f"✅ First run detected - will check {first_run_count} emails")
    else:
        logger.info(f"✅ Ongoing monitoring - will check {ongoing_count} emails")
        
        # Show some stats
        stats = tracker.get_stats()
        logger.info(f"Previously processed emails: {stats['total_processed']}")
        logger.info(f"Processed today: {stats['processed_today']}")
    
    return is_first_run

def simulate_first_run():
    """Simulate what happens during first run."""
    logger.info("\n=== Simulating First Run Behavior ===")
    
    # Backup existing processed emails file if it exists
    from config.settings import settings
    processed_file = settings.PROCESSED_EMAILS_FILE
    backup_file = f"{processed_file}.backup"
    
    if os.path.exists(processed_file):
        logger.info(f"Backing up existing processed emails to {backup_file}")
        os.rename(processed_file, backup_file)
    
    try:
        # Test first run detection
        from services.email_tracker import EmailTracker
        tracker = EmailTracker()
        
        logger.info(f"First run status: {tracker.is_first_run()}")
        logger.info("This would trigger fetching 50 emails instead of 10")
        
        # Add a fake processed email to simulate running
        tracker.mark_email_processed("test_email_123", "Test Email Subject", "processed")
        
        # Check again
        logger.info(f"After processing one email, first run status: {tracker.is_first_run()}")
        logger.info("Now it would fetch only 10 emails for ongoing monitoring")
        
    finally:
        # Restore backup if it exists
        if os.path.exists(backup_file):
            if os.path.exists(processed_file):
                os.remove(processed_file)
            os.rename(backup_file, processed_file)
            logger.info("Restored original processed emails file")

def main():
    """Main test function."""
    logger.info("🚀 Testing First Run vs Ongoing Monitoring Logic")
    
    # Test current state
    test_first_run_detection()
    
    # Simulate first run behavior
    simulate_first_run()
    
    logger.info("\n✅ Test completed!")
    logger.info("When you start the agent:")
    logger.info("- First time: Will check 50 recent emails")
    logger.info("- Subsequent runs: Will check only 10 emails every 15 minutes")
    logger.info("- This optimizes API usage while ensuring no emails are missed")

if __name__ == "__main__":
    main()
