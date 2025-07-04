"""
Test cases for consensus workflow functionality
"""

import pytest
from unittest.mock import Mock, patch

import mcp_sdk
from mcp_sdk.providers.base import ModelResponse


class TestConsensusWorkflow:
    """Test consensus workflow functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        # Mock API keys for testing
        self.test_api_keys = {
            'openai': 'test-openai-key',
            'gemini': 'test-gemini-key'
        }
    
    @patch('mcp_sdk.core.provider_manager.OpenAIModelProvider')
    @patch('mcp_sdk.core.provider_manager.GeminiModelProvider')
    def test_get_consensus_with_multiple_models(self, mock_gemini, mock_openai):
        """Test consensus gathering with multiple models."""
        # Setup mock providers
        mock_openai_provider = Mock()
        mock_gemini_provider = Mock()
        
        # Mock responses from different models
        openai_response = ModelResponse(
            content="Python Pros: Easy to learn, great libraries, readable code. Cons: Slower execution, GIL limitations. Go Pros: Fast compilation, excellent concurrency, simple deployment. Cons: Verbose error handling, smaller ecosystem.",
            model_name="gpt-3.5-turbo",
            usage={"input_tokens": 20, "output_tokens": 45}
        )
        
        gemini_response = ModelResponse(
            content="Python excels in data science and rapid prototyping with rich libraries like NumPy, pandas. However, performance can be limiting for CPU-intensive tasks. Go shines in system programming and microservices with superior concurrency model and fast compilation, but has steeper learning curve for beginners.",
            model_name="gemini-1.5-flash",
            usage={"input_tokens": 35, "output_tokens": 52}
        )
        
        # Synthesis response
        synthesis_response = ModelResponse(
            content="Both experts agree that Python and Go serve different purposes effectively. Python is ideal for data science, AI/ML, and rapid prototyping due to its extensive libraries and readability. Go excels in system programming, microservices, and performance-critical applications with its superior concurrency and compilation speed. The choice depends on project requirements: Python for data-heavy and research work, Go for scalable backend systems.",
            model_name="gpt-3.5-turbo",
            usage={"input_tokens": 100, "output_tokens": 75}
        )
        
        # Configure mock providers
        mock_openai_provider.generate_content.side_effect = [openai_response, synthesis_response]
        mock_openai_provider.validate_model_name.side_effect = lambda x: x in ["gpt-3.5-turbo"]
        
        mock_gemini_provider.generate_content.return_value = gemini_response
        mock_gemini_provider.validate_model_name.side_effect = lambda x: x in ["gemini-1.5-flash"]
        
        mock_openai.return_value = mock_openai_provider
        mock_gemini.return_value = mock_gemini_provider
        
        # Configure SDK
        mcp_sdk.configure(self.test_api_keys)
        
        # Test consensus
        result = mcp_sdk.get_consensus(
            "Pros and cons of Python vs Go", 
            ["gpt-3.5-turbo", "gemini-1.5-flash"]
        )
        
        # Assertions
        assert result is not None
        assert len(result) > 0
        assert "Python" in result
        assert "Go" in result
        # Should contain synthesized insights from both models
        assert any(word in result.lower() for word in ["both", "agree", "different", "choice", "depends"])
    
    @patch('mcp_sdk.core.provider_manager.OpenAIModelProvider')
    def test_consensus_handles_single_model(self, mock_openai):
        """Test consensus with single model (should work like regular chat)."""
        # Setup mock provider
        mock_provider = Mock()
        mock_response = ModelResponse(
            content="Quantum computing leverages quantum mechanical phenomena like superposition and entanglement to process information in ways classical computers cannot. Quantum bits (qubits) can exist in multiple states simultaneously, enabling parallel computation. Key applications include cryptography, optimization, and simulation of quantum systems.",
            model_name="gpt-4o-mini",
            usage={"input_tokens": 15, "output_tokens": 60}
        )
        
        mock_provider.generate_content.return_value = mock_response
        mock_provider.validate_model_name.return_value = True
        
        mock_openai.return_value = mock_provider
        
        # Configure SDK
        mcp_sdk.configure(self.test_api_keys)
        
        # Test single model consensus
        result = mcp_sdk.get_consensus("Explain quantum computing", ["gpt-4o-mini"])
        
        # Assertions
        assert result is not None
        assert len(result) > 0
        assert "quantum" in result.lower()
        assert result == mock_response.content  # Should be identical to single model response
    
    @patch('mcp_sdk.core.provider_manager.OpenAIModelProvider')
    @patch('mcp_sdk.core.provider_manager.GeminiModelProvider')
    def test_consensus_with_model_failure(self, mock_gemini, mock_openai):
        """Test consensus when one model fails."""
        # Setup mock providers
        mock_openai_provider = Mock()
        mock_gemini_provider = Mock()
        
        # OpenAI works fine
        openai_response = ModelResponse(
            content="Machine learning is a subset of AI that enables computers to learn from data without explicit programming.",
            model_name="gpt-3.5-turbo",
            usage={"input_tokens": 10, "output_tokens": 25}
        )
        
        # Gemini fails
        mock_openai_provider.generate_content.return_value = openai_response
        mock_openai_provider.validate_model_name.return_value = True
        
        mock_gemini_provider.generate_content.side_effect = Exception("API Error")
        mock_gemini_provider.validate_model_name.return_value = True
        
        mock_openai.return_value = mock_openai_provider
        mock_gemini.return_value = mock_gemini_provider
        
        # Configure SDK
        mcp_sdk.configure(self.test_api_keys)
        
        # Test consensus with failure
        result = mcp_sdk.get_consensus(
            "What is machine learning?", 
            ["gpt-3.5-turbo", "gemini-1.5-flash"]
        )
        
        # Should still work with the successful model
        assert result is not None
        assert len(result) > 0
        assert "machine learning" in result.lower()
    
    def test_consensus_empty_models_list(self):
        """Test consensus with empty models list."""
        # Configure SDK
        mcp_sdk.configure(self.test_api_keys)
        
        # Test with empty list
        with pytest.raises(ValueError, match="At least one model must be specified"):
            mcp_sdk.get_consensus("Test question", [])
    
    @patch('mcp_sdk.core.provider_manager.get_provider_for_model')
    def test_consensus_no_available_providers(self, mock_get_provider):
        """Test consensus when no providers are available."""
        # Mock no providers available
        mock_get_provider.return_value = None
        
        # Configure SDK
        mcp_sdk.configure(self.test_api_keys)
        
        # Test with unavailable models
        with pytest.raises(ValueError, match="No provider available for model"):
            mcp_sdk.get_consensus("Test question", ["unavailable-model"])
