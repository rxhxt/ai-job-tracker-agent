"""
Configuration settings for the Job AI Agent.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # Gmail API Configuration
    GMAIL_CLIENT_ID: str = os.getenv('GMAIL_CLIENT_ID', '')
    GMAIL_CLIENT_SECRET: str = os.getenv('GMAIL_CLIENT_SECRET', '')
    GMAIL_SCOPES: List[str] = ['https://www.googleapis.com/auth/gmail.readonly']
    
    # Google Sheets API Configuration
    SHEETS_CLIENT_ID: str = os.getenv('SHEETS_CLIENT_ID', '')
    SHEETS_CLIENT_SECRET: str = os.getenv('SHEETS_CLIENT_SECRET', '')
    SHEETS_SCOPES: List[str] = ['https://www.googleapis.com/auth/spreadsheets']
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL: str = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    # Email Configuration
    SMTP_SERVER: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_ADDRESS: str = os.getenv('EMAIL_ADDRESS', '')
    EMAIL_PASSWORD: str = os.getenv('EMAIL_PASSWORD', '')
    
    # Google Sheets Configuration
    SPREADSHEET_ID: str = os.getenv('SPREADSHEET_ID', '')
    WORKSHEET_NAME: str = os.getenv('WORKSHEET_NAME', 'Job Applications')
    
    # Notification Configuration
    NOTIFICATION_EMAILS: List[str] = [
        email.strip() 
        for email in os.getenv('NOTIFICATION_EMAILS', '').split(',') 
        if email.strip()
    ]
    
    # Application Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    MAX_EMAILS_PER_RUN: int = int(os.getenv('MAX_EMAILS_PER_RUN', '15'))  # Legacy setting, now unused
    FIRST_RUN_EMAIL_COUNT: int = int(os.getenv('FIRST_RUN_EMAIL_COUNT', '50'))
    ONGOING_EMAIL_COUNT: int = int(os.getenv('ONGOING_EMAIL_COUNT', '10'))
    DAYS_TO_LOOK_BACK: int = int(os.getenv('DAYS_TO_LOOK_BACK', '1'))
    POLLING_INTERVAL_MINUTES: int = int(os.getenv('POLLING_INTERVAL_MINUTES', '15'))
    
    # File paths
    GMAIL_TOKEN_FILE: str = 'tokens/gmail_token.json'
    GMAIL_CREDENTIALS_FILE: str = 'gmail_credentials.json'
    SHEETS_CREDENTIALS_FILE: str = 'sheets_credentials.json'
    PROCESSED_EMAILS_FILE: str = 'data/processed_emails.json'
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate required settings and return list of missing configurations."""
        missing = []
        
        # Required settings for core functionality
        if not cls.GMAIL_CLIENT_ID:
            missing.append('GMAIL_CLIENT_ID')
        if not cls.GMAIL_CLIENT_SECRET:
            missing.append('GMAIL_CLIENT_SECRET')
        if not cls.SPREADSHEET_ID:
            missing.append('SPREADSHEET_ID')
        
        # Email settings are optional if notifications are disabled
        # Only validate if at least one email setting is provided (indicating user wants notifications)
        if cls.EMAIL_ADDRESS or cls.EMAIL_PASSWORD or cls.NOTIFICATION_EMAILS:
            if not cls.EMAIL_ADDRESS:
                missing.append('EMAIL_ADDRESS')
            if not cls.EMAIL_PASSWORD:
                missing.append('EMAIL_PASSWORD')
            
        return missing

# Global settings instance
settings = Settings()
