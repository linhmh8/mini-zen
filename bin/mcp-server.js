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

// Install Python dependencies with virtual environment
function installDependencies() {
  const python = findPython();
  const requirementsPath = path.join(packageDir, 'requirements.txt');
  const venvPath = path.join(packageDir, 'venv');
  
  console.error('📦 Setting up Python virtual environment...');
  
  // Create virtual environment
  const createVenv = spawn(python, ['-m', 'venv', venvPath], {
    stdio: 'inherit',
    cwd: packageDir
  });
  
  createVenv.on('close', (code) => {
    if (code === 0) {
      // Install dependencies in venv
      const venvPython = process.platform === 'win32' 
        ? path.join(venvPath, 'Scripts', 'python.exe')
        : path.join(venvPath, 'bin', 'python');
        
      console.error('📥 Installing dependencies...');
      const install = spawn(venvPython, ['-m', 'pip', 'install', '-r', requirementsPath], {
        stdio: 'inherit',
        cwd: packageDir
      });
      
      install.on('close', (installCode) => {
        if (installCode === 0) {
          // Mark dependencies as installed
          require('fs').writeFileSync(path.join(packageDir, '.dependencies_installed'), '');
          startServer();
        } else {
          console.error('❌ Failed to install dependencies');
          process.exit(1);
        }
      });
    } else {
      console.error('❌ Failed to create virtual environment');
      process.exit(1);
    }
  });
}

// Start the MCP server
function startServer() {
  const venvPath = path.join(packageDir, 'venv');
  
  // Use venv python if available, otherwise system python
  const venvPython = process.platform === 'win32' 
    ? path.join(venvPath, 'Scripts', 'python.exe')
    : path.join(venvPath, 'bin', 'python');
    
  const python = require('fs').existsSync(venvPython) ? venvPython : findPython();
  
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