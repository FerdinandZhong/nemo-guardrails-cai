#!/bin/bash
set -eox pipefail

# Start NeMo Guardrails Server
# This script is called by start_application.py
# We're already in the project root directory thanks to PathManager

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Set environment variables for NeMo Guardrails
export LOG_LEVEL=${LOG_LEVEL:-INFO}

# Get config path from environment or use default
CONFIG_PATH=${GUARDRAILS_CONFIG_PATH:-examples/config}

# Verify config exists
if [ ! -d "$CONFIG_PATH" ]; then
    echo "Warning: Config directory not found at $CONFIG_PATH"
    echo "Using default config from examples/local_test"
    CONFIG_PATH="examples/local_test"
fi

echo "==============================================="
echo "Starting NeMo Guardrails Server"
echo "==============================================="
echo "Config Path: $CONFIG_PATH"
echo "LOG_LEVEL: $LOG_LEVEL"
echo "CDSW_APP_PORT: ${CDSW_APP_PORT:-8080} (auto-detected by server)"
echo ""

# Start the NeMo Guardrails server using the CLI
# The CDSW_APP_PORT environment variable is automatically set by CAI
python -m nemoguardrails server \
    --config "$CONFIG_PATH" \
    --port "${CDSW_APP_PORT:-8080}" \
    --verbose

echo "==============================================="
echo "NeMo Guardrails Server stopped"
echo "==============================================="
