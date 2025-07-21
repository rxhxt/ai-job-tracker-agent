#!/bin/bash

# Job AI Agent - Shell Script Launcher
# Usage: ./job-agent.sh [path/to/.env]

set -e  # Exit on any error

# Default values
DEFAULT_ENV_FILE=".env"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Job AI Agent - Automated Job Application Tracking"
    echo ""
    echo "Usage:"
    echo "  $0 [path/to/.env]"
    echo "  $0 --help"
    echo "  $0 --test"
    echo ""
    echo "Examples:"
    echo "  $0                           # Use .env in current directory"
    echo "  $0 /path/to/my.env          # Use specific .env file"
    echo "  $0 --test                   # Test configuration only"
    echo ""
    echo "Options:"
    echo "  --help, -h    Show this help message"
    echo "  --test, -t    Test configuration and exit"
    echo "  --install, -i Install dependencies"
}

# Function to install dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip3 first."
        exit 1
    fi
    
    # Install requirements
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        pip3 install -r "$SCRIPT_DIR/requirements.txt"
        print_status "Dependencies installed successfully"
    else
        print_warning "requirements.txt not found, installing common dependencies..."
        pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client google-generativeai schedule python-dotenv
        print_status "Common dependencies installed"
    fi
}

# Function to check if virtual environment should be used
setup_python_env() {
    # Check if we're already in a virtual environment
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_status "Using active virtual environment: $VIRTUAL_ENV"
        return 0
    fi
    
    # Check if there's a virtual environment in the project
    if [ -d "$SCRIPT_DIR/.venv" ]; then
        print_info "Found virtual environment, activating..."
        source "$SCRIPT_DIR/.venv/bin/activate"
        print_status "Virtual environment activated"
        return 0
    fi
    
    # Check if there's a venv directory
    if [ -d "$SCRIPT_DIR/venv" ]; then
        print_info "Found virtual environment, activating..."
        source "$SCRIPT_DIR/venv/bin/activate"
        print_status "Virtual environment activated"
        return 0
    fi
    
    print_warning "No virtual environment found, using system Python"
}

# Function to validate .env file
validate_env_file() {
    local env_file="$1"
    
    if [ ! -f "$env_file" ]; then
        print_error "Configuration file not found: $env_file"
        echo ""
        echo "Please create a .env file with the following variables:"
        echo "  GMAIL_CLIENT_ID=your_gmail_client_id"
        echo "  GMAIL_CLIENT_SECRET=your_gmail_client_secret"
        echo "  GEMINI_API_KEY=your_gemini_api_key"
        echo "  SPREADSHEET_ID=your_google_sheets_id"
        echo ""
        echo "See .env.example for a complete template."
        exit 1
    fi
    
    print_status "Configuration file found: $env_file"
    
    # Check for required variables
    local required_vars=("GMAIL_CLIENT_ID" "GMAIL_CLIENT_SECRET" "GEMINI_API_KEY" "SPREADSHEET_ID")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$env_file" || [ -z "$(grep "^${var}=" "$env_file" | cut -d'=' -f2-)" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Missing required environment variables in $env_file:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        echo ""
        echo "Please add these variables to your .env file."
        exit 1
    fi
    
    print_status "Configuration validation passed"
}

# Main function
main() {
    local env_file="$DEFAULT_ENV_FILE"
    local test_mode=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_usage
                exit 0
                ;;
            --test|-t)
                test_mode=true
                shift
                ;;
            --install|-i)
                install_dependencies
                exit 0
                ;;
            --*)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                env_file="$1"
                shift
                ;;
        esac
    done
    
    # Convert to absolute path
    if [[ "$env_file" != /* ]]; then
        env_file="$(pwd)/$env_file"
    fi
    
    echo "🤖 Job AI Agent - Automated Job Application Tracking"
    echo "=================================================="
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Setup Python environment
    setup_python_env
    
    # Validate .env file
    validate_env_file "$env_file"
    
    # Test mode - just validate and exit
    if [ "$test_mode" = true ]; then
        print_info "Running configuration test..."
        python3 job_agent.py --config "$env_file" --test
        print_status "Test completed successfully!"
        exit 0
    fi
    
    # Run the job agent
    print_info "Starting Job AI Agent..."
    print_info "Press Ctrl+C to stop"
    echo ""
    
    # Export the config file path and run
    export JOB_AGENT_CONFIG="$env_file"
    python3 job_agent.py --config "$env_file"
}

# Run main function with all arguments
main "$@"
