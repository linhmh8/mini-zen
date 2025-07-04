# 🤖 AI Discussion Server

Standalone MCP server cho multi-model AI discussions. Có thể call từ Augment để thảo luận giữa nhiều AI models.

## 🚀 Quick Start

### 1. Tách folder này ra khỏi project
```bash
# Copy toàn bộ folder mcp_sdk ra ngoài
cp -r mcp_sdk ~/ai-discussion-server
cd ~/ai-discussion-server
```

### 2. Chạy server
```bash
# Cách 1: Auto setup (khuyến nghị)
./start_local.sh

# Cách 2: Manual
python3 -m pip install -r requirements.txt
python3 local_server.py
```

### 3. Configure Augment
Thêm vào Augment config:
```json
{
  "mcpServers": {
    "ai-discussion": {
      "command": "python3",
      "args": ["mcp_discussion_server.py"],
      "cwd": "/Users/your-username/ai-discussion-server",
      "env": {
        "OPENROUTER_API_KEY": "your_openrouter_api_key_here",
        "GEMINI_API_KEY": "your_gemini_api_key_here"
      }
    }
  }
}
```

### 4. Restart Augment

### 5. Sử dụng trong Augment chat
```
Hãy thảo luận về React vs Vue giữa r1 và gemini flash
```

## 🎯 Available Tools trong Augment

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

## Supported Models

### OpenAI
- `gpt-4o-mini`
- `gpt-4o`
- `o3-mini`
- `o3`

### Google Gemini
- `gemini-1.5-flash`
- `gemini-1.5-pro`
- `gemini-2.5-flash`
- `gemini-2.5-pro`

### OpenRouter
- Various models available through OpenRouter API

## Testing

Run the test suite:

```bash
# Unit tests
python -m pytest tests/ -v

# Real API tests (requires API keys)
python test_real_api.py
```

## Token Optimization

This SDK is designed for minimal token usage:
- Chat prompt: ~12 tokens
- Consensus prompt: ~55 tokens

Both prompts are under the 100-token target for maximum efficiency.

## Architecture

The SDK follows a clean architecture:

```
mcp_sdk/
├── core/
│   ├── main_logic.py      # Core chat and consensus functions
│   └── provider_manager.py # Provider management and routing
├── providers/             # AI model providers
├── system_prompts/        # Minimized system prompts
└── utils/                 # Essential utilities
```

## License

MIT License
