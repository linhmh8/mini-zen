#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

// Get the directory where this package is installed
const packageDir = path.dirname(__dirname);
const pythonScript = path.join(packageDir, 'mcp_discussion_server.py');

// Check if Python is available
function findPython() {
  const pythonCommands = ['python3', 'python'];
  
  for (const cmd of pythonCommands) {
    try {
      const result = spawn(cmd, ['--version'], { stdio: 'pipe' });
      if (result) return cmd;
    } catch (e) {
      continue;
    }
  }
  
  console.error('❌ Python not found. Please install Python 3.7+');
  process.exit(1);
}

// Install Python dependencies if needed
function installDependencies() {
  const python = findPython();
  const requirementsPath = path.join(packageDir, 'requirements.txt');
  
  console.error('📦 Installing Python dependencies...');
  const install = spawn(python, ['-m', 'pip', 'install', '-r', requirementsPath], {
    stdio: 'inherit',
    cwd: packageDir
  });
  
  install.on('close', (code) => {
    if (code === 0) {
      startServer();
    } else {
      console.error('❌ Failed to install dependencies');
      process.exit(1);
    }
  });
}

// Start the MCP server
function startServer() {
  const python = findPython();
  
  const server = spawn(python, [pythonScript], {
    stdio: 'inherit',
    cwd: packageDir,
    env: { ...process.env }
  });
  
  server.on('close', (code) => {
    process.exit(code);
  });
  
  // Handle termination signals
  process.on('SIGINT', () => server.kill('SIGINT'));
  process.on('SIGTERM', () => server.kill('SIGTERM'));
}

// Check if dependencies are installed
const fs = require('fs');
const dependenciesInstalled = fs.existsSync(path.join(packageDir, '.dependencies_installed'));

if (!dependenciesInstalled) {
  installDependencies();
} else {
  startServer();
}