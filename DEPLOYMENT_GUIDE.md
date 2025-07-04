# 🚀 AI Discussion Server - Deployment Guide

## 🏠 Option 1: Local Development

### Quick Start
```bash
# Clone và setup
git clone <repo>
cd mcp_sdk

# Start server (auto-installs dependencies)
./start_local.sh
```

Server sẽ chạy tại:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs  
- **Health:** http://localhost:8000/health

### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API keys
export OPENROUTER_API_KEY="your-key"
export GEMINI_API_KEY="your-key"

# Start server
python local_server.py
```

## 🌐 Option 2: Docker Local

```bash
# Build và run với Docker
docker-compose up --build

# Hoặc chỉ build
docker build -t ai-discussion-server .
docker run -p 8000:8000 \
  -e OPENROUTER_API_KEY="your-key" \
  -e GEMINI_API_KEY="your-key" \
  ai-discussion-server
```

## ☁️ Option 3: Cloud Deployment

### Railway (Khuyến nghị - Free tier)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login và deploy
railway login
railway init
railway add

# Set environment variables
railway variables set OPENROUTER_API_KEY="your-key"
railway variables set GEMINI_API_KEY="your-key"

# Deploy
railway up
```

### Render.com (Free tier)
1. Connect GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python local_server.py`
4. Add environment variables
5. Deploy

### Heroku
```bash
# Install Heroku CLI
heroku create ai-discussion-server

# Set environment variables
heroku config:set OPENROUTER_API_KEY="your-key"
heroku config:set GEMINI_API_KEY="your-key"

# Deploy
git push heroku main
```

### DigitalOcean App Platform
1. Create new app from GitHub
2. Set build command: `pip install -r requirements.txt`
3. Set run command: `python local_server.py`
4. Add environment variables
5. Deploy

## 🔧 API Usage

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Multi-Model Discussion
```bash
curl -X POST "http://localhost:8000/discuss" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Should I use React or Vue for my startup?",
    "models": ["deepseek/deepseek-r1", "google/gemini-flash-1.5"],
    "include_claude": true
  }'
```

### 3. Simple Chat
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain async programming in Python",
    "model": "deepseek/deepseek-r1"
  }'
```

### 4. Consensus
```bash
curl -X POST "http://localhost:8000/consensus" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Best database for a social media app?",
    "models": ["deepseek/deepseek-r1"]
  }'
```

### 5. List Models
```bash
curl http://localhost:8000/models
```

## 🔗 Integration với Augment

### Option A: HTTP Calls (Khuyến nghị)
Augment có thể call HTTP API trực tiếp:

```python
import requests

def discuss_with_ai(topic, models=None):
    response = requests.post("http://localhost:8000/discuss", json={
        "topic": topic,
        "models": models or ["deepseek/deepseek-r1"],
        "include_claude": True
    })
    return response.json()["data"]["discussion"]

# Usage
result = discuss_with_ai("Python vs Go for backend")
print(result)
```

### Option B: MCP Protocol
Nếu Augment hỗ trợ MCP, sử dụng `mcp_discussion_server.py`

## 🎯 Usage Examples

### Startup Decision Making
```bash
curl -X POST "http://localhost:8000/discuss" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Microservices vs Monolith for early-stage startup",
    "models": ["deepseek/deepseek-r1"],
    "include_claude": true
  }'
```

### Technology Comparison
```bash
curl -X POST "http://localhost:8000/consensus" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "PostgreSQL vs MongoDB for e-commerce platform",
    "models": ["deepseek/deepseek-r1"]
  }'
```

### Code Review Discussion
```bash
curl -X POST "http://localhost:8000/discuss" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Review this Python function and suggest improvements: def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
    "models": ["deepseek/deepseek-r1"],
    "include_claude": false
  }'
```

## 🔒 Security & Production

### Environment Variables
```bash
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here...
GEMINI_API_KEY=your_gemini_api_key_here...

# Optional
OPENAI_API_KEY=your_openai_api_key_here
PORT=8000
HOST=0.0.0.0
```

### Production Considerations
1. **Rate Limiting:** Add rate limiting middleware
2. **Authentication:** Add API key authentication
3. **CORS:** Configure CORS for your domain
4. **Logging:** Set up proper logging
5. **Monitoring:** Add health checks và metrics
6. **SSL:** Use HTTPS in production

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring

### Health Check Endpoint
```bash
# Check if server is healthy
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "configured": true
}
```

### Logs
```bash
# View logs (Docker)
docker-compose logs -f

# View logs (local)
tail -f server.log
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

2. **API keys not working**
   ```bash
   curl http://localhost:8000/health
   # Check if configured: true
   ```

3. **Model not found**
   ```bash
   curl http://localhost:8000/models
   # Check available models
   ```

4. **CORS errors**
   - Server has CORS enabled for all origins
   - Check browser console for errors

### Performance Tuning
- Use multiple workers: `uvicorn local_server:app --workers 4`
- Add Redis caching for repeated requests
- Implement request queuing for high load

## 🚀 Ready to Deploy!

Choose your preferred deployment method:
- **Local Development:** `./start_local.sh`
- **Docker:** `docker-compose up`
- **Cloud:** Railway, Render, Heroku, DigitalOcean

Server sẽ expose REST API để Augment có thể call và thực hiện multi-model discussions! 🎉
