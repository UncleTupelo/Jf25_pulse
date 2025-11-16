#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for You.com API integration
Agent: Joef-JR-API
Agent ID: 76e9f5ab-fd40-4dc8-b88f-5ceb3664d170
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from opencontext.llm.youcom_client import YouComClient


def test_youcom_api():
    """Test the You.com API integration"""

    # Get API key from environment
    api_key = os.getenv("YOUCOM_API_KEY")

    if not api_key:
        print("❌ Error: YOUCOM_API_KEY environment variable not set")
        print("\nPlease set your API key:")
        print("  export YOUCOM_API_KEY='ydc-sk-8f86...your-full-key...'")
        return False

    if api_key == "ydc-sk-8f86...ab" or "..." in api_key:
        print("❌ Error: Please replace the example API key with your full key")
        print("\nYour API key should look like:")
        print("  ydc-sk-8f86xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        return False

    print("🔧 Testing You.com API Integration")
    print(f"   Agent: Joef-JR-API")
    print(f"   Agent ID: 76e9f5ab-fd40-4dc8-b88f-5ceb3664d170")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
    print()

    try:
        # Initialize client
        client = YouComClient(api_key=api_key)
        print("✓ Client initialized successfully")

        # Test agent run
        print("\n📤 Sending test request to Joef-JR-API...")
        test_input = "Hello! Can you tell me what you can do?"

        result = client.run_agent(
            agent_id="76e9f5ab-fd40-4dc8-b88f-5ceb3664d170",
            input_text=test_input,
            stream=False
        )

        print("✓ Request successful!")
        print("\n📥 Response:")
        print("-" * 60)
        print(result)
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease check:")
        print("  1. Your API key is correct")
        print("  2. The agent ID is valid")
        print("  3. You have internet connection")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("You.com API Test - Joef-JR-API")
    print("=" * 60)
    print()

    success = test_youcom_api()

    print()
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed - see errors above")
    print("=" * 60)

    sys.exit(0 if success else 1)
