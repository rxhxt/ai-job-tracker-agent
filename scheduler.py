"""
Scheduler for continuous job tracking monitoring.
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
import signal
import sys

from main import JobAIAgent
from utils.helpers import FileUtils
from config.settings import settings

logger = logging.getLogger(__name__)

class JobScheduler:
    """Scheduler for running the Job AI Agent at regular intervals."""
    
    def __init__(self):
        self.agent = JobAIAgent()
        self.running = True
        self.last_run = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def run_job_check(self):
        """Run the job checking process."""
        try:
            logger.info("=== Starting scheduled job check ===")
            start_time = datetime.now()
            
            # For continuous monitoring, always check last 1 day with latest 15 emails
            days_back = 1  # Always check recent emails
            
            # Run the agent
            success = self.agent.run(days_back=days_back)
            
            # Update last run time
            self.last_run = datetime.now()
            
            # Log completion
            duration = (datetime.now() - start_time).total_seconds()
            status = "successfully" if success else "with errors"
            logger.info(f"Scheduled job check completed {status} in {duration:.2f} seconds")
            
            # Send daily summary if it's the first run of the day
            if self._is_first_run_today():
                self._send_daily_summary()
            
        except Exception as e:
            logger.error(f"Error in scheduled job check: {e}")
    
    def _is_first_run_today(self) -> bool:
        """Check if this is the first run today."""
        if not self.last_run:
            return True
        
        return self.last_run.date() < datetime.now().date()
    
    def _send_daily_summary(self):
        """Send daily summary notification."""
        try:
            stats = self.agent.stats
            self.agent.notification_service.send_daily_summary(
                new_applications=stats.get('new_applications', 0),
                updates=stats.get('status_updates', 0),
                interviews=stats.get('notifications_sent', 0),  # Approximate
                assessments=0  # Would need to track separately
            )
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
    
    def start_monitoring(self):
        """Start continuous monitoring with scheduled checks."""
        logger.info("Starting Job AI Agent continuous monitoring...")
        
        # Test configuration before starting
        if not self.agent.test_configuration():
            logger.error("Configuration test failed. Please fix issues before starting monitoring.")
            return False
        
        # Schedule regular checks every 15 minutes
        schedule.every(settings.POLLING_INTERVAL_MINUTES).minutes.do(self.run_job_check)
        schedule.every().day.at("09:00").do(self.run_job_check)  # Morning check
        schedule.every().day.at("18:00").do(self.run_job_check)  # Evening check
        
        logger.info("Scheduled job checks:")
        logger.info(f"- Every {settings.POLLING_INTERVAL_MINUTES} minutes")
        logger.info("- Daily at 9:00 AM")
        logger.info("- Daily at 6:00 PM")
        
        # Run initial check
        logger.info("Running initial job check...")
        self.run_job_check()
        
        # Main monitoring loop
        logger.info("Job AI Agent monitoring started. Press Ctrl+C to stop.")
        logger.info(f"Will check for new emails every {settings.POLLING_INTERVAL_MINUTES} minutes")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds for scheduled jobs
        
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            return False
        
        finally:
            logger.info("Job AI Agent monitoring stopped")
        
        return True
    
    def run_once(self, days_back: int = None):
        """Run the agent once and exit."""
        logger.info("Running Job AI Agent once...")
        
        # Test configuration
        if not self.agent.test_configuration():
            logger.error("Configuration test failed")
            return False
        
        # Run the agent
        days = days_back or settings.DAYS_TO_LOOK_BACK
        success = self.agent.run(days_back=days)
        
        if success:
            logger.info("Job AI Agent completed successfully")
        else:
            logger.error("Job AI Agent completed with errors")
        
        return success

def main():
    """Main entry point for scheduler."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Job AI Agent Scheduler")
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--days', type=int, default=7, help='Number of days to look back')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    
    # Setup logging
    FileUtils.setup_logging(args.log_level)
    
    # Create scheduler
    scheduler = JobScheduler()
    
    try:
        if args.once:
            success = scheduler.run_once(days_back=args.days)
            sys.exit(0 if success else 1)
        else:
            success = scheduler.start_monitoring()
            sys.exit(0 if success else 1)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
