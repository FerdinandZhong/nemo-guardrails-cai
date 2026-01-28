"""Base model service interface for locally hosted models."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseModelService(ABC):
    """Base class for model services.

    This defines the interface for locally hosted models that can be used
    for various checks (jailbreak detection, toxicity, etc.) in NeMo Guardrails.
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the model service.

        Args:
            config: Model configuration dictionary containing:
                - model_name: Name/path of the model
                - device: Device to run on ('cpu', 'cuda', 'mps')
                - batch_size: Batch size for inference
                - max_length: Maximum sequence length
                - threshold: Classification threshold (if applicable)
                - Additional model-specific parameters
        """
        self.config = config
        self.model_name = config.get("model_name")
        self.device = config.get("device", "cpu")
        self.batch_size = config.get("batch_size", 1)
        self.max_length = config.get("max_length", 512)
        self.threshold = config.get("threshold", 0.5)
        self.model = None
        self.tokenizer = None

        logger.info(f"Initializing {self.__class__.__name__} with config: {config}")

    @abstractmethod
    def load(self) -> None:
        """Load the model and tokenizer into memory.

        This should initialize self.model and self.tokenizer.
        """
        pass

    @abstractmethod
    def predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Run prediction on a batch of texts.

        Args:
            texts: List of input texts to classify/analyze

        Returns:
            List of prediction results, each containing:
                - score: Confidence score (0-1)
                - label: Predicted label/class
                - is_safe: Boolean indicating if content is safe (if applicable)
                - Additional model-specific fields
        """
        pass

    def predict_single(self, text: str) -> Dict[str, Any]:
        """Run prediction on a single text.

        Args:
            text: Input text

        Returns:
            Prediction result dictionary
        """
        return self.predict([text])[0]

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None

    def unload(self) -> None:
        """Unload the model from memory."""
        self.model = None
        self.tokenizer = None
        logger.info(f"Unloaded {self.__class__.__name__}")

    def health_check(self) -> Dict[str, Any]:
        """Check service health status.

        Returns:
            Health status dictionary
        """
        return {
            "service": self.__class__.__name__,
            "model_name": self.model_name,
            "device": self.device,
            "loaded": self.is_loaded(),
            "status": "healthy" if self.is_loaded() else "not_loaded",
        }
