#!/bin/bash
set -e

echo "=============================================================="
echo "Starting NeMo Guardrails environment setup"
echo "=============================================================="

# Sync latest code from git
echo "Syncing latest code from repository..."
cd /home/cdsw
if git pull origin feature/implementation; then
    echo "✓ Code synced successfully"
else
    echo "⚠ Git pull failed (continuing with existing code)"
fi

VENV_PATH="/home/cdsw/.venv"

# Check if virtual environment exists
if [ -d "$VENV_PATH" ]; then
    echo "✓ Virtual environment already exists at $VENV_PATH"
    echo "  Reusing existing environment..."
else
    echo "Creating new virtual environment at $VENV_PATH"
    python3 -m venv "$VENV_PATH"
    echo "✓ Virtual environment created successfully"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Try to upgrade pip (non-critical)
echo "Attempting to upgrade pip..."
if pip install --upgrade pip; then
    echo "✓ Pip upgraded successfully"
else
    echo "⚠ Pip upgrade failed (continuing anyway)"
fi

# Install dependencies
echo "Installing dependencies..."
pip install "nemoguardrails>=0.9.0"
pip install "fastapi>=0.109.0"
pip install "uvicorn>=0.27.0"
pip install "pyyaml>=6.0.0"
pip install "pydantic>=2.0.0"
pip install "requests>=2.31.0"

echo "✓ All dependencies installed successfully"

# Verify installation
echo "Verifying installation..."
python -c "import nemoguardrails; print(f'NeMo Guardrails version: {nemoguardrails.__version__}')"

echo "=============================================================="
echo "Environment setup completed successfully"
echo "Virtual environment location: $VENV_PATH"
echo "=============================================================="
