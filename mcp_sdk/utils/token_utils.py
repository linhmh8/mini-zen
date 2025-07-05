"""
Token counting utilities for managing API context limits

This module provides functions for estimating token counts to ensure
requests stay within the Gemini API's context window limits.

Note: The estimation uses a simple character-to-token ratio which is
approximate. For production systems requiring precise token counts,
consider using the actual tokenizer for the specific model.
"""

# Default fallback for token limit (conservative estimate)
DEFAULT_CONTEXT_WINDOW = 200_000  # Conservative fallback for unknown models

# Token estimation cache for performance
_token_cache = {}
_cache_max_size = 1000


def estimate_tokens(text: str, model_name: str = None, use_cache: bool = True) -> int:
    """
    Estimate token count with model-specific approximations and caching.

    Uses improved heuristics based on content type and model family.
    More accurate than simple character counting. Includes caching for performance.

    Args:
        text: The text to estimate tokens for
        model_name: Optional model name for model-specific estimation
        use_cache: Whether to use token estimation cache

    Returns:
        int: Estimated number of tokens
    """
    if not text:
        return 0

    # Create cache key
    cache_key = None
    if use_cache:
        cache_key = (hash(text), model_name)
        if cache_key in _token_cache:
            return _token_cache[cache_key]

    # Model-specific token ratios (chars per token)
    model_ratios = {
        'claude-4': 3.7,        # Claude 4.0 (Augment internal)
        'claude': 3.8,          # General Claude models
        'gemini-2.5-pro': 4.0,  # Gemini 2.5 Pro (improved tokenization)
        'gemini-2.5-flash': 4.1, # Gemini 2.5 Flash
        'gemini-2.5': 4.0,      # General Gemini 2.5 family
        'gemini': 4.2,          # Older Gemini models
        'deepseek-r1': 3.4,     # DeepSeek R1 (more efficient tokenization)
        'deepseek': 3.4,        # General DeepSeek models
    }

    # Determine ratio based on model
    ratio = 4.0  # Default fallback
    if model_name:
        model_lower = model_name.lower()
        for model_family, model_ratio in model_ratios.items():
            if model_family in model_lower:
                ratio = model_ratio
                break

    # Content type adjustments
    base_tokens = len(text) / ratio

    # Code content typically has more tokens per character
    if _is_code_content(text):
        base_tokens *= 1.2

    # JSON/structured data is more token-dense
    if _is_structured_content(text):
        base_tokens *= 1.15

    result = int(base_tokens)

    # Cache the result
    if use_cache and cache_key:
        _manage_cache_size()
        _token_cache[cache_key] = result

    return result


def _is_code_content(text: str) -> bool:
    """Check if text appears to be code."""
    code_indicators = ['{', '}', '()', 'def ', 'class ', 'import ', 'function', 'const ', 'let ', 'var ']
    return any(indicator in text for indicator in code_indicators)


def _is_structured_content(text: str) -> bool:
    """Check if text appears to be structured data (JSON, XML, etc)."""
    structured_indicators = ['{"', '"}', '</', '/>', '<?xml']
    return any(indicator in text for indicator in structured_indicators)


def _manage_cache_size():
    """Manage token cache size to prevent memory bloat."""
    global _token_cache
    if len(_token_cache) >= _cache_max_size:
        # Remove oldest 20% of entries
        items_to_remove = len(_token_cache) // 5
        keys_to_remove = list(_token_cache.keys())[:items_to_remove]
        for key in keys_to_remove:
            del _token_cache[key]


def clear_token_cache():
    """Clear the token estimation cache."""
    global _token_cache
    _token_cache.clear()


def get_cache_stats() -> dict:
    """Get token cache statistics."""
    return {
        'cache_size': len(_token_cache),
        'max_size': _cache_max_size,
        'hit_ratio': getattr(get_cache_stats, '_hits', 0) / max(getattr(get_cache_stats, '_total', 1), 1)
    }


def check_token_limit(text: str, context_window: int = DEFAULT_CONTEXT_WINDOW) -> tuple[bool, int]:
    """
    Check if text exceeds the specified token limit.

    This function is used to validate that prepared prompts will fit
    within the model's context window, preventing API errors and ensuring
    reliable operation.

    Args:
        text: The text to check
        context_window: The model's context window size (defaults to conservative fallback)

    Returns:
        Tuple[bool, int]: (is_within_limit, estimated_tokens)
        - is_within_limit: True if the text fits within context_window
        - estimated_tokens: The estimated token count
    """
    estimated = estimate_tokens(text)
    return estimated <= context_window, estimated
