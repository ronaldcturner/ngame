#!/bin/bash

# NGAME UI Installation Script
# This script handles common installation issues and provides alternative methods

echo "🚀 NGAME UI Installation Script"
echo "================================"

# Check Python version - improved detection
echo "📋 Checking Python version..."

# Try different Python commands
PYTHON_CMD=""
PYTHON_VERSION=""

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+\.\d+' | head -1)
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1 | grep -oP '\d+\.\d+\.\d+' | head -1)
else
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "Found Python: $PYTHON_CMD version $PYTHON_VERSION"

# Extract major and minor version numbers
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "Major version: $MAJOR_VERSION, Minor version: $MINOR_VERSION"

# Check if Python version is 3.8 or higher
if [ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -ge 8 ]; then
    echo "✅ Python $PYTHON_VERSION is compatible"
elif [ "$MAJOR_VERSION" -gt 3 ]; then
    echo "✅ Python $PYTHON_VERSION is compatible (newer than 3.8)"
else
    echo "❌ Python $PYTHON_VERSION is too old. Please upgrade to Python 3.8+"
    exit 1
fi

# Check if pip is available
echo "📋 Checking pip..."
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 is available"
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    echo "✅ pip is available"
    PIP_CMD="pip"
else
    echo "❌ pip not found. Please install pip first."
    exit 1
fi

# Upgrade pip
echo "📋 Upgrading pip..."
$PIP_CMD install --upgrade pip

# Install system dependencies (for macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📋 Installing system dependencies for macOS..."
    if command -v brew &> /dev/null; then
        brew install openssl
    else
        echo "⚠️  Homebrew not found. You may need to install OpenSSL manually."
    fi
fi

# Install system dependencies (for Ubuntu/Debian)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📋 Installing system dependencies for Linux..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-dev build-essential libssl-dev libffi-dev
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-devel gcc openssl-devel libffi-devel
    else
        echo "⚠️  Package manager not found. You may need to install dependencies manually."
    fi
fi

# Try minimal installation first
echo "📋 Attempting minimal installation..."
if $PIP_CMD install -r requirements-minimal.txt; then
    echo "✅ Minimal installation successful"
    
    # Try to install additional packages one by one
    echo "📋 Installing additional packages..."
    
    # Flask-SocketIO (optional - can run without it)
    if $PIP_CMD install Flask-SocketIO; then
        echo "✅ Flask-SocketIO installed"
    else
        echo "⚠️  Flask-SocketIO installation failed. UI will work without real-time features."
    fi
    
    # Other optional packages
    for package in "python-socketio" "python-engineio" "Werkzeug" "Jinja2" "MarkupSafe" "itsdangerous" "click" "blinker"; do
        if $PIP_CMD install $package; then
            echo "✅ $package installed"
        else
            echo "⚠️  $package installation failed"
        fi
    done
    
else
    echo "❌ Minimal installation failed"
    echo "📋 Trying alternative installation methods..."
    
    # Try with --user flag
    if $PIP_CMD install --user -r requirements-minimal.txt; then
        echo "✅ Installation with --user flag successful"
    else
        echo "❌ Installation failed even with --user flag"
        echo "📋 Please try manual installation:"
        echo "   pip install Flask requests"
        exit 1
    fi
fi

# Create necessary directories
echo "📋 Creating directories..."
mkdir -p output
mkdir -p uploads
mkdir -p logs

# Set permissions
chmod 755 output uploads logs

echo ""
echo "🎉 Installation completed!"
echo "================================"
echo ""
echo "To start the NGAME UI:"
echo "  $PYTHON_CMD app.py"
echo ""
echo "Or use the simplified version:"
echo "  $PYTHON_CMD app-simple.py"
echo ""
echo "Then open your browser to:"
echo "  http://localhost:5000"
echo ""
echo "If you encounter any issues:"
echo "  1. Try: pip install --upgrade setuptools wheel"
echo "  2. Try: pip install --user Flask requests"
echo "  3. Check the troubleshooting section in README.md"
echo "" 