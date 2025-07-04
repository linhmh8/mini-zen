#!/usr/bin/env python3
"""
Test available models in mcp_sdk
"""

import os
import sys

# Add mcp_sdk to path
sys.path.insert(0, os.path.dirname(__file__))

import mcp_sdk
from mcp_sdk.core.provider_manager import list_available_models

# Set API keys
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"
os.environ["GEMINI_API_KEY"] = "your_gemini_api_key_here"

# Configure SDK
api_keys = {
    'openai': os.environ["OPENAI_API_KEY"],
    'gemini': os.environ["GEMINI_API_KEY"]
}

mcp_sdk.configure(api_keys)

# List available models
models = list_available_models()
print("Available models by provider:")
for provider, model_list in models.items():
    print(f"\n{provider}:")
    for model in model_list[:5]:  # Show first 5 models
        print(f"  - {model}")
    if len(model_list) > 5:
        print(f"  ... and {len(model_list) - 5} more")

# Test with a known model
print("\n" + "="*50)
print("Testing with known models...")

# Try OpenAI models
openai_models = ["o3-mini", "gpt-4o-mini", "o4-mini"]
for model in openai_models:
    try:
        response, history = mcp_sdk.chat("Hello", model)
        print(f"✅ {model}: {response[:50]}...")
        break
    except Exception as e:
        print(f"❌ {model}: {e}")

# Try Gemini models  
gemini_models = ["gemini-1.5-flash", "gemini-2.5-flash", "flash"]
for model in gemini_models:
    try:
        response, history = mcp_sdk.chat("Hello", model)
        print(f"✅ {model}: {response[:50]}...")
        break
    except Exception as e:
        print(f"❌ {model}: {e}")
