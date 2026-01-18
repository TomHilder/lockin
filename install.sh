#!/bin/bash

# Lockin Installation Script for macOS
# This script installs Lockin in a dedicated virtual environment
# Supports both uv and pip package managers

set -e

echo "🔒 Lockin Installation"
echo "====================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: Lockin is designed for macOS only"
    exit 1
fi

# Configuration
LOCKIN_DIR="$HOME/.lockin"
VENV_DIR="$LOCKIN_DIR/venv"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENTS_DIR/com.lockin.engine.plist"

# Create Lockin directory
echo "📁 Creating Lockin directory..."
mkdir -p "$LOCKIN_DIR"

# Detect package manager (prefer uv if available)
USE_UV=false
if command -v uv &> /dev/null; then
    USE_UV=true
    echo "✓ Found uv package manager"
else
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Error: Python 3 is required but not found"
        echo "Please install Python 3 from https://www.python.org/"
        echo "Or install uv from https://docs.astral.sh/uv/"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "✓ Found Python $PYTHON_VERSION (using pip)"
fi

# Create virtual environment and install
if $USE_UV; then
    echo "🐍 Creating virtual environment with uv..."
    uv venv "$VENV_DIR"

    echo "📥 Installing Lockin..."
    VIRTUAL_ENV="$VENV_DIR" uv pip install -e . > /dev/null
else
    echo "🐍 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Upgrade pip
    echo "📦 Upgrading pip..."
    pip install --upgrade pip > /dev/null

    # Install Lockin
    echo "📥 Installing Lockin..."
    pip install -e . > /dev/null
fi

echo "✓ Lockin installed"

# Get Python path from venv
PYTHON_PATH="$VENV_DIR/bin/python"

# Create LaunchAgent plist
echo "⚙️  Setting up background engine..."
mkdir -p "$LAUNCH_AGENTS_DIR"

# Replace placeholders in plist
sed "s|PYTHON_PATH_PLACEHOLDER|$PYTHON_PATH|g; s|LOCKIN_DIR_PLACEHOLDER|$LOCKIN_DIR|g" \
    com.lockin.engine.plist > "$PLIST_FILE"

# Load LaunchAgent
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

echo "✓ Background engine installed and started"

# Add to PATH
SHELL_RC=""
if [[ -n "$ZSH_VERSION" ]] || [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ -n "$BASH_VERSION" ]] || [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [[ -n "$SHELL_RC" ]]; then
    # Check if already in PATH
    if ! grep -q "lockin/venv/bin" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# Lockin" >> "$SHELL_RC"
        echo "export PATH=\"$VENV_DIR/bin:\$PATH\"" >> "$SHELL_RC"
        echo "✓ Added to PATH in $SHELL_RC"
        echo "  Please run: source $SHELL_RC"
    fi
fi

# Verify installation
sleep 2
if "$VENV_DIR/bin/lockin" --help &>/dev/null; then
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "Try it out:"
    echo "  lockin           # Show dashboard"
    echo "  lockin 30        # Start 30-minute work session"
    echo "  lockin break 5   # Start 5-minute break"
    echo ""
    echo "The engine is now running in the background."
    echo "It will start automatically on login."
else
    echo ""
    echo "⚠️  Installation completed but verification failed."
    echo "You may need to restart your terminal."
fi
