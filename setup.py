"""
Setup script for Job AI Agent.
"""

import os
import json
import logging
from typing import Dict, Any

from config.settings import settings
from utils.helpers import FileUtils, ValidationUtils

logger = logging.getLogger(__name__)

def setup_directories():
    """Create necessary directories."""
    directories = [
        'logs',
        'tokens',
        'credentials'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def validate_environment():
    """Validate environment configuration."""
    print("\n=== Validating Environment ===")
    
    missing = settings.validate()
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease update your .env file with the missing variables.")
        return False
    
    print("✓ All required environment variables are set")
    return True

def validate_credentials():
    """Validate credential files."""
    print("\n=== Validating Credentials ===")
    
    # Check Gmail credentials
    if os.path.exists(settings.GMAIL_CREDENTIALS_FILE):
        print(f"✓ Gmail credentials file found: {settings.GMAIL_CREDENTIALS_FILE}")
    else:
        print(f"❌ Gmail credentials file missing: {settings.GMAIL_CREDENTIALS_FILE}")
        print("   Please download your Gmail API credentials from Google Cloud Console")
    
    # Check Sheets credentials
    if os.path.exists(settings.SHEETS_CREDENTIALS_FILE):
        print(f"✓ Sheets credentials file found: {settings.SHEETS_CREDENTIALS_FILE}")
    else:
        print(f"❌ Sheets credentials file missing: {settings.SHEETS_CREDENTIALS_FILE}")
        print("   Please download your Google Sheets service account credentials")
    
    # Validate email addresses
    if ValidationUtils.is_valid_email(settings.EMAIL_ADDRESS):
        print(f"✓ Email address is valid: {settings.EMAIL_ADDRESS}")
    else:
        print(f"❌ Invalid email address: {settings.EMAIL_ADDRESS}")
    
    # Validate spreadsheet ID
    if ValidationUtils.validate_spreadsheet_id(settings.SPREADSHEET_ID):
        print(f"✓ Spreadsheet ID is valid: {settings.SPREADSHEET_ID}")
    else:
        print(f"❌ Invalid spreadsheet ID: {settings.SPREADSHEET_ID}")

def create_sample_env():
    """Create a sample .env file if it doesn't exist."""
    if not os.path.exists('.env'):
        print("\n=== Creating Sample .env File ===")
        
        # Try to use credential helper
        try:
            from extract_credentials import extract_gmail_credentials, extract_sheets_service_account
            
            gmail_id, gmail_secret = extract_gmail_credentials()
            sheets_email = extract_sheets_service_account()
            
            if gmail_id and gmail_secret:
                print("✓ Found Gmail credentials, creating customized .env")
                # Create customized .env with actual values
                env_content = f"""# Gmail API credentials
GMAIL_CLIENT_ID={gmail_id}
GMAIL_CLIENT_SECRET={gmail_secret}

# Google Sheets API credentials (using service account)
SHEETS_CLIENT_ID=
SHEETS_CLIENT_SECRET=

# Gemini API key (for email parsing)
GEMINI_API_KEY=your_gemini_api_key

# Email configuration for notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Google Sheets configuration
SPREADSHEET_ID=your_google_sheets_id
WORKSHEET_NAME=Job Applications

# Email addresses to notify for interviews/assessments
NOTIFICATION_EMAILS=your_email@gmail.com
"""
                with open('.env', 'w') as f:
                    f.write(env_content)
                
                if sheets_email:
                    print(f"📌 Remember to share your Google Sheet with: {sheets_email}")
            else:
                # Fall back to template
                raise Exception("Could not extract credentials")
                
        except Exception:
            # Copy from .env.example as fallback
            if os.path.exists('.env.example'):
                with open('.env.example', 'r') as src:
                    with open('.env', 'w') as dst:
                        dst.write(src.read())
                print("✓ Created .env file from .env.example")
            else:
                print("❌ .env.example file not found")
        
        print("Please edit .env file with your actual credentials")
    else:
        print("✓ .env file already exists")

def setup_google_sheets():
    """Provide instructions for Google Sheets setup."""
    print("\n=== Google Sheets Setup Instructions ===")
    print("1. Create a new Google Sheet")
    print("2. Copy the spreadsheet ID from the URL")
    print("3. Update SPREADSHEET_ID in your .env file")
    print("4. Share the sheet with your service account email")
    print("5. The agent will automatically create headers on first run")

def test_configuration():
    """Test the configuration."""
    print("\n=== Testing Configuration ===")
    
    try:
        from main import JobAIAgent
        agent = JobAIAgent()
        
        if agent.test_configuration():
            print("🎉 Configuration test passed!")
            return True
        else:
            print("❌ Configuration test failed")
            return False
    
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

def main():
    """Main setup function."""
    print("🤖 Job AI Agent Setup")
    print("=" * 50)
    
    # Setup logging
    FileUtils.setup_logging()
    
    # Create directories
    print("\n=== Setting up Directories ===")
    setup_directories()
    
    # Create sample .env
    create_sample_env()
    
    # Validate environment
    env_valid = validate_environment()
    
    # Validate credentials
    validate_credentials()
    
    # Provide setup instructions
    setup_google_sheets()
    
    # Test configuration if environment is valid
    if env_valid:
        test_passed = test_configuration()
    else:
        test_passed = False
    
    print("\n" + "=" * 50)
    if test_passed:
        print("✅ Setup completed successfully!")
        print("\nYou can now run the Job AI Agent:")
        print("  python main.py --test")
        print("  python main.py --days 7")
        print("  python scheduler.py")
    else:
        print("⚠️  Setup completed with issues")
        print("Please resolve the configuration issues before running the agent")
    
    print("\nFor help, check the README.md file")

if __name__ == "__main__":
    main()
