#!/bin/bash
# Environment setup script for local testing

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "NeMo Guardrails - Local Testing Environment Setup"
echo "========================================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if .env.example exists
if [ ! -f "$SCRIPT_DIR/.env.example" ]; then
    echo -e "${RED}❌ Error: .env.example not found${NC}"
    exit 1
fi

# Check if .env already exists
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file already exists${NC}"
    echo ""
    read -p "Do you want to overwrite it? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
        echo ""
    else
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
        echo -e "${GREEN}✅ Created new .env file from template${NC}"
        echo ""
    fi
else
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo -e "${GREEN}✅ Created .env file from template${NC}"
    echo ""
fi

# Prompt for OpenAI API key
echo -e "${BLUE}Please enter your OpenAI API key:${NC}"
echo "(Get it from: https://platform.openai.com/api-keys)"
echo ""
read -p "OPENAI_API_KEY: " api_key

if [ -z "$api_key" ]; then
    echo -e "${RED}❌ Error: API key cannot be empty${NC}"
    exit 1
fi

# Update .env file
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$api_key/" "$SCRIPT_DIR/.env"
else
    # Linux
    sed -i "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$api_key/" "$SCRIPT_DIR/.env"
fi

echo ""
echo -e "${GREEN}✅ API key saved to .env file${NC}"
echo ""

# Check if nemoguardrails is installed
echo "Checking dependencies..."
if ! python3 -c "import nemoguardrails" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  nemoguardrails not installed${NC}"
    echo ""
    read -p "Install it now? (Y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "Installing nemoguardrails..."
        pip3 install nemoguardrails
        echo ""
        echo -e "${GREEN}✅ nemoguardrails installed${NC}"
    fi
else
    echo -e "${GREEN}✅ nemoguardrails is installed${NC}"
fi

echo ""
echo "========================================================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================================================"
echo ""
echo "To use these settings, run:"
echo -e "  ${BLUE}source $SCRIPT_DIR/.env${NC}"
echo ""
echo "Or export them:"
echo -e "  ${BLUE}export \$(cat $SCRIPT_DIR/.env | grep -v '^#' | xargs)${NC}"
echo ""
echo "Then start the server:"
echo -e "  ${BLUE}python examples/local_test/test_server.py${NC}"
echo ""
echo "========================================================================"
