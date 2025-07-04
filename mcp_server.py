#!/usr/bin/env python3
"""
MCP Server for mcp_sdk

This server exposes the mcp_sdk functionality as MCP tools that can be called
from Augment or other MCP clients.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List

# Add mcp_sdk to path
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    ToolsCapability,
    ServerCapabilities,
)

import mcp_sdk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("mcp-sdk-server")

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

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="chat",
            description="Start or continue an AI conversation with context preservation",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The message to send to the AI"
                    },
                    "model": {
                        "type": "string", 
                        "description": "Model to use (e.g., 'gpt-4o-mini', 'gemini-1.5-flash')",
                        "default": "gpt-4o-mini"
                    },
                    "history": {
                        "type": "array",
                        "description": "Previous conversation history (optional)",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {"type": "string"},
                                "content": {"type": "string"}
                            }
                        },
                        "default": []
                    }
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="consensus",
            description="Get consensus analysis from multiple AI models",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The question or topic to get consensus on"
                    },
                    "models": {
                        "type": "array",
                        "description": "List of models to consult",
                        "items": {"type": "string"},
                        "default": ["gpt-4o-mini", "gemini-1.5-flash"]
                    }
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="configure_sdk",
            description="Configure API keys for the SDK",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_keys": {
                        "type": "object",
                        "description": "API keys for different providers",
                        "properties": {
                            "openai": {"type": "string"},
                            "gemini": {"type": "string"},
                            "openrouter": {"type": "string"}
                        }
                    }
                },
                "required": ["api_keys"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "configure_sdk":
            global _configured
            api_keys = arguments.get("api_keys", {})
            mcp_sdk.configure(api_keys)
            _configured = True
            return [TextContent(
                type="text",
                text=f"SDK configured successfully with providers: {list(api_keys.keys())}"
            )]
        
        # Ensure SDK is configured for other tools
        ensure_configured()
        
        if name == "chat":
            prompt = arguments["prompt"]
            model = arguments.get("model", "gpt-4o-mini")
            history = arguments.get("history", [])
            
            response, new_history = mcp_sdk.chat(prompt, model, history)
            
            result = {
                "response": response,
                "history": new_history,
                "model_used": model
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "consensus":
            prompt = arguments["prompt"]
            models = arguments.get("models", ["gpt-4o-mini", "gemini-1.5-flash"])
            
            consensus = mcp_sdk.get_consensus(prompt, models)
            
            result = {
                "consensus": consensus,
                "models_consulted": models
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

@server.list_resources()
async def handle_list_resources():
    """List available resources."""
    return []

@server.read_resource()
async def handle_read_resource(uri: str):
    """Read a resource."""
    raise ValueError(f"Resource not found: {uri}")

async def main():
    """Main entry point."""
    # Configure server capabilities
    server.request_context.session.capabilities = ServerCapabilities(
        tools=ToolsCapability()
    )
    
    logger.info("MCP SDK Server starting...")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-sdk-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities()
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
