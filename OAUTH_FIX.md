# Google OAuth Verification Issue - Solutions

## Problem
You're seeing: "Access blocked: Job AI Agent has not completed the Google verification process"

This happens because Google requires apps that access user data to go through a verification process for public use.

## Solutions

### Solution 1: Add Yourself as a Test User (Recommended)

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Select your project

2. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" → "OAuth consent screen"
   - If you haven't configured it yet:
     - Choose "External" user type
     - Fill in the required fields:
       - App name: "Job AI Agent"
       - User support email: Your email
       - Developer contact information: Your email

3. **Add Test Users**
   - In the OAuth consent screen configuration
   - Scroll down to "Test users" section
   - Click "Add users"
   - Add your Gmail address (the one you want to access)
   - Click "Save"

4. **Save and Continue**
   - Complete all the OAuth consent screen steps
   - You don't need to submit for verification for personal use

### Solution 2: Use Internal User Type (If Possible)

If you have a Google Workspace account:
1. Go to "OAuth consent screen"
2. Choose "Internal" user type instead of "External"
3. This bypasses the verification requirement

### Solution 3: Modify Scopes (Alternative)

If the above doesn't work, try using more restrictive scopes:

1. **Update the Gmail scopes in your code**
   ```python
   # In config/settings.py, change from:
   GMAIL_SCOPES: List[str] = ['https://www.googleapis.com/auth/gmail.readonly']
   
   # To more specific scope:
   GMAIL_SCOPES: List[str] = ['https://www.googleapis.com/auth/gmail.metadata']
   ```

2. **Or use the most basic scope:**
   ```python
   GMAIL_SCOPES: List[str] = ['https://www.googleapis.com/auth/gmail.labels']
   ```

### Solution 4: Re-create OAuth Credentials

Sometimes recreating the credentials helps:

1. **Delete existing credentials**
   - Go to "APIs & Services" → "Credentials"
   - Delete the existing OAuth 2.0 Client ID

2. **Create new credentials**
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop application"
   - Name: "Job AI Agent Personal"
   - Download the new JSON file

3. **Replace the credential file**
   - Replace your `gmail_credentials.json` with the new file
   - Delete the `tokens/` folder if it exists (to force re-authentication)

## Step-by-Step Fix (Most Common Solution)

1. **Add yourself as a test user:**
   ```
   Google Cloud Console → APIs & Services → OAuth consent screen → Test users → Add users
   ```

2. **Clear existing tokens:**
   ```bash
   rm -rf tokens/
   ```

3. **Try authentication again:**
   ```bash
   python main.py --test
   ```

## Verification Status

Your app is currently in "Testing" mode, which means:
- ✅ You can add up to 100 test users
- ✅ Perfect for personal use
- ✅ No verification needed
- ❌ Only test users can access it

For personal use, you don't need to submit for verification!

## Alternative: Use Service Account Only

If OAuth2 continues to be problematic, you can modify the code to use only service accounts:

1. **For Gmail access**, you'd need to:
   - Set up domain-wide delegation (more complex)
   - Or use the Gmail API with service account (limited functionality)

2. **Keep using service account for Sheets** (this already works)

## Next Steps

1. Try Solution 1 (add test users) first
2. Clear tokens and re-authenticate
3. If still having issues, try recreating credentials
4. Contact me if you need help with any of these steps

The easiest fix is usually just adding yourself as a test user in the OAuth consent screen!
