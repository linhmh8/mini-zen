# mcp_sdk/__init__.py
"""
MCP SDK - Lightweight Python library for AI-to-AI conversation threading and consensus workflows.

This SDK provides two core functionalities:
1. AI-to-AI Conversation Threading: Create and maintain stateful, contextual conversation threads
2. Consensus Workflow: Synthesize opinions from multiple AI models

Usage:
    import mcp_sdk
    
    # Configure API keys
    mcp_sdk.configure({
        'openai': 'your-openai-key',
        'gemini': 'your-gemini-key',
        'openrouter': 'your-openrouter-key'
    })
    
    # Start a conversation
    response, history = mcp_sdk.chat("Hello, how are you?", "gpt-4o-mini")
    
    # Continue the conversation
    response, history = mcp_sdk.chat("What's my name?", "gpt-4o-mini", history=history)
    
    # Get consensus from multiple models
    consensus = mcp_sdk.get_consensus("Pros and cons of Python vs Go", ["gpt-4o-mini", "gemini-1.5-flash"])
"""

from .core.main_logic import chat_session, get_consensus_from_models
from .core.provider_manager import initialize_providers

__version__ = "0.1.0"

def configure(api_keys: dict):
    """Configure API keys for the providers.
    
    Args:
        api_keys: Dictionary with provider names as keys and API keys as values.
                 Supported providers: 'openai', 'gemini', 'openrouter'
    
    Example:
        configure({
            'openai': 'sk-...',
            'gemini': 'AI...',
            'openrouter': 'sk-or-...'
        })
    """
    initialize_providers(api_keys)

def chat(prompt: str, model: str, history: list = None):
    """Start or continue a conversation.
    
    Args:
        prompt: The user's message
        model: Model name to use (e.g., 'gpt-4o-mini', 'gemini-1.5-flash')
        history: Previous conversation history (optional)
    
    Returns:
        tuple: (response, new_history) where response is the AI's reply
               and new_history contains the updated conversation history
    """
    if history is None:
        history = []
    
    response, continuation_id = chat_session(prompt, model, history)
    
    # Update history with the new exchange
    new_history = history + [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response}
    ]
    
    return response, new_history

def get_consensus(prompt: str, models: list[str]):
    """Get consensus from multiple models.
    
    Args:
        prompt: The question or topic to get consensus on
        models: List of model names to consult
    
    Returns:
        str: Synthesized consensus response from all models
    """
    return get_consensus_from_models(prompt, models)
