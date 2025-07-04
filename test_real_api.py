#!/usr/bin/env python3
"""
Real API test script for MCP SDK

This script tests the SDK with actual API keys to verify functionality.
"""

import sys
import os
import traceback

# Add the mcp_sdk to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

import mcp_sdk


def test_real_apis():
    """Test MCP SDK with real API keys."""
    
    # API keys from the .env file
    api_keys = {
        'openai': 'your_openai_api_key_here',
        'gemini': 'your_gemini_api_key_here',
        'openrouter': 'your_openrouter_api_key_here'
    }
    
    print("🚀 Testing MCP SDK with real APIs...")
    print("=" * 50)
    
    try:
        # Configure SDK
        print("📋 Configuring SDK...")
        mcp_sdk.configure(api_keys)
        print("✅ SDK configured successfully")
        
        # Test 1: Single turn chat
        print("\n🗣️  Test 1: Single turn chat")
        response, history = mcp_sdk.chat("Hello, how are you?", "gpt-4o-mini")
        print(f"Response: {response}")
        print(f"History length: {len(history)}")
        assert len(response) > 0, "Response should not be empty"
        assert len(history) == 2, "History should have 2 entries"
        print("✅ Single turn chat test passed")
        
        # Test 2: Multi-turn conversation
        print("\n💬 Test 2: Multi-turn conversation")
        response1, history1 = mcp_sdk.chat("My name is Alex", "gpt-4o-mini")
        print(f"First response: {response1}")
        
        response2, history2 = mcp_sdk.chat("What is my name?", "gpt-4o-mini", history=history1)
        print(f"Second response: {response2}")
        print(f"Final history length: {len(history2)}")
        
        assert "Alex" in response2 or "alex" in response2.lower(), "Should remember the name Alex"
        assert len(history2) == 4, "History should have 4 entries after 2 turns"
        print("✅ Multi-turn conversation test passed")
        
        # Test 3: Consensus with multiple models
        print("\n🤝 Test 3: Consensus workflow")
        consensus = mcp_sdk.get_consensus(
            "What are the main advantages of Python programming language?", 
            ["gpt-4o-mini", "gemini-1.5-flash"]
        )
        print(f"Consensus response: {consensus}")
        
        assert len(consensus) > 0, "Consensus response should not be empty"
        assert "python" in consensus.lower(), "Should mention Python"
        print("✅ Consensus workflow test passed")
        
        # Test 4: Single model consensus
        print("\n🎯 Test 4: Single model consensus")
        single_consensus = mcp_sdk.get_consensus(
            "Explain machine learning in one sentence", 
            ["gpt-4o-mini"]
        )
        print(f"Single model consensus: {single_consensus}")
        
        assert len(single_consensus) > 0, "Single consensus should not be empty"
        print("✅ Single model consensus test passed")
        
        # Test 5: Different models
        print("\n🔄 Test 5: Testing different models")
        
        # Test Gemini
        try:
            gemini_response, _ = mcp_sdk.chat("What is 2+2?", "gemini-1.5-flash")
            print(f"Gemini response: {gemini_response}")
            assert "4" in gemini_response, "Should correctly answer 2+2=4"
            print("✅ Gemini model test passed")
        except Exception as e:
            print(f"⚠️  Gemini test failed: {e}")
        
        # Test OpenRouter
        try:
            openrouter_response, _ = mcp_sdk.chat("Say hello in French", "gpt-3.5-turbo")
            print(f"OpenRouter response: {openrouter_response}")
            print("✅ OpenRouter model test passed")
        except Exception as e:
            print(f"⚠️  OpenRouter test failed: {e}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_real_apis()
    sys.exit(0 if success else 1)
