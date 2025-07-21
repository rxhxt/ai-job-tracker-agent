"""
Authentication utilities for Google APIs.
"""

import json
import os
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)

class GoogleAuthenticator:
    """Handle Google API authentication."""
    
    @staticmethod
    def get_gmail_credentials(scopes: list, credentials_file: str, token_file: str) -> Optional[Credentials]:
        """
        Get Gmail API credentials using OAuth2 flow.
        
        Args:
            scopes: List of required OAuth scopes
            credentials_file: Path to Gmail credentials JSON file
            token_file: Path to store/retrieve access token
            
        Returns:
            Credentials object or None if authentication fails
        """
        creds = None
        
        # Create tokens directory if it doesn't exist
        os.makedirs(os.path.dirname(token_file), exist_ok=True)
        
        # Load existing token
        if os.path.exists(token_file):
            try:
                creds = Credentials.from_authorized_user_file(token_file, scopes)
            except Exception as e:
                logger.warning(f"Error loading existing token: {e}")
                creds = None
        
        # If no valid credentials, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed Gmail credentials")
                except RefreshError as e:
                    logger.error(f"Failed to refresh credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(credentials_file):
                    logger.error(f"Gmail credentials file not found: {credentials_file}")
                    return None
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
                    creds = flow.run_local_server(port=0)
                    logger.info("Completed Gmail OAuth flow")
                except Exception as e:
                    logger.error(f"OAuth flow failed: {e}")
                    return None
            
            # Save credentials for next run
            try:
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
                logger.info(f"Saved Gmail credentials to {token_file}")
            except Exception as e:
                logger.error(f"Failed to save credentials: {e}")
        
        return creds
    
    @staticmethod
    def get_sheets_credentials(credentials_file: str, scopes: list) -> Optional[service_account.Credentials]:
        """
        Get Google Sheets API credentials using service account.
        
        Args:
            credentials_file: Path to service account JSON file
            scopes: List of required OAuth scopes
            
        Returns:
            Service account credentials or None if authentication fails
        """
        if not os.path.exists(credentials_file):
            logger.error(f"Sheets credentials file not found: {credentials_file}")
            return None
        
        try:
            creds = service_account.Credentials.from_service_account_file(
                credentials_file, scopes=scopes
            )
            logger.info("Loaded Google Sheets service account credentials")
            return creds
        except Exception as e:
            logger.error(f"Failed to load Sheets credentials: {e}")
            return None
    
    @staticmethod
    def validate_credentials(creds: Credentials) -> bool:
        """
        Validate that credentials are valid and not expired.
        
        Args:
            creds: Credentials to validate
            
        Returns:
            True if credentials are valid, False otherwise
        """
        if not creds:
            return False
        
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    return True
                except RefreshError:
                    return False
            return False
        
        return True
