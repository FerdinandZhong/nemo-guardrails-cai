"""HuggingFace model service implementation."""

import logging
from typing import Any, Dict, List, Optional
import torch

from nemo_guardrails_cai.models.base import BaseModelService

logger = logging.getLogger(__name__)


class HuggingFaceModelService(BaseModelService):
    """HuggingFace model service for PyTorch/Transformers models.

    Supports:
    - BERT-based models for classification (jailbreak detection, toxicity, etc.)
    - DistilBERT, RoBERTa, and other transformer models
    - Custom fine-tuned models

    Example models:
    - unitary/toxic-bert (toxicity detection)
    - textattack/bert-base-uncased-SST-2 (sentiment)
    - Custom jailbreak detection models
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize HuggingFace model service.

        Args:
            config: Configuration dictionary containing:
                - model_name: HuggingFace model name or local path
                - device: 'cpu', 'cuda', or 'mps'
                - task_type: 'classification', 'ner', etc.
                - labels: List of label names (optional)
                - use_fast_tokenizer: Whether to use fast tokenizer (default: True)
        """
        super().__init__(config)
        self.task_type = config.get("task_type", "classification")
        self.labels = config.get("labels", ["safe", "unsafe"])
        self.use_fast_tokenizer = config.get("use_fast_tokenizer", True)
        self._pipeline = None

    def load(self) -> None:
        """Load the HuggingFace model and tokenizer."""
        try:
            from transformers import (
                AutoTokenizer,
                AutoModelForSequenceClassification,
                pipeline
            )

            logger.info(f"Loading HuggingFace model: {self.model_name}")

            # Determine device
            if self.device == "cuda" and torch.cuda.is_available():
                device = 0  # First GPU
                logger.info("Using CUDA device")
            elif self.device == "mps" and torch.backends.mps.is_available():
                device = "mps"
                logger.info("Using MPS device (Apple Silicon)")
            else:
                device = -1  # CPU
                logger.info("Using CPU device")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                use_fast=self.use_fast_tokenizer
            )
            logger.info("Tokenizer loaded successfully")

            # Load model
            if self.task_type == "classification":
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name
                )
                logger.info("Classification model loaded successfully")

                # Create pipeline for easier inference
                self._pipeline = pipeline(
                    "text-classification",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=device,
                    max_length=self.max_length,
                    truncation=True
                )
                logger.info("Pipeline created successfully")

            else:
                raise ValueError(f"Unsupported task type: {self.task_type}")

            logger.info(f"Model {self.model_name} loaded successfully on {device}")

        except ImportError:
            logger.error(
                "transformers and torch are required for HuggingFace models. "
                "Install with: pip install transformers torch"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise

    def predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Run prediction on a batch of texts.

        Args:
            texts: List of input texts

        Returns:
            List of prediction results
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load() first.")

        try:
            # Run inference
            results = self._pipeline(texts, batch_size=self.batch_size)

            # Process results
            predictions = []
            for result in results:
                # Handle different output formats
                if isinstance(result, list):
                    # Multiple labels returned
                    result = result[0]

                label = result.get("label", "LABEL_0")
                score = result.get("score", 0.0)

                # Map labels to meaningful names
                label_name = self._map_label(label)

                # Determine if content is safe
                is_safe = self._determine_safety(label_name, score)

                predictions.append({
                    "label": label_name,
                    "score": float(score),
                    "is_safe": is_safe,
                    "raw_label": label,
                    "threshold": self.threshold
                })

            return predictions

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

    def _map_label(self, raw_label: str) -> str:
        """Map raw model labels to meaningful names.

        Args:
            raw_label: Raw label from model (e.g., 'LABEL_0', 'toxic')

        Returns:
            Mapped label name
        """
        # Handle generic LABEL_X format
        if raw_label.startswith("LABEL_"):
            try:
                idx = int(raw_label.split("_")[1])
                if idx < len(self.labels):
                    return self.labels[idx]
            except (ValueError, IndexError):
                pass

        # Return as-is if already meaningful
        return raw_label.lower()

    def _determine_safety(self, label: str, score: float) -> bool:
        """Determine if content is safe based on label and score.

        Args:
            label: Predicted label
            score: Confidence score

        Returns:
            True if content is safe, False otherwise
        """
        # Labels that indicate unsafe content
        unsafe_labels = {
            "unsafe", "toxic", "jailbreak", "harmful",
            "negative", "attack", "malicious"
        }

        # Check if label indicates unsafe content
        is_unsafe_label = label.lower() in unsafe_labels

        # If unsafe label with high confidence, mark as unsafe
        if is_unsafe_label and score > self.threshold:
            return False

        # Otherwise, consider safe
        return True

    def set_labels(self, labels: List[str]) -> None:
        """Update label mapping.

        Args:
            labels: List of label names in order
        """
        self.labels = labels
        logger.info(f"Updated labels to: {labels}")

    def set_threshold(self, threshold: float) -> None:
        """Update classification threshold.

        Args:
            threshold: New threshold value (0-1)
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")

        self.threshold = threshold
        logger.info(f"Updated threshold to: {threshold}")
