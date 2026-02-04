#!/bin/bash
set -eox pipefail

# NeMo Guardrails Application Startup Script
# This script runs in the CAI Application environment and:
# 1. Activates the virtual environment
# 2. Sets up environment variables
# 3. Runs the NeMo Guardrails server

PROJECT_ROOT="${PROJECT_ROOT:-/home/cdsw}"
cd "$PROJECT_ROOT"

echo "==============================================="
echo "🚀 Starting NeMo Guardrails Server"
echo "==============================================="
echo "Project root: $PROJECT_ROOT"
echo ""

# Activate virtual environment
VENV_PATH=".venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    echo "📦 Activating virtual environment..."
    source "$VENV_PATH"
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "Please ensure setup_environment job has completed"
    exit 1
fi

# Set environment variables
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export GUARDRAILS_CONFIG_PATH="${GUARDRAILS_CONFIG_PATH:-examples/config}"

# Verify config path exists
if [ ! -d "$GUARDRAILS_CONFIG_PATH" ]; then
    echo "⚠️  Config path not found at $GUARDRAILS_CONFIG_PATH"
    echo "Using default: examples/local_test"
    export GUARDRAILS_CONFIG_PATH="examples/local_test"
fi

echo ""
echo "Configuration:"
echo "  Config Path: $GUARDRAILS_CONFIG_PATH"
echo "  Log Level: $LOG_LEVEL"
echo "  Host: 127.0.0.1"
echo "  Port: ${CDSW_APP_PORT:-8100}"
echo ""

# Start NeMo Guardrails server
# Note: Use --host 127.0.0.1 because CAI's proxy already binds to 0.0.0.0
echo "Starting NeMo Guardrails server..."
python -m nemoguardrails server \
    --config "$GUARDRAILS_CONFIG_PATH" \
    --host 127.0.0.1 \
    --port "${CDSW_APP_PORT:-8100}" \
    --verbose

echo "==============================================="
echo "NeMo Guardrails Server stopped"
echo "==============================================="
