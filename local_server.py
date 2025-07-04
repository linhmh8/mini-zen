#!/usr/bin/env python3
"""
Local HTTP Server for AI Discussion

Chạy local server để Augment có thể call qua HTTP thay vì MCP protocol.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add mcp_sdk to path
sys.path.insert(0, os.path.dirname(__file__))

import mcp_sdk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AI Discussion Server",
    description="Local server for multi-model AI discussions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global configuration state
_configured = False

def ensure_configured():
    """Ensure SDK is configured with API keys."""
    global _configured
    if not _configured:
        # Try to configure from environment variables
        api_keys = {}
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key_here":
            api_keys['openai'] = openai_key
            
        gemini_key = os.getenv("GEMINI_API_KEY") 
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            api_keys['gemini'] = gemini_key
            
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key and openrouter_key != "your_openrouter_api_key_here":
            api_keys['openrouter'] = openrouter_key
        
        if not api_keys:
            raise ValueError("No API keys found. Please set OPENAI_API_KEY, GEMINI_API_KEY, or OPENROUTER_API_KEY")
        
        mcp_sdk.configure(api_keys)
        _configured = True
        logger.info(f"SDK configured with providers: {list(api_keys.keys())}")

# Request models
class DiscussRequest(BaseModel):
    topic: str
    models: List[str] = ["deepseek/deepseek-r1", "google/gemini-flash-1.5"]
    include_claude: bool = True

class ChatRequest(BaseModel):
    message: str
    model: str = "deepseek/deepseek-r1"

class ConsensusRequest(BaseModel):
    question: str
    models: List[str] = ["deepseek/deepseek-r1"]

# Response models
class APIResponse(BaseModel):
    success: bool
    data: Any = None
    error: str = None

async def multi_model_discussion(topic: str, models: List[str] = None) -> str:
    """
    Conduct a discussion between multiple AI models.
    """
    if models is None:
        models = ["deepseek/deepseek-r1"]
    
    ensure_configured()
    
    discussion_result = f"🗣️ **Multi-Model Discussion: {topic}**\n"
    discussion_result += "=" * 60 + "\n\n"
    
    responses = []
    
    # Get individual responses from each model
    for i, model in enumerate(models, 1):
        try:
            logger.info(f"Getting response from {model}...")
            
            # Build context with previous responses
            context_prompt = f"Topic for discussion: {topic}\n\n"
            
            if responses:
                context_prompt += "Previous perspectives:\n\n"
                for j, prev_resp in enumerate(responses, 1):
                    context_prompt += f"**Model {j} ({prev_resp['model']}):**\n{prev_resp['response']}\n\n"
                
                context_prompt += f"Now provide your own unique perspective on: {topic}\n"
                context_prompt += "Consider the previous viewpoints but offer your own analysis and insights."
            else:
                context_prompt += f"Provide your perspective and analysis on: {topic}"
            
            # Get response from model
            response, _ = mcp_sdk.chat(context_prompt, model)
            
            responses.append({
                "model": model,
                "response": response
            })
            
            # Add to discussion result
            discussion_result += f"**🤖 Model {i}: {model}**\n"
            discussion_result += f"{response}\n\n"
            discussion_result += "-" * 40 + "\n\n"
            
        except Exception as e:
            logger.error(f"Error getting response from {model}: {e}")
            discussion_result += f"**❌ Model {i}: {model}**\n"
            discussion_result += f"Error: {str(e)}\n\n"
            discussion_result += "-" * 40 + "\n\n"
    
    # Add synthesis if we have multiple responses
    if len(responses) > 1:
        try:
            synthesis_prompt = f"Original topic: {topic}\n\n"
            synthesis_prompt += "Multiple AI models have provided their perspectives:\n\n"
            
            for i, resp in enumerate(responses, 1):
                synthesis_prompt += f"**Perspective {i} ({resp['model']}):**\n{resp['response']}\n\n"
            
            synthesis_prompt += """
Please provide a synthesis that:
1. Identifies key points of agreement and disagreement
2. Highlights the most valuable insights from each perspective
3. Offers a balanced conclusion
4. Points out any unique angles or blind spots

Synthesis:"""
            
            # Use the first available model for synthesis
            synthesis_model = models[0]
            synthesis_response, _ = mcp_sdk.chat(synthesis_prompt, synthesis_model)
            
            discussion_result += "**🎯 Synthesis & Conclusion**\n"
            discussion_result += f"*Synthesized by {synthesis_model}*\n\n"
            discussion_result += synthesis_response + "\n\n"
            
        except Exception as e:
            logger.error(f"Error in synthesis: {e}")
            discussion_result += f"**❌ Synthesis Error:** {str(e)}\n\n"
    
    discussion_result += f"**📊 Discussion Summary:**\n"
    discussion_result += f"- Topic: {topic}\n"
    discussion_result += f"- Models consulted: {len(responses)}/{len(models)}\n"
    discussion_result += f"- Successful responses: {len([r for r in responses if 'error' not in r])}\n"
    
    return discussion_result

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "AI Discussion Server is running", "status": "healthy"}

@app.get("/health")
async def health():
    """Health check with configuration status."""
    try:
        ensure_configured()
        return {"status": "healthy", "configured": True}
    except Exception as e:
        return {"status": "unhealthy", "configured": False, "error": str(e)}

@app.post("/discuss", response_model=APIResponse)
async def discuss(request: DiscussRequest):
    """Start a multi-model discussion."""
    try:
        # Add Claude's perspective if requested
        claude_perspective = ""
        if request.include_claude:
            claude_perspective = f"""**🤖 Claude Sonnet (Augment Assistant):**

As your Augment assistant, here's my perspective on: {request.topic}

*[This would be Claude's analysis of the topic, providing a baseline perspective before consulting other models]*

I'll now facilitate a discussion with other AI models to get diverse viewpoints on this topic.

"""
        
        # Get discussion from other models
        discussion = await multi_model_discussion(request.topic, request.models)
        
        # Combine Claude's perspective with the discussion
        full_result = claude_perspective + discussion
        
        return APIResponse(success=True, data={"discussion": full_result})
        
    except Exception as e:
        logger.error(f"Error in discuss: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=APIResponse)
async def chat(request: ChatRequest):
    """Simple chat with a specific model."""
    try:
        ensure_configured()
        
        response, _ = mcp_sdk.chat(request.message, request.model)
        
        return APIResponse(success=True, data={
            "response": response,
            "model": request.model
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/consensus", response_model=APIResponse)
async def consensus(request: ConsensusRequest):
    """Get consensus from multiple models."""
    try:
        ensure_configured()
        
        consensus_result = mcp_sdk.get_consensus(request.question, request.models)
        
        return APIResponse(success=True, data={
            "consensus": consensus_result,
            "models": request.models,
            "question": request.question
        })
        
    except Exception as e:
        logger.error(f"Error in consensus: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """List available models."""
    try:
        ensure_configured()
        from mcp_sdk.core.provider_manager import list_available_models
        models = list_available_models()
        return APIResponse(success=True, data={"models": models})
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Set API keys from environment
    os.environ.setdefault("OPENROUTER_API_KEY", "your_openrouter_api_key_here")
    os.environ.setdefault("GEMINI_API_KEY", "your_gemini_api_key_here")
    
    print("🚀 Starting AI Discussion Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🔧 Health check: http://localhost:8000/health")
    
    uvicorn.run(
        "local_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
