#!/usr/bin/env python3
"""
Demo script for using mcp_sdk in Augment

This demonstrates how to use the SDK as function calls in Augment.
"""

import os
import sys

# Add mcp_sdk to path
sys.path.insert(0, os.path.dirname(__file__))

from function_interface import ai_chat, ai_consensus

# Set API keys (in real usage, use environment variables)
os.environ["OPENROUTER_API_KEY"] = "your_openrouter_api_key_here"

def demo_code_review():
    """Demo: AI code review với consensus."""
    print("🔍 Demo: AI Code Review")
    print("=" * 40)
    
    code = """
def calculate_factorial(n):
    if n == 0:
        return 1
    else:
        return n * calculate_factorial(n-1)
"""
    
    prompt = f"Review this Python code and suggest improvements:\n\n{code}"
    
    result = ai_consensus(prompt, ["deepseek/deepseek-r1"])
    
    if result['success']:
        print("📝 Code Review:")
        print(result['consensus'])
    else:
        print(f"❌ Error: {result['error']}")
    
    return result

def demo_interactive_assistant():
    """Demo: Interactive coding assistant với context."""
    print("\n💬 Demo: Interactive Assistant")
    print("=" * 40)
    print("(Type 'exit' to quit)")
    
    history = []
    
    # Simulate some interactions
    interactions = [
        "I'm working on a Python web API",
        "What framework should I use?", 
        "How do I handle authentication?",
        "exit"
    ]
    
    for user_input in interactions:
        print(f"\nYou: {user_input}")
        
        if user_input.lower() in ['exit', 'quit']:
            print("👋 Goodbye!")
            break
            
        result = ai_chat(user_input, "deepseek/deepseek-r1", history)
        
        if result['success']:
            print(f"AI: {result['response']}")
            history = result['history']
            print(f"(Context: {result['turn_count']} turns)")
        else:
            print(f"❌ Error: {result['error']}")
    
    return history

def demo_multi_model_consensus():
    """Demo: Multi-model consensus for important decisions."""
    print("\n🤝 Demo: Multi-Model Consensus")
    print("=" * 40)
    
    question = "Should I use microservices or monolith architecture for a new startup?"
    
    # Use multiple free models for consensus
    models = [
        "deepseek/deepseek-r1",
        "meta-llama/llama-3.2-3b-instruct:free"
    ]
    
    print(f"Question: {question}")
    print(f"Consulting models: {models}")
    
    result = ai_consensus(question, models)
    
    if result['success']:
        print("\n🎯 Consensus Decision:")
        print(result['consensus'])
        print(f"\n📊 Based on {result['model_count']} models")
    else:
        print(f"❌ Error: {result['error']}")
    
    return result

def demo_error_handling():
    """Demo: Error handling và fallback."""
    print("\n⚠️  Demo: Error Handling")
    print("=" * 40)
    
    # Try invalid model first
    print("Trying invalid model...")
    result = ai_chat("Hello", "invalid-model-name")
    
    if not result['success']:
        print(f"❌ Expected error: {result['error']}")
        
        # Fallback to working model
        print("Falling back to working model...")
        result = ai_chat("Hello", "deepseek/deepseek-r1")
        
        if result['success']:
            print(f"✅ Fallback success: {result['response']}")
        else:
            print(f"❌ Fallback failed: {result['error']}")
    
    return result

# Augment Integration Functions
def augment_ai_chat(prompt: str, model: str = "deepseek/deepseek-r1", context: list = None):
    """
    Augment-friendly AI chat function.
    
    Args:
        prompt: User message
        model: AI model to use
        context: Previous conversation context
    
    Returns:
        dict: Response with success status and content
    """
    return ai_chat(prompt, model, context)

def augment_ai_consensus(question: str, models: list = None):
    """
    Augment-friendly consensus function.
    
    Args:
        question: Question to get consensus on
        models: List of models to consult
    
    Returns:
        dict: Consensus response with metadata
    """
    if models is None:
        models = ["deepseek/deepseek-r1", "meta-llama/llama-3.2-3b-instruct:free"]
    
    return ai_consensus(question, models)

def main():
    """Run all demos."""
    print("🚀 MCP SDK Demo for Augment")
    print("=" * 50)
    
    try:
        # Run demos
        demo_code_review()
        demo_interactive_assistant()
        demo_multi_model_consensus()
        demo_error_handling()
        
        print("\n✅ All demos completed successfully!")
        
        # Show integration info
        print("\n" + "=" * 50)
        print("📖 Integration in Augment:")
        print("""
# Import functions
from augment_demo import augment_ai_chat, augment_ai_consensus

# Simple chat
result = augment_ai_chat("Explain async/await in Python")
print(result['response'])

# Multi-turn conversation
context = []
result1 = augment_ai_chat("I'm building a REST API", context=context)
result2 = augment_ai_chat("How do I add rate limiting?", context=result1['history'])

# Get consensus on architecture decisions
result = augment_ai_consensus("Should I use PostgreSQL or MongoDB?")
print(result['consensus'])
        """)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
