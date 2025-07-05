#!/bin/bash
# AI Discussion Server - Easy Installation

echo "🚀 Installing AI Discussion Server..."

# Create installation directory
INSTALL_DIR="$HOME/ai-discussion-server"
echo "📁 Installing to: $INSTALL_DIR"

# Clone or update
if [ -d "$INSTALL_DIR" ]; then
    echo "📥 Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull
else
    echo "📥 Cloning repository..."
    git clone https://github.com/YOUR_USERNAME/ai-discussion-server.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Install dependencies
echo "📦 Installing dependencies..."
python3 -m pip install -r requirements.txt

# Create .env template
if [ ! -f ".env" ]; then
    echo "🔑 Creating .env template..."
    cat > .env << 'EOF'
# Replace with your actual API keys
OPENROUTER_API_KEY=your_openrouter_key_here
GEMINI_API_KEY=your_gemini_key_here
EOF
    echo "⚠️  Please edit .env file with your API keys!"
fi

# Show Augment config
echo ""
echo "🎯 Add this to your Augment config:"
echo "{"
echo "  \"mcpServers\": {"
echo "    \"ai-discussion\": {"
echo "      \"command\": \"python3\","
echo "      \"args\": [\"mcp_discussion_server.py\"],"
echo "      \"cwd\": \"$INSTALL_DIR\","
echo "      \"env\": {"
echo "        \"OPENROUTER_API_KEY\": \"your_actual_key\","
echo "        \"GEMINI_API_KEY\": \"your_actual_key\""
echo "      }"
echo "    }"
echo "  }"
echo "}"
echo ""
echo "✅ Installation complete!"
echo "📝 Next steps:"
echo "1. Edit $INSTALL_DIR/.env with your API keys"
echo "2. Add the config above to Augment"
echo "3. Restart Augment"