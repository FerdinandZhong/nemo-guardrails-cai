#!/usr/bin/env python3
"""
Build script for NeMo Guardrails project.

This script:
1. Detects if running in CAI (IS_COMPOSABLE) or locally
2. Sets up virtual environment
3. Installs dependencies
4. Verifies NeMo Guardrails installation

This approach matches the pattern used in CAI_AMP projects.
"""

import subprocess
import os
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for building the project."""

    # Check if we're in a CAI (IS_COMPOSABLE) environment
    is_composable = os.getenv("IS_COMPOSABLE")

    if is_composable:
        # If running in CAI, change to the specified project root
        project_root = Path("/home/cdsw/nemo-guardrails-cai")
        logger.info(f"Running in CAI environment")
        logger.info(f"Project root: {project_root}")
    else:
        # Otherwise, use the current directory as the project root
        project_root = Path.cwd()
        logger.info(f"Running locally")
        logger.info(f"Project root: {project_root}")

    # Add project root to Python path
    sys.path.insert(0, str(project_root))

    # Change to project root directory
    os.chdir(project_root)
    logger.info(f"Changed to directory: {os.getcwd()}")

    # Execute the build shell script
    logger.info("=" * 60)
    logger.info("Building NeMo Guardrails Project")
    logger.info("=" * 60)

    try:
        # Run the bash script
        result = subprocess.run(
            ["bash", "build/shell_scripts/build_client.sh"],
            check=True,
            cwd=project_root
        )

        logger.info("=" * 60)
        logger.info("Build completed successfully")
        logger.info("=" * 60)

        return result.returncode

    except subprocess.CalledProcessError as e:
        logger.error(f"Build failed with exit code {e.returncode}")
        return e.returncode
    except Exception as e:
        logger.error(f"Error during build: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
