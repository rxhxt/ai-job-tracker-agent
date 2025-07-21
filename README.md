# Job AI Agent

An intelligent AI agent that automatically tracks job applications by reading Gmail, parsing emails, and maintaining a Google Sheets database.

## Features

- 📧 **Gmail Integration**: Automatically reads and analyzes emails
- 🔍 **AI-Powered Email Parsing**: Identifies job applications, rejections, and interview notifications
- 📊 **Google Sheets Integration**: Maintains a comprehensive job tracking database
- 📨 **Smart Notifications**: Sends email alerts for interviews and assessments
- 🤖 **Automated Processing**: Runs continuously to keep your job tracking up-to-date

## Setup

### 1. Prerequisites

- Python 3.8 or higher
- Google Account with Gmail and Google Sheets access
- Google Gemini API key (optional, for advanced email parsing)

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd job-ai-agent

# Install dependencies
pip install -r requirements.txt
```

### 3. Google API Setup

**📋 For detailed step-by-step instructions, see [CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md)**

#### Quick Overview:
- **Gmail API**: Create OAuth2 credentials in Google Cloud Console
- **Google Sheets API**: Create service account credentials
- **Gemini API**: Get API key from Google AI Studio

#### Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials JSON file as `gmail_credentials.json`

#### Google Sheets API
1. In the same Google Cloud project
2. Enable Google Sheets API
3. Create service account credentials
4. Download the credentials JSON file as `sheets_credentials.json`
5. Share your Google Sheet with the service account email

#### Gemini API (Optional)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key for Gemini
3. Add the API key to your .env file as GEMINI_API_KEY

### 4. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 5. Google Sheets Setup

Create a Google Sheet with the following columns:
- Date Applied
- Company
- Position
- Status
- Email Date
- Notes

## Usage

### First Run Setup

```bash
# Run setup script first
python setup.py

# Test configuration
python main.py --test
```

**⚠️ Google OAuth Issue?** If you see "Access blocked" error, see [OAUTH_FIX.md](OAUTH_FIX.md)

### Run the Agent

```bash
python main.py
```

### Run Continuously (Recommended)

```bash
python scheduler.py
```

This will:
- Check for new emails every 15 minutes
- Process only the latest 15 emails to avoid API limits
- Skip already processed emails (no duplicates)
- Only call Gemini API for genuinely new emails
- Run continuously in the background

### Manual Processing

```bash
# Process emails from last 1 day (default for continuous monitoring)
python main.py --days 1

# Process specific email
python main.py --email-id <email_id>

# Test configuration
python main.py --test
```

## Configuration

You can customize the monitoring behavior in your `.env` file:

```bash
# Check latest 15 emails every run (prevents API overuse)
MAX_EMAILS_PER_RUN=15

# Look back 1 day for recent emails
DAYS_TO_LOOK_BACK=1

# Check for new emails every 15 minutes
POLLING_INTERVAL_MINUTES=15
```

## Project Structure

```
job-ai-agent/
├── main.py                 # Main application entry point
├── scheduler.py            # Continuous monitoring scheduler
├── config/
│   └── settings.py         # Configuration management
├── services/
│   ├── gmail_service.py    # Gmail API integration
│   ├── sheets_service.py   # Google Sheets integration
│   ├── email_parser.py     # AI email parsing logic
│   └── notification_service.py # Email notifications
├── models/
│   └── job_application.py  # Data models
├── utils/
│   ├── auth.py            # Authentication utilities
│   └── helpers.py         # Helper functions
└── tests/                 # Unit tests
```

## Email Patterns Detected

The AI agent can identify:

### Job Applications
- Application confirmations
- "Thank you for applying" emails
- Application acknowledgments

### Rejections
- Rejection emails
- "We decided to move forward with other candidates"
- "Unfortunately" patterns

### Interviews & Assessments
- Interview invitations
- Assessment requests
- "Next steps" communications
- Calendar invites

## Troubleshooting

### Common Issues

#### "Access blocked: Job AI Agent has not completed the Google verification process"
This is a common OAuth2 issue. **Solution**: Add yourself as a test user in Google Cloud Console.
📖 **Detailed fix**: See [OAUTH_FIX.md](OAUTH_FIX.md)

#### "Authentication failed" or "Invalid credentials"
- Check that credential files are in the correct location
- Verify environment variables in `.env` file
- Delete `tokens/` folder and re-authenticate

#### "Permission denied" for Google Sheets
- Ensure you've shared your Google Sheet with the service account email
- Check that the spreadsheet ID is correct in `.env`

#### No emails being processed
- Verify Gmail API scopes include `gmail.readonly`
- Check that you have job-related emails in the specified date range
- Look at logs in `logs/` directory for detailed error messages

### Getting Help
- Check the `logs/` directory for detailed error messages
- Run `python main.py --test` to diagnose configuration issues
- See `CREDENTIALS_SETUP.md` for credential setup help
- See `OAUTH_FIX.md` for Google OAuth issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

If you encounter any issues, please check the logs in `logs/` directory or create an issue in the repository.
