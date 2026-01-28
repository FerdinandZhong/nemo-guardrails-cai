#!/bin/bash
# Helper script to run local tests with conda environment

CONDA_ENV="vllm-playground-env"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "Running with conda environment: $CONDA_ENV"
echo "========================================================================"
echo ""

# Check if environment exists
if ! conda env list | grep -q "^$CONDA_ENV "; then
    echo -e "${RED}❌ Conda environment '$CONDA_ENV' not found${NC}"
    echo "Available environments:"
    conda env list
    exit 1
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY not set${NC}"
    echo ""
    echo "Set it with:"
    echo "  export OPENAI_API_KEY='sk-proj-your-key-here'"
    echo ""
    echo "Or load from .env:"
    echo "  export \$(cat examples/local_test/.env | grep -v '^#' | xargs)"
    exit 1
fi

echo -e "${GREEN}✅ Using conda environment: $CONDA_ENV${NC}"
echo -e "${GREEN}✅ OPENAI_API_KEY is set${NC}"
echo ""

# Run the command passed as argument, or start server by default
if [ $# -eq 0 ]; then
    echo -e "${BLUE}Starting test server...${NC}"
    echo ""
    conda run -n "$CONDA_ENV" python examples/local_test/test_server.py
else
    echo -e "${BLUE}Running: $@${NC}"
    echo ""
    conda run -n "$CONDA_ENV" "$@"
fi
