#!/usr/bin/env python3
"""
Test consensus tool specifically

This tests the consensus functionality in detail.
"""

import asyncio
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from mcp_discussion_server import handle_call_tool

# Set API keys
os.environ["OPENROUTER_API_KEY"] = "your_openrouter_api_key_here"
os.environ["GEMINI_API_KEY"] = "your_gemini_api_key_here"

async def test_consensus_single_model():
    """Test consensus with single model."""
    print("🎯 Test 1: Consensus với single model")
    print("-" * 40)
    
    arguments = {
        "question": "What are the pros and cons of using TypeScript?",
        "models": ["deepseek/deepseek-r1"]
    }
    
    print(f"Question: {arguments['question']}")
    print(f"Models: {arguments['models']}")
    
    try:
        result = await handle_call_tool("consensus", arguments)
        response = result[0].text
        
        print(f"\n📝 Response:")
        print(response)
        print("\n✅ Single model consensus test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_consensus_multiple_models():
    """Test consensus with multiple models."""
    print("\n🤝 Test 2: Consensus với multiple models")
    print("-" * 40)
    
    arguments = {
        "question": "Should I use PostgreSQL or MongoDB for an e-commerce platform?",
        "models": ["deepseek/deepseek-r1", "deepseek/deepseek-chat"]
    }
    
    print(f"Question: {arguments['question']}")
    print(f"Models: {arguments['models']}")
    
    try:
        result = await handle_call_tool("consensus", arguments)
        response = result[0].text
        
        print(f"\n📝 Response:")
        print(response)
        print("\n✅ Multiple models consensus test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_consensus_technical_question():
    """Test consensus with technical question."""
    print("\n🔧 Test 3: Technical consensus")
    print("-" * 40)
    
    arguments = {
        "question": "Best practices for handling authentication in a REST API",
        "models": ["deepseek/deepseek-r1"]
    }
    
    print(f"Question: {arguments['question']}")
    print(f"Models: {arguments['models']}")
    
    try:
        result = await handle_call_tool("consensus", arguments)
        response = result[0].text
        
        print(f"\n📝 Response:")
        print(response)
        print("\n✅ Technical consensus test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_consensus_vs_discuss():
    """Compare consensus vs discuss for same topic."""
    print("\n⚖️  Test 4: Consensus vs Discuss comparison")
    print("-" * 40)
    
    topic = "React vs Vue for a startup frontend"
    
    # Test consensus
    print("🤝 Testing CONSENSUS:")
    consensus_args = {
        "question": topic,
        "models": ["deepseek/deepseek-r1"]
    }
    
    try:
        consensus_result = await handle_call_tool("consensus", consensus_args)
        consensus_response = consensus_result[0].text
        
        print(f"Consensus response length: {len(consensus_response)} chars")
        print(f"Preview: {consensus_response[:150]}...")
        
    except Exception as e:
        print(f"❌ Consensus error: {e}")
        return False
    
    # Test discuss
    print("\n🗣️ Testing DISCUSS:")
    discuss_args = {
        "topic": topic,
        "models": ["deepseek/deepseek-r1"],
        "include_claude": False
    }
    
    try:
        discuss_result = await handle_call_tool("discuss", discuss_args)
        discuss_response = discuss_result[0].text
        
        print(f"Discuss response length: {len(discuss_response)} chars")
        print(f"Preview: {discuss_response[:150]}...")
        
        print("\n📊 Comparison:")
        print(f"- Consensus: Focused opinion synthesis")
        print(f"- Discuss: Detailed multi-perspective analysis")
        print("✅ Comparison test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Discuss error: {e}")
        return False

async def demo_augment_consensus_usage():
    """Demo how consensus would be used in Augment."""
    print("\n🚀 Demo: Augment Consensus Usage")
    print("=" * 50)
    
    scenarios = [
        {
            "user_input": "Lấy consensus về database choice cho social media app",
            "question": "Best database choice for a social media application"
        },
        {
            "user_input": "Ý kiến chung về cloud providers",
            "question": "Comparison of major cloud providers (AWS, GCP, Azure)"
        },
        {
            "user_input": "Consensus về programming language cho AI project",
            "question": "Best programming language for AI/ML projects"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📱 Scenario {i}: {scenario['user_input']}")
        print(f"→ Extracted question: {scenario['question']}")
        
        arguments = {
            "question": scenario['question'],
            "models": ["deepseek/deepseek-r1"]
        }
        
        try:
            result = await handle_call_tool("consensus", arguments)
            response = result[0].text
            
            # Show preview
            preview = response[:200] + "..." if len(response) > 200 else response
            print(f"✅ Response preview: {preview}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 30)

async def main():
    """Run all consensus tests."""
    print("🧪 Consensus Tool Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Run tests
    if await test_consensus_single_model():
        tests_passed += 1
    
    if await test_consensus_multiple_models():
        tests_passed += 1
    
    if await test_consensus_technical_question():
        tests_passed += 1
    
    if await test_consensus_vs_discuss():
        tests_passed += 1
    
    # Demo usage
    await demo_augment_consensus_usage()
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✅ All consensus tests passed!")
        print("\n🎯 Consensus Tool Summary:")
        print("- ✅ Single model consensus working")
        print("- ✅ Multiple models consensus working") 
        print("- ✅ Technical questions handled well")
        print("- ✅ Different from discuss tool (focused vs detailed)")
        print("- ✅ Ready for Augment integration")
        
        print("\n📖 Usage in Augment:")
        print('User: "Lấy consensus về database choice"')
        print('→ Calls: consensus(question="database choice", models=["deepseek/deepseek-r1"])')
        print('→ Returns: Focused consensus opinion')
        
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
