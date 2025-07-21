# Credentials Setup Guide for Job AI Agent

This guide will walk you through obtaining all necessary credentials for the Job AI Agent.

## 1. Gmail API Credentials

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "job-ai-agent")
4. Click "Create"

### Step 2: Enable Gmail API
1. In your project, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on "Gmail API" and click "Enable"

### Step 3: Create OAuth2 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in app name: "Job AI Agent"
   - Add your email as developer contact
   - Add scopes: `https://www.googleapis.com/auth/gmail.readonly`
4. For OAuth client ID:
   - Application type: "Desktop application"
   - Name: "Job AI Agent Gmail"
5. Download the JSON file and save it as `gmail_credentials.json` in your project root

## 2. Google Sheets API Credentials

### Step 1: Enable Google Sheets API
1. In the same Google Cloud project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on "Google Sheets API" and click "Enable"

### Step 2: Create Service Account
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service account"
3. Name: "job-ai-agent-sheets"
4. Description: "Service account for Job AI Agent Google Sheets access"
5. Click "Create and Continue"
6. Skip role assignment (click "Continue")
7. Click "Done"

### Step 3: Generate Service Account Key
1. In the Credentials page, find your service account
2. Click on the service account email
3. Go to "Keys" tab
4. Click "Add Key" → "Create new key"
5. Choose "JSON" format
6. Download the file and save it as `sheets_credentials.json` in your project root

### Step 4: Share Google Sheet with Service Account
1. Create a new Google Sheet for job tracking
2. Copy the service account email from the JSON file (looks like `job-ai-agent-sheets@your-project.iam.gserviceaccount.com`)
3. Share your Google Sheet with this email address (Editor access)
4. Copy the spreadsheet ID from the URL (the long string between `/d/` and `/edit`)

## 3. Gemini API Key

### Option 1: Using Google AI Studio (Recommended)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Choose "Create API key in new project" or use existing project
5. Copy the generated API key

### Option 2: Using Google Cloud Console
1. In your Google Cloud project, go to "APIs & Services" → "Library"
2. Search for "Generative Language API"
3. Enable the API
4. Go to "APIs & Services" → "Credentials"
5. Click "Create Credentials" → "API key"
6. Copy the API key

## 4. Email Configuration for Notifications

### For Gmail (Recommended)
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification
   - Scroll down to "App passwords"
   - Select app: "Mail"
   - Select device: "Other (custom name)" → "Job AI Agent"
   - Copy the 16-character password

### Email Settings
- SMTP_SERVER: `smtp.gmail.com`
- SMTP_PORT: `587`
- EMAIL_ADDRESS: Your Gmail address
- EMAIL_PASSWORD: The app password (not your regular password)

## 5. Google Sheets Setup

### Create Your Job Tracking Sheet
1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it "Job Applications" (or whatever you prefer)
4. The agent will automatically create headers on first run
5. Copy the spreadsheet ID from the URL

Example URL: `https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit`
Spreadsheet ID: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

## 6. Configure Environment Variables

Create a `.env` file in your project root with these values:

```bash
# Gmail API credentials
GMAIL_CLIENT_ID=your_client_id_from_gmail_credentials.json
GMAIL_CLIENT_SECRET=your_client_secret_from_gmail_credentials.json

# Google Sheets API - Use service account (no client ID/secret needed)
SHEETS_CLIENT_ID=
SHEETS_CLIENT_SECRET=

# Gemini API key
GEMINI_API_KEY=your_gemini_api_key

# Email configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Google Sheets configuration
SPREADSHEET_ID=your_spreadsheet_id
WORKSHEET_NAME=Job Applications

# Notification emails (comma-separated)
NOTIFICATION_EMAILS=your_email@gmail.com,another_email@gmail.com
```

## 7. File Structure

After obtaining credentials, your project should have:
```
job-ai-agent/
├── gmail_credentials.json      # OAuth2 credentials for Gmail
├── sheets_credentials.json     # Service account credentials for Sheets
├── .env                       # Environment variables
└── ... (other project files)
```

## 8. Security Notes

- Never commit credential files to version control
- Keep your API keys secure and rotate them periodically
- Use the minimum required scopes for each service
- Consider using Google Cloud Secret Manager for production deployments

## 9. Testing Your Setup

Run the setup script to test your configuration:
```bash
python setup.py
```

Or test the configuration directly:
```bash
python main.py --test
```

## Troubleshooting

### Common Issues:
1. **Gmail API quota exceeded**: Wait or request quota increase
2. **Permission denied for Sheets**: Ensure service account email is shared with the sheet
3. **Authentication errors**: Check that credential files are in the correct location
4. **Gemini API errors**: Verify API key is correct and API is enabled

### Getting Help:
- Check the logs in the `logs/` directory for detailed error messages
- Verify all environment variables are set correctly
- Ensure all APIs are enabled in Google Cloud Console
