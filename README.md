# 🤖 AI Discussion MCP Server

Optimized MCP server for multi-model AI discussions with intelligent context management and token optimization.

## ✨ Features

- **Multi-Model Support**: Claude 4.0 (Augment internal), Gemini 2.5 Pro/Flash, DeepSeek R1
- **Context Optimization**: Intelligent token management and compression
- **Cost Efficient**: Claude 4.0 free via Augment, optimized pricing for other models
- **Parallel Processing**: Simultaneous model calls for faster discussions
- **Smart Context Sharing**: All models receive the same conversation context

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Create or update `augment_config.json`:
```json
{
  "openrouter_api_key": "your_openrouter_key_for_deepseek_r1",
  "gemini_api_key": "your_google_api_key_for_gemini"
}
```

### 3. Add to Augment
Add to your Augment MCP configuration:
```json
{
  "mcpServers": {
    "ai-discussion": {
      "command": "python3",
      "args": ["mcp_discussion_server.py"],
      "cwd": "/path/to/mcp_sdk",
      "env": {
        "OPENROUTER_API_KEY": "your_openrouter_api_key",
        "GEMINI_API_KEY": "your_gemini_api_key"
      }
    }
  }
}
```

### 4. Usage in Augment
```
Thảo luận giữa Claude, Gemini và DeepSeek về cách tối ưu database performance
```

## 🛠️ Available Tools

### Core Discussion Tools

### 1. `discuss` - Multi-Model Discussion
**Purpose:** Detailed multi-perspective analysis với synthesis
**Usage:** "Hãy thảo luận về [topic] giữa r1 và gemini"

**Examples:**
- "Thảo luận về microservices vs monolith cho startup"
- "So sánh Python vs Go cho backend API"
- "Discuss pros and cons of TypeScript"

### 2. `chat` - Simple Chat
**Purpose:** Direct conversation với specific model
**Usage:** "Chat với [model] về [topic]"

**Examples:**
- "Chat với deepseek về async programming"
- "Hỏi r1 về best practices cho REST API"
- "Ask AI about JWT implementation"

### 3. `consensus` - Multi-Model Consensus
**Purpose:** Focused opinion synthesis với clear recommendation
**Usage:** "Lấy consensus về [question]"

**Examples:**
- "Consensus về database choice cho e-commerce platform"
- "Ý kiến chung về cloud providers (AWS vs GCP vs Azure)"
- "Lấy consensus về programming language cho AI project"

**📊 Tool Comparison:**
- **`discuss`** = Detailed exploration 🔍
- **`chat`** = Quick answers ⚡
- **`consensus`** = Clear decisions 🎯

## API Reference

### `configure(api_keys: dict)`

Configure API keys for the providers.

**Parameters:**
- `api_keys`: Dictionary with provider names as keys and API keys as values
  - Supported providers: `'openai'`, `'gemini'`, `'openrouter'`

### `chat(prompt: str, model: str, history: list = None)`

Start or continue a conversation.

**Parameters:**
- `prompt`: The user's message
- `model`: Model name to use (e.g., `'gpt-4o-mini'`, `'gemini-1.5-flash'`)
- `history`: Previous conversation history (optional)

**Returns:**
- `tuple`: `(response, new_history)` where response is the AI's reply and new_history contains the updated conversation history

### `get_consensus(prompt: str, models: list[str])`

Get consensus from multiple models.

**Parameters:**
- `prompt`: The question or topic to get consensus on
- `models`: List of model names to consult

**Returns:**
- `str`: Synthesized consensus response from all models

## 🎯 Supported Models

### Claude (Augment Internal - FREE)
- `claude-4` - Claude 4.0 via Augment internal (no API costs)
- `claude` - General Claude reference

### Google Gemini
- `gemini-2.5-pro` - 2M context window, best quality
- `gemini-2.5-flash` - 1M context window, fast & cost-effective
- `gemini-2.5-flash-preview-04-17` - Preview version
- `gemini-2.5-flash-lite-preview-06-17` - Lightweight version

### OpenRouter
- `deepseek-r1` - Cost-effective reasoning model
- `deepseek/deepseek-r1` - Full OpenRouter format

## 💰 Cost Optimization

Optimized for minimal costs:
- **Claude 4.0**: $0.00 (free via Augment internal)
- **Gemini 2.5 Flash**: $0.0008 per 6.5K tokens
- **DeepSeek R1**: $0.0112 per 6.5K tokens

## 🚀 Performance Features

- **Context Compression**: 31% reduction with quality preservation
- **Token Caching**: Faster estimation with LRU cache
- **Parallel Processing**: Multiple model calls simultaneously
- **Smart Budget Management**: Intelligent token allocation

## 📁 Project Structure

```
mcp_sdk/
├── core/
│   ├── main_logic.py           # Core chat and consensus functions
│   └── provider_manager.py     # Provider management and routing
├── providers/                  # AI model providers (Google, OpenRouter)
├── system_prompts/             # Optimized system prompts
└── utils/
    ├── token_utils.py          # Model-specific token estimation
    ├── context_compression.py  # Intelligent text compression
    ├── model_optimizer.py      # Per-model optimizations
    ├── token_budget.py         # Budget management
    └── conversation_memory.py  # Context persistence
```

## 📚 Documentation

- `OPTIMIZATION_SUMMARY.md` - Detailed optimization guide and results
- `README.md` - This file

## 📄 License

MIT License
