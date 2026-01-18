#!/bin/bash

# Development script to run Lockin engine locally (without LaunchAgent)
# This is useful for testing or running without full installation
# Supports both uv and pip package managers

echo "🔒 Lockin Development Mode"
echo "=========================="
echo ""

# Detect package manager and setup environment
if command -v uv &> /dev/null; then
    echo "✓ Using uv package manager"

    # Check if .venv exists, create if not
    if [[ ! -d ".venv" ]]; then
        echo "📦 Creating virtual environment..."
        uv venv
    fi

    # Check if dependencies installed
    if ! uv run python -c "import rich" 2>/dev/null; then
        echo "📦 Installing dependencies..."
        uv pip install -e . -q
    fi

    echo ""
    echo "Starting Lockin engine in development mode..."
    echo "Press Ctrl+C to stop"
    echo ""
    echo "In another terminal, run:"
    echo "  uv run lockin 30   # Start 30-min work session"
    echo "  uv run lockin      # Attach to session"
    echo ""

    uv run python -m lockin.engine_main
else
    echo "✓ Using pip (uv not found)"

    # Check if in virtual environment
    if [[ -z "$VIRTUAL_ENV" ]]; then
        echo "⚠️  Not in a virtual environment"
        echo "Creating one in .venv..."
        python3 -m venv .venv
        source .venv/bin/activate
        echo "📦 Installing dependencies..."
        pip install -e . -q
    else
        echo "✓ Using virtual environment: $VIRTUAL_ENV"
    fi

    # Check if dependencies installed
    if ! python -c "import rich" 2>/dev/null; then
        echo "📦 Installing dependencies..."
        pip install -e . -q
    fi

    echo ""
    echo "Starting Lockin engine in development mode..."
    echo "Press Ctrl+C to stop"
    echo ""
    echo "In another terminal, run:"
    echo "  lockin 30        # Start 30-min work session"
    echo "  lockin           # Attach to session"
    echo ""

    python -m lockin.engine_main
fi
