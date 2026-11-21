#!/bin/bash

# NGAME UI Simple Installation Script
# A simpler version that focuses on getting the UI running quickly

echo "🚀 NGAME UI Simple Installation"
echo "================================"

# Simple Python check
echo "📋 Checking Python..."
if command -v python3 &> /dev/null; then
    echo "✅ Python3 found"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    echo "✅ Python found"
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

# Show Python version
echo "📋 Python version:"
$PYTHON_CMD --version

# Check pip
echo "📋 Checking pip..."
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 found"
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    echo "✅ pip found"
    PIP_CMD="pip"
else
    echo "❌ pip not found. Installing pip..."
    $PYTHON_CMD -m ensurepip --upgrade
    PIP_CMD="$PYTHON_CMD -m pip"
fi

# Upgrade pip
echo "📋 Upgrading pip..."
$PIP_CMD install --upgrade pip

# Install minimal requirements
echo "📋 Installing minimal requirements..."
$PIP_CMD install Flask requests

# Try to install additional packages (optional)
echo "📋 Installing additional packages (optional)..."
$PIP_CMD install Flask-SocketIO || echo "⚠️  Flask-SocketIO failed - UI will work without real-time features"
$PIP_CMD install Werkzeug Jinja2 MarkupSafe || echo "⚠️  Some packages failed - continuing anyway"

# Create directories
echo "📋 Creating directories..."
mkdir -p output uploads logs
chmod 755 output uploads logs

echo ""
echo "🎉 Simple installation completed!"
echo "================================"
echo ""
echo "To start the NGAME UI:"
echo "  $PYTHON_CMD app-simple.py"
echo ""
echo "Then open your browser to:"
echo "  http://localhost:5000"
echo ""
echo "If you want the full version with real-time features:"
echo "  $PYTHON_CMD app.py"
echo "" 