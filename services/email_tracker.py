"""
Email tracking service to avoid processing duplicates.
"""

import json
import os
import logging
from typing import Set, Dict, Any
from datetime import datetime, timedelta
from config.settings import settings

logger = logging.getLogger(__name__)

class EmailTracker:
    """Track processed emails to avoid duplicates."""
    
    def __init__(self):
        self.processed_emails_file = settings.PROCESSED_EMAILS_FILE
        self.processed_emails: Dict[str, Dict[str, Any]] = {}
        self._load_processed_emails()
    
    def _load_processed_emails(self) -> None:
        """Load processed emails from file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.processed_emails_file), exist_ok=True)
            
            if os.path.exists(self.processed_emails_file):
                with open(self.processed_emails_file, 'r') as f:
                    data = json.load(f)
                    self.processed_emails = data
                logger.info(f"Loaded {len(self.processed_emails)} processed email records")
            else:
                logger.info("No existing processed emails file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading processed emails: {e}")
            self.processed_emails = {}
    
    def _save_processed_emails(self) -> None:
        """Save processed emails to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.processed_emails_file), exist_ok=True)
            
            with open(self.processed_emails_file, 'w') as f:
                json.dump(self.processed_emails, f, indent=2, default=str)
            logger.debug(f"Saved {len(self.processed_emails)} processed email records")
        except Exception as e:
            logger.error(f"Error saving processed emails: {e}")
    
    def is_email_processed(self, email_id: str) -> bool:
        """
        Check if an email has already been processed.
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            True if email was already processed
        """
        return email_id in self.processed_emails
    
    def mark_email_processed(self, email_id: str, email_subject: str, processing_result: str = "processed") -> None:
        """
        Mark an email as processed.
        
        Args:
            email_id: Gmail message ID
            email_subject: Email subject for reference
            processing_result: Result of processing (processed, skipped, error)
        """
        self.processed_emails[email_id] = {
            'processed_at': datetime.now().isoformat(),
            'subject': email_subject[:100],  # Truncate long subjects
            'result': processing_result
        }
        self._save_processed_emails()
        logger.debug(f"Marked email as {processing_result}: {email_subject[:50]}...")
    
    def get_new_emails(self, email_list: list) -> list:
        """
        Filter out already processed emails from a list.
        
        Args:
            email_list: List of EmailData objects
            
        Returns:
            List of unprocessed EmailData objects
        """
        new_emails = []
        for email_data in email_list:
            if not self.is_email_processed(email_data.email_id):
                new_emails.append(email_data)
            else:
                logger.debug(f"Skipping already processed email: {email_data.subject[:50]}...")
        
        logger.info(f"Found {len(new_emails)} new emails out of {len(email_list)} total")
        return new_emails
    
    def cleanup_old_records(self, days_to_keep: int = 30) -> None:
        """
        Clean up old processed email records.
        
        Args:
            days_to_keep: Number of days to keep records
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        initial_count = len(self.processed_emails)
        
        # Filter out old records
        self.processed_emails = {
            email_id: data for email_id, data in self.processed_emails.items()
            if datetime.fromisoformat(data['processed_at']) > cutoff_date
        }
        
        removed_count = initial_count - len(self.processed_emails)
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old processed email records")
            self._save_processed_emails()
    
    def is_first_run(self) -> bool:
        """
        Check if this is the first run of the agent.
        
        Returns:
            True if no emails have been processed before, False otherwise
        """
        return len(self.processed_emails) == 0
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about processed emails."""
        total = len(self.processed_emails)
        today = datetime.now().date()
        
        today_count = sum(
            1 for data in self.processed_emails.values()
            if datetime.fromisoformat(data['processed_at']).date() == today
        )
        
        return {
            'total_processed': total,
            'processed_today': today_count
        }
