#!/usr/bin/env python3
"""
Basic usage example for NeMo Guardrails CAI.

This example shows how to:
1. Create a guardrails configuration
2. Start a guardrails server
3. Make requests to the server
"""

import asyncio
from pathlib import Path
from nemo_guardrails_cai import GuardrailsServer, GuardrailsConfig


async def main():
    """Main example function."""
    print("=" * 60)
    print("NeMo Guardrails Basic Usage Example")
    print("=" * 60)

    # Create configuration
    config = GuardrailsConfig(
        config_path=Path("examples/config"),
        llm_model="gpt-3.5-turbo",
        port=8080,  # Default port for CAI
        log_level="INFO"
    )

    print(f"\n📝 Configuration:")
    print(f"  Config Path: {config.config_path}")
    print(f"  LLM Model: {config.llm_model}")
    print(f"  Port: {config.port}")

    # Create server
    print(f"\n🚀 Starting guardrails server...")
    server = GuardrailsServer(config)

    # In production, you would call server.start()
    # For this example, we'll just initialize the rails
    server.initialize_rails()

    print(f"\n✅ Server initialized successfully!")
    print(f"\n💡 You can now use the server:")
    print(f"  - Local: http://localhost:{config.port}")
    print(f"  - OpenAI compatible endpoint: http://localhost:{config.port}/v1")

    # Example usage
    print(f"\n📮 Example request:")
    prompt = "Hello, how can you help me?"

    try:
        response = await server.generate(prompt)
        print(f"\n  User: {prompt}")
        print(f"  Bot: {response}")
    except Exception as e:
        print(f"\n  Error: {e}")
        print(f"  Note: Make sure OPENAI_API_KEY is set in environment")

    print(f"\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
