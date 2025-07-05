# 🚀 Quick Install - AI Discussion Server

## One-line install:
```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/ai-discussion-server/main/install.sh | bash
```

## Manual install:
```bash
git clone https://github.com/YOUR_USERNAME/ai-discussion-server.git ~/ai-discussion-server
cd ~/ai-discussion-server
python3 -m pip install -r requirements.txt
```

## Setup API Keys:
1. Get OpenRouter key: https://openrouter.ai/keys
2. Edit `~/ai-discussion-server/.env`:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-key
GEMINI_API_KEY=your-gemini-key
```

## Add to Augment:
```json
{
  "mcpServers": {
    "ai-discussion": {
      "command": "python3",
      "args": ["mcp_discussion_server.py"],
      "cwd": "/Users/YOUR_USERNAME/ai-discussion-server",
      "env": {
        "OPENROUTER_API_KEY": "your_actual_key",
        "GEMINI_API_KEY": "your_actual_key"
      }
    }
  }
}
```

## Usage:
```
Hãy thảo luận về React vs Vue giữa r1 và gemini flash
```

**That's it!** 🎉