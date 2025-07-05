"""
Context Compression Utilities

Provides intelligent text compression and summarization for optimizing
context window usage and reducing token costs.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from .token_utils import estimate_tokens

logger = logging.getLogger(__name__)


def compress_conversation_turn(content: str, target_compression: float = 0.7) -> str:
    """
    Compress conversation turn content while preserving key information.

    Args:
        content: Original content to compress
        target_compression: Target compression ratio (0.7 = 70% of original size)

    Returns:
        Compressed content
    """
    if not content or target_compression >= 1.0:
        return content

    # Apply multiple compression techniques
    compressed = content

    # 1. Remove redundant whitespace
    compressed = re.sub(r'\s+', ' ', compressed)
    compressed = re.sub(r'\n\s*\n', '\n', compressed)

    # 2. Compress common phrases
    compressed = _compress_common_phrases(compressed)

    # 3. Remove filler words if still too long
    current_ratio = len(compressed) / len(content)
    if current_ratio > target_compression:
        compressed = _remove_filler_words(compressed)

    # 4. Summarize sentences if still too long
    current_ratio = len(compressed) / len(content)
    if current_ratio > target_compression:
        compressed = _summarize_sentences(compressed, target_compression)

    logger.debug(f"Compressed content from {len(content)} to {len(compressed)} chars "
                f"({len(compressed)/len(content):.2%} of original)")

    return compressed


def _compress_common_phrases(text: str) -> str:
    """Replace common phrases with shorter equivalents."""
    replacements = {
        r'\bI think that\b': 'I think',
        r'\bIt seems like\b': 'Seems',
        r'\bIn my opinion\b': 'IMO',
        r'\bAs you can see\b': 'See',
        r'\bFor example\b': 'e.g.',
        r'\bThat is to say\b': 'i.e.',
        r'\bIn other words\b': 'IOW',
        r'\bAs a result\b': 'Thus',
        r'\bHowever\b': 'But',
        r'\bTherefore\b': 'So',
        r'\bNevertheless\b': 'Still',
        r'\bFurthermore\b': 'Also',
        r'\bAdditionally\b': 'Plus',
        r'\bConsequently\b': 'So',
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def _remove_filler_words(text: str) -> str:
    """Remove common filler words and phrases."""
    filler_patterns = [
        r'\b(um|uh|er|ah)\b',
        r'\b(you know|like|basically|actually|literally)\b',
        r'\b(kind of|sort of)\b',
        r'\b(I mean)\b',
        r'\b(well|so|now)\b(?=\s)',  # Only at start of sentences
    ]

    for pattern in filler_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _summarize_sentences(text: str, target_ratio: float) -> str:
    """Summarize by keeping most important sentences."""
    sentences = re.split(r'[.!?]+', text)
    if len(sentences) <= 2:
        return text

    # Score sentences by importance (simple heuristic)
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue

        score = 0
        # Longer sentences often contain more information
        score += len(sentence) * 0.1
        # First and last sentences are often important
        if i == 0 or i == len(sentences) - 1:
            score += 50
        # Sentences with numbers/data are important
        if re.search(r'\d+', sentence):
            score += 20
        # Sentences with keywords are important
        keywords = ['error', 'issue', 'problem', 'solution', 'result', 'conclusion']
        for keyword in keywords:
            if keyword.lower() in sentence.lower():
                score += 15

        scored_sentences.append((score, sentence))

    # Sort by score and take top sentences
    scored_sentences.sort(reverse=True)
    target_count = max(1, int(len(scored_sentences) * target_ratio))

    # Reconstruct text with top sentences in original order
    selected_sentences = [sent for _, sent in scored_sentences[:target_count]]
    return '. '.join(selected_sentences) + '.'


def compress_file_content(content: str, max_tokens: int, model_name: str = None) -> str:
    """
    Compress file content to fit within token limit.

    Args:
        content: File content to compress
        max_tokens: Maximum tokens allowed
        model_name: Model name for token estimation

    Returns:
        Compressed content that fits within token limit
    """
    current_tokens = estimate_tokens(content, model_name)

    if current_tokens <= max_tokens:
        return content

    # Calculate target compression ratio
    target_ratio = max_tokens / current_tokens

    # Apply compression techniques
    compressed = content

    # 1. Remove comments if it's code
    if _is_code_content(content):
        compressed = _remove_code_comments(compressed)

    # 2. Remove excessive whitespace
    compressed = re.sub(r'\n\s*\n\s*\n', '\n\n', compressed)  # Max 2 consecutive newlines
    compressed = re.sub(r'[ \t]+', ' ', compressed)  # Normalize spaces

    # 3. If still too long, truncate intelligently
    current_tokens = estimate_tokens(compressed, model_name)
    if current_tokens > max_tokens:
        compressed = _intelligent_truncate(compressed, max_tokens, model_name)

    return compressed


def _is_code_content(content: str) -> bool:
    """Check if content appears to be code."""
    code_indicators = [
        'def ', 'class ', 'import ', 'function', 'const ', 'let ', 'var ',
        '{', '}', '()', '=>', '//', '/*', '*/', '#'
    ]
    return any(indicator in content for indicator in code_indicators)


def _remove_code_comments(content: str) -> str:
    """Remove comments from code content."""
    # Remove single-line comments
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)

    # Remove multi-line comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)
    content = re.sub(r"'''.*?'''", '', content, flags=re.DOTALL)

    return content


def _intelligent_truncate(content: str, max_tokens: int, model_name: str = None) -> str:
    """Intelligently truncate content to fit token limit."""
    lines = content.split('\n')

    # Keep important lines (function definitions, class definitions, etc.)
    important_patterns = [
        r'^\s*(def|class|function|const|let|var)\s+',
        r'^\s*(import|from|#include)',
        r'^\s*//\s*(TODO|FIXME|NOTE)',
    ]

    important_lines = []
    regular_lines = []

    for i, line in enumerate(lines):
        is_important = any(re.match(pattern, line) for pattern in important_patterns)
        if is_important:
            important_lines.append((i, line))
        else:
            regular_lines.append((i, line))

    # Start with important lines
    result_lines = [line for _, line in important_lines]
    current_tokens = estimate_tokens('\n'.join(result_lines), model_name)

    # Add regular lines until we hit the limit
    for _, line in regular_lines:
        line_tokens = estimate_tokens(line, model_name)
        if current_tokens + line_tokens <= max_tokens:
            result_lines.append(line)
            current_tokens += line_tokens
        else:
            break

    # Add truncation notice
    if len(result_lines) < len(lines):
        result_lines.append(f'\n[... truncated {len(lines) - len(result_lines)} lines to fit token limit ...]')

    return '\n'.join(result_lines)