#!/bin/bash
# Test NPX package locally

echo "🧪 Testing local NPX package..."

# Create test directory
TEST_DIR="/tmp/test-ai-discussion"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"

# Copy package files
cp -r . "$TEST_DIR/"
cd "$TEST_DIR"

# Test the command
echo "🚀 Testing: node bin/mcp-server.js"
OPENROUTER_API_KEY="test" GEMINI_API_KEY="test" node bin/mcp-server.js