#!/usr/bin/env python3
"""
Entry point for running NeMo Guardrails as a CAI Application.

This script is designed to be run directly in Cloudera AI (CML) environments
as an Application. It automatically detects the CDSW_APP_PORT environment
variable and starts the server accordingly.

Usage in CAI:
    python app.py

The script will:
1. Load configuration from the config directory or environment variables
2. Initialize the NeMo Guardrails server
3. Start the server on the port specified by CDSW_APP_PORT (or default to 8080)
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


def main():
    """Main entry point for CAI Application deployment."""

    logger.info("=" * 70)
    logger.info("Starting NeMo Guardrails Server for Cloudera AI")
    logger.info("=" * 70)

    # Check if running in CAI environment
    if "CDSW_APP_PORT" in os.environ:
        logger.info(f"Detected CAI environment - CDSW_APP_PORT: {os.environ['CDSW_APP_PORT']}")
    else:
        logger.warning("CDSW_APP_PORT not found - may not be running in CAI Application mode")

    # Get configuration path from environment or use default
    config_path = os.environ.get("GUARDRAILS_CONFIG_PATH", "config")
    config_file = os.environ.get("GUARDRAILS_CONFIG_FILE")

    logger.info(f"Guardrails config path: {config_path}")

    try:
        from nemo_guardrails_cai import GuardrailsServer, GuardrailsConfig

        # Load configuration
        if config_file and Path(config_file).exists():
            logger.info(f"Loading configuration from file: {config_file}")
            config = GuardrailsConfig.from_yaml(config_file)
        else:
            logger.info("Using default configuration")
            config = GuardrailsConfig(
                config_path=Path(config_path),
                host="0.0.0.0",
                log_level=os.environ.get("LOG_LEVEL", "INFO")
            )

        # Override with environment variables if present
        if "LLM_MODEL" in os.environ:
            config.llm_model = os.environ["LLM_MODEL"]
            logger.info(f"Using LLM model from environment: {config.llm_model}")

        if "LLM_API_KEY" in os.environ:
            config.llm_api_key = os.environ["LLM_API_KEY"]
            logger.info("LLM API key loaded from environment")

        if "LLM_API_BASE" in os.environ:
            config.llm_api_base = os.environ["LLM_API_BASE"]
            logger.info(f"Using LLM API base: {config.llm_api_base}")

        # Create and start server
        logger.info("Initializing Guardrails Server...")
        server = GuardrailsServer(config)

        logger.info("Starting server...")
        server.start()

    except FileNotFoundError as e:
        logger.error(f"Configuration not found: {e}")
        logger.error("Make sure the guardrails config directory exists and is properly configured")
        sys.exit(1)
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Make sure nemo-guardrails-cai is properly installed")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
