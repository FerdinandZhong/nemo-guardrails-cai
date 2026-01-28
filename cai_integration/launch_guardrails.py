#!/usr/bin/env python3
"""
Launch NeMo Guardrails server as a CML Application.

This script:
1. Loads configuration
2. Creates a CML Application for the guardrails server
3. Monitors startup
4. Saves connection info
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Optional

# Add parent directory to path to import caikit
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "caikit"))

try:
    from caikit import CMLClient
except ImportError:
    logging.error("caikit package not found. Please install it first.")
    sys.exit(1)

import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GuardrailsDeployer:
    """Manages NeMo Guardrails deployment on CML."""

    def __init__(
        self,
        cml_host: str,
        api_key: str,
        project_id: str,
        config_path: str = "guardrails_config.yaml"
    ):
        """Initialize the deployer.

        Args:
            cml_host: CML instance URL
            api_key: CML API key
            project_id: CML project ID
            config_path: Path to guardrails configuration file
        """
        self.client = CMLClient(host=cml_host, api_key=api_key)
        self.project_id = project_id
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        config_file = Path(self.config_path)

        if not config_file.exists():
            logger.warning(f"Config file not found: {config_file}, using defaults")
            return self._default_config()

        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        logger.info(f"Loaded configuration from {config_file}")
        return config

    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            "server": {
                "cpu": 4,
                "memory": 16,
            },
            "guardrails": {
                "config_path": "config"
            }
        }

    def create_application(self) -> dict:
        """Create CML Application for guardrails server.

        Returns:
            Application creation response
        """
        server_config = self.config.get("server", {})
        guardrails_config = self.config.get("guardrails", {})

        app_name = "nemo-guardrails-server"

        logger.info(f"Creating application: {app_name}")

        # Build startup script
        startup_script = self._build_startup_script(guardrails_config)

        # Create application
        app_config = {
            "name": app_name,
            "description": "NeMo Guardrails Server",
            "script": startup_script,
            "cpu": server_config.get("cpu", 4),
            "memory": server_config.get("memory", 16),
            "environment": {
                "GUARDRAILS_CONFIG_PATH": guardrails_config.get("config_path", "config"),
            },
            "bypass_authentication": server_config.get("bypass_authentication", False),
        }

        # Check if runtime is specified
        if "runtime_identifier" in server_config:
            app_config["runtime_identifier"] = server_config["runtime_identifier"]

        try:
            app = self.client.applications.create(
                project_id=self.project_id,
                **app_config
            )

            logger.info(f"Application created successfully: {app.id}")
            return app

        except Exception as e:
            logger.error(f"Failed to create application: {e}")
            raise

    def _build_startup_script(self, guardrails_config: dict) -> str:
        """Build the startup script for the application.

        Uses NeMo Guardrails CLI for proper initialization and configuration.

        Args:
            guardrails_config: Guardrails configuration dictionary

        Returns:
            Startup script as string
        """
        config_path = guardrails_config.get("config_path", "examples/config")
        log_level = guardrails_config.get("log_level", "INFO")

        script = f"""#!/bin/bash
set -eox pipefail

# NeMo Guardrails Application Startup Script
# This script runs in CAI environment

# Activate virtual environment if it exists
if [ -d "/home/cdsw/.venv" ]; then
    echo "Activating virtual environment..."
    source /home/cdsw/.venv/bin/activate
fi

# Set environment variables
export GUARDRAILS_CONFIG_PATH={config_path}
export LOG_LEVEL={log_level}

# Verify config path exists
if [ ! -d "$GUARDRAILS_CONFIG_PATH" ]; then
    echo "Warning: Config path not found at $GUARDRAILS_CONFIG_PATH"
    echo "Using default: examples/local_test"
    export GUARDRAILS_CONFIG_PATH="examples/local_test"
fi

# Start guardrails server using NeMo Guardrails CLI
# CDSW_APP_PORT is automatically set by CAI
echo "==============================================="
echo "Starting NeMo Guardrails Server"
echo "==============================================="
echo "Config Path: $GUARDRAILS_CONFIG_PATH"
echo "Log Level: $LOG_LEVEL"
echo "Port: ${{CDSW_APP_PORT:-8080}}"
echo ""

cd /home/cdsw

# Use NeMo Guardrails CLI for proper initialization
python -m nemoguardrails server \\
    --config "$GUARDRAILS_CONFIG_PATH" \\
    --port "${{CDSW_APP_PORT:-8080}}" \\
    --verbose

echo "==============================================="
echo "NeMo Guardrails Server stopped"
echo "==============================================="
"""
        return script

    def wait_for_app_ready(self, app_id: str, timeout: int = 300) -> bool:
        """Wait for application to be ready.

        Args:
            app_id: Application ID
            timeout: Timeout in seconds

        Returns:
            True if ready, False if timeout
        """
        logger.info(f"Waiting for application {app_id} to be ready...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                app = self.client.applications.get(self.project_id, app_id)

                if app.status == "running":
                    logger.info("Application is running")
                    return True

                logger.info(f"Application status: {app.status}")
                time.sleep(10)

            except Exception as e:
                logger.warning(f"Error checking application status: {e}")
                time.sleep(10)

        logger.error("Timeout waiting for application to be ready")
        return False

    def save_connection_info(self, app: dict, output_path: str = "/home/cdsw/guardrails_info.json"):
        """Save application connection information.

        Args:
            app: Application object
            output_path: Path to save connection info
        """
        info = {
            "app_id": app.id,
            "app_name": app.name,
            "subdomain": app.subdomain,
            "url": f"https://{app.subdomain}",
            "status": app.status,
            "created_at": str(app.created_at) if hasattr(app, 'created_at') else None,
        }

        with open(output_path, 'w') as f:
            json.dump(info, f, indent=2)

        logger.info(f"Connection info saved to {output_path}")
        logger.info(f"Guardrails server URL: {info['url']}")


def main():
    """Main deployment function."""
    # Get environment variables
    cml_host = os.environ.get("CML_HOST")
    api_key = os.environ.get("CML_API_KEY")
    project_id = os.environ.get("CDSW_PROJECT_ID")
    config_path = os.environ.get("GUARDRAILS_CONFIG", "guardrails_config.yaml")

    if not all([cml_host, api_key, project_id]):
        logger.error("Missing required environment variables: CML_HOST, CML_API_KEY, CDSW_PROJECT_ID")
        sys.exit(1)

    try:
        logger.info("=" * 60)
        logger.info("Starting NeMo Guardrails deployment")
        logger.info("=" * 60)

        # Create deployer
        deployer = GuardrailsDeployer(
            cml_host=cml_host,
            api_key=api_key,
            project_id=project_id,
            config_path=config_path
        )

        # Create application
        app = deployer.create_application()

        # Wait for application to be ready
        if not deployer.wait_for_app_ready(app.id):
            logger.error("Application failed to start")
            sys.exit(1)

        # Save connection info
        deployer.save_connection_info(app)

        logger.info("=" * 60)
        logger.info("Deployment completed successfully")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Deployment failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
