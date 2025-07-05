"""
Main Logic for MCP SDK

Core functions for chat sessions and consensus workflows.
"""

import asyncio
import logging
import uuid
from typing import List, Optional, Tuple, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from .provider_manager import get_provider_for_model
from ..system_prompts.light_chat import CHAT_PROMPT
from ..system_prompts.light_consensus import CONSENSUS_PROMPT
from ..utils.model_optimizer import get_optimizer

logger = logging.getLogger(__name__)

def chat_session(prompt: str, model: str, history: Optional[List[Dict[str, str]]] = None,
                conversation_context: str = "") -> Tuple[str, str]:
    """Execute a chat session with conversation history and additional context.

    Args:
        prompt: User's message
        model: Model name to use
        history: Previous conversation history (list of {"role": "user/assistant", "content": "..."})
        conversation_context: Additional context (files, previous analysis, etc.)

    Returns:
        Tuple of (response, continuation_id)
    """
    if history is None:
        history = []

    # Get provider for the model
    provider = get_provider_for_model(model)
    if not provider:
        raise ValueError(f"No provider available for model: {model}")

    # Build conversation history
    history_context = ""
    if history:
        for turn in history:
            role = turn.get("role", "")
            content = turn.get("content", "")
            if role == "user":
                history_context += f"User: {content}\n"
            elif role == "assistant":
                history_context += f"Assistant: {content}\n"

    # Combine all context
    full_context = ""
    if conversation_context:
        full_context += f"=== CONTEXT ===\n{conversation_context}\n\n"
    if history_context:
        full_context += f"=== CONVERSATION HISTORY ===\n{history_context}\n"

    # Add current prompt
    full_prompt = full_context + f"User: {prompt}\nAssistant:"

    # Optimize for the specific model
    optimizer = get_optimizer(model)
    optimized_prompt, _ = optimizer.optimize_prompt(full_prompt)
    temperature = optimizer.get_recommended_temperature('general')

    try:
        # Generate response
        response = provider.generate_content(
            prompt=optimized_prompt,
            model_name=model,
            system_prompt=CHAT_PROMPT,
            temperature=temperature
        )

        # Generate continuation ID for this session
        continuation_id = str(uuid.uuid4())

        logger.info(f"Chat session completed for model {model}")
        return response.content, continuation_id

    except Exception as e:
        logger.error(f"Error in chat session: {e}")
        raise

def get_consensus_from_models(prompt: str, models: List[str], use_parallel: bool = True,
                            conversation_context: str = "") -> str:
    """Get consensus from multiple AI models with optional parallel processing.

    Args:
        prompt: The question or topic to get consensus on
        models: List of model names to consult
        use_parallel: Whether to process models in parallel (default: True)
        conversation_context: Additional context from previous conversation

    Returns:
        Synthesized consensus response
    """
    if not models:
        raise ValueError("At least one model must be specified")

    if len(models) == 1:
        # Single model - just return its response
        full_prompt = _build_full_context(prompt, conversation_context)
        return _get_single_model_response(full_prompt, models[0])

    # Build full context that all models will see
    full_context = _build_full_context(prompt, conversation_context)

    # Optimize prompts for each model (but all get the same full context)
    optimized_prompts = {}
    for model in models:
        optimizer = get_optimizer(model)
        optimized_prompt, _ = optimizer.optimize_prompt(full_context)
        optimized_prompts[model] = optimized_prompt

    if use_parallel and len(models) > 1:
        # Parallel processing - all models get the same optimized context
        responses = _get_parallel_responses(optimized_prompts)
    else:
        # Sequential processing (fallback)
        responses = _get_sequential_responses(optimized_prompts)

    if not responses:
        raise RuntimeError("No models were able to provide responses")

    # Synthesize final consensus
    return _synthesize_consensus(prompt, responses, models)


def _get_parallel_responses(optimized_prompts: Dict[str, str]) -> List[Dict[str, Any]]:
    """Get responses from multiple models in parallel."""
    responses = []

    # Use ThreadPoolExecutor for parallel API calls
    with ThreadPoolExecutor(max_workers=min(len(optimized_prompts), 5)) as executor:
        # Submit all tasks
        future_to_model = {
            executor.submit(_get_single_model_response, prompt, model): model
            for model, prompt in optimized_prompts.items()
        }

        # Collect results as they complete
        for future in as_completed(future_to_model):
            model = future_to_model[future]
            try:
                response = future.result(timeout=60)  # 60 second timeout per model
                responses.append({
                    "model": model,
                    "response": response
                })
                logger.info(f"Got response from {model} ({len(responses)}/{len(optimized_prompts)})")
            except Exception as e:
                logger.error(f"Error getting response from {model}: {e}")
                continue

    return responses


