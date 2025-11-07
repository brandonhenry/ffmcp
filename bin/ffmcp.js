#!/usr/bin/env node

/**
 * ffmcp CLI wrapper - forwards commands to Python ffmcp
 */

const { spawn } = require('child_process');
const { execSync } = require('child_process');

// Forward all arguments to Python ffmcp
const args = process.argv.slice(2);

// Try to find Python ffmcp command
// First try: python3 -m ffmcp.cli (most reliable)
// Second try: ffmcp-python (if installed with different name)
// Third try: check if ffmcp is available in PATH (but not this npm wrapper)

function findPythonFfmcp() {
  // Check if python3 -m ffmcp.cli works (most reliable)
  try {
    execSync('python3 -m ffmcp.cli --version 2>&1', { stdio: 'pipe', timeout: 2000 });
    return ['python3', ['-m', 'ffmcp.cli', ...args]];
  } catch (e) {
    // Try python (without 3) as fallback
    try {
      execSync('python -m ffmcp.cli --version 2>&1', { stdio: 'pipe', timeout: 2000 });
      return ['python', ['-m', 'ffmcp.cli', ...args]];
    } catch (e2) {
      // Try direct ffmcp command, but check it's not this npm wrapper
      try {
        const which = execSync('which ffmcp', { encoding: 'utf8', stdio: 'pipe' }).trim();
        // If it's not pointing to our npm wrapper, use it
        if (!which.includes('node_modules') && !which.includes('.nvm')) {
          return ['ffmcp', args];
        }
      } catch (e3) {
        // Ignore
      }
    }
  }
  return null;
}

const pythonCmd = findPythonFfmcp();

if (!pythonCmd) {
  console.error('Error: Python ffmcp is not installed.');
  console.error('');
  console.error('The postinstall script should have installed it automatically.');
  console.error('If installation failed, try running manually:');
  console.error('');
  console.error('  npm install -g ffmcp  # Reinstall to trigger postinstall');
  console.error('');
  console.error('Or install from source:');
  console.error('  git clone https://github.com/brandonhenry/ffmcp.git');
  console.error('  cd ffmcp');
  console.error('  python3 -m pip install -e .');
  console.error('');
  console.error('See https://github.com/brandonhenry/ffmcp for more information.');
  process.exit(1);
}

const [command, commandArgs] = pythonCmd;

const child = spawn(command, commandArgs, {
  stdio: 'inherit',
  env: process.env,
});

child.on('error', (error) => {
  console.error('Error:', error.message);
  console.error('');
  console.error('Make sure Python ffmcp is installed. See:');
  console.error('https://github.com/brandonhenry/ffmcp');
  process.exit(1);
});

child.on('exit', (code) => {
  process.exit(code || 0);
});

