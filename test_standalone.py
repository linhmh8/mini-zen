#!/usr/bin/env python3
"""
Test script for standalone AI Discussion Server

Verify everything works before using with Augment.
"""

import os
import sys
import asyncio

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all imports work."""
    print("📦 Testing imports...")
    
    try:
        import mcp_sdk
        print("✅ mcp_sdk imported")
        
        from mcp_discussion_server import multi_model_discussion, handle_call_tool
        print("✅ MCP server components imported")
        
        from function_interface import ai_chat, ai_consensus
        print("✅ Function interface imported")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test API key configuration."""
    print("\n🔑 Testing configuration...")
    
    # Load .env file if it exists
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Check API keys
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if openrouter_key and openrouter_key.startswith('sk-or-'):
        print("✅ OpenRouter API key found")
    else:
        print("⚠️  OpenRouter API key not found or invalid")
    
    if gemini_key and gemini_key.startswith('AIza'):
        print("✅ Gemini API key found")
    else:
        print("⚠️  Gemini API key not found or invalid")
    
    return bool(openrouter_key or gemini_key)

async def test_mcp_tools():
    """Test MCP tools functionality."""
    print("\n🛠️  Testing MCP tools...")
    
    try:
        from mcp_discussion_server import handle_call_tool
        
        # Test discuss tool
        print("Testing discuss tool...")
        result = await handle_call_tool("discuss", {
            "topic": "Quick test: Python vs JavaScript",
            "models": ["deepseek/deepseek-r1"],
            "include_claude": False
        })
        
        if result and len(result) > 0 and hasattr(result[0], 'text'):
            print("✅ Discuss tool working")
            return True
        else:
            print("❌ Discuss tool failed")
            return False
            
    except Exception as e:
        print(f"❌ MCP tools error: {e}")
        return False

def test_function_interface():
    """Test function interface."""
    print("\n🔧 Testing function interface...")
    
    try:
        from function_interface import ai_chat
        
        result = ai_chat("Say hello in one word", "deepseek/deepseek-r1")
        
        if result['success'] and result['response']:
            print("✅ Function interface working")
            print(f"Sample response: {result['response'][:50]}...")
            return True
        else:
            print(f"❌ Function interface failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Function interface error: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 AI Discussion Server Standalone Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please run: pip install -r requirements.txt")
        return False
    
    # Test configuration
    if not test_configuration():
        print("\n❌ Configuration test failed. Please check .env file")
        return False
    
    # Test MCP tools
    if not await test_mcp_tools():
        print("\n❌ MCP tools test failed")
        return False
    
    # Test function interface
    if not test_function_interface():
        print("\n❌ Function interface test failed")
        return False
    
    print("\n✅ All tests passed!")
    print("\n🎉 Server is ready for Augment integration!")
    print("\n📋 Next steps:")
    print("1. Copy this folder to a permanent location")
    print("2. Add MCP server config to Augment")
    print("3. Restart Augment")
    print("4. Test in Augment: 'Hãy thảo luận về React vs Vue'")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
