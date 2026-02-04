#!/usr/bin/env python3
"""
Launch NeMo Guardrails server as a CAI (CML) Application.

This script:
1. Loads configuration
2. Creates a CAI Application for the guardrails server
3. Monitors startup
4. Saves connection info

Uses direct CAI REST API calls instead of external dependencies.
"""

import os
import sys
import json
import logging
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any

import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GuardrailsDeployer:
    """Manages NeMo Guardrails deployment on CAI using REST API."""

    def __init__(
        self,
        cml_host: str,
        api_key: str,
        project_id: str,
        config_path: str = "guardrails_config.yaml",
    ):
        """Initialize the deployer.

        Args:
            cml_host: CAI instance URL
            api_key: CAI API key
            project_id: CAI project ID
            config_path: Path to guardrails configuration file
        """
        self.cml_host = cml_host
        self.api_key = api_key
        self.project_id = project_id
        self.config_path = config_path
        self.api_url = f"{cml_host.rstrip('/')}/api/v2"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key.strip()}",
        }
        self.config = self._load_config()

    def make_request(
        self, method: str, endpoint: str, data: dict = None, params: dict = None
    ) -> Optional[Dict[str, Any]]:
        """Make a request to the CAI REST API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            Response JSON as dictionary, or None on error
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30,
            )

            if 200 <= response.status_code < 300:
                if response.text:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {}
                return {}
            else:
                logger.error(f"API Error ({response.status_code}): {response.text[:200]}")
                return None

        except Exception as e:
            logger.error(f"Request error: {e}")
            return None

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        config_file = Path(self.config_path)

        if not config_file.exists():
            logger.warning(f"Config file not found: {config_file}, using defaults")
            return self._default_config()

        with open(config_file, "r") as f:
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
            "guardrails": {"config_path": "config"},
        }

    def create_application(self) -> Optional[Dict[str, Any]]:
        """Create CAI Application for guardrails server.

        Returns:
            Application object with id, name, subdomain, etc.
        """
        server_config = self.config.get("server", {})
        guardrails_config = self.config.get("guardrails", {})

        app_name = "nemo-guardrails-server"

        logger.info(f"Creating application: {app_name}")

        # Build startup script
        startup_script = self._build_startup_script()

        # Build application configuration
        app_data = {
            "name": app_name,
            "description": "NeMo Guardrails Server",
            "script": startup_script,
            "cpu": server_config.get("cpu", 4),
            "memory": server_config.get("memory", 16),
            "environment": {
                "GUARDRAILS_CONFIG_PATH": guardrails_config.get("config_path", "config"),
            },
            "bypass_authentication": server_config.get("bypass_authentication", True),
            "runtime_identifier": server_config.get(
                "runtime_identifier",
                "docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-pbj-jupyterlab-python3.11-cuda:2025.09.1-b5",
            ),
        }

        try:
            # Create application via REST API
            result = self.make_request(
                "POST", f"projects/{self.project_id}/applications", data=app_data
            )

            if result and "id" in result:
                logger.info(f"Application created successfully: {result.get('id')}")
                return result
            else:
                logger.error("No application ID in response")
                return None

        except Exception as e:
            logger.error(f"Failed to create application: {e}")
            return None

    def _build_startup_script(self) -> str:
        """Build the startup script for the application.

        Returns a simple bash wrapper that calls the Python entry point script.
        The Python script (app_startup.py) handles environment setup and launches
        the NeMo Guardrails server via the bash script (app_startup.sh).

        Returns:
            Startup script as string
        """
        script = """#!/bin/bash
set -eox pipefail

# CAI Application Startup Wrapper
# This simple script calls the Python entry point which handles all setup

cd /home/cdsw

# Execute the Python startup script
exec python cai_integration/app_startup.py
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
                result = self.make_request(
                    "GET", f"projects/{self.project_id}/applications/{app_id}"
                )

                if result:
                    status = result.get("status", "unknown")

                    if status == "running":
                        logger.info("Application is running")
                        return True

                    logger.info(f"Application status: {status}")

                time.sleep(10)

            except Exception as e:
                logger.warning(f"Error checking application status: {e}")
                time.sleep(10)

        logger.error("Timeout waiting for application to be ready")
        return False

    def save_connection_info(
        self, app: Dict[str, Any], output_path: str = "/home/cdsw/guardrails_info.json"
    ):
        """Save application connection information.

        Args:
            app: Application dictionary from API response
            output_path: Path to save connection info
        """
        subdomain = app.get("subdomain", app.get("name", "guardrails"))
        info = {
            "app_id": app.get("id"),
            "app_name": app.get("name"),
            "subdomain": subdomain,
            "url": f"https://{subdomain}",
            "status": app.get("status"),
            "created_at": app.get("created_at"),
        }

        with open(output_path, "w") as f:
            json.dump(info, f, indent=2)

        logger.info(f"Connection info saved to {output_path}")
        logger.info(f"Guardrails server URL: {info['url']}")


def main():
    """Main deployment function."""
    # Get environment variables from CAI built-in variables
    # CDSW_DOMAIN: CAI domain (e.g., "ml-xxxxx.cloudera.site")
    # CDSW_APIV2_KEY: CAI API key
    # CDSW_PROJECT_ID: Project ID
    cdsw_domain = os.environ.get("CDSW_DOMAIN")
    api_key = os.environ.get("CDSW_APIV2_KEY")
    project_id = os.environ.get("CDSW_PROJECT_ID")
    config_path = os.environ.get("GUARDRAILS_CONFIG", "guardrails_config.yaml")

    # Construct CML host from domain
    cml_host = f"https://{cdsw_domain}" if cdsw_domain else None

    if not all([cdsw_domain, api_key, project_id]):
        logger.error(
            "Missing required environment variables: CDSW_DOMAIN, CDSW_APIV2_KEY, CDSW_PROJECT_ID"
        )
        sys.exit(1)

    try:
        logger.info("=" * 60)
        logger.info("Starting NeMo Guardrails deployment")
        logger.info("=" * 60)

        # Create deployer
        deployer = GuardrailsDeployer(
            cml_host=cml_host, api_key=api_key, project_id=project_id, config_path=config_path
        )

        # Create application
        app = deployer.create_application()
        if not app:
            logger.error("Failed to create application")
            sys.exit(1)

        app_id = app.get("id")
        if not app_id:
            logger.error("No application ID returned from API")
            sys.exit(1)

        # Wait for application to be ready
        if not deployer.wait_for_app_ready(app_id):
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
