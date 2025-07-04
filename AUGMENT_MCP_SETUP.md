# Cách sử dụng AI Discussion MCP Server trong Augment

## 🎯 Mục tiêu

Bạn có thể gõ trong Augment:
> "Hãy thảo luận về vấn đề này giữa r1 và gemini flash"

Và Augment sẽ tự động:
1. Gọi tool `discuss` từ MCP server
2. Thảo luận giữa Claude Sonnet (bạn), DeepSeek R1, và Gemini Flash
3. Tổng hợp kết quả và đưa ra synthesis

## 🚀 Setup

### Bước 1: Copy MCP Server

Copy thư mục `mcp_sdk` vào một vị trí cố định trên máy:
```bash
cp -r /Users/linhmh/Projects/zen-mcp-server/mcp_sdk ~/ai-discussion-server/
```

### Bước 2: Configure Augment

Thêm vào Augment config (thường là `~/.config/augment/config.json` hoặc tương tự):

```json
{
  "mcpServers": {
    "ai-discussion": {
      "command": "python3",
      "args": ["mcp_discussion_server.py"],
      "cwd": "/Users/linhmh/ai-discussion-server/mcp_sdk",
      "env": {
        "OPENROUTER_API_KEY": "your_openrouter_api_key_here",
        "GEMINI_API_KEY": "your_gemini_api_key_here"
      }
    }
  }
}
```

**Lưu ý:** Thay đổi `cwd` path cho phù hợp với vị trí bạn copy server.

### Bước 3: Restart Augment

Restart Augment để load MCP server mới.

## 🛠️ Available Tools

### 1. `discuss` - Multi-Model Discussion

**Mô tả:** Tạo cuộc thảo luận giữa nhiều AI models về một topic

**Usage trong Augment:**
```
Hãy thảo luận về "Should I use React or Vue for my startup?" giữa r1 và gemini flash
```

**Parameters:**
- `topic` (required): Chủ đề thảo luận
- `models` (optional): List models để tham gia
- `include_claude` (optional): Có bao gồm Claude perspective không

**Example output:**
```
🗣️ Multi-Model Discussion: Should I use React or Vue for my startup?
============================================================

🤖 Claude Sonnet (Augment Assistant):
As your Augment assistant, here's my perspective on: Should I use React or Vue for my startup?
[Claude's analysis...]

🤖 Model 1: deepseek/deepseek-r1
[DeepSeek R1's analysis...]

🤖 Model 2: google/gemini-flash-1.5  
[Gemini's analysis...]

🎯 Synthesis & Conclusion
[Combined analysis from all models...]
```

### 2. `chat` - Simple Chat

**Mô tả:** Chat đơn giản với một model cụ thể

**Usage:**
```
Chat với deepseek r1: "Explain async/await in Python"
```

### 3. `consensus` - Multi-Model Consensus

**Mô tả:** Lấy consensus từ nhiều models

**Usage:**
```
Lấy consensus về "Best database for a social media app"
```

## 🎨 Usage Examples trong Augment

### Example 1: Architecture Discussion
```
User: Hãy thảo luận về microservices vs monolith cho startup giữa r1 và gemini

Augment sẽ call: discuss(topic="microservices vs monolith cho startup", models=["deepseek/deepseek-r1", "google/gemini-flash-1.5"])
```

### Example 2: Technology Choice
```
User: So sánh Python vs Go cho backend API, cần ý kiến từ nhiều AI

Augment sẽ call: discuss(topic="Python vs Go cho backend API")
```

### Example 3: Code Review Discussion
```
User: Review code này và thảo luận cách improve:
[code snippet]

Augment sẽ call: discuss(topic="Code review và improvement suggestions cho: [code]")
```

## 🔧 Recommended Models

### Free/Cheap Models (OpenRouter):
- `deepseek/deepseek-r1` - Reasoning model mới nhất
- `deepseek/deepseek-chat` - Chat model tốt
- `google/gemini-flash-1.5` - Gemini qua OpenRouter
- `meta-llama/llama-3.2-3b-instruct:free` - Free model

### Direct API Models:
- `gemini-1.5-flash` - Gemini trực tiếp (nếu có API key)

## 🎯 Workflow trong Augment

1. **User gõ request** với từ khóa như "thảo luận", "discuss", "so sánh"
2. **Augment nhận diện** cần multi-model discussion
3. **Augment calls** `discuss` tool với topic và models
4. **MCP server** thực hiện:
   - Lấy perspective từ Claude (nếu enabled)
   - Gọi từng model để lấy analysis
   - Tổng hợp synthesis
5. **Return kết quả** formatted cho user

## 🐛 Troubleshooting

### Server không start:
```bash
# Test manually
cd ~/ai-discussion-server/mcp_sdk
OPENROUTER_API_KEY="your-key" python3 mcp_discussion_server.py
```

### Model không available:
- Check model names trên OpenRouter
- Verify API keys
- Try fallback models

### Augment không thấy tools:
- Check config path
- Restart Augment
- Check logs

## 🚀 Advanced Usage

### Custom Model Lists:
```json
{
  "topic": "Best programming language for AI",
  "models": ["deepseek/deepseek-r1", "deepseek/deepseek-chat", "google/gemini-flash-1.5"],
  "include_claude": true
}
```

### Specialized Discussions:
- **Code Review:** Include code snippets in topic
- **Architecture:** Focus on scalability and trade-offs  
- **Technology Choice:** Compare pros/cons
- **Problem Solving:** Multi-angle analysis

## 💡 Tips

1. **Be specific** trong topic để có analysis tốt hơn
2. **Use 2-3 models** cho balance giữa quality và speed
3. **Include context** trong topic (startup size, requirements, etc.)
4. **Try different model combinations** cho perspectives khác nhau

Bây giờ bạn có thể gõ trong Augment và có cuộc thảo luận multi-AI ngay lập tức! 🎉
