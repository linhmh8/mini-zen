"""
Provider Manager for MCP SDK

Simplified provider management for the lightweight SDK.
Handles initialization and routing of AI model providers.
"""

import logging
from typing import Dict, Optional

from ..providers.base import ModelProvider, ProviderType
from ..providers.openai_provider import OpenAIModelProvider
from ..providers.gemini import GeminiModelProvider
from ..providers.openrouter import OpenRouterProvider

logger = logging.getLogger(__name__)

class ProviderManager:
    """Simplified provider manager for MCP SDK."""
    
    def __init__(self):
        self._providers: Dict[ProviderType, ModelProvider] = {}
        self._initialized = False
    
    def initialize(self, api_keys: dict):
        """Initialize providers with API keys.
        
        Args:
            api_keys: Dictionary with provider names as keys and API keys as values.
                     Supported: 'openai', 'gemini', 'openrouter'
        """
        self._providers.clear()
        
        # Initialize OpenAI provider
        if 'openai' in api_keys and api_keys['openai']:
            try:
                provider = OpenAIModelProvider(api_key=api_keys['openai'])
                self._providers[ProviderType.OPENAI] = provider
                logger.info("OpenAI provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI provider: {e}")
        
        # Initialize Gemini provider
        if 'gemini' in api_keys and api_keys['gemini']:
            try:
                provider = GeminiModelProvider(api_key=api_keys['gemini'])
                self._providers[ProviderType.GOOGLE] = provider
                logger.info("Gemini provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini provider: {e}")
        
        # Initialize OpenRouter provider
        if 'openrouter' in api_keys and api_keys['openrouter']:
            try:
                provider = OpenRouterProvider(api_key=api_keys['openrouter'])
                self._providers[ProviderType.OPENROUTER] = provider
                logger.info("OpenRouter provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenRouter provider: {e}")
        
        if not self._providers:
            raise ValueError("At least one API key must be provided")
        
        self._initialized = True
        logger.info(f"Provider manager initialized with {len(self._providers)} providers")
    
    def get_provider_for_model(self, model_name: str) -> Optional[ModelProvider]:
        """Get the appropriate provider for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelProvider instance that supports the model, or None
        """
        if not self._initialized:
            raise RuntimeError("Provider manager not initialized. Call initialize() first.")
        
        # Provider priority: OpenAI -> Gemini -> OpenRouter
        priority_order = [ProviderType.OPENAI, ProviderType.GOOGLE, ProviderType.OPENROUTER]
        
        for provider_type in priority_order:
            if provider_type in self._providers:
                provider = self._providers[provider_type]
                if provider.validate_model_name(model_name):
                    logger.debug(f"Model {model_name} routed to {provider_type}")
                    return provider
        
        logger.warning(f"No provider found for model: {model_name}")
        return None
    
    def list_available_models(self) -> Dict[str, list]:
        """List all available models by provider.
        
        Returns:
            Dictionary mapping provider names to lists of model names
        """
        if not self._initialized:
            return {}
        
        models = {}
        for provider_type, provider in self._providers.items():
            try:
                provider_models = list(provider.SUPPORTED_MODELS.keys())
                models[provider_type.value] = provider_models
            except Exception as e:
                logger.error(f"Error listing models for {provider_type}: {e}")
                models[provider_type.value] = []
        
        return models

# Global provider manager instance
_provider_manager = ProviderManager()

def initialize_providers(api_keys: dict):
    """Initialize the global provider manager.
    
    Args:
        api_keys: Dictionary with provider names as keys and API keys as values
    """
    _provider_manager.initialize(api_keys)

def get_provider_for_model(model_name: str) -> Optional[ModelProvider]:
    """Get provider for a specific model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        ModelProvider instance or None
    """
    return _provider_manager.get_provider_for_model(model_name)

def list_available_models() -> Dict[str, list]:
    """List all available models.
    
    Returns:
        Dictionary mapping provider names to model lists
    """
    return _provider_manager.list_available_models()
