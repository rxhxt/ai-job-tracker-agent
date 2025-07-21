"""
Gmail API service for reading and processing emails.
"""

import base64
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from models.job_application import EmailData, EmailType
from utils.auth import GoogleAuthenticator
from utils.helpers import EmailParser, DateUtils
from config.settings import settings

logger = logging.getLogger(__name__)

class GmailService:
    """Service for interacting with Gmail API."""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self._initialize_service()
    
    def _initialize_service(self) -> None:
        """Initialize Gmail API service."""
        try:
            self.credentials = GoogleAuthenticator.get_gmail_credentials(
                scopes=settings.GMAIL_SCOPES,
                credentials_file=settings.GMAIL_CREDENTIALS_FILE,
                token_file=settings.GMAIL_TOKEN_FILE
            )
            
            if self.credentials:
                self.service = build('gmail', 'v1', credentials=self.credentials)
                logger.info("Gmail service initialized successfully")
            else:
                logger.error("Failed to get Gmail credentials")
                
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {e}")
    
    def get_recent_emails(self, days_back: int = 1, max_results: int = None, is_first_run: bool = False) -> List[EmailData]:
        """
        Get recent emails that might be job-related.
        
        Args:
            days_back: Number of days to look back (default 1 for recent monitoring)
            max_results: Maximum number of emails to retrieve (auto-determined if None)
            is_first_run: Whether this is the first run of the agent
            
        Returns:
            List of EmailData objects
        """
        if not self.service:
            logger.error("Gmail service not initialized")
            return []
        
        # Determine max_results based on first run or ongoing monitoring
        if max_results is None:
            max_results = settings.FIRST_RUN_EMAIL_COUNT if is_first_run else settings.ONGOING_EMAIL_COUNT
            
        logger.info(f"Fetching emails - First run: {is_first_run}, Max results: {max_results}")
        
        try:
            # Build search query for recent job-related emails
            start_date, _ = DateUtils.get_date_range(days_back)
            date_str = DateUtils.format_date_for_gmail_query(start_date)
            
            # Search for recent emails with job-related keywords - more specific for monitoring
            query = f'after:{date_str} (from:noreply OR from:careers OR from:jobs OR from:hr OR from:recruiting OR from:talent OR subject:application OR subject:interview OR subject:position OR subject:opportunity OR subject:"thank you" OR subject:assessment OR subject:coding OR subject:technical OR subject:next OR subject:congratulations)'
            
            logger.info(f"Gmail query: {query}")
            
            # Get message list
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = result.get('messages', [])
            logger.info(f"Found {len(messages)} potentially job-related emails")
            
            # Process each message
            emails = []
            for message in messages:
                email_data = self._process_email(message['id'])
                if email_data:
                    emails.append(email_data)
            
            # Sort by date (newest first)
            emails.sort(key=lambda x: x.date, reverse=True)
            
            return emails
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting emails: {e}")
            return []
    
    def get_email_by_id(self, email_id: str) -> Optional[EmailData]:
        """
        Get a specific email by ID.
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            EmailData object or None
        """
        if not self.service:
            logger.error("Gmail service not initialized")
            return None
        
        return self._process_email(email_id)
    
    def _process_email(self, email_id: str) -> Optional[EmailData]:
        """
        Process a single email message.
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            EmailData object or None
        """
        try:
            # Get message details
            message = self.service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
            
            # Extract basic information
            subject = headers.get('Subject', '')
            sender = headers.get('From', '')
            date_str = headers.get('Date', '')
            
            # Parse date
            email_date = DateUtils.parse_email_date(date_str) or datetime.now(timezone.utc)
            
            # Extract body
            body = self._extract_email_body(message['payload'])
            body = EmailParser.clean_email_content(body)
            
            # Create EmailData object
            email_data = EmailData(
                email_id=email_id,
                subject=subject,
                sender=sender,
                date=email_date,
                body=body
            )
            
            # Classify email type and extract company/position
            self._classify_email(email_data)
            
            logger.debug(f"Processed email: {subject[:50]}...")
            return email_data
            
        except HttpError as e:
            logger.error(f"Error processing email {email_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error processing email {email_id}: {e}")
            return None
    
    def _extract_email_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract text content from email payload.
        
        Args:
            payload: Gmail message payload
            
        Returns:
            Email body text
        """
        body = ""
        
        # Handle different payload structures
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif part['mimeType'] == 'text/html' and not body:
                    # Use HTML if no plain text available
                    data = part['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        else:
            # Single part message
            if payload['mimeType'] in ['text/plain', 'text/html']:
                data = payload['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return body
    
    def _classify_email(self, email_data: EmailData) -> None:
        """
        Classify email type and extract relevant information.
        
        Args:
            email_data: EmailData object to classify
        """
        content = f"{email_data.subject} {email_data.body}".lower()
        
        # Check for different email types
        from utils.helpers import EmailPatterns
        
        # Check for rejections first (higher priority)
        for pattern in EmailPatterns.REJECTION_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                email_data.email_type = EmailType.REJECTION
                email_data.confidence = 0.9
                break
        
        # Check for interviews
        if email_data.email_type == EmailType.OTHER:
            for pattern in EmailPatterns.INTERVIEW_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    email_data.email_type = EmailType.INTERVIEW_INVITATION
                    email_data.confidence = 0.8
                    break
        
        # Check for assessments
        if email_data.email_type == EmailType.OTHER:
            for pattern in EmailPatterns.ASSESSMENT_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    email_data.email_type = EmailType.ASSESSMENT_REQUEST
                    email_data.confidence = 0.8
                    break
        
        # Check for application confirmations
        if email_data.email_type == EmailType.OTHER:
            for pattern in EmailPatterns.APPLICATION_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    email_data.email_type = EmailType.APPLICATION_CONFIRMATION
                    email_data.confidence = 0.7
                    break
        
        # Extract company and position
        email_data.company = EmailParser.extract_company_from_email(
            email_data.sender, email_data.subject, email_data.body
        )
        email_data.position = EmailParser.extract_position_from_content(
            email_data.subject, email_data.body
        )
        
        logger.debug(f"Classified email as {email_data.email_type} with confidence {email_data.confidence}")
    
    def mark_email_as_read(self, email_id: str) -> bool:
        """
        Mark an email as read.
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to mark email as read: {e}")
            return False
