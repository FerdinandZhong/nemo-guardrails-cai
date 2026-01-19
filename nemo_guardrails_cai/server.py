"""NeMo Guardrails server for CAI deployment."""

import logging
import os
from pathlib import Path
from typing import Optional

from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.server import api

from nemo_guardrails_cai.config import GuardrailsConfig


logger = logging.getLogger(__name__)


class GuardrailsServer:
    """NeMo Guardrails server wrapper for CAI deployment.

    This class provides a simple interface for deploying NeMo Guardrails
    in Cloudera AI environments.

    Example:
        >>> config = GuardrailsConfig(
        ...     config_path=Path("config"),
        ...     llm_model="gpt-3.5-turbo",
        ...     port=8000
        ... )
        >>> server = GuardrailsServer(config)
        >>> server.start()
    """

    def __init__(self, config: GuardrailsConfig):
        """Initialize the guardrails server.

        Args:
            config: GuardrailsConfig instance
        """
        self.config = config
        self.rails: Optional[LLMRails] = None

        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        logger.info(f"Initializing Guardrails Server with config: {config}")

    def initialize_rails(self) -> None:
        """Initialize NeMo Guardrails with the provided configuration."""
        logger.info(f"Loading guardrails config from {self.config.config_path}")

        if not self.config.config_path.exists():
            raise FileNotFoundError(
                f"Guardrails config path not found: {self.config.config_path}"
            )

        # Initialize local models first (if configured)
        if self.config.local_models:
            logger.info("Initializing local models...")
            try:
                from nemo_guardrails_cai.models.registry import ModelRegistry

                ModelRegistry.load_from_config({"models": self.config.local_models})
                logger.info("Local models initialized successfully")
            except ImportError:
                logger.warning(
                    "Could not import ModelRegistry. Local models will not be available. "
                    "Install transformers and torch: pip install transformers torch"
                )
            except Exception as e:
                logger.error(f"Failed to initialize local models: {e}")
                # Continue without local models

        # Load guardrails configuration
        rails_config = RailsConfig.from_path(str(self.config.config_path))

        # Override LLM configuration if provided
        if self.config.llm_model:
            logger.info(f"Using LLM model: {self.config.llm_model}")
            if rails_config.models:
                rails_config.models[0].model = self.config.llm_model

        if self.config.llm_api_key:
            os.environ["OPENAI_API_KEY"] = self.config.llm_api_key

        if self.config.llm_api_base:
            os.environ["OPENAI_API_BASE"] = self.config.llm_api_base

        # Initialize LLMRails
        self.rails = LLMRails(rails_config)

        # Register custom actions
        try:
            from nemo_guardrails_cai.actions import model_checks
            self.rails.register_action(model_checks.check_jailbreak_local, "check_jailbreak_local")
            self.rails.register_action(model_checks.check_toxicity_local, "check_toxicity_local")
            self.rails.register_action(model_checks.check_with_local_model, "check_with_local_model")
            logger.info("Custom model check actions registered")
        except Exception as e:
            logger.warning(f"Could not register custom actions: {e}")

        logger.info("Guardrails initialized successfully")

    def start(self) -> None:
        """Start the guardrails server.

        This starts a FastAPI server that exposes the guardrails API.
        For CAI deployment, the port is automatically determined from CDSW_APP_PORT.
        """
        if self.rails is None:
            self.initialize_rails()

        # Use CDSW_APP_PORT if available (CAI deployment), otherwise use configured port
        port = int(os.environ.get("CDSW_APP_PORT", self.config.port))

        logger.info(f"Starting Guardrails Server on {self.config.host}:{port}")
        if "CDSW_APP_PORT" in os.environ:
            logger.info("Running in CAI mode - using CDSW_APP_PORT")

        # Configure the FastAPI app
        app = api.app

        # Register the rails instance
        api.app.rails = self.rails

        # Start the server
        import uvicorn
        uvicorn.run(
            app,
            host=self.config.host,
            port=port,
            log_level=self.config.log_level.lower(),
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response using guardrails.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters for generation

        Returns:
            Generated response
        """
        if self.rails is None:
            self.initialize_rails()

        response = await self.rails.generate_async(messages=[{
            "role": "user",
            "content": prompt
        }])

        return response.get("content", "")

    def health_check(self) -> dict:
        """Check server health status.

        Returns:
            Health status dictionary
        """
        return {
            "status": "healthy" if self.rails is not None else "not_initialized",
            "version": "0.1.0",
            "config_path": str(self.config.config_path),
        }


def create_server_from_config(config_path: str) -> GuardrailsServer:
    """Create a GuardrailsServer from a YAML configuration file.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        GuardrailsServer instance
    """
    config = GuardrailsConfig.from_yaml(config_path)
    return GuardrailsServer(config)


def main():
    """Main entry point for running the server."""
    import argparse

    parser = argparse.ArgumentParser(description="NeMo Guardrails Server for CAI")
    parser.add_argument(
        "--config",
        type=str,
        default="server_config.yaml",
        help="Path to server configuration file"
    )
    parser.add_argument(
        "--config-path",
        type=str,
        help="Path to guardrails configuration directory (overrides config file)"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Server port (overrides config file)"
    )

    args = parser.parse_args()

    # Load configuration
    if Path(args.config).exists():
        config = GuardrailsConfig.from_yaml(args.config)
    else:
        config = GuardrailsConfig()

    # Override with command line arguments
    if args.config_path:
        config.config_path = Path(args.config_path)
    if args.port:
        config.port = args.port

    # Create and start server
    server = GuardrailsServer(config)
    server.start()


if __name__ == "__main__":
    main()
