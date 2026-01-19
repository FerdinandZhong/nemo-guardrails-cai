#!/usr/bin/env python3
"""
Standalone model service for hosting ML models in CAI.

This script allows you to run classification models (e.g., BERT for jailbreak detection)
as a separate service in CAI, which can then be used by the guardrails server.

Usage:
    # Run as a standalone FastAPI service
    python model_service.py --model protectai/deberta-v3-base-prompt-injection-v2 \
                           --port 8081 \
                           --device cpu

    # In CAI, CDSW_APP_PORT will be used automatically
    python model_service.py --model unitary/toxic-bert
"""

import argparse
import logging
import os
from typing import Dict, List, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from nemo_guardrails_cai.models.registry import ModelRegistry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Local Model Service",
    description="Standalone service for hosting ML models for guardrails",
    version="0.1.0"
)

# Global model registry
registry = ModelRegistry()


class PredictionRequest(BaseModel):
    """Request model for predictions."""
    texts: List[str]
    model_name: str = "default"


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    predictions: List[Dict[str, Any]]
    model_name: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    models: Dict[str, Any]


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check service health and model status."""
    health = registry.health_check()
    return {
        "status": "healthy" if health["total_models"] > 0 else "no_models_loaded",
        "models": health["models"]
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Run prediction on texts using specified model.

    Args:
        request: Prediction request containing texts and model name

    Returns:
        Prediction results

    Raises:
        HTTPException: If model not found or prediction fails
    """
    try:
        model = registry.get_model(request.model_name)
        if model is None:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{request.model_name}' not found"
            )

        if not model.is_loaded():
            raise HTTPException(
                status_code=503,
                detail=f"Model '{request.model_name}' is not loaded"
            )

        # Run predictions
        predictions = model.predict(request.texts)

        return {
            "predictions": predictions,
            "model_name": request.model_name
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """List all registered models."""
    return registry.list_models()


def main():
    """Main entry point for model service."""
    parser = argparse.ArgumentParser(
        description="Local Model Service for NeMo Guardrails"
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="HuggingFace model name or path to local model"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="default",
        help="Name to register the model under (default: 'default')"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda", "mps"],
        help="Device to run model on (default: cpu)"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to run service on (default: from CDSW_APP_PORT or 8081)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Classification threshold (default: 0.5)"
    )
    parser.add_argument(
        "--labels",
        type=str,
        nargs="+",
        default=["safe", "unsafe"],
        help="Label names for classification (default: safe unsafe)"
    )

    args = parser.parse_args()

    # Determine port
    port = args.port
    if port is None:
        port = int(os.environ.get("CDSW_APP_PORT", 8081))

    logger.info("=" * 70)
    logger.info("Starting Local Model Service")
    logger.info("=" * 70)
    logger.info(f"Model: {args.model}")
    logger.info(f"Model Name: {args.model_name}")
    logger.info(f"Device: {args.device}")
    logger.info(f"Port: {port}")
    logger.info(f"Threshold: {args.threshold}")
    logger.info(f"Labels: {args.labels}")

    # Load model
    try:
        logger.info("Loading model...")
        registry.register_model(
            name=args.model_name,
            model_type="huggingface",
            config={
                "model_name": args.model,
                "device": args.device,
                "task_type": "classification",
                "labels": args.labels,
                "threshold": args.threshold,
                "batch_size": 1,
                "max_length": 512,
            },
            auto_load=True
        )
        logger.info("Model loaded successfully")

    except Exception as e:
        logger.error(f"Failed to load model: {e}", exc_info=True)
        return 1

    # Start service
    logger.info(f"Starting service on {args.host}:{port}")
    logger.info("=" * 70)

    uvicorn.run(
        app,
        host=args.host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
