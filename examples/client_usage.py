#!/usr/bin/env python3
"""
Client usage example for NeMo Guardrails.

This example shows how to interact with a deployed guardrails server
using the OpenAI Python client.
"""

from openai import OpenAI


def main():
    """Main example function."""
    print("=" * 60)
    print("NeMo Guardrails Client Usage Example")
    print("=" * 60)

    # Connect to guardrails server
    # For local server:
    base_url = "http://localhost:8000/v1"

    # For CML deployed server:
    # base_url = "https://guardrails-xyz.ml.example.cloudera.site/v1"

    print(f"\n🔌 Connecting to: {base_url}")

    client = OpenAI(
        base_url=base_url,
        api_key="dummy"  # Not required for local deployment
    )

    # Example 1: Simple chat completion
    print(f"\n📝 Example 1: Simple Chat Completion")
    print("-" * 60)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, how are you?"}
            ]
        )

        print(f"User: Hello, how are you?")
        print(f"Bot: {response.choices[0].message.content}")

    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Multi-turn conversation
    print(f"\n📝 Example 2: Multi-turn Conversation")
    print("-" * 60)

    messages = [
        {"role": "user", "content": "What is machine learning?"},
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        print(f"User: {messages[0]['content']}")
        print(f"Bot: {response.choices[0].message.content}")

        # Add bot response to conversation
        messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })

        # Ask follow-up question
        messages.append({
            "role": "user",
            "content": "Can you give me an example?"
        })

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        print(f"\nUser: {messages[-1]['content']}")
        print(f"Bot: {response.choices[0].message.content}")

    except Exception as e:
        print(f"Error: {e}")

    # Example 3: Testing guardrails (off-topic question)
    print(f"\n📝 Example 3: Testing Guardrails")
    print("-" * 60)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "What do you think about politics?"}
            ]
        )

        print(f"User: What do you think about politics?")
        print(f"Bot: {response.choices[0].message.content}")
        print(f"\n💡 Notice: The guardrail should prevent off-topic discussion")

    except Exception as e:
        print(f"Error: {e}")

    print(f"\n" + "=" * 60)


if __name__ == "__main__":
    main()
