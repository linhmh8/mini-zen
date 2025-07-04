"""
Test cases for conversation threading functionality
"""

import pytest
import os
from unittest.mock import Mock, patch

import mcp_sdk
from mcp_sdk.providers.base import ModelResponse


class TestConversationThreading:
    """Test conversation threading functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        # Mock API keys for testing
        self.test_api_keys = {
            'openai': 'test-openai-key',
            'gemini': 'test-gemini-key'
        }
    
    @patch('mcp_sdk.core.provider_manager.OpenAIModelProvider')
    @patch('mcp_sdk.core.provider_manager.GeminiModelProvider')
    def test_single_turn_chat(self, mock_gemini, mock_openai):
        """Test single turn chat functionality."""
        # Setup mock provider
        mock_provider = Mock()
        mock_response = ModelResponse(
            content="Hello! I'm doing well, thank you for asking.",
            model_name="gpt-4o-mini",
            usage={"input_tokens": 10, "output_tokens": 15}
        )
        mock_provider.generate_content.return_value = mock_response
        mock_provider.validate_model_name.return_value = True
        
        mock_openai.return_value = mock_provider
        
        # Configure SDK
        mcp_sdk.configure(self.test_api_keys)
        
        # Test single turn chat
        response, history = mcp_sdk.chat("Hello", "gpt-4o-mini")
        
        # Assertions
        assert response is not None
        assert len(response) > 0
        assert len(history) == 2  # User message + assistant response
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == response
    
    @patch('mcp_sdk.core.provider_manager.OpenAIModelProvider')
    @patch('mcp_sdk.core.provider_manager.GeminiModelProvider')
    def test_multi_turn_conversation(self, mock_gemini, mock_openai):
        """Test multi-turn conversation with context preservation."""
        # Setup mock provider
        mock_provider = Mock()
        
        # First response
        mock_response_1 = ModelResponse(
            content="Nice to meet you, Alex!",
            model_name="gpt-4o-mini",
            usage={"input_tokens": 10, "output_tokens": 8}
        )

        # Second response (should remember the name)
        mock_response_2 = ModelResponse(
            content="Your name is Alex, as you told me earlier.",
            model_name="gpt-4o-mini",
            usage={"input_tokens": 25, "output_tokens": 12}
        )
        
        mock_provider.generate_content.side_effect = [mock_response_1, mock_response_2]
        mock_provider.validate_model_name.return_value = True
        
        mock_openai.return_value = mock_provider
        
        # Configure SDK
        mcp_sdk.configure(self.test_api_keys)
        
        # First turn
        response_1, history_1 = mcp_sdk.chat("My name is Alex", "gpt-4o-mini")
        
        # Second turn with history
        response_2, history_2 = mcp_sdk.chat("What is my name?", "gpt-4o-mini", history=history_1)
        
        # Assertions
        assert "Alex" in response_2
        assert len(history_2) == 4  # 2 turns, 2 messages each
        
        # Verify conversation flow
        assert history_2[0]["content"] == "My name is Alex"
        assert history_2[1]["content"] == response_1
        assert history_2[2]["content"] == "What is my name?"
        assert history_2[3]["content"] == response_2
    
    @patch('mcp_sdk.core.provider_manager.OpenAIModelProvider')
    @patch('mcp_sdk.core.provider_manager.GeminiModelProvider')
    def test_context_is_not_leaking(self, mock_gemini, mock_openai):
        """Test that different sessions don't leak context."""
        # Setup mock provider
        mock_provider = Mock()
        
        # Responses for session A
        mock_response_a1 = ModelResponse(
            content="Hello Alice! Nice to meet you.",
            model_name="gpt-4o-mini",
            usage={"input_tokens": 10, "output_tokens": 10}
        )

        mock_response_a2 = ModelResponse(
            content="Your name is Alice.",
            model_name="gpt-4o-mini",
            usage={"input_tokens": 20, "output_tokens": 8}
        )

        # Responses for session B
        mock_response_b1 = ModelResponse(
            content="Hello Bob! Nice to meet you.",
            model_name="gpt-4o-mini",
            usage={"input_tokens": 10, "output_tokens": 10}
        )

        mock_response_b2 = ModelResponse(
            content="Your name is Bob.",
            model_name="gpt-4o-mini",
            usage={"input_tokens": 20, "output_tokens": 8}
        )
        
        mock_provider.generate_content.side_effect = [
            mock_response_a1, mock_response_a2, 
            mock_response_b1, mock_response_b2
        ]
        mock_provider.validate_model_name.return_value = True
        
        mock_openai.return_value = mock_provider
        
        # Configure SDK
        mcp_sdk.configure(self.test_api_keys)
        
        # Session A
        response_a1, history_a = mcp_sdk.chat("My name is Alice", "gpt-4o-mini")
        response_a2, history_a = mcp_sdk.chat("What is my name?", "gpt-4o-mini", history=history_a)
        
        # Session B (independent)
        response_b1, history_b = mcp_sdk.chat("My name is Bob", "gpt-4o-mini")
        response_b2, history_b = mcp_sdk.chat("What is my name?", "gpt-4o-mini", history=history_b)
        
        # Assertions - no context leaking
        assert "Alice" not in response_b2
        assert "Bob" not in response_a2
        assert "Alice" in response_a2
        assert "Bob" in response_b2
        
        # Verify histories are independent
        assert len(history_a) == 4
        assert len(history_b) == 4
        assert history_a != history_b
