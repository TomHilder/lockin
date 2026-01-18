#!/bin/bash

# Lockin Uninstall Script for macOS

set -e

echo "🔓 Lockin Uninstallation"
echo "======================="
echo ""

# Configuration
LOCKIN_DIR="$HOME/.lockin"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENTS_DIR/com.lockin.engine.plist"

# Stop and remove LaunchAgent
if [[ -f "$PLIST_FILE" ]]; then
    echo "🛑 Stopping background engine..."
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    rm "$PLIST_FILE"
    echo "✓ Background engine stopped and removed"
fi

# Ask about data
echo ""
read -p "Do you want to delete your session history? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing data directory..."
    rm -rf "$LOCKIN_DIR"
    echo "✓ All data removed"
else
    # Just remove venv but keep data
    if [[ -d "$LOCKIN_DIR/venv" ]]; then
        echo "🗑️  Removing virtual environment..."
        rm -rf "$LOCKIN_DIR/venv"
        echo "✓ Virtual environment removed (data preserved)"
    fi
fi

# Note about PATH
echo ""
echo "⚠️  Note: You may want to remove Lockin from your PATH"
echo "Check ~/.zshrc or ~/.bashrc for the Lockin PATH entry"

echo ""
echo "✅ Uninstallation complete"
