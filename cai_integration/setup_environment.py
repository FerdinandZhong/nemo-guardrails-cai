#!/usr/bin/env python3
"""
Setup Python environment for NeMo Guardrails in CML.

This script runs as a CML job to:
1. Create a Python virtual environment
2. Install NeMo Guardrails and dependencies
3. Verify installation
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


VENV_PATH = Path("/home/cdsw/.venv")
REQUIREMENTS = [
    "nemoguardrails>=0.9.0",
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "pyyaml>=6.0.0",
    "pydantic>=2.0.0",
    "requests>=2.31.0",
]


def run_command(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result.

    Args:
        cmd: Command as a list of strings
        check: Whether to raise exception on failure

    Returns:
        CompletedProcess instance
    """
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Combine stderr with stdout
        text=True,
        check=check
    )

    if result.stdout:
        # Print all output, whether success or failure
        for line in result.stdout.strip().split('\n'):
            if line:
                logger.info(f"  {line}")

    return result


def create_venv():
    """Create Python virtual environment."""
    logger.info(f"Creating virtual environment at {VENV_PATH}")

    if VENV_PATH.exists():
        logger.info("Virtual environment already exists, removing old one...")
        run_command(["rm", "-rf", str(VENV_PATH)])

    run_command([sys.executable, "-m", "venv", str(VENV_PATH)])
    logger.info("Virtual environment created successfully")


def install_dependencies():
    """Install required Python packages."""
    logger.info("Installing dependencies...")

    pip_path = VENV_PATH / "bin" / "pip"

    # Try to upgrade pip (non-critical, skip if fails)
    try:
        logger.info("Attempting to upgrade pip...")
        run_command([str(pip_path), "install", "--upgrade", "pip"], check=False)
        logger.info("Pip upgrade completed")
    except Exception as e:
        logger.warning(f"Pip upgrade failed (continuing anyway): {e}")

    # Install requirements
    for package in REQUIREMENTS:
        logger.info(f"Installing {package}...")
        run_command([str(pip_path), "install", package])

    logger.info("All dependencies installed successfully")


def verify_installation():
    """Verify NeMo Guardrails installation."""
    logger.info("Verifying installation...")

    python_path = VENV_PATH / "bin" / "python"

    # Test import
    result = run_command([
        str(python_path), "-c",
        "import nemoguardrails; print(f'NeMo Guardrails version: {nemoguardrails.__version__}')"
    ])

    if result.returncode == 0:
        logger.info("Installation verified successfully")
        return True
    else:
        logger.error("Installation verification failed")
        return False


def main():
    """Main setup function."""
    try:
        logger.info("=" * 60)
        logger.info("Starting NeMo Guardrails environment setup")
        logger.info("=" * 60)

        # Create virtual environment
        create_venv()

        # Install dependencies
        install_dependencies()

        # Verify installation
        if not verify_installation():
            logger.error("Setup failed - installation verification failed")
            sys.exit(1)

        logger.info("=" * 60)
        logger.info("Environment setup completed successfully")
        logger.info(f"Virtual environment location: {VENV_PATH}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Setup failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
