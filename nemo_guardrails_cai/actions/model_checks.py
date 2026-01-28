"""Custom actions for NeMo Guardrails using locally hosted models.

These actions integrate with the ModelRegistry to perform various checks
using locally hosted models in CAI.
"""

import logging
from typing import Optional

from nemo_guardrails_cai.models.registry import ModelRegistry

logger = logging.getLogger(__name__)


async def check_jailbreak_local(context: Optional[dict] = None) -> bool:
    """Check for jailbreak attempts using locally hosted model.

    This action can be used in guardrails flows like:
        $is_jailbreak = execute check_jailbreak_local

    Args:
        context: NeMo Guardrails context containing user message

    Returns:
        True if jailbreak detected (content is unsafe), False otherwise
    """
    try:
        # Get the user message from context
        if context is None:
            logger.warning("No context provided to check_jailbreak_local")
            return False

        user_message = context.get("user_message", "")
        if not user_message:
            logger.warning("No user message in context")
            return False

        logger.info(f"Checking for jailbreak: {user_message[:100]}...")

        # Get the jailbreak detection model from registry
        model_name = context.get("jailbreak_model", "jailbreak_detector")
        registry = ModelRegistry()
        model = registry.get_model(model_name)

        if model is None:
            logger.error(f"Jailbreak model '{model_name}' not found in registry")
            # Fail safe: allow the message if model not available
            return False

        # Run prediction
        result = model.predict_single(user_message)

        logger.info(f"Jailbreak check result: {result}")

        # Return True if jailbreak detected (content is unsafe)
        is_jailbreak = not result.get("is_safe", True)

        return is_jailbreak

    except Exception as e:
        logger.error(f"Error in check_jailbreak_local: {e}", exc_info=True)
        # Fail safe: allow the message if check fails
        return False


async def check_toxicity_local(context: Optional[dict] = None) -> bool:
    """Check for toxic content using locally hosted model.

    This action can be used in guardrails flows like:
        $is_toxic = execute check_toxicity_local

    Args:
        context: NeMo Guardrails context containing user message

    Returns:
        True if toxic content detected, False otherwise
    """
    try:
        # Get the user message from context
        if context is None:
            logger.warning("No context provided to check_toxicity_local")
            return False

        user_message = context.get("user_message", "")
        if not user_message:
            logger.warning("No user message in context")
            return False

        logger.info(f"Checking for toxicity: {user_message[:100]}...")

        # Get the toxicity detection model from registry
        model_name = context.get("toxicity_model", "toxicity_detector")
        registry = ModelRegistry()
        model = registry.get_model(model_name)

        if model is None:
            logger.error(f"Toxicity model '{model_name}' not found in registry")
            # Fail safe: allow the message if model not available
            return False

        # Run prediction
        result = model.predict_single(user_message)

        logger.info(f"Toxicity check result: {result}")

        # Return True if toxic content detected
        is_toxic = not result.get("is_safe", True)

        return is_toxic

    except Exception as e:
        logger.error(f"Error in check_toxicity_local: {e}", exc_info=True)
        # Fail safe: allow the message if check fails
        return False


async def check_with_local_model(
    model_name: str, text: Optional[str] = None, context: Optional[dict] = None
) -> dict:
    """Generic action to check text with any locally hosted model.

    This is a flexible action that can be used with any registered model:
        $result = execute check_with_local_model(model_name="my_model")

    Args:
        model_name: Name of the model in the registry
        text: Text to check (if None, uses user_message from context)
        context: NeMo Guardrails context

    Returns:
        Dictionary with prediction results:
            - is_safe: Boolean indicating if content is safe
            - score: Confidence score
            - label: Predicted label
    """
    try:
        # Get the text to check
        if text is None:
            if context is None:
                logger.warning("No text or context provided")
                return {"is_safe": True, "score": 0.0, "label": "unknown"}

            text = context.get("user_message", "")
            if not text:
                logger.warning("No text found in context")
                return {"is_safe": True, "score": 0.0, "label": "unknown"}

        logger.info(f"Checking with model '{model_name}': {text[:100]}...")

        # Get the model from registry
        registry = ModelRegistry()
        model = registry.get_model(model_name)

        if model is None:
            logger.error(f"Model '{model_name}' not found in registry")
            # Fail safe: return safe result if model not available
            return {"is_safe": True, "score": 0.0, "label": "model_not_found"}

        # Run prediction
        result = model.predict_single(text)

        logger.info(f"Check result: {result}")

        return result

    except Exception as e:
        logger.error(f"Error in check_with_local_model: {e}", exc_info=True)
        # Fail safe: return safe result if check fails
        return {"is_safe": True, "score": 0.0, "label": "error"}


# Register actions with NeMo Guardrails
# These will be available in Colang flows
def register_actions():
    """Register custom actions with NeMo Guardrails.

    Call this function when initializing the guardrails server.
    """
    from nemoguardrails import RailsConfig

    # Actions are automatically discovered by NeMo Guardrails
    # if they are defined in this module
    logger.info("Custom model check actions registered")
