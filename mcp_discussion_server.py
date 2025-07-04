#!/usr/bin/env python3
"""
MCP Discussion Server

A standalone MCP server that provides AI discussion tools.
Can be called from Augment without copying any files.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List

# Add mcp_sdk to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        TextContent,
        Tool,
        ToolsCapability,
        ServerCapabilities,
    )
except ImportError:
    print("MCP not available, running in standalone mode")
    # Fallback for testing without MCP
    class Server:
        def __init__(self, name): pass
        def list_tools(self): return lambda func: func
        def call_tool(self): return lambda func: func

    class Tool:
        def __init__(self, **kwargs): pass

    class TextContent:
        def __init__(self, **kwargs):
            self.text = kwargs.get('text', '')
            self.type = kwargs.get('type', 'text')

import mcp_sdk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("mcp-discussion-server")

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

async def multi_model_discussion(topic: str, models: List[str] = None) -> str:
    """
    Conduct a discussion between multiple AI models.
    
    Args:
        topic: The topic to discuss
        models: List of models to include in discussion
        
    Returns:
        Formatted discussion result
    """
    if models is None:
        models = ["deepseek/deepseek-r1", "gemini-1.5-flash"]
    
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

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="discuss",
            description="Start a multi-model AI discussion on any topic. Models will provide different perspectives and a synthesis will be generated.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic or question to discuss"
                    },
                    "models": {
                        "type": "array",
                        "description": "List of AI models to include in discussion (optional)",
                        "items": {"type": "string"},
                        "default": ["deepseek/deepseek-r1", "gemini-1.5-flash"]
                    },
                    "include_claude": {
                        "type": "boolean",
                        "description": "Whether to include Claude's perspective in the discussion",
                        "default": True
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="chat",
            description="Simple chat with a specific AI model",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to send to the AI"
                    },
                    "model": {
                        "type": "string",
                        "description": "AI model to use",
                        "default": "deepseek/deepseek-r1"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="consensus",
            description="Get consensus opinion from multiple AI models",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Question to get consensus on"
                    },
                    "models": {
                        "type": "array",
                        "description": "List of models to consult",
                        "items": {"type": "string"},
                        "default": ["deepseek/deepseek-r1", "gemini-1.5-flash"]
                    }
                },
                "required": ["question"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "discuss":
            topic = arguments["topic"]
            models = arguments.get("models", ["deepseek/deepseek-r1", "gemini-1.5-flash"])
            include_claude = arguments.get("include_claude", True)
            
            # Add Claude's perspective if requested
            if include_claude:
                claude_perspective = f"""**🤖 Claude Sonnet (Augment Assistant):**

As your Augment assistant, here's my perspective on: {topic}

*[This would be Claude's analysis of the topic, providing a baseline perspective before consulting other models]*

I'll now facilitate a discussion with other AI models to get diverse viewpoints on this topic.

"""
            else:
                claude_perspective = ""
            
            # Get discussion from other models
            discussion = await multi_model_discussion(topic, models)
            
            # Combine Claude's perspective with the discussion
            full_result = claude_perspective + discussion
            
            return [TextContent(type="text", text=full_result)]
        
        elif name == "chat":
            ensure_configured()
            message = arguments["message"]
            model = arguments.get("model", "deepseek/deepseek-r1")
            
            response, _ = mcp_sdk.chat(message, model)
            
            result = f"**{model}:** {response}"
            return [TextContent(type="text", text=result)]
        
        elif name == "consensus":
            ensure_configured()
            question = arguments["question"]
            models = arguments.get("models", ["deepseek/deepseek-r1", "gemini-1.5-flash"])
            
            consensus = mcp_sdk.get_consensus(question, models)
            
            result = f"**Consensus on:** {question}\n\n{consensus}\n\n*Based on {len(models)} models*"
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point for MCP server."""
    try:
        from mcp.server.stdio import stdio_server
        
        logger.info("MCP Discussion Server starting...")
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-discussion-server",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities()
                )
            )
    except ImportError:
        # Fallback for testing without MCP
        logger.info("Running in test mode (MCP not available)")
        
        # Test the discussion function
        topic = "Should startups use microservices or monolith architecture?"
        result = await multi_model_discussion(topic)
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
