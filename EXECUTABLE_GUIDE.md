# Job AI Agent - Executable Distribution

## Quick Start

The Job AI Agent can now be run as a standalone executable with custom configuration files.

## Usage Options

### 1. Python Script (Cross-platform)
```bash
# Use default .env file
python job_agent.py

# Use custom config file
python job_agent.py /path/to/my-config.env
python job_agent.py --config ./configs/production.env

# Test configuration only
python job_agent.py --test
python job_agent.py --config /path/to/config.env --test
```

### 2. Shell Script (Linux/macOS)
```bash
# Make executable (first time only)
chmod +x job-agent.sh

# Use default .env file
./job-agent.sh

# Use custom config file
./job-agent.sh /path/to/my-config.env

# Test configuration
./job-agent.sh --test

# Install dependencies
./job-agent.sh --install
```

### 3. Batch Script (Windows)
```cmd
# Use default .env file
job-agent.bat

# Use custom config file
job-agent.bat C:\path\to\my-config.env

# Test configuration
job-agent.bat --test

# Install dependencies
job-agent.bat --install
```

## Configuration File

Create a `.env` file with your settings:

```bash
# Gmail API credentials
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret

# Gemini API key
GEMINI_API_KEY=your_gemini_api_key

# Google Sheets configuration
SPREADSHEET_ID=your_google_sheets_id
WORKSHEET_NAME=job-search

# Email notifications (optional - leave empty to disable)
EMAIL_ADDRESS=
EMAIL_PASSWORD=
NOTIFICATION_EMAILS=

# Monitoring settings
FIRST_RUN_EMAIL_COUNT=50
ONGOING_EMAIL_COUNT=10
POLLING_INTERVAL_MINUTES=15
DAYS_TO_LOOK_BACK=1
```

## Distribution Examples

### For End Users

1. **Simple Setup:**
```bash
# Clone or download the job agent
git clone https://github.com/user/job-ai-agent.git
cd job-ai-agent

# Create your config file
cp .env.example my-job-config.env
# Edit my-job-config.env with your credentials

# Run with your config
./job-agent.sh my-job-config.env
```

2. **Multiple Configurations:**
```bash
# Different configs for different purposes
./job-agent.sh ./configs/personal.env     # Personal job search
./job-agent.sh ./configs/freelance.env    # Freelance opportunities
./job-agent.sh ./configs/remote.env       # Remote-only positions
```

### For System Administrators

1. **System-wide Installation:**
```bash
# Install to /opt
sudo cp -r job-ai-agent /opt/
sudo chmod +x /opt/job-ai-agent/job-agent.sh

# Create system service with custom config
sudo systemctl start job-agent@/path/to/config.env
```

2. **Docker Deployment:**
```bash
# Build container with config mounted
docker run -d \
  --name job-agent \
  -v /path/to/config.env:/app/.env \
  job-ai-agent:latest
```

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `[config_file]` | Path to .env configuration file | `./job-agent.sh /home/user/my.env` |
| `--config, -c` | Alternative way to specify config | `python job_agent.py -c my.env` |
| `--test, -t` | Test configuration and exit | `./job-agent.sh --test` |
| `--help, -h` | Show help message | `python job_agent.py --help` |
| `--install, -i` | Install dependencies | `./job-agent.sh --install` |
| `--version, -v` | Show version information | `python job_agent.py --version` |

## Features

### ✅ **What the executable provides:**
- **Custom configuration files** - Use any .env file path
- **Configuration validation** - Checks required settings before running
- **Dependency management** - Automatic virtual environment detection
- **Cross-platform support** - Works on Windows, macOS, Linux
- **Test mode** - Validate settings without starting the scheduler
- **Detailed logging** - Shows configuration summary and status
- **Error handling** - Clear error messages for common issues

### 🔧 **Configuration Summary Display:**
When starting, you'll see:
```
🤖 Job AI Agent - Automated Job Application Tracking
==================================================
✅ Loaded configuration from: /path/to/my.env
✅ Configuration validation passed

📋 Configuration Summary:
   • Gmail Client ID: 960862407935-g34c5e...
   • Gemini API Key: AIzaSyCRHZWZ1dN9Ia...
   • Spreadsheet ID: 1ucpKB5ujM5TuzzakigW...
   • Worksheet Name: job-search
   • First Run Count: 50
   • Ongoing Count: 10
   • Check Interval: 15 minutes
   • Email Notifications: Disabled

==================================================
🚀 Starting Job AI Agent Scheduler...
Press Ctrl+C to stop
```

## Deployment Scenarios

### 1. **Personal Use**
```bash
# Keep config private
./job-agent.sh ~/.config/job-agent.env
```

### 2. **Team/Organization**
```bash
# Shared config with different credentials
./job-agent.sh /shared/configs/team-job-search.env
```

### 3. **Multiple Instances**
```bash
# Run multiple instances with different configs
./job-agent.sh ./config1.env &
./job-agent.sh ./config2.env &
./job-agent.sh ./config3.env &
```

### 4. **Scheduled Execution**
```bash
# Add to crontab for automatic startup
echo "@reboot /path/to/job-agent.sh /path/to/config.env" | crontab -
```

## Troubleshooting

### Common Issues:

1. **"Configuration file not found"**
   - Check the file path is correct
   - Use absolute paths for reliability

2. **"Missing required environment variables"**
   - Ensure all required fields are in your .env file
   - Check for typos in variable names

3. **"Python not found"**
   - Install Python 3.8+ from python.org
   - Make sure Python is in your system PATH

4. **"Permission denied"**
   - Make script executable: `chmod +x job-agent.sh`

## Security Notes

- Keep your `.env` files secure and private
- Never commit `.env` files to version control
- Use different API keys for different environments
- Regularly rotate your API credentials

This executable setup makes the Job AI Agent easy to deploy and manage across different environments and configurations!
