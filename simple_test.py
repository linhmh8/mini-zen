#!/usr/bin/env python3
"""
Simple test with working models
"""

import os
import sys

# Add mcp_sdk to path
sys.path.insert(0, os.path.dirname(__file__))

from function_interface import ai_chat, ai_consensus

# Set API keys
os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"
os.environ["GEMINI_API_KEY"] = "your_gemini_api_key_here"
os.environ["OPENROUTER_API_KEY"] = "your_openrouter_api_key_here"

print("🚀 Simple Function Interface Test")
print("=" * 50)

# Test 1: Try with free/accessible models
print("💬 Test 1: Chat with free models")
try:
    # Try OpenRouter models (usually free or cheap)
    openrouter_models = [
        "deepseek/deepseek-r1",
        "deepseek/deepseek-chat",
        "google/gemini-flash-1.5",
        "meta-llama/llama-3.2-3b-instruct:free",
        "microsoft/phi-3-mini-128k-instruct:free"
    ]

    working_model = None
    for model in openrouter_models:
        print(f"Trying {model}...")
        result = ai_chat("Hello, say hi back", model)
        if result['success']:
            print(f"✅ {model}: {result['response'][:50]}...")
            working_model = model
            break
        else:
            print(f"❌ {model}: {result['error'][:100]}...")

    # Try Gemini models directly (should be free with API key)
    if not working_model:
        gemini_models = ["gemini-1.5-flash", "gemini-pro"]

        for model in gemini_models:
            print(f"Trying {model}...")
            result = ai_chat("Hello, say hi back", model)
            if result['success']:
                print(f"✅ {model}: {result['response'][:50]}...")
                working_model = model
                break
            else:
                print(f"❌ {model}: {result['error'][:100]}...")

except Exception as e:
    print(f"❌ Chat test failed: {e}")

# Test 2: Multi-turn conversation
print("\n🔄 Test 2: Multi-turn conversation")
try:
    # First turn - use a free model
    test_model = "deepseek/deepseek-r1"  # Free on OpenRouter
    result1 = ai_chat("My name is Bob", test_model)
    if result1['success']:
        print(f"First: {result1['response'][:50]}...")

        # Second turn
        result2 = ai_chat("What's my name?", test_model, result1['history'])
        if result2['success']:
            print(f"Second: {result2['response']}")
            if "Bob" in result2['response'] or "bob" in result2['response'].lower():
                print("✅ Context preserved!")
            else:
                print("⚠️  Context may not be preserved")
        else:
            print(f"❌ Second turn failed: {result2['error']}")
    else:
        print(f"❌ First turn failed: {result1['error']}")
        
except Exception as e:
    print(f"❌ Multi-turn test failed: {e}")

# Test 3: Single model consensus
print("\n🎯 Test 3: Single model consensus")
try:
    result = ai_consensus("What is Python?", ["deepseek/deepseek-r1"])
    if result['success']:
        print(f"✅ Consensus: {result['consensus'][:100]}...")
    else:
        print(f"❌ Consensus failed: {result['error']}")
        
except Exception as e:
    print(f"❌ Consensus test failed: {e}")

print("\n🎉 Simple test completed!")

# Show usage instructions
print("\n" + "="*50)
print("📖 Usage in Augment:")
print("""
# Import the function interface
from function_interface import ai_chat, ai_consensus

# Simple chat
result = ai_chat("Hello, how are you?", "gpt-3.5-turbo")
print(result['response'])

# Multi-turn conversation
result1 = ai_chat("My name is Alice", "gpt-3.5-turbo")
result2 = ai_chat("What's my name?", "gpt-3.5-turbo", result1['history'])
print(result2['response'])  # Should mention Alice

# Consensus from multiple models
result = ai_consensus("Pros and cons of Python", ["gpt-3.5-turbo", "gpt-4"])
print(result['consensus'])
""")
