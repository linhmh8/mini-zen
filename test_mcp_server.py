#!/usr/bin/env python3
"""
Test script for MCP SDK Server

This script tests the MCP server functionality by simulating tool calls.
"""

import asyncio
import json
import os
import sys

# Add mcp_sdk to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_mcp_server():
    """Test MCP server functionality."""
    print("🧪 Testing MCP SDK Server...")
    print("=" * 50)
    
    # Set environment variables
    os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"
    os.environ["GEMINI_API_KEY"] = "your_gemini_api_key_here"
    os.environ["OPENROUTER_API_KEY"] = "your_openrouter_api_key_here"
    
    # Import after setting env vars
    from mcp_server import handle_call_tool, handle_list_tools
    
    try:
        # Test 1: List tools
        print("📋 Test 1: List available tools")
        tools = await handle_list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")
        assert len(tools) == 3, f"Expected 3 tools, got {len(tools)}"
        print("✅ List tools test passed")
        
        # Test 2: Chat tool
        print("\n💬 Test 2: Chat tool")
        chat_args = {
            "prompt": "Hello, how are you?",
            "model": "gpt-4o-mini"
        }
        result = await handle_call_tool("chat", chat_args)
        response_data = json.loads(result[0].text)
        print(f"Chat response: {response_data['response'][:100]}...")
        assert "response" in response_data, "Response should contain 'response' field"
        assert "history" in response_data, "Response should contain 'history' field"
        print("✅ Chat tool test passed")
        
        # Test 3: Multi-turn conversation
        print("\n🔄 Test 3: Multi-turn conversation")
        # First turn
        first_args = {
            "prompt": "My name is Alice",
            "model": "gpt-4o-mini"
        }
        first_result = await handle_call_tool("chat", first_args)
        first_data = json.loads(first_result[0].text)
        
        # Second turn with history
        second_args = {
            "prompt": "What is my name?",
            "model": "gpt-4o-mini",
            "history": first_data["history"]
        }
        second_result = await handle_call_tool("chat", second_args)
        second_data = json.loads(second_result[0].text)
        
        print(f"Second response: {second_data['response']}")
        assert "Alice" in second_data['response'] or "alice" in second_data['response'].lower(), \
            "Should remember the name Alice"
        print("✅ Multi-turn conversation test passed")
        
        # Test 4: Consensus tool
        print("\n🤝 Test 4: Consensus tool")
        consensus_args = {
            "prompt": "What are the main benefits of Python?",
            "models": ["gpt-4o-mini"]  # Use single model for faster testing
        }
        consensus_result = await handle_call_tool("consensus", consensus_args)
        consensus_data = json.loads(consensus_result[0].text)
        print(f"Consensus: {consensus_data['consensus'][:100]}...")
        assert "consensus" in consensus_data, "Response should contain 'consensus' field"
        assert "python" in consensus_data['consensus'].lower(), "Should mention Python"
        print("✅ Consensus tool test passed")
        
        print("\n🎉 All MCP server tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
