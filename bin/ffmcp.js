#!/usr/bin/env node

/**
 * ffmcp CLI wrapper - forwards commands to Python ffmcp
 */

const { spawn } = require('child_process');

// Forward all arguments to Python ffmcp
const args = process.argv.slice(2);

const child = spawn('ffmcp', args, {
  stdio: 'inherit',
  env: process.env,
});

child.on('error', (error) => {
  if (error.code === 'ENOENT') {
    console.error('Error: Python ffmcp is not installed.');
    console.error('Please install it first:');
    console.error('  pip install -e .');
    console.error('Or see https://github.com/brandonhenry/ffmcp for installation instructions.');
    process.exit(1);
  } else {
    console.error('Error:', error.message);
    process.exit(1);
  }
});

child.on('exit', (code) => {
  process.exit(code || 0);
});

