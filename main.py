"""
Main Job AI Agent application.
"""

import argparse
import logging
from datetime import datetime
from typing import List, Tuple

from config.settings import settings
from services.gmail_service import GmailService
from services.sheets_service import SheetsService
from services.email_parser import EmailParsingService
from services.notification_service import NotificationService
from services.email_tracker import EmailTracker
from models.job_application import EmailData, EmailType, JobApplication, JobStatus
from utils.helpers import FileUtils

logger = logging.getLogger(__name__)

class JobAIAgent:
    """Main application class for the Job AI Agent."""
    
    def __init__(self):
        self.gmail_service = GmailService()
        self.sheets_service = SheetsService()
        self.email_parser = EmailParsingService()
        self.notification_service = NotificationService()
        self.email_tracker = EmailTracker()
        
        # Statistics
        self.stats = {
            'emails_processed': 0,
            'emails_checked': 0,
            'new_applications': 0,
            'status_updates': 0,
            'notifications_sent': 0,
            'errors': 0,
            'duplicates_skipped': 0
        }
    
    def run(self, days_back: int = None, email_id: str = None) -> bool:
        """
        Run the job tracking agent.
        
        Args:
            days_back: Number of days to look back for emails
            email_id: Specific email ID to process
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting Job AI Agent")
        
        # Validate configuration
        validation_errors = settings.validate()
        if validation_errors:
            logger.error(f"Configuration errors: {', '.join(validation_errors)}")
            return False
        
        try:
            if email_id:
                # Process specific email
                return self._process_specific_email(email_id)
            else:
                # Process recent emails
                days = days_back or settings.DAYS_TO_LOOK_BACK
                return self._process_recent_emails(days)
        
        except Exception as e:
            logger.error(f"Unexpected error in main execution: {e}")
            self.stats['errors'] += 1
            return False
        
        finally:
            self._log_statistics()
    
    def _process_specific_email(self, email_id: str) -> bool:
        """Process a specific email by ID."""
        logger.info(f"Processing specific email: {email_id}")
        
        email_data = self.gmail_service.get_email_by_id(email_id)
        if not email_data:
            logger.error(f"Could not retrieve email with ID: {email_id}")
            return False
        
        return self._process_email(email_data)
    
    def _process_recent_emails(self, days_back: int) -> bool:
        """Process recent emails for job-related content."""
        # Check if this is the first run
        is_first_run = self.email_tracker.is_first_run()
        max_emails = settings.FIRST_RUN_EMAIL_COUNT if is_first_run else settings.ONGOING_EMAIL_COUNT
        
        logger.info(f"Processing emails from the last {days_back} days")
        logger.info(f"{'First run' if is_first_run else 'Ongoing monitoring'} - checking max {max_emails} emails")
        
        # Get recent emails with dynamic max_results
        emails = self.gmail_service.get_recent_emails(
            days_back=days_back,
            is_first_run=is_first_run
        )
        
        if not emails:
            logger.info("No emails found to process")
            return True
        
        self.stats['emails_checked'] = len(emails)
        logger.info(f"Found {len(emails)} emails to check")
        
        # Filter out already processed emails
        new_emails = self.email_tracker.get_new_emails(emails)
        
        if not new_emails:
            logger.info("No new emails to process (all were already processed)")
            self.stats['duplicates_skipped'] = len(emails)
            return True
        
        logger.info(f"Processing {len(new_emails)} new emails (skipped {len(emails) - len(new_emails)} duplicates)")
        self.stats['duplicates_skipped'] = len(emails) - len(new_emails)
        
        # Process each new email
        success_count = 0
        for email_data in new_emails:
            try:
                if self._process_email(email_data):
                    success_count += 1
                    self.email_tracker.mark_email_processed(
                        email_data.email_id, 
                        email_data.subject, 
                        "processed"
                    )
                else:
                    self.email_tracker.mark_email_processed(
                        email_data.email_id, 
                        email_data.subject, 
                        "skipped"
                    )
            except Exception as e:
                logger.error(f"Error processing email {email_data.email_id}: {e}")
                self.stats['errors'] += 1
                self.email_tracker.mark_email_processed(
                    email_data.email_id, 
                    email_data.subject, 
                    "error"
                )
        
        logger.info(f"Successfully processed {success_count}/{len(new_emails)} new emails")
        
        # Cleanup old tracking records periodically
        self.email_tracker.cleanup_old_records(days_to_keep=30)
        
        return success_count == len(new_emails)
    
    def _process_email(self, email_data: EmailData) -> bool:
        """
        Process a single email.
        
        Args:
            email_data: EmailData object to process
            
        Returns:
            True if successful, False otherwise
        """
        self.stats['emails_processed'] += 1
        
        logger.debug(f"Processing email: {email_data.subject[:50]}...")
        
        # Parse email for job application information
        job_application = self.email_parser.parse_job_email(email_data)
        
        if not job_application:
            logger.debug("Email does not contain job application information")
            return True
        
        # Handle the job application
        success = self._handle_job_application(job_application, email_data)
        
        # Send notifications if needed
        if success and self.notification_service.should_send_notification(email_data):
            if self.notification_service.send_notification_for_email(email_data):
                self.stats['notifications_sent'] += 1
            else:
                logger.warning(f"Failed to send notification for email: {email_data.email_id}")
        
        return success
    
    def _handle_job_application(self, job_application: JobApplication, email_data: EmailData) -> bool:
        """
        Handle a parsed job application.
        
        Args:
            job_application: JobApplication object
            email_data: Original email data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if this application already exists
            existing_app = self.sheets_service.find_job_application(
                job_application.company, job_application.position
            )
            
            if existing_app:
                # Update existing application
                updated_app = self._merge_application_data(existing_app, job_application, email_data)
                if self.sheets_service.update_job_application(updated_app):
                    self.stats['status_updates'] += 1
                    logger.info(f"Updated application: {job_application.company} - {job_application.position}")
                    return True
                else:
                    logger.error(f"Failed to update application: {job_application.company} - {job_application.position}")
                    return False
            else:
                # Add new application
                if self.sheets_service.add_job_application(job_application):
                    self.stats['new_applications'] += 1
                    logger.info(f"Added new application: {job_application.company} - {job_application.position}")
                    return True
                else:
                    logger.error(f"Failed to add application: {job_application.company} - {job_application.position}")
                    return False
        
        except Exception as e:
            logger.error(f"Error handling job application: {e}")
            return False
    
    def _merge_application_data(self, existing: JobApplication, new: JobApplication, email_data: EmailData) -> JobApplication:
        """
        Merge existing application data with new information.
        
        Args:
            existing: Existing JobApplication
            new: New JobApplication data
            email_data: Email data for additional context
            
        Returns:
            Merged JobApplication
        """
        # Update status based on email type
        if email_data.email_type == EmailType.REJECTION:
            existing.status = JobStatus.REJECTED
        elif email_data.email_type == EmailType.INTERVIEW_INVITATION:
            existing.status = JobStatus.INTERVIEW_SCHEDULED
        elif email_data.email_type == EmailType.ASSESSMENT_REQUEST:
            existing.status = JobStatus.ASSESSMENT_RECEIVED
        elif email_data.email_type == EmailType.OFFER:
            existing.status = JobStatus.OFFER_RECEIVED
        
        # Update email information
        existing.email_date = email_data.date
        existing.email_subject = email_data.subject
        existing.email_id = email_data.email_id
        
        # Append to notes if there's new information
        if new.notes and new.notes not in existing.notes:
            if existing.notes:
                existing.notes += f" | {new.notes}"
            else:
                existing.notes = new.notes
        
        return existing
    
    def _log_statistics(self) -> None:
        """Log processing statistics."""
        tracker_stats = self.email_tracker.get_stats()
        
        logger.info("=== Job AI Agent Statistics ===")
        logger.info(f"Emails checked: {self.stats['emails_checked']}")
        logger.info(f"Emails processed: {self.stats['emails_processed']}")
        logger.info(f"Duplicates skipped: {self.stats['duplicates_skipped']}")
        logger.info(f"New applications: {self.stats['new_applications']}")
        logger.info(f"Status updates: {self.stats['status_updates']}")
        logger.info(f"Notifications sent: {self.stats['notifications_sent']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"Total processed emails in DB: {tracker_stats['total_processed']}")
        logger.info(f"Processed today: {tracker_stats['processed_today']}")
        logger.info("===============================")
    
    def test_configuration(self) -> bool:
        """
        Test all service configurations.
        
        Returns:
            True if all tests pass, False otherwise
        """
        logger.info("Testing Job AI Agent configuration...")
        
        all_passed = True
        
        # Test Gmail service
        if self.gmail_service.service:
            logger.info("✓ Gmail service configured correctly")
        else:
            logger.error("✗ Gmail service configuration failed")
            all_passed = False
        
        # Test Google Sheets service
        if self.sheets_service.service:
            logger.info("✓ Google Sheets service configured correctly")
        else:
            logger.error("✗ Google Sheets service configuration failed")
            all_passed = False
        
        # Test email parser
        if self.email_parser.gemini_model:
            logger.info("✓ Gemini email parser configured correctly")
        else:
            logger.warning("⚠ Gemini not configured, using pattern-based parsing")
        
        # Test notification service
        notification_test = self.notification_service.test_email_configuration()
        if notification_test:
            if not self.notification_service.email_address:
                logger.info("✓ Email notifications disabled (will only update sheets)")
            else:
                logger.info("✓ Email notifications configured correctly")
        else:
            logger.error("✗ Email notification configuration failed")
            all_passed = False
        
        if all_passed:
            logger.info("🎉 All configurations are working correctly!")
        else:
            logger.error("❌ Some configurations failed. Please check your settings.")
        
        return all_passed

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Job AI Agent - Automated job application tracking")
    parser.add_argument('--days', type=int, default=7, help='Number of days to look back for emails')
    parser.add_argument('--email-id', type=str, help='Specific email ID to process')
    parser.add_argument('--test', action='store_true', help='Test configuration only')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    
    # Setup logging
    FileUtils.setup_logging(args.log_level)
    
    # Create and run agent
    agent = JobAIAgent()
    
    if args.test:
        success = agent.test_configuration()
    else:
        success = agent.run(days_back=args.days, email_id=args.email_id)
    
    if success:
        logger.info("Job AI Agent completed successfully")
        exit(0)
    else:
        logger.error("Job AI Agent completed with errors")
        exit(1)

if __name__ == "__main__":
    main()
