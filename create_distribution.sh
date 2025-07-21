#!/bin/bash

# Job AI Agent - Distribution Package Creator
# Creates a distributable package with executable scripts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"
PACKAGE_NAME="job-ai-agent-executable"
VERSION="1.0.0"

echo "📦 Creating Job AI Agent Distribution Package"
echo "=============================================="

# Clean previous builds
if [ -d "$DIST_DIR" ]; then
    echo "🧹 Cleaning previous build..."
    rm -rf "$DIST_DIR"
fi

mkdir -p "$DIST_DIR/$PACKAGE_NAME"

echo "📋 Copying files..."

# Core Python files
cp -r *.py "$DIST_DIR/$PACKAGE_NAME/"
cp -r services/ "$DIST_DIR/$PACKAGE_NAME/"
cp -r models/ "$DIST_DIR/$PACKAGE_NAME/"
cp -r utils/ "$DIST_DIR/$PACKAGE_NAME/"
cp -r config/ "$DIST_DIR/$PACKAGE_NAME/"

# Executable scripts
cp job-agent.sh "$DIST_DIR/$PACKAGE_NAME/"
cp job-agent.bat "$DIST_DIR/$PACKAGE_NAME/"
chmod +x "$DIST_DIR/$PACKAGE_NAME/job-agent.sh"

# Configuration and documentation
cp .env.example "$DIST_DIR/$PACKAGE_NAME/"
cp requirements.txt "$DIST_DIR/$PACKAGE_NAME/"
cp EXECUTABLE_GUIDE.md "$DIST_DIR/$PACKAGE_NAME/README.md"
cp OAUTH_FIX.md "$DIST_DIR/$PACKAGE_NAME/"

# Create credentials directories
mkdir -p "$DIST_DIR/$PACKAGE_NAME/tokens"
mkdir -p "$DIST_DIR/$PACKAGE_NAME/data"
mkdir -p "$DIST_DIR/$PACKAGE_NAME/logs"

# Create a simple install script
cat > "$DIST_DIR/$PACKAGE_NAME/install.sh" << 'EOF'
#!/bin/bash

echo "🤖 Job AI Agent - Installation Script"
echo "====================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install dependencies
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Make executable
chmod +x job-agent.sh

echo "✅ Installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Copy .env.example to .env"
echo "2. Edit .env with your API credentials"
echo "3. Run: ./job-agent.sh --test"
echo "4. Start monitoring: ./job-agent.sh"

EOF

chmod +x "$DIST_DIR/$PACKAGE_NAME/install.sh"

# Create Windows install script
cat > "$DIST_DIR/$PACKAGE_NAME/install.bat" << 'EOF'
@echo off
echo 🤖 Job AI Agent - Installation Script
echo =====================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Install dependencies
echo 📦 Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Dependencies installed
) else (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

echo ✅ Installation completed!
echo.
echo 📋 Next steps:
echo 1. Copy .env.example to .env
echo 2. Edit .env with your API credentials
echo 3. Run: job-agent.bat --test
echo 4. Start monitoring: job-agent.bat

pause
EOF

# Create package info
cat > "$DIST_DIR/$PACKAGE_NAME/package_info.txt" << EOF
Job AI Agent - Executable Package
=================================

Version: $VERSION
Package Date: $(date)
Platform: Cross-platform (Windows, macOS, Linux)

Contents:
- job_agent.py          Main Python executable
- job-agent.sh          Shell script launcher (Linux/macOS)
- job-agent.bat         Batch script launcher (Windows)
- install.sh/.bat       Installation scripts
- requirements.txt      Python dependencies
- .env.example          Configuration template
- README.md             Comprehensive usage guide
- services/             Core application modules
- models/               Data models
- utils/                Utility functions
- config/               Configuration handling

Quick Start:
1. Run install.sh (Linux/macOS) or install.bat (Windows)
2. Copy .env.example to .env and edit with your credentials
3. Test: ./job-agent.sh --test
4. Run: ./job-agent.sh

For detailed instructions, see README.md
EOF

# Create archive
cd "$DIST_DIR"
if command -v zip &> /dev/null; then
    echo "📦 Creating ZIP archive..."
    zip -r "${PACKAGE_NAME}-v${VERSION}.zip" "$PACKAGE_NAME/"
    echo "✅ Created: ${PACKAGE_NAME}-v${VERSION}.zip"
fi

if command -v tar &> /dev/null; then
    echo "📦 Creating TAR.GZ archive..."
    tar -czf "${PACKAGE_NAME}-v${VERSION}.tar.gz" "$PACKAGE_NAME/"
    echo "✅ Created: ${PACKAGE_NAME}-v${VERSION}.tar.gz"
fi

cd "$SCRIPT_DIR"

echo ""
echo "🎉 Distribution package created successfully!"
echo "📁 Location: $DIST_DIR"
echo ""
echo "📦 Package contents:"
ls -la "$DIST_DIR"
echo ""
echo "🚀 Ready for distribution!"

# Show usage examples
echo ""
echo "📋 Distribution Examples:"
echo ""
echo "1. Send to users:"
echo "   scp ${PACKAGE_NAME}-v${VERSION}.tar.gz user@server:/home/user/"
echo ""
echo "2. GitHub release:"
echo "   gh release create v${VERSION} ${PACKAGE_NAME}-v${VERSION}.zip ${PACKAGE_NAME}-v${VERSION}.tar.gz"
echo ""
echo "3. User installation:"
echo "   tar -xzf ${PACKAGE_NAME}-v${VERSION}.tar.gz"
echo "   cd ${PACKAGE_NAME}"
echo "   ./install.sh"
echo "   cp .env.example .env"
echo "   # Edit .env with credentials"
echo "   ./job-agent.sh --test"
echo "   ./job-agent.sh"
