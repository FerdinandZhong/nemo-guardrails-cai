#!/usr/bin/env python3
"""
Simple test to verify the server is working.
Just makes one request to check if guardrails are responding.
"""

import requests
import json
import sys

def test_server():
    """Make a simple request to test the server."""

    url = "http://localhost:8080/v1/chat/completions"

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hello, can you tell me what 2+2 is?"}
        ]
    }

    print("Testing server at:", url)
    print("Sending request...")
    print()

    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print()

        if response.status_code == 200:
            data = response.json()
            if "messages" in data and len(data["messages"]) > 0:
                content = data["messages"][0].get("content", "")
                print("✅ Success!")
                print()
                print("Response:", content[:200])
                print()
                return 0
            else:
                print("❌ Unexpected response format")
                print(json.dumps(data, indent=2))
                return 1
        else:
            print("❌ Error response")
            print(response.text)
            return 1

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        print("Make sure the server is running:")
        print("  ./examples/local_test/run_with_conda.sh")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_server())
