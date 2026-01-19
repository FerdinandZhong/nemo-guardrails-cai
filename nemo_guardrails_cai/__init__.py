"""
NVIDIA NeMo Guardrails integration for Cloudera AI.

This package provides a production-ready deployment solution for running
NVIDIA NeMo Guardrails in Cloudera Machine Learning (CML) environments.
"""

__version__ = "0.1.0"
__author__ = "Cloudera AI Team"
__license__ = "Apache-2.0"

from nemo_guardrails_cai.server import GuardrailsServer
from nemo_guardrails_cai.config import GuardrailsConfig

__all__ = [
    "GuardrailsServer",
    "GuardrailsConfig",
]
