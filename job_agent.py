#!/usr/bin/env python3
"""
Job AI Agent - Executable Entry Point

Usage:
    python job_agent.py [path/to/.env]
    python job_agent.py --config /path/to/config.env
    python job_agent.py --help

Examples:
    python job_agent.py
    python job_agent.py /home/user/my_job_config.env
    python job_agent.py --config ./configs/production.env
"""

import sys
import os
import argparse
from pathlib import Path

def load_env_file(env_path: str) -> bool:
    """Load environment variables from the specified .env file."""
    if not os.path.exists(env_path):
        print(f"❌ Error: .env file not found: {env_path}")
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)
        print(f"✅ Loaded configuration from: {env_path}")
        return True
    except ImportError:
        print("❌ Error: python-dotenv not installed. Install with: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False

def validate_config() -> bool:
    """Validate that required configuration is present."""
    required_vars = [
        'GMAIL_CLIENT_ID',
        'GMAIL_CLIENT_SECRET', 
        'GEMINI_API_KEY',
        'SPREADSHEET_ID'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("Please check your .env file contains these variables.")
        return False
    
    print("✅ Configuration validation passed")
    return True

def run_scheduler():
    """Start the job scheduler."""
    try:
        from scheduler import main as run_scheduler_main
        print("🚀 Starting Job AI Agent Scheduler...")
        print("Press Ctrl+C to stop")
        run_scheduler_main()
    except ImportError as e:
        print(f"❌ Error importing scheduler: {e}")
        print("Make sure you're running from the correct directory")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ Scheduler stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error running scheduler: {e}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Job AI Agent - Automated job application tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Use .env in current directory
  %(prog)s /path/to/my.env              # Use specific .env file
  %(prog)s --config ./configs/prod.env  # Use config file with --config flag
  %(prog)s --test                       # Test configuration only
        """
    )
    
    parser.add_argument(
        'env_file', 
        nargs='?', 
        default='.env',
        help='Path to .env configuration file (default: .env)'
    )
    
    parser.add_argument(
        '--config', '-c',
        dest='config_file',
        help='Alternative way to specify config file path'
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Test configuration and exit (don\'t start scheduler)'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Job AI Agent v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Determine which config file to use
    env_file = args.config_file if args.config_file else args.env_file
    
    # Convert to absolute path
    env_path = os.path.abspath(env_file)
    
    print("🤖 Job AI Agent - Automated Job Application Tracking")
    print("=" * 50)
    
    # Load environment file
    if not load_env_file(env_path):
        sys.exit(1)
    
    # Validate configuration
    if not validate_config():
        sys.exit(1)
    
    # If test mode, exit after validation
    if args.test:
        print("✅ Configuration test completed successfully!")
        sys.exit(0)
    
    # Show configuration summary
    print("\n📋 Configuration Summary:")
    print(f"   • Gmail Client ID: {os.getenv('GMAIL_CLIENT_ID', 'Not set')[:20]}...")
    print(f"   • Gemini API Key: {os.getenv('GEMINI_API_KEY', 'Not set')[:20]}...")
    print(f"   • Spreadsheet ID: {os.getenv('SPREADSHEET_ID', 'Not set')[:20]}...")
    print(f"   • Worksheet Name: {os.getenv('WORKSHEET_NAME', 'job-search')}")
    print(f"   • First Run Count: {os.getenv('FIRST_RUN_EMAIL_COUNT', '50')}")
    print(f"   • Ongoing Count: {os.getenv('ONGOING_EMAIL_COUNT', '10')}")
    print(f"   • Check Interval: {os.getenv('POLLING_INTERVAL_MINUTES', '15')} minutes")
    
    email_notifications = os.getenv('EMAIL_ADDRESS') and os.getenv('EMAIL_PASSWORD')
    print(f"   • Email Notifications: {'Enabled' if email_notifications else 'Disabled'}")
    
    print("\n" + "=" * 50)
    
    # Start the scheduler
    success = run_scheduler()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
