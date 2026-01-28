#!/bin/bash
set -eox pipefail

# Build and setup for NeMo Guardrails deployment
# This script:
# 1. Creates and activates virtual environment
# 2. Installs project dependencies
# 3. Installs additional dependencies for NeMo Guardrails

echo "==============================================="
echo "Building NeMo Guardrails Environment"
echo "==============================================="

# Setup virtual environment
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip and setuptools
echo "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install project dependencies
echo "Installing project dependencies..."
if [ -f "pyproject.toml" ]; then
    # Install main package and all extras
    pip install -e ".[dev]"

    # Install nemoguardrails if not already installed via dependencies
    pip install nemoguardrails>=0.19.0
else
    echo "Warning: pyproject.toml not found"
    # Minimal installation for NeMo Guardrails
    pip install nemoguardrails>=0.19.0 openai pyyaml
fi

# Verify installation
echo "Verifying NeMo Guardrails installation..."
python -c "import nemoguardrails; print(f'NeMo Guardrails version: {nemoguardrails.__version__}')"

echo ""
echo "==============================================="
echo "Build completed successfully!"
echo "==============================================="
echo ""
echo "Virtual environment location: $VENV_DIR"
echo ""
echo "To activate the environment manually:"
echo "  source $VENV_DIR/bin/activate"
echo ""
