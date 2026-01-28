#!/usr/bin/env python3
"""
Local test script for NeMo Guardrails with default rails.

This script starts a simple guardrails server for local testing.
It uses the default built-in rails from NeMo Guardrails.

Usage:
    python examples/local_test/test_server.py

Requirements:
    - OPENAI_API_KEY environment variable set
    - nemoguardrails installed: pip install nemoguardrails
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_requirements():
    """Check if all requirements are met."""
    logger.info("Checking requirements...")

    # Check OPENAI_API_KEY
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("❌ OPENAI_API_KEY not set!")
        logger.info("Please set it: export OPENAI_API_KEY='your-key-here'")
        return False

    # Check if nemoguardrails is installed
    try:
        import nemoguardrails
        logger.info(f"✅ NeMo Guardrails version: {nemoguardrails.__version__}")
    except ImportError:
        logger.error("❌ NeMo Guardrails not installed!")
        logger.info("Install it: pip install nemoguardrails")
        return False

    # Check config file
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.exists():
        logger.error(f"❌ Config file not found: {config_path}")
        return False

    logger.info(f"✅ Config file found: {config_path}")
    return True


def start_server():
    """Start the guardrails server using NeMo Guardrails CLI."""
    try:
        from pathlib import Path
        import subprocess

        config_path = Path(__file__).parent
        port = int(os.environ.get("CDSW_APP_PORT", 8080))

        logger.info("=" * 70)
        logger.info("Starting NeMo Guardrails Server (Local Test)")
        logger.info("=" * 70)
        logger.info(f"Config path: {config_path}")
        logger.info(f"Port: {port}")
        logger.info("")
        logger.info("🚀 Starting server on http://localhost:8080")
        logger.info("   Config: Local Test (examples/local_test/config.yml)")
        logger.info("   OpenAI-compatible endpoint: http://localhost:8080/v1")
        logger.info("   Chat UI: http://localhost:8080")
        logger.info("")
        logger.info("Test with:")
        logger.info("   python examples/local_test/test_client.py")
        logger.info("   Or open http://localhost:8080 in your browser")
        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 70)
        logger.info("")

        # Use the NeMo Guardrails CLI to start the server
        # This is more reliable than trying to manually configure the FastAPI app
        cmd = [
            "nemoguardrails",
            "server",
            "--config", str(config_path),
            "--port", str(port),
        ]

        logger.info(f"Running: {' '.join(cmd)}")
        logger.info("")

        subprocess.run(cmd, check=False)

    except KeyboardInterrupt:
        logger.info("\n👋 Server stopped")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point."""
    if not check_requirements():
        sys.exit(1)

    start_server()


if __name__ == "__main__":
    main()
