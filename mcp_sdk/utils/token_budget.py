"""
Token Budget Manager

Intelligent token allocation and budget management for optimizing
context window usage across different content types.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from .token_utils import estimate_tokens
from .model_optimizer import get_optimizer

logger = logging.getLogger(__name__)


@dataclass
class TokenBudget:
    """Token budget allocation for different content types."""
    total_budget: int
    system_prompt: int
    conversation_history: int
    file_content: int
    user_prompt: int
    response_reserve: int
    
    def get_available_budget(self) -> int:
        """Get remaining budget after allocations."""
        allocated = (self.system_prompt + self.conversation_history + 
                    self.file_content + self.user_prompt + self.response_reserve)
        return max(0, self.total_budget - allocated)
    
    def get_utilization(self) -> float:
        """Get budget utilization percentage."""
        allocated = (self.system_prompt + self.conversation_history + 
                    self.file_content + self.user_prompt + self.response_reserve)
        return allocated / self.total_budget if self.total_budget > 0 else 0.0


class TokenBudgetManager:
    """Manages token budgets and allocations for optimal context usage."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.optimizer = get_optimizer(model_name)
        self.context_allocation = self.optimizer.get_context_allocation()
        
    def create_budget(self, 
                     system_prompt: str = "",
                     user_prompt: str = "",
                     conversation_history: str = "",
                     files: List[str] = None) -> TokenBudget:
        """
        Create an optimal token budget based on actual content.
        
        Args:
            system_prompt: System prompt text
            user_prompt: User's current prompt
            conversation_history: Previous conversation context
            files: List of file paths to include
            
        Returns:
            TokenBudget with optimal allocations
        """
        if files is None:
            files = []
        
        # Calculate actual token usage
        system_tokens = estimate_tokens(system_prompt, self.model_name) if system_prompt else 0
        user_tokens = estimate_tokens(user_prompt, self.model_name) if user_prompt else 0
        history_tokens = estimate_tokens(conversation_history, self.model_name) if conversation_history else 0
        
        # Estimate file tokens
        file_tokens = 0
        for file_path in files:
            try:
                from .file_utils import estimate_file_tokens
                file_tokens += estimate_file_tokens(file_path)
            except Exception as e:
                logger.warning(f"Could not estimate tokens for {file_path}: {e}")
        
        # Get base allocations from model optimizer
        total_context = self.context_allocation['files'] + self.context_allocation['conversation'] + \
                       self.context_allocation['system_prompt']
        response_reserve = self.context_allocation['response_reserve']
        
        # Adjust allocations based on actual usage
        budget = self._optimize_allocations(
            total_context=total_context,
            response_reserve=response_reserve,
            actual_system=system_tokens,
            actual_user=user_tokens,
            actual_history=history_tokens,
            actual_files=file_tokens
        )
        
        logger.debug(f"Created budget for {self.model_name}: {budget.get_utilization():.1%} utilization")
        return budget
    
    def _optimize_allocations(self, 
                            total_context: int,
                            response_reserve: int,
                            actual_system: int,
                            actual_user: int,
                            actual_history: int,
                            actual_files: int) -> TokenBudget:
        """Optimize token allocations based on actual usage."""
        
        # Start with actual usage
        system_allocation = actual_system
        user_allocation = actual_user
        history_allocation = actual_history
        file_allocation = actual_files
        
        # Calculate total needed
        total_needed = system_allocation + user_allocation + history_allocation + file_allocation
        
        # If we're over budget, we need to compress
        if total_needed > total_context:
            compression_ratio = total_context / total_needed
            
            # Prioritize system prompt and user prompt (don't compress these)
            protected_tokens = system_allocation + user_allocation
            available_for_content = total_context - protected_tokens
            
            if available_for_content > 0:
                # Distribute remaining budget between history and files
                content_total = history_allocation + file_allocation
                if content_total > 0:
                    history_ratio = history_allocation / content_total
                    file_ratio = file_allocation / content_total
                    
                    history_allocation = int(available_for_content * history_ratio)
                    file_allocation = int(available_for_content * file_ratio)
                else:
                    history_allocation = available_for_content // 2
                    file_allocation = available_for_content // 2
            else:
                # Extreme case - even system + user exceeds budget
                logger.warning(f"System + user prompts exceed budget: {protected_tokens} > {total_context}")
                history_allocation = 0
                file_allocation = 0
        
        # If we're under budget, we can expand allocations
        elif total_needed < total_context:
            extra_budget = total_context - total_needed
            
            # Distribute extra budget (prefer files over history for most models)
            if self.optimizer.config.get('prefers_structured_output'):
                # Models that prefer structure get more file budget
                file_allocation += int(extra_budget * 0.7)
                history_allocation += int(extra_budget * 0.3)
            else:
                # Other models get more conversation budget
                history_allocation += int(extra_budget * 0.6)
                file_allocation += int(extra_budget * 0.4)
        
        return TokenBudget(
            total_budget=total_context + response_reserve,
            system_prompt=system_allocation,
            user_prompt=user_allocation,
            conversation_history=history_allocation,
            file_content=file_allocation,
            response_reserve=response_reserve
        )
    
    def check_budget_compliance(self, budget: TokenBudget, 
                              actual_content: Dict[str, str]) -> Dict[str, bool]:
        """
        Check if actual content fits within budget allocations.
        
        Args:
            budget: Token budget to check against
            actual_content: Dict with keys: system_prompt, user_prompt, 
                          conversation_history, file_content
                          
        Returns:
            Dict indicating compliance for each content type
        """
        compliance = {}
        
        for content_type, content in actual_content.items():
            if not content:
                compliance[content_type] = True
                continue
                
            actual_tokens = estimate_tokens(content, self.model_name)
            budget_allocation = getattr(budget, content_type, 0)
            
            compliance[content_type] = actual_tokens <= budget_allocation
            
            if not compliance[content_type]:
                logger.warning(f"{content_type} exceeds budget: {actual_tokens} > {budget_allocation}")
        
        return compliance
    
    def suggest_optimizations(self, budget: TokenBudget, 
                            actual_content: Dict[str, str]) -> List[str]:
        """
        Suggest optimizations when budget is exceeded.
        
        Args:
            budget: Current token budget
            actual_content: Actual content being used
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        compliance = self.check_budget_compliance(budget, actual_content)
        
        for content_type, is_compliant in compliance.items():
            if not is_compliant:
                content = actual_content.get(content_type, "")
                actual_tokens = estimate_tokens(content, self.model_name)
                budget_allocation = getattr(budget, content_type, 0)
                excess = actual_tokens - budget_allocation
                
                if content_type == "conversation_history":
                    suggestions.append(
                        f"Compress conversation history by {excess} tokens "
                        f"(consider removing older turns or summarizing)"
                    )
                elif content_type == "file_content":
                    suggestions.append(
                        f"Reduce file content by {excess} tokens "
                        f"(consider excluding older files or truncating large files)"
                    )
                elif content_type == "user_prompt":
                    suggestions.append(
                        f"Shorten user prompt by {excess} tokens "
                        f"(consider more concise phrasing)"
                    )
                elif content_type == "system_prompt":
                    suggestions.append(
                        f"Optimize system prompt by {excess} tokens "
                        f"(consider using a more concise system prompt)"
                    )
        
        # Overall suggestions
        utilization = budget.get_utilization()
        if utilization > 0.95:
            suggestions.append(
                f"Overall budget utilization is very high ({utilization:.1%}). "
                f"Consider using a model with a larger context window."
            )
        
        return suggestions
    
    def get_budget_summary(self, budget: TokenBudget) -> str:
        """Get a human-readable budget summary."""
        utilization = budget.get_utilization()
        available = budget.get_available_budget()
        
        summary = f"""Token Budget Summary for {self.model_name}:
Total Budget: {budget.total_budget:,} tokens
Allocations:
  - System Prompt: {budget.system_prompt:,} tokens
  - User Prompt: {budget.user_prompt:,} tokens  
  - Conversation History: {budget.conversation_history:,} tokens
  - File Content: {budget.file_content:,} tokens
  - Response Reserve: {budget.response_reserve:,} tokens
  
Utilization: {utilization:.1%}
Available: {available:,} tokens"""
        
        return summary


def create_budget_manager(model_name: str) -> TokenBudgetManager:
    """Factory function to create a token budget manager."""
    return TokenBudgetManager(model_name)
