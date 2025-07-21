"""
Helper utilities for the Job AI Agent.
"""

import re
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import html

logger = logging.getLogger(__name__)

class EmailPatterns:
    """Regular expression patterns for email classification."""
    
    # Job application confirmation patterns
    APPLICATION_PATTERNS = [
        r"thank you for (your )?application",
        r"application (has been )?received",
        r"we have received your application",
        r"your application for.*has been submitted",
        r"application confirmation",
        r"thank you for applying",
        r"application acknowledged"
    ]
    
    # Rejection patterns
    REJECTION_PATTERNS = [
        r"we regret to inform",
        r"unfortunately.*not selected",
        r"decided to move forward with other candidates",
        r"your application.*not successful",
        r"we will not be moving forward",
        r"position has been filled",
        r"not the right fit",
        r"thank you for your interest.*however"
    ]
    
    # Interview invitation patterns
    INTERVIEW_PATTERNS = [
        r"interview.*scheduled",
        r"would like to interview",
        r"next step.*interview",
        r"invite.*interview",
        r"schedule.*interview",
        r"interview invitation",
        r"phone.*interview",
        r"video.*interview"
    ]
    
    # Assessment patterns
    ASSESSMENT_PATTERNS = [
        r"assessment.*complete",
        r"coding.*challenge",
        r"technical.*assessment",
        r"take.*assessment",
        r"online.*test",
        r"skills.*assessment",
        r"programming.*test"
    ]

class EmailParser:
    """Utility class for parsing email content."""
    
    @staticmethod
    def clean_email_content(content: str) -> str:
        """Clean and normalize email content."""
        if not content:
            return ""
        
        # Decode HTML entities
        content = html.unescape(content)
        
        # Remove HTML tags (basic cleaning)
        content = re.sub(r'<[^>]+>', '', content)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove excessive line breaks
        content = re.sub(r'\n\s*\n', '\n', content)
        
        return content.strip()
    
    @staticmethod
    def extract_company_from_email(sender: str, subject: str, content: str) -> str:
        """Extract company name from email metadata."""
        # Try to extract from sender domain
        if '@' in sender:
            domain = sender.split('@')[1].lower()
            # Remove common email providers
            if domain not in ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']:
                company = domain.split('.')[0]
                return company.title()
        
        # Try to extract from subject
        subject_patterns = [
            r'from ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+team',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+careers'
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, subject)
            if match:
                return match.group(1)
        
        return ""
    
    @staticmethod
    def extract_position_from_content(subject: str, content: str) -> str:
        """Extract job position from email content."""
        position_patterns = [
            r'position.*?:\s*([^,\n]+)',
            r'role.*?:\s*([^,\n]+)',
            r'for the ([^,\n]+) position',
            r'for the ([^,\n]+) role',
            r'applied for:\s*([^,\n]+)',
            r'position of ([^,\n]+)'
        ]
        
        # First try subject line
        for pattern in position_patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Then try content
        for pattern in position_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""

class DateUtils:
    """Utility functions for date handling."""
    
    @staticmethod
    def parse_email_date(date_str: str) -> Optional[datetime]:
        """Parse email date string to datetime object."""
        if not date_str:
            return None
        
        # Common email date formats
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%d %b %Y %H:%M:%S %z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d"
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                # If no timezone info, assume UTC
                if parsed_date.tzinfo is None:
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                return parsed_date
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    @staticmethod
    def get_date_range(days_back: int) -> Tuple[datetime, datetime]:
        """Get date range for email search."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days_back)
        return start_date, end_date
    
    @staticmethod
    def format_date_for_gmail_query(date: datetime) -> str:
        """Format date for Gmail API query."""
        return date.strftime("%Y/%m/%d")

class FileUtils:
    """Utility functions for file operations."""
    
    @staticmethod
    def ensure_directory_exists(file_path: str) -> None:
        """Ensure the directory for a file path exists."""
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def setup_logging(log_level: str = "INFO") -> None:
        """Setup logging configuration."""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"job_agent_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

class ValidationUtils:
    """Utility functions for data validation."""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_spreadsheet_id(spreadsheet_id: str) -> bool:
        """Validate Google Sheets spreadsheet ID format."""
        # Google Sheets ID is typically 44 characters long
        return bool(spreadsheet_id and len(spreadsheet_id) >= 40)
