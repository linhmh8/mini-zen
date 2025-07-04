"""
Test cases for token optimization
"""

import pytest
import tiktoken

from mcp_sdk.system_prompts.light_chat import CHAT_PROMPT
from mcp_sdk.system_prompts.light_consensus import CONSENSUS_PROMPT


class TestTokenOptimization:
    """Test token optimization requirements."""
    
    def setup_method(self):
        """Setup test environment."""
        # Use GPT-4 tokenizer for token counting
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
    
    def test_chat_prompt_token_count(self):
        """Test that chat prompt is under 100 tokens."""
        token_count = len(self.tokenizer.encode(CHAT_PROMPT))
        
        print(f"Chat prompt token count: {token_count}")
        print(f"Chat prompt content: {repr(CHAT_PROMPT)}")
        
        assert token_count < 100, f"Chat prompt has {token_count} tokens, should be < 100"
    
    def test_consensus_prompt_token_count(self):
        """Test that consensus prompt is under 100 tokens."""
        token_count = len(self.tokenizer.encode(CONSENSUS_PROMPT))
        
        print(f"Consensus prompt token count: {token_count}")
        print(f"Consensus prompt content: {repr(CONSENSUS_PROMPT)}")
        
        assert token_count < 100, f"Consensus prompt has {token_count} tokens, should be < 100"
    
    def test_prompts_are_meaningful(self):
        """Test that prompts are not just empty strings."""
        assert len(CHAT_PROMPT.strip()) > 0, "Chat prompt should not be empty"
        assert len(CONSENSUS_PROMPT.strip()) > 0, "Consensus prompt should not be empty"
        
        # Should contain key instruction words
        assert any(word in CHAT_PROMPT.lower() for word in ["assistant", "helpful", "ai"]), \
            "Chat prompt should contain AI assistant instructions"
        
        assert any(word in CONSENSUS_PROMPT.lower() for word in ["expert", "analysis", "perspective"]), \
            "Consensus prompt should contain expert analysis instructions"
