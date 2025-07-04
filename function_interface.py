#!/usr/bin/env python3
"""
Function Interface for mcp_sdk

This module provides a simple function call interface that can be used
directly in Augment or other environments without MCP protocol overhead.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

# Add mcp_sdk to path
sys.path.insert(0, os.path.dirname(__file__))

import mcp_sdk

# Global configuration state
_configured = False

def ensure_configured():
    """Ensure SDK is configured with API keys."""
    global _configured
    if not _configured:
        # Try to configure from environment variables
        api_keys = {}
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key_here":
            api_keys['openai'] = openai_key
            
        gemini_key = os.getenv("GEMINI_API_KEY") 
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            api_keys['gemini'] = gemini_key
            
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key and openrouter_key != "your_openrouter_api_key_here":
            api_keys['openrouter'] = openrouter_key
        
        if not api_keys:
            raise ValueError("No API keys found. Please set OPENAI_API_KEY, GEMINI_API_KEY, or OPENROUTER_API_KEY")
        
        mcp_sdk.configure(api_keys)
        _configured = True
        print(f"SDK configured with providers: {list(api_keys.keys())}")

def ai_chat(prompt: str, model: str = "gpt-4o-mini", history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Start or continue an AI conversation with context preservation.
    
    Args:
        prompt: The message to send to the AI
        model: Model to use (e.g., 'gpt-4o-mini', 'gemini-1.5-flash')
        history: Previous conversation history (optional)
    
    Returns:
        Dict containing response, updated history, and metadata
    """
    ensure_configured()
    
    if history is None:
        history = []
    
    try:
        response, new_history = mcp_sdk.chat(prompt, model, history)
        
        return {
            "success": True,
            "response": response,
            "history": new_history,
            "model_used": model,
            "turn_count": len(new_history) // 2
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model_used": model
        }

def ai_consensus(prompt: str, models: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get consensus analysis from multiple AI models.
    
    Args:
        prompt: The question or topic to get consensus on
        models: List of models to consult (default: ["gpt-4o-mini", "gemini-1.5-flash"])
    
    Returns:
        Dict containing consensus response and metadata
    """
    ensure_configured()
    
    if models is None:
        models = ["gpt-4o-mini", "gemini-1.5-flash"]
    
    try:
        consensus = mcp_sdk.get_consensus(prompt, models)
        
        return {
            "success": True,
            "consensus": consensus,
            "models_consulted": models,
            "model_count": len(models)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "models_consulted": models
        }

def configure_api_keys(api_keys: Dict[str, str]) -> Dict[str, Any]:
    """
    Configure API keys for the SDK.
    
    Args:
        api_keys: Dictionary with provider names as keys and API keys as values
    
    Returns:
        Dict containing configuration status
    """
    global _configured
    
    try:
        mcp_sdk.configure(api_keys)
        _configured = True
        
        return {
            "success": True,
            "message": f"SDK configured successfully with providers: {list(api_keys.keys())}",
            "providers": list(api_keys.keys())
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_available_functions() -> List[Dict[str, Any]]:
    """
    Get list of available functions with their descriptions.
    
    Returns:
        List of function descriptions
    """
    return [
        {
            "name": "ai_chat",
            "description": "Start or continue an AI conversation with context preservation",
            "parameters": {
                "prompt": {"type": "string", "required": True, "description": "The message to send to the AI"},
                "model": {"type": "string", "required": False, "default": "gpt-4o-mini", "description": "Model to use"},
                "history": {"type": "array", "required": False, "description": "Previous conversation history"}
            },
            "returns": "Dict with response, history, and metadata"
        },
        {
            "name": "ai_consensus", 
            "description": "Get consensus analysis from multiple AI models",
            "parameters": {
                "prompt": {"type": "string", "required": True, "description": "The question or topic to get consensus on"},
                "models": {"type": "array", "required": False, "default": ["gpt-4o-mini", "gemini-1.5-flash"], "description": "List of models to consult"}
            },
            "returns": "Dict with consensus response and metadata"
        },
        {
            "name": "configure_api_keys",
            "description": "Configure API keys for the SDK",
            "parameters": {
                "api_keys": {"type": "object", "required": True, "description": "API keys for different providers"}
            },
            "returns": "Dict with configuration status"
        }
    ]

# Example usage functions for testing
def example_chat():
    """Example of using ai_chat function."""
    print("🗣️  Example: AI Chat")
    
    # Single turn
    result1 = ai_chat("Hello, my name is Bob")
    print(f"Response: {result1['response']}")
    
    # Multi-turn with context
    result2 = ai_chat("What's my name?", history=result1['history'])
    print(f"Response: {result2['response']}")
    
    return result2

def example_consensus():
    """Example of using ai_consensus function."""
    print("🤝 Example: AI Consensus")
    
    result = ai_consensus("What are the pros and cons of Python vs JavaScript?")
    if result['success']:
        print(f"Consensus: {result['consensus'][:200]}...")
    else:
        print(f"Error: {result['error']}")
    
    return result

if __name__ == "__main__":
    # Set API keys from environment
    os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"
    os.environ["GEMINI_API_KEY"] = "your_gemini_api_key_here"
    
    print("🚀 Testing Function Interface...")
    print("=" * 50)
    
    # Test functions
    example_chat()
    print()
    example_consensus()
    
    print("\n✅ Function interface tests completed!")
