"""Model registry for managing multiple locally hosted models."""

import logging
from typing import Any, Dict, Optional

from nemo_guardrails_cai.models.base import BaseModelService
from nemo_guardrails_cai.models.huggingface import HuggingFaceModelService

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Registry for managing multiple model services.

    This allows NeMo Guardrails to use different models for different checks:
    - Jailbreak detection model
    - Toxicity detection model
    - Hallucination detection model
    - Custom check models
    """

    _instance: Optional["ModelRegistry"] = None
    _models: Dict[str, BaseModelService] = {}

    def __new__(cls):
        """Singleton pattern to ensure one registry instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register_model(
        cls,
        name: str,
        model_type: str,
        config: Dict[str, Any],
        auto_load: bool = True
    ) -> BaseModelService:
        """Register a new model service.

        Args:
            name: Unique name for this model (e.g., 'jailbreak_detector')
            model_type: Type of model service ('huggingface', 'custom')
            config: Model configuration dictionary
            auto_load: Whether to load the model immediately

        Returns:
            Initialized model service

        Raises:
            ValueError: If model type is not supported
        """
        logger.info(f"Registering model '{name}' of type '{model_type}'")

        # Create model service based on type
        if model_type == "huggingface":
            model_service = HuggingFaceModelService(config)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

        # Load model if requested
        if auto_load:
            try:
                model_service.load()
                logger.info(f"Model '{name}' loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model '{name}': {e}")
                raise

        # Store in registry
        cls._models[name] = model_service
        logger.info(f"Model '{name}' registered successfully")

        return model_service

    @classmethod
    def get_model(cls, name: str) -> Optional[BaseModelService]:
        """Get a registered model service by name.

        Args:
            name: Name of the model

        Returns:
            Model service or None if not found
        """
        return cls._models.get(name)

    @classmethod
    def list_models(cls) -> Dict[str, Dict[str, Any]]:
        """List all registered models.

        Returns:
            Dictionary mapping model names to their info
        """
        return {
            name: {
                "type": model.__class__.__name__,
                "loaded": model.is_loaded(),
                "model_name": model.model_name,
                "device": model.device
            }
            for name, model in cls._models.items()
        }

    @classmethod
    def unregister_model(cls, name: str) -> bool:
        """Unregister and unload a model.

        Args:
            name: Name of the model to unregister

        Returns:
            True if model was unregistered, False if not found
        """
        if name in cls._models:
            model = cls._models[name]
            model.unload()
            del cls._models[name]
            logger.info(f"Model '{name}' unregistered")
            return True

        logger.warning(f"Model '{name}' not found in registry")
        return False

    @classmethod
    def unregister_all(cls) -> None:
        """Unregister all models."""
        for name in list(cls._models.keys()):
            cls.unregister_model(name)
        logger.info("All models unregistered")

    @classmethod
    def health_check(cls) -> Dict[str, Any]:
        """Check health status of all registered models.

        Returns:
            Health status dictionary
        """
        return {
            "total_models": len(cls._models),
            "models": {
                name: model.health_check()
                for name, model in cls._models.items()
            }
        }

    @classmethod
    def predict(cls, model_name: str, text: str) -> Dict[str, Any]:
        """Run prediction using a registered model.

        Args:
            model_name: Name of the model to use
            text: Input text

        Returns:
            Prediction result

        Raises:
            ValueError: If model not found
            RuntimeError: If model not loaded
        """
        model = cls.get_model(model_name)
        if model is None:
            raise ValueError(f"Model '{model_name}' not found in registry")

        if not model.is_loaded():
            raise RuntimeError(f"Model '{model_name}' is not loaded")

        return model.predict_single(text)

    @classmethod
    def load_from_config(cls, config: Dict[str, Any]) -> None:
        """Load multiple models from configuration.

        Args:
            config: Configuration dictionary with models section:
                models:
                  jailbreak_detector:
                    type: huggingface
                    model_name: "my-org/jailbreak-bert"
                    device: cuda
                    threshold: 0.7
                  toxicity_detector:
                    type: huggingface
                    model_name: "unitary/toxic-bert"
                    device: cpu
        """
        models_config = config.get("models", {})

        if not models_config:
            logger.warning("No models configured")
            return

        logger.info(f"Loading {len(models_config)} models from configuration")

        for name, model_config in models_config.items():
            try:
                model_type = model_config.pop("type", "huggingface")
                auto_load = model_config.pop("auto_load", True)

                cls.register_model(
                    name=name,
                    model_type=model_type,
                    config=model_config,
                    auto_load=auto_load
                )
            except Exception as e:
                logger.error(f"Failed to load model '{name}': {e}")
                # Continue loading other models
                continue

        logger.info(f"Successfully loaded {len(cls._models)} models")
