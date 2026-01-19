"""Configuration management for NeMo Guardrails in CAI."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml


@dataclass
class GuardrailsConfig:
    """Configuration for NeMo Guardrails server.

    Attributes:
        config_path: Path to guardrails configuration directory
        host: Server host address
        port: Server port (default: 8080 for CAI compatibility, overridden by CDSW_APP_PORT in CAI)
        llm_provider: LLM provider (openai, huggingface, etc.)
        llm_model: LLM model name
        llm_api_key: API key for LLM provider
        llm_api_base: Base URL for LLM API
        streaming: Enable streaming responses
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        cors_origins: List of allowed CORS origins
        additional_config: Additional configuration parameters
    """

    config_path: Path = field(default_factory=lambda: Path("config"))
    host: str = "0.0.0.0"
    port: int = 8080  # Default port for CAI Applications
    llm_provider: str = "openai"
    llm_model: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_api_base: Optional[str] = None
    streaming: bool = True
    log_level: str = "INFO"
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    additional_config: Dict[str, Any] = field(default_factory=dict)
    local_models: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # Local model configurations

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "GuardrailsConfig":
        """Load configuration from YAML file.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            GuardrailsConfig instance
        """
        with open(yaml_path, "r") as f:
            config_dict = yaml.safe_load(f)

        # Extract relevant fields
        config_path = config_dict.get("config_path", "config")
        server_config = config_dict.get("server", {})
        llm_config = config_dict.get("llm", {})
        local_models_config = config_dict.get("local_models", {})

        return cls(
            config_path=Path(config_path),
            host=server_config.get("host", "0.0.0.0"),
            port=server_config.get("port", 8080),  # Default port for CAI Applications
            llm_provider=llm_config.get("provider", "openai"),
            llm_model=llm_config.get("model"),
            llm_api_key=llm_config.get("api_key"),
            llm_api_base=llm_config.get("api_base"),
            streaming=server_config.get("streaming", True),
            log_level=server_config.get("log_level", "INFO"),
            cors_origins=server_config.get("cors_origins", ["*"]),
            additional_config=config_dict.get("additional_config", {}),
            local_models=local_models_config,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Configuration as dictionary
        """
        return {
            "config_path": str(self.config_path),
            "server": {
                "host": self.host,
                "port": self.port,
                "streaming": self.streaming,
                "log_level": self.log_level,
                "cors_origins": self.cors_origins,
            },
            "llm": {
                "provider": self.llm_provider,
                "model": self.llm_model,
                "api_key": self.llm_api_key,
                "api_base": self.llm_api_base,
            },
            "additional_config": self.additional_config,
            "local_models": self.local_models,
        }

    def save(self, yaml_path: str) -> None:
        """Save configuration to YAML file.

        Args:
            yaml_path: Path to save YAML configuration
        """
        with open(yaml_path, "w") as f:
            yaml.safe_dump(self.to_dict(), f, default_flow_style=False)
