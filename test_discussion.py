#!/usr/bin/env python3
"""
Test script for AI Discussion MCP Server

This simulates how Augment would call the discussion tools.
"""

import asyncio
import os
import sys

# Add mcp_sdk to path
sys.path.insert(0, os.path.dirname(__file__))

from mcp_discussion_server import multi_model_discussion, handle_call_tool

# Set API keys
os.environ["OPENROUTER_API_KEY"] = "your_openrouter_api_key_here"
os.environ["GEMINI_API_KEY"] = "your_gemini_api_key_here"

async def test_discussion_tool():
    """Test the discuss tool like Augment would call it."""
    print("🎯 Testing AI Discussion Tool")
    print("=" * 60)
    
    # Simulate Augment calling the discuss tool
    arguments = {
        "topic": "Should I use React or Vue.js for my startup frontend?",
        "models": ["deepseek/deepseek-r1"],  # Use only working model for demo
        "include_claude": True
    }
    
    print(f"📝 Topic: {arguments['topic']}")
    print(f"🤖 Models: {arguments['models']}")
    print(f"🧠 Include Claude: {arguments['include_claude']}")
    print("\n" + "=" * 60)
    
    try:
        # Call the tool handler
        result = await handle_call_tool("discuss", arguments)
        
        # Print the result
        print(result[0].text)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_chat_tool():
    """Test the simple chat tool."""
    print("\n" + "=" * 60)
    print("💬 Testing Simple Chat Tool")
    print("=" * 60)
    
    arguments = {
        "message": "Explain the difference between async and sync programming in 2 sentences",
        "model": "deepseek/deepseek-r1"
    }
    
    print(f"💭 Message: {arguments['message']}")
    print(f"🤖 Model: {arguments['model']}")
    print("\n" + "-" * 40)
    
    try:
        result = await handle_call_tool("chat", arguments)
        print(result[0].text)
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_consensus_tool():
    """Test the consensus tool."""
    print("\n" + "=" * 60)
    print("🤝 Testing Consensus Tool")
    print("=" * 60)
    
    arguments = {
        "question": "What's the best approach for handling user authentication in a web app?",
        "models": ["deepseek/deepseek-r1"]
    }
    
    print(f"❓ Question: {arguments['question']}")
    print(f"🤖 Models: {arguments['models']}")
    print("\n" + "-" * 40)
    
    try:
        result = await handle_call_tool("consensus", arguments)
        print(result[0].text)
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def demo_augment_scenarios():
    """Demo scenarios that would happen in Augment."""
    print("\n" + "=" * 60)
    print("🚀 Demo: Augment Usage Scenarios")
    print("=" * 60)
    
    scenarios = [
        {
            "user_input": "Hãy thảo luận về Python vs JavaScript cho backend",
            "tool_call": {
                "name": "discuss",
                "arguments": {
                    "topic": "Python vs JavaScript cho backend development",
                    "models": ["deepseek/deepseek-r1"],
                    "include_claude": True
                }
            }
        },
        {
            "user_input": "Chat với AI về best practices cho REST API",
            "tool_call": {
                "name": "chat", 
                "arguments": {
                    "message": "What are the top 5 best practices for designing REST APIs?",
                    "model": "deepseek/deepseek-r1"
                }
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📱 Scenario {i}:")
        print(f"User: {scenario['user_input']}")
        print(f"Tool Call: {scenario['tool_call']['name']}({scenario['tool_call']['arguments']})")
        print("\n🤖 AI Response:")
        print("-" * 40)
        
        try:
            result = await handle_call_tool(
                scenario['tool_call']['name'],
                scenario['tool_call']['arguments']
            )
            
            # Show first 200 chars of response
            response = result[0].text
            if len(response) > 200:
                print(response[:200] + "...")
                print(f"\n[Full response: {len(response)} characters]")
            else:
                print(response)
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 40)

async def main():
    """Run all tests."""
    print("🧪 AI Discussion MCP Server Test Suite")
    print("=" * 60)
    
    try:
        # Test individual tools
        await test_discussion_tool()
        await test_chat_tool() 
        await test_consensus_tool()
        
        # Demo Augment scenarios
        await demo_augment_scenarios()
        
        print("\n✅ All tests completed!")
        
        # Show usage summary
        print("\n" + "=" * 60)
        print("📖 Usage Summary for Augment:")
        print("""
1. Add MCP server to Augment config
2. User types: "Thảo luận về X giữa r1 và gemini"
3. Augment calls: discuss(topic="X", models=["deepseek/deepseek-r1", "gemini-1.5-flash"])
4. Get multi-model analysis with synthesis
5. Present formatted result to user

Available tools:
- discuss: Multi-model discussion with synthesis
- chat: Simple chat with specific model  
- consensus: Multi-model consensus opinion

Ready for Augment integration! 🚀
        """)
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
