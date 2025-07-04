#!/bin/bash
# Setup script for standalone AI Discussion Server

echo "🚀 Setting up AI Discussion Server..."
echo "=" * 50

# Get current directory
CURRENT_DIR=$(pwd)
echo "📍 Current directory: $CURRENT_DIR"

# Check if we're in the right directory
if [ ! -f "mcp_discussion_server.py" ]; then
    echo "❌ Error: mcp_discussion_server.py not found!"
    echo "Please run this script from the mcp_sdk directory"
    exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found! Please install Python 3.8+"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies!"
    exit 1
fi

# Test server
echo "🧪 Testing server..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    import mcp_sdk
    print('✅ MCP SDK imported successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Server test failed!"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔑 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys!"
fi

# Make scripts executable
chmod +x start_local.sh
chmod +x setup_standalone.sh

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys (if needed)"
echo "2. Start server: ./start_local.sh"
echo "3. Configure Augment with this path: $CURRENT_DIR"
echo "4. Restart Augment"
echo "5. Test in Augment chat: 'Hãy thảo luận về React vs Vue'"
echo ""
echo "🔧 Augment config example:"
echo '{'
echo '  "mcpServers": {'
echo '    "ai-discussion": {'
echo '      "command": "python3",'
echo '      "args": ["mcp_discussion_server.py"],'
echo "      \"cwd\": \"$CURRENT_DIR\","
echo '      "env": {'
echo '        "OPENROUTER_API_KEY": "your-key",'
echo '        "GEMINI_API_KEY": "your-key"'
echo '      }'
echo '    }'
echo '  }'
echo '}'
echo ""
echo "🚀 Ready to go!"
