# Sử dụng MCP SDK trong Augment

## Cách 1: Function Calls trực tiếp (Khuyến nghị)

### Setup

1. **Copy mcp_sdk folder** vào project của bạn
2. **Set environment variables** với API keys:

```bash
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key" 
export OPENROUTER_API_KEY="your-openrouter-key"
```

### Import và sử dụng

```python
# Import function interface
from mcp_sdk.function_interface import ai_chat, ai_consensus, configure_api_keys

# Hoặc configure trực tiếp (nếu không dùng env vars)
configure_api_keys({
    'openai': 'your-openai-key',
    'gemini': 'your-gemini-key', 
    'openrouter': 'your-openrouter-key'
})
```

### Các function có sẵn

#### 1. `ai_chat()` - AI Conversation với Context

```python
# Chat đơn giản
result = ai_chat("Hello, how are you?", "deepseek/deepseek-r1")
print(result['response'])

# Multi-turn conversation với context preservation
result1 = ai_chat("My name is Alice", "deepseek/deepseek-r1")
result2 = ai_chat("What's my name?", "deepseek/deepseek-r1", result1['history'])
print(result2['response'])  # Sẽ nhớ tên "Alice"

# Response format:
{
    "success": True,
    "response": "AI response text",
    "history": [...],  # Updated conversation history
    "model_used": "deepseek/deepseek-r1",
    "turn_count": 2
}
```

#### 2. `ai_consensus()` - Multi-Model Consensus

```python
# Consensus từ nhiều models
result = ai_consensus(
    "What are the pros and cons of Python vs JavaScript?",
    ["deepseek/deepseek-r1", "meta-llama/llama-3.2-3b-instruct:free"]
)
print(result['consensus'])

# Single model consensus
result = ai_consensus("Explain machine learning", ["deepseek/deepseek-r1"])

# Response format:
{
    "success": True,
    "consensus": "Synthesized response from all models",
    "models_consulted": ["model1", "model2"],
    "model_count": 2
}
```

### Recommended Models (Free/Cheap)

#### OpenRouter Models (Miễn phí hoặc rẻ):
- `deepseek/deepseek-r1` - Mới nhất, reasoning model
- `deepseek/deepseek-chat` - Chat model tốt
- `meta-llama/llama-3.2-3b-instruct:free` - Miễn phí
- `microsoft/phi-3-mini-128k-instruct:free` - Miễn phí
- `google/gemini-flash-1.5` - Qua OpenRouter

#### Gemini Models (Với API key):
- `gemini-1.5-flash` - Nhanh, miễn phí quota
- `gemini-1.5-pro` - Mạnh hơn

### Example Usage trong Augment

```python
# File: ai_helper.py
from mcp_sdk.function_interface import ai_chat, ai_consensus

def smart_code_review(code: str) -> str:
    """AI code review với consensus từ nhiều models."""
    prompt = f"Review this code and suggest improvements:\n\n{code}"
    
    result = ai_consensus(prompt, [
        "deepseek/deepseek-r1",
        "meta-llama/llama-3.2-3b-instruct:free"
    ])
    
    return result['consensus'] if result['success'] else f"Error: {result['error']}"

def interactive_coding_assistant():
    """Interactive coding assistant với context."""
    history = []
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        result = ai_chat(user_input, "deepseek/deepseek-r1", history)
        if result['success']:
            print(f"AI: {result['response']}")
            history = result['history']
        else:
            print(f"Error: {result['error']}")

# Sử dụng
code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

review = smart_code_review(code)
print(review)
```

## Cách 2: MCP Server (Nếu cần MCP protocol)

Nếu bạn muốn sử dụng qua MCP protocol:

1. **Install MCP dependencies** (nếu có):
```bash
pip install mcp>=1.0.0
```

2. **Run MCP server**:
```bash
python3 mcp_server.py
```

3. **Configure trong Augment** với `augment_config.json`

## Token Optimization

SDK được tối ưu cho token usage:
- **Chat prompt**: ~12 tokens
- **Consensus prompt**: ~55 tokens  
- **Total overhead**: < 100 tokens per request

## Error Handling

```python
result = ai_chat("Hello", "invalid-model")
if not result['success']:
    print(f"Error: {result['error']}")
    # Fallback to different model
    result = ai_chat("Hello", "deepseek/deepseek-r1")
```

## Best Practices

1. **Sử dụng free models** cho development: `deepseek/deepseek-r1`
2. **Preserve conversation history** cho multi-turn chats
3. **Handle errors gracefully** với fallback models
4. **Use consensus** cho important decisions
5. **Set environment variables** thay vì hardcode API keys

## Troubleshooting

- **"No provider found"**: Check model name spelling
- **API errors**: Verify API keys và model availability  
- **Import errors**: Ensure mcp_sdk folder trong Python path
- **Token limits**: Use shorter prompts hoặc fewer models trong consensus
