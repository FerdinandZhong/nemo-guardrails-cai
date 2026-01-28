#!/usr/bin/env python3
"""
Start NeMo Guardrails Application in CAI environment.

This script:
1. Detects if running in CAI (IS_COMPOSABLE) or locally
2. Uses PathManager to handle directory context
3. Executes the start_application.sh shell script

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
    """Main entry point for starting the application."""

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

    # Execute the start application shell script
    logger.info("=" * 60)
    logger.info("Starting NeMo Guardrails Application")
    logger.info("=" * 60)

    try:
        # Run the bash script
        result = subprocess.run(
            ["bash", "build/shell_scripts/start_application.sh"],
            check=True,
            cwd=project_root
        )

        logger.info("Application completed successfully")
        return result.returncode

    except subprocess.CalledProcessError as e:
        logger.error(f"Application failed with exit code {e.returncode}")
        return e.returncode
    except Exception as e:
        logger.error(f"Error starting application: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
