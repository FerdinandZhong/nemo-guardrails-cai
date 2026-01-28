#!/bin/bash
# Quick start script for local testing of NeMo Guardrails

set -e

echo "========================================================================"
echo "NeMo Guardrails - Local Testing Quick Start"
echo "========================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ Error: OPENAI_API_KEY not set${NC}"
    echo ""
    echo "Please set your OpenAI API key:"
    echo "  export OPENAI_API_KEY='your-key-here'"
    echo ""
    echo "Get your API key from: https://platform.openai.com/api-keys"
    exit 1
fi

echo -e "${GREEN}✅ OPENAI_API_KEY is set${NC}"

# Check if nemoguardrails is installed
if ! python -c "import nemoguardrails" 2>/dev/null; then
    echo -e "${RED}❌ Error: nemoguardrails not installed${NC}"
    echo ""
    echo "Installing nemoguardrails..."
    pip install nemoguardrails
    echo ""
fi

echo -e "${GREEN}✅ nemoguardrails is installed${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$PROJECT_ROOT"

echo ""
echo "========================================================================"
echo "Starting test server..."
echo "========================================================================"
echo ""
echo "Server will start on http://localhost:8080"
echo ""
echo "To test the server:"
echo "  1. Open another terminal"
echo "  2. Run: python examples/local_test/test_client.py"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================================================"
echo ""

# Start the server
python examples/local_test/test_server.py
