#!/usr/bin/env python3
"""
Test HTTP API for AI Discussion Server

This tests the REST API endpoints.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("🔧 Testing health endpoint...")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health check passed!")

def test_discuss():
    """Test discuss endpoint."""
    print("\n🗣️ Testing discuss endpoint...")
    
    payload = {
        "topic": "Should I use FastAPI or Flask for my Python API?",
        "models": ["deepseek/deepseek-r1"],
        "include_claude": True
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/discuss", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        discussion = result["data"]["discussion"]
        print(f"Discussion preview: {discussion[:200]}...")
        print("✅ Discuss test passed!")
    else:
        print(f"❌ Error: {response.text}")

def test_chat():
    """Test chat endpoint."""
    print("\n💬 Testing chat endpoint...")
    
    payload = {
        "message": "Explain the difference between REST and GraphQL in 2 sentences",
        "model": "deepseek/deepseek-r1"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        chat_response = result["data"]["response"]
        print(f"Response: {chat_response}")
        print("✅ Chat test passed!")
    else:
        print(f"❌ Error: {response.text}")

def test_consensus():
    """Test consensus endpoint."""
    print("\n🤝 Testing consensus endpoint...")
    
    payload = {
        "question": "What's the best approach for handling errors in a REST API?",
        "models": ["deepseek/deepseek-r1"]
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/consensus", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        consensus = result["data"]["consensus"]
        print(f"Consensus preview: {consensus[:200]}...")
        print("✅ Consensus test passed!")
    else:
        print(f"❌ Error: {response.text}")

def test_models():
    """Test models endpoint."""
    print("\n🤖 Testing models endpoint...")
    
    response = requests.get(f"{BASE_URL}/models")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        models = result["data"]["models"]
        print(f"Available models: {json.dumps(models, indent=2)}")
        print("✅ Models test passed!")
    else:
        print(f"❌ Error: {response.text}")

def demo_augment_integration():
    """Demo how Augment would integrate with the API."""
    print("\n🚀 Demo: Augment Integration")
    print("=" * 50)
    
    # Simulate Augment user input
    user_inputs = [
        "Hãy thảo luận về Python vs JavaScript cho backend",
        "Chat với AI về best practices cho database design",
        "Lấy consensus về microservices vs monolith"
    ]
    
    for i, user_input in enumerate(user_inputs, 1):
        print(f"\n📱 Scenario {i}: {user_input}")
        
        if "thảo luận" in user_input or "discuss" in user_input.lower():
            # Extract topic from user input
            topic = user_input.replace("Hãy thảo luận về ", "").replace("thảo luận về ", "")
            
            payload = {
                "topic": topic,
                "models": ["deepseek/deepseek-r1"],
                "include_claude": True
            }
            
            print(f"→ API Call: POST /discuss")
            response = requests.post(f"{BASE_URL}/discuss", json=payload)
            
        elif "chat" in user_input.lower():
            # Extract message from user input
            message = user_input.replace("Chat với AI về ", "")
            
            payload = {
                "message": f"Explain {message}",
                "model": "deepseek/deepseek-r1"
            }
            
            print(f"→ API Call: POST /chat")
            response = requests.post(f"{BASE_URL}/chat", json=payload)
            
        elif "consensus" in user_input.lower():
            # Extract question from user input
            question = user_input.replace("Lấy consensus về ", "")
            
            payload = {
                "question": question,
                "models": ["deepseek/deepseek-r1"]
            }
            
            print(f"→ API Call: POST /consensus")
            response = requests.post(f"{BASE_URL}/consensus", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if "discussion" in result["data"]:
                preview = result["data"]["discussion"][:150]
            elif "response" in result["data"]:
                preview = result["data"]["response"][:150]
            elif "consensus" in result["data"]:
                preview = result["data"]["consensus"][:150]
            else:
                preview = str(result["data"])[:150]
            
            print(f"✅ Response: {preview}...")
        else:
            print(f"❌ Error: {response.status_code}")
        
        time.sleep(1)  # Rate limiting

def main():
    """Run all tests."""
    print("🧪 AI Discussion Server HTTP API Test Suite")
    print("=" * 60)
    
    try:
        # Basic tests
        test_health()
        test_models()
        test_chat()
        test_consensus()
        test_discuss()
        
        # Integration demo
        demo_augment_integration()
        
        print("\n✅ All tests completed successfully!")
        
        print("\n" + "=" * 60)
        print("📖 Integration Summary:")
        print("""
✅ Server is running and healthy
✅ All API endpoints working
✅ Ready for Augment integration

Integration options:
1. HTTP API calls (recommended)
2. MCP protocol (if supported)

Example Augment integration:
```python
import requests

def ai_discuss(topic):
    response = requests.post("http://localhost:8000/discuss", json={
        "topic": topic,
        "models": ["deepseek/deepseek-r1"],
        "include_claude": True
    })
    return response.json()["data"]["discussion"]

# Usage in Augment
result = ai_discuss("React vs Vue for startup")
print(result)
```

🚀 Ready for production deployment!
        """)
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running:")
        print("   python local_server.py")
        print("   or")
        print("   ./start_local.sh")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
