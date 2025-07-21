#!/usr/bin/env python3
"""
Helper script to extract credentials information for .env file.
"""

import json
import os
import sys

def extract_gmail_credentials():
    """Extract Gmail OAuth2 credentials from JSON file."""
    if not os.path.exists('gmail_credentials.json'):
        print("❌ gmail_credentials.json not found")
        print("Please download your Gmail OAuth2 credentials from Google Cloud Console")
        return None, None
    
    try:
        with open('gmail_credentials.json', 'r') as f:
            creds = json.load(f)
        
        # OAuth2 credentials are usually under 'installed' or 'web' key
        if 'installed' in creds:
            client_data = creds['installed']
        elif 'web' in creds:
            client_data = creds['web']
        else:
            print("❌ Unexpected Gmail credentials format")
            return None, None
        
        client_id = client_data.get('client_id')
        client_secret = client_data.get('client_secret')
        
        if client_id and client_secret:
            print("✅ Gmail credentials found:")
            print(f"   Client ID: {client_id}")
            print(f"   Client Secret: {client_secret}")
            return client_id, client_secret
        else:
            print("❌ Missing client_id or client_secret in Gmail credentials")
            return None, None
    
    except Exception as e:
        print(f"❌ Error reading Gmail credentials: {e}")
        return None, None

def extract_sheets_service_account():
    """Extract service account email from Sheets credentials."""
    if not os.path.exists('sheets_credentials.json'):
        print("❌ sheets_credentials.json not found")
        print("Please download your Google Sheets service account credentials")
        return None
    
    try:
        with open('sheets_credentials.json', 'r') as f:
            creds = json.load(f)
        
        service_email = creds.get('client_email')
        project_id = creds.get('project_id')
        
        if service_email:
            print("✅ Google Sheets service account found:")
            print(f"   Service Email: {service_email}")
            print(f"   Project ID: {project_id}")
            print(f"   📌 Remember to share your Google Sheet with: {service_email}")
            return service_email
        else:
            print("❌ Missing client_email in Sheets credentials")
            return None
    
    except Exception as e:
        print(f"❌ Error reading Sheets credentials: {e}")
        return None

def generate_env_template():
    """Generate a .env file template with extracted values."""
    print("\n" + "="*60)
    print("🔧 GENERATING .ENV FILE TEMPLATE")
    print("="*60)
    
    # Extract credentials
    gmail_client_id, gmail_client_secret = extract_gmail_credentials()
    sheets_service_email = extract_sheets_service_account()
    
    # Generate .env content
    env_content = f"""# Gmail API credentials
GMAIL_CLIENT_ID={gmail_client_id or 'your_gmail_client_id'}
GMAIL_CLIENT_SECRET={gmail_client_secret or 'your_gmail_client_secret'}

# Google Sheets API credentials (using service account - no client ID/secret needed)
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

    # Write to .env file
    if os.path.exists('.env'):
        response = input("\n⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Aborted. Existing .env file preserved.")
            return
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ Generated .env file successfully!")
        print("\n📝 Next steps:")
        print("1. Edit .env file with your actual values:")
        if not gmail_client_id:
            print("   - Add your Gmail Client ID and Secret")
        if sheets_service_email:
            print(f"   - Share your Google Sheet with: {sheets_service_email}")
        print("   - Add your Gemini API key")
        print("   - Add your email address and app password")
        print("   - Add your Google Sheets spreadsheet ID")
        print("2. Run: python main.py --test")
        
    except Exception as e:
        print(f"❌ Error writing .env file: {e}")

def main():
    """Main function."""
    print("🤖 Job AI Agent - Credentials Helper")
    print("="*50)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--generate-env':
        generate_env_template()
    else:
        print("Checking credential files...\n")
        extract_gmail_credentials()
        print()
        extract_sheets_service_account()
        
        print("\n" + "="*50)
        print("💡 To generate a .env file template, run:")
        print("   python extract_credentials.py --generate-env")
        print("\n📖 For detailed setup instructions, see:")
        print("   CREDENTIALS_SETUP.md")

if __name__ == "__main__":
    main()
