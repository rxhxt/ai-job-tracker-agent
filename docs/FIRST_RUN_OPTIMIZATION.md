# First Run vs Ongoing Monitoring Optimization

## Overview

The Job AI Agent now implements smart email fetching that adapts based on whether it's the first time running or part of ongoing monitoring.

## How It Works

### First Run Detection
- **Trigger**: When `data/processed_emails.json` doesn't exist or is empty
- **Behavior**: Fetches **50 emails** to catch up on recent activity
- **Purpose**: Ensures no recent job emails are missed when starting the agent

### Ongoing Monitoring  
- **Trigger**: After the first run when emails have been processed
- **Behavior**: Fetches only **10 emails** every 15 minutes
- **Purpose**: Efficient monitoring with minimal API usage

## Benefits

### 1. **Comprehensive Initial Scan**
- 50 emails typically covers 1-2 days of email activity
- Catches recent job applications, responses, or interviews
- No missed opportunities when first setting up the agent

### 2. **Efficient Ongoing Operations**
- 10 emails per 15-minute check is more than sufficient
- Most people don't receive 10+ job emails every 15 minutes
- Reduces Gmail API and Gemini API calls significantly

### 3. **Smart Resource Management**
- Fewer API calls = lower costs and better rate limit compliance
- Faster processing during regular monitoring
- Duplicate prevention ensures no email is processed twice

## Configuration

You can customize these values in your `.env` file:

```bash
# First run: check more emails to catch up
FIRST_RUN_EMAIL_COUNT=50

# Ongoing monitoring: check fewer emails for efficiency  
ONGOING_EMAIL_COUNT=10
```

## Implementation Details

### Email Tracker Integration
```python
# Check if this is first run
is_first_run = self.email_tracker.is_first_run()

# Use appropriate email count
max_emails = FIRST_RUN_EMAIL_COUNT if is_first_run else ONGOING_EMAIL_COUNT
```

### Gmail Service Logic
```python
def get_recent_emails(self, is_first_run: bool = False):
    max_results = 50 if is_first_run else 10
    # Fetch emails accordingly
```

## Testing

Run the test script to see this behavior:

```bash
python test_first_run.py
```

This will show:
- Current first run status
- Which email count would be used
- Statistics about previously processed emails

## Logging Output

You'll see clear indicators in the logs:

```
INFO - First run - checking max 50 emails
INFO - Found 45 emails to check
INFO - Processing 12 new emails (skipped 33 duplicates)
```

vs.

```  
INFO - Ongoing monitoring - checking max 10 emails
INFO - Found 8 emails to check  
INFO - Processing 2 new emails (skipped 6 duplicates)
```

## Edge Cases Handled

1. **Empty Email Tracker**: Treated as first run
2. **Corrupted Tracker File**: Falls back to first run behavior  
3. **Manual Email Count Override**: Can still specify `max_results` parameter
4. **API Failures**: Graceful degradation with appropriate logging

This optimization ensures the agent is both thorough during initial setup and efficient during continuous operation.