def _get_sequential_responses(optimized_prompts: Dict[str, str]) -> List[Dict[str, Any]]:
    """Get responses from multiple models sequentially (fallback)."""
    responses = []

    for i, (model, prompt) in enumerate(optimized_prompts.items()):
        try:
            logger.info(f"Getting response from model {i+1}/{len(optimized_prompts)}: {model}")

            response = _get_single_model_response(prompt, model)
            responses.append({
                "model": model,
                "response": response
            })

        except Exception as e:
            logger.error(f"Error getting response from {model}: {e}")
            continue

    return responses

def _build_full_context(prompt: str, conversation_context: str = "") -> str:
    """Build full context that all models will see.

    Args:
        prompt: The main question/topic
        conversation_context: Additional context from previous conversation

    Returns:
        Full context string that all models will receive
    """
    if not conversation_context:
        return prompt

    # Combine conversation context with current prompt
    full_context = f"""=== CONVERSATION CONTEXT ===
{conversation_context}

=== CURRENT QUESTION ===
{prompt}

Please analyze the current question while considering the conversation context above."""

    return full_context


def _get_single_model_response(prompt: str, model: str) -> str:
    """Get response from a single model.

    Args:
        prompt: The prompt to send (already includes full context)
        model: Model name

    Returns:
        Model's response
    """
    provider = get_provider_for_model(model)
    if not provider:
        raise ValueError(f"No provider available for model: {model}")

    # Get model-specific temperature
    optimizer = get_optimizer(model)
    temperature = optimizer.get_recommended_temperature('analytical')

    response = provider.generate_content(
        prompt=prompt,
        model_name=model,
        system_prompt=CONSENSUS_PROMPT,
        temperature=temperature
    )

    return response.content

def _build_consensus_context(original_prompt: str, previous_responses: List[Dict[str, Any]]) -> str:
    """Build context for consensus gathering.
    
    Args:
        original_prompt: The original user question
        previous_responses: List of previous model responses
        
    Returns:
        Formatted context string
    """
    if not previous_responses:
        return original_prompt
    
    context = f"Original question: {original_prompt}\n\n"
    context += "Previous expert analyses:\n\n"
    
    for i, resp in enumerate(previous_responses, 1):
        context += f"Expert {i} ({resp['model']}):\n{resp['response']}\n\n"
    
    context += f"Now provide your own analysis of the original question: {original_prompt}"
    
    return context

def _synthesize_consensus(original_prompt: str, responses: List[Dict[str, Any]], models: List[str]) -> str:
    """Synthesize final consensus from all responses.
    
    Args:
        original_prompt: The original question
        responses: All model responses
        models: List of model names used
        
    Returns:
        Final synthesized consensus
    """
    # Use the first available model for synthesis
    synthesis_model = models[0]
    for model in models:
        if model.startswith(('gpt-4', 'claude', 'gemini-2')):
            synthesis_model = model
            break
    
    # Build synthesis prompt
    synthesis_prompt = f"Original question: {original_prompt}\n\n"
    synthesis_prompt += "Expert analyses to synthesize:\n\n"
    
    for i, resp in enumerate(responses, 1):
        synthesis_prompt += f"Expert {i} ({resp['model']}):\n{resp['response']}\n\n"
    
    synthesis_prompt += """
Based on all the expert analyses above, provide a comprehensive synthesis that:
1. Identifies key points of agreement
2. Addresses any disagreements or different perspectives
3. Provides a balanced final conclusion
4. Highlights the most important insights

Synthesis:"""
    
    try:
        return _get_single_model_response(synthesis_prompt, synthesis_model)
    except Exception as e:
        logger.error(f"Error in synthesis: {e}")
        # Fallback: return a simple summary
        return _create_fallback_summary(original_prompt, responses)

def _create_fallback_summary(original_prompt: str, responses: List[Dict[str, Any]]) -> str:
    """Create a simple fallback summary when synthesis fails.

    Args:
        original_prompt: The original question
        responses: All model responses

    Returns:
        Simple summary of responses
    """
    summary = f"Consensus Analysis for: {original_prompt}\n\n"

    for i, resp in enumerate(responses, 1):
        summary += f"Model {i} ({resp['model']}):\n{resp['response']}\n\n"

    summary += f"Summary: {len(responses)} models provided analysis on this topic."

    return summary
