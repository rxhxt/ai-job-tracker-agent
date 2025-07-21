#!/usr/bin/env python3
"""
Helper script to reset authentication tokens and re-authenticate.
"""

import os
import shutil

def clear_tokens():
    """Clear existing authentication tokens."""
    tokens_dir = "tokens"
    
    if os.path.exists(tokens_dir):
        try:
            shutil.rmtree(tokens_dir)
            print(f"✅ Cleared tokens directory: {tokens_dir}")
        except Exception as e:
            print(f"❌ Error clearing tokens: {e}")
    else:
        print(f"ℹ️  Tokens directory doesn't exist: {tokens_dir}")

def check_credentials():
    """Check if credential files exist."""
    files_to_check = [
        'gmail_credentials.json',
        'sheets_credentials.json',
        '.env'
    ]
    
    print("\n📋 Checking credential files:")
    all_present = True
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing!")
            all_present = False
    
    return all_present

def main():
    """Main function."""
    print("🔄 Authentication Reset Helper")
    print("=" * 40)
    
    # Check credentials first
    if not check_credentials():
        print("\n❌ Missing credential files. Please set up credentials first.")
        print("📖 See CREDENTIALS_SETUP.md for help")
        return
    
    # Clear tokens
    print("\n🧹 Clearing authentication tokens...")
    clear_tokens()
    
    print("\n✅ Authentication reset complete!")
    print("\n🚀 Next steps:")
    print("1. If you're having OAuth issues, add yourself as a test user:")
    print("   📖 See OAUTH_FIX.md for detailed instructions")
    print("2. Run the test command:")
    print("   python main.py --test")
    print("3. Follow the authentication prompts in your browser")

if __name__ == "__main__":
    main()
