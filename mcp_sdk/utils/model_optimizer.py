"""
Model-Specific Optimization Manager

Provides model-specific optimizations for token usage, context management,
and performance tuning based on each model's characteristics.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from .token_utils import estimate_tokens
from .context_compression import compress_conversation_turn, compress_file_content

logger = logging.getLogger(__name__)


class ModelOptimizer:
    """Manages model-specific optimizations for token and context efficiency."""
    
    # Model-specific configurations
    MODEL_CONFIGS = {
        # Claude models (using Augment internal - Claude 4.0)
        'claude-4': {
            'context_window': 200000,  # Augment internal Claude 4.0
            'optimal_chunk_size': 8000,
            'compression_threshold': 0.9,
            'supports_function_calling': True,
            'prefers_structured_output': True,
            'provider': 'augment_internal',
        },
        'claude': {  # Fallback for any claude reference
            'context_window': 200000,
            'optimal_chunk_size': 8000,
            'compression_threshold': 0.9,
            'supports_function_calling': True,
            'prefers_structured_output': True,
            'provider': 'augment_internal',
        },

        # Gemini 2.5 models (latest from Google)
        'gemini-2.5-pro': {
            'context_window': 2000000,  # Gemini 2.5 Pro has 2M context
            'optimal_chunk_size': 15000,
            'compression_threshold': 0.9,
            'supports_function_calling': True,
            'prefers_structured_output': True,
            'provider': 'google',
        },
        'gemini-2.5-flash': {
            'context_window': 1000000,  # Gemini 2.5 Flash has 1M context
            'optimal_chunk_size': 10000,
            'compression_threshold': 0.8,
            'supports_function_calling': True,
            'prefers_structured_output': True,
            'provider': 'google',
        },
        'gemini-2.5-flash-preview-04-17': {
            'context_window': 1000000,
            'optimal_chunk_size': 10000,
            'compression_threshold': 0.8,
            'supports_function_calling': True,
            'prefers_structured_output': True,
            'provider': 'google',
        },
        'gemini-2.5-flash-lite-preview-06-17': {
            'context_window': 1000000,
            'optimal_chunk_size': 8000,
            'compression_threshold': 0.7,  # Lite version, more aggressive compression
            'supports_function_calling': True,
            'prefers_structured_output': True,
            'provider': 'google',
        },

        # DeepSeek R1 (via OpenRouter)
        'deepseek-r1': {
            'context_window': 65536,  # DeepSeek R1 context window
            'optimal_chunk_size': 4000,
            'compression_threshold': 0.7,
            'supports_function_calling': False,
            'prefers_structured_output': False,
            'provider': 'openrouter',
        },
        'deepseek/deepseek-r1': {  # Full OpenRouter format
            'context_window': 65536,
            'optimal_chunk_size': 4000,
            'compression_threshold': 0.7,
            'supports_function_calling': False,
            'prefers_structured_output': False,
            'provider': 'openrouter',
        },
    }
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.config = self._get_model_config(model_name)
        
    def _get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model."""
        model_lower = model_name.lower()

        # Try exact match first
        if model_lower in self.MODEL_CONFIGS:
            return self.MODEL_CONFIGS[model_lower]

        # Try partial matches for model families
        for config_key, config in self.MODEL_CONFIGS.items():
            if config_key in model_lower:
                return config

        # Special handling for model families
        if 'claude' in model_lower:
            return self.MODEL_CONFIGS['claude']
        elif 'gemini-2.5' in model_lower:
            if 'flash' in model_lower:
                return self.MODEL_CONFIGS['gemini-2.5-flash']
            else:
                return self.MODEL_CONFIGS['gemini-2.5-pro']
        elif 'deepseek' in model_lower:
            return self.MODEL_CONFIGS['deepseek-r1']

        # Default fallback configuration
        return {
            'context_window': 100000,
            'optimal_chunk_size': 4000,
            'compression_threshold': 0.8,
            'supports_function_calling': False,
            'prefers_structured_output': False,
            'provider': 'unknown',
        }
    
    def optimize_prompt(self, prompt: str, context: str = "") -> Tuple[str, str]:
        """
        Optimize prompt and context for the specific model.
        
        Args:
            prompt: Main prompt text
            context: Additional context (conversation history, files, etc.)
            
        Returns:
            Tuple of (optimized_prompt, optimized_context)
        """
        total_text = prompt + context
        total_tokens = estimate_tokens(total_text, self.model_name)
        
        # If within limits, return as-is
        if total_tokens <= self.config['context_window'] * 0.9:  # 90% safety margin
            return prompt, context
        
        logger.info(f"Optimizing prompt for {self.model_name}: {total_tokens} tokens -> target: {self.config['context_window']}")
        
        # Calculate how much we need to compress
        target_tokens = int(self.config['context_window'] * 0.85)  # 85% of limit
        compression_ratio = target_tokens / total_tokens
        
        # Optimize context first (usually larger)
        optimized_context = context
        if context:
            optimized_context = self._optimize_context(context, compression_ratio)
        
        # Check if we need to optimize prompt too
        remaining_tokens = target_tokens - estimate_tokens(optimized_context, self.model_name)
        prompt_tokens = estimate_tokens(prompt, self.model_name)
        
        optimized_prompt = prompt
        if prompt_tokens > remaining_tokens:
            prompt_compression = remaining_tokens / prompt_tokens
            optimized_prompt = compress_conversation_turn(prompt, prompt_compression)
        
        final_tokens = estimate_tokens(optimized_prompt + optimized_context, self.model_name)
        logger.info(f"Optimization complete: {total_tokens} -> {final_tokens} tokens "
                   f"({final_tokens/total_tokens:.2%} of original)")
        
        return optimized_prompt, optimized_context
    
    def _optimize_context(self, context: str, compression_ratio: float) -> str:
        """Optimize context based on model characteristics."""
        if compression_ratio >= 1.0:
            return context
        
        # Use model-specific compression threshold
        target_compression = max(compression_ratio, self.config['compression_threshold'])
        
        # Apply compression
        if self.config.get('prefers_structured_output'):
            # For models that prefer structured output, preserve structure
            return self._structured_compression(context, target_compression)
        else:
            # For other models, use general compression
            return compress_conversation_turn(context, target_compression)
    
    def _structured_compression(self, context: str, target_compression: float) -> str:
        """Compress while preserving structure for models that prefer it."""
        # Split into sections
        sections = context.split('\n===')
        
        compressed_sections = []
        for section in sections:
            if section.strip():
                # Compress each section individually
                compressed = compress_conversation_turn(section, target_compression)
                compressed_sections.append(compressed)
        
        return '\n==='.join(compressed_sections)
    
    def get_optimal_batch_size(self) -> int:
        """Get optimal batch size for this model."""
        return max(1, self.config['context_window'] // self.config['optimal_chunk_size'])
    
    def should_use_function_calling(self) -> bool:
        """Check if this model supports and benefits from function calling."""
        return self.config.get('supports_function_calling', False)
    
    def get_recommended_temperature(self, task_type: str = 'general') -> float:
        """Get recommended temperature based on model and task type."""
        base_temps = {
            'creative': 0.8,
            'analytical': 0.3,
            'coding': 0.1,
            'general': 0.7,
        }

        base_temp = base_temps.get(task_type, 0.7)

        # Adjust based on model characteristics
        if 'claude' in self.model_name.lower():
            return base_temp * 0.9  # Claude 4.0 is well-balanced
        elif 'gemini-2.5' in self.model_name.lower():
            return base_temp * 0.95  # Gemini 2.5 is more refined
        elif 'deepseek' in self.model_name.lower():
            return base_temp * 1.1  # DeepSeek R1 benefits from slightly higher temp

        return base_temp
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for the given token usage.

        Note: This uses approximate pricing and should be updated with current rates.
        """
        # Approximate pricing per 1K tokens (as of 2025)
        pricing = {
            # Claude models (Augment internal - no external cost)
            'claude': {'input': 0.0, 'output': 0.0},  # Free via Augment internal
            'claude-4': {'input': 0.0, 'output': 0.0},  # Free via Augment internal

            # Gemini 2.5 models (Google pricing)
            'gemini-2.5-pro': {'input': 0.00125, 'output': 0.005},  # Updated Gemini 2.5 Pro pricing
            'gemini-2.5-flash': {'input': 0.000075, 'output': 0.0003},  # Gemini 2.5 Flash pricing
            'gemini-2.5-flash-preview': {'input': 0.000075, 'output': 0.0003},
            'gemini-2.5-flash-lite': {'input': 0.00005, 'output': 0.0002},  # Lite version cheaper

            # DeepSeek R1 (OpenRouter pricing)
            'deepseek-r1': {'input': 0.0014, 'output': 0.0028},  # DeepSeek R1 via OpenRouter
            'deepseek/deepseek-r1': {'input': 0.0014, 'output': 0.0028},
        }

        model_pricing = None
        model_lower = self.model_name.lower()

        # Try exact match first
        for model_key, prices in pricing.items():
            if model_key in model_lower:
                model_pricing = prices
                break

        # Fallback for model families
        if not model_pricing:
            if 'claude' in model_lower:
                model_pricing = pricing['claude']  # Free via Augment
            elif 'gemini-2.5' in model_lower:
                if 'flash' in model_lower:
                    model_pricing = pricing['gemini-2.5-flash']
                else:
                    model_pricing = pricing['gemini-2.5-pro']
            elif 'deepseek' in model_lower:
                model_pricing = pricing['deepseek-r1']
            else:
                # Default pricing for unknown models
                model_pricing = {'input': 0.001, 'output': 0.002}

        input_cost = (input_tokens / 1000) * model_pricing['input']
        output_cost = (output_tokens / 1000) * model_pricing['output']

        return input_cost + output_cost
    
    def get_context_allocation(self) -> Dict[str, int]:
        """Get recommended context allocation for different content types."""
        total_context = self.config['context_window']
        
        # Reserve space for response
        response_reserve = min(4000, total_context * 0.2)
        available_context = total_context - response_reserve
        
        # Allocate based on model characteristics
        if self.config.get('prefers_structured_output'):
            # Models that prefer structure can handle more files
            return {
                'files': int(available_context * 0.6),
                'conversation': int(available_context * 0.3),
                'system_prompt': int(available_context * 0.1),
                'response_reserve': response_reserve,
            }
        else:
            # Other models prefer more conversation context
            return {
                'files': int(available_context * 0.4),
                'conversation': int(available_context * 0.5),
                'system_prompt': int(available_context * 0.1),
                'response_reserve': response_reserve,
            }


def get_optimizer(model_name: str) -> ModelOptimizer:
    """Factory function to get model optimizer."""
    return ModelOptimizer(model_name)


def optimize_for_model(model_name: str, prompt: str, context: str = "") -> Tuple[str, str]:
    """Convenience function to optimize prompt and context for a specific model."""
    optimizer = get_optimizer(model_name)
    return optimizer.optimize_prompt(prompt, context)
