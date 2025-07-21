@echo off
REM Job AI Agent - Windows Batch Launcher
REM Usage: job-agent.bat [path\to\.env]

setlocal enabledelayedexpansion

REM Default values
set "DEFAULT_ENV_FILE=.env"
set "SCRIPT_DIR=%~dp0"
set "ENV_FILE=%DEFAULT_ENV_FILE%"
set "TEST_MODE=false"

REM Parse command line arguments
:parse_args
if "%~1"=="" goto end_parse
if "%~1"=="--help" goto show_help
if "%~1"=="-h" goto show_help
if "%~1"=="--test" (
    set "TEST_MODE=true"
    shift
    goto parse_args
)
if "%~1"=="-t" (
    set "TEST_MODE=true"
    shift
    goto parse_args
)
if "%~1"=="--install" goto install_deps
if "%~1"=="-i" goto install_deps
set "ENV_FILE=%~1"
shift
goto parse_args
:end_parse

REM Convert to absolute path if needed
if not "%ENV_FILE:~1,1%"==":" (
    set "ENV_FILE=%CD%\%ENV_FILE%"
)

echo 🤖 Job AI Agent - Automated Job Application Tracking
echo ==================================================

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist "%ENV_FILE%" (
    echo ❌ Error: Configuration file not found: %ENV_FILE%
    echo.
    echo Please create a .env file with the following variables:
    echo   GMAIL_CLIENT_ID=your_gmail_client_id
    echo   GMAIL_CLIENT_SECRET=your_gmail_client_secret
    echo   GEMINI_API_KEY=your_gemini_api_key
    echo   SPREADSHEET_ID=your_google_sheets_id
    echo.
    echo See .env.example for a complete template.
    pause
    exit /b 1
)

echo ✅ Configuration file found: %ENV_FILE%

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo ℹ️ Found virtual environment, activating...
    call .venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else if exist "venv\Scripts\activate.bat" (
    echo ℹ️ Found virtual environment, activating...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️ No virtual environment found, using system Python
)

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo ℹ️ Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error installing dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
)

REM Test mode
if "%TEST_MODE%"=="true" (
    echo ℹ️ Running configuration test...
    python job_agent.py --config "%ENV_FILE%" --test
    if errorlevel 1 (
        echo ❌ Configuration test failed
        pause
        exit /b 1
    )
    echo ✅ Test completed successfully!
    pause
    exit /b 0
)

REM Run the job agent
echo ℹ️ Starting Job AI Agent...
echo ℹ️ Press Ctrl+C to stop
echo.

python job_agent.py --config "%ENV_FILE%"
if errorlevel 1 (
    echo ❌ Job AI Agent exited with error
    pause
    exit /b 1
)

echo ✅ Job AI Agent stopped
pause
exit /b 0

:show_help
echo Job AI Agent - Automated Job Application Tracking
echo.
echo Usage:
echo   %~nx0 [path\to\.env]
echo   %~nx0 --help
echo   %~nx0 --test
echo.
echo Examples:
echo   %~nx0                        # Use .env in current directory
echo   %~nx0 C:\path\to\my.env     # Use specific .env file
echo   %~nx0 --test                # Test configuration only
echo.
echo Options:
echo   --help, -h    Show this help message
echo   --test, -t    Test configuration and exit
echo   --install, -i Install dependencies
pause
exit /b 0

:install_deps
echo ℹ️ Installing Python dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo ⚠️ requirements.txt not found, installing common dependencies...
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client google-generativeai schedule python-dotenv
)
echo ✅ Dependencies installed successfully
pause
exit /b 0
