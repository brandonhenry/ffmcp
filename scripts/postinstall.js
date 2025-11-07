#!/usr/bin/env node

/**
 * Postinstall script to automatically install Python ffmcp package
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const packageDir = __dirname.replace(/[\\/]scripts$/, '');
const pythonSourceDir = path.join(packageDir, 'ffmcp');
const setupPy = path.join(packageDir, 'setup.py');

console.log('📦 ffmcp: Installing Python dependencies...');

// Check if Python source files exist
if (!fs.existsSync(setupPy) || !fs.existsSync(pythonSourceDir)) {
  console.warn('⚠️  Warning: Python source files not found. Python features may not work.');
  console.warn('   Make sure you installed from npm, not from source.');
  process.exit(0);
}

// Check if Python 3 is available
let pythonCmd = 'python3';
try {
  execSync('python3 --version', { stdio: 'pipe' });
} catch (e) {
  try {
    execSync('python --version', { stdio: 'pipe' });
    pythonCmd = 'python';
  } catch (e2) {
    console.error('❌ Error: Python 3 is required but not found.');
    console.error('   Please install Python 3.8+ and try again.');
    console.error('   Visit: https://www.python.org/downloads/');
    process.exit(1);
  }
}

// Check if Python ffmcp is already installed
try {
  execSync(`${pythonCmd} -m ffmcp.cli --version 2>&1`, { stdio: 'pipe', timeout: 2000 });
  console.log('✅ Python ffmcp is already installed.');
  process.exit(0);
} catch (e) {
  // Not installed, continue with installation
}

// Install Python package with all dependencies
try {
  console.log(`   Installing Python package and all AI provider dependencies...`);
  
  // First install the package itself in editable mode
  const installPackageCmd = `${pythonCmd} -m pip install -e "${packageDir}" --quiet --disable-pip-version-check`;
  execSync(installPackageCmd, {
    stdio: 'pipe',
    cwd: packageDir,
    env: { ...process.env, PIP_DISABLE_PIP_VERSION_CHECK: '1' }
  });
  
  // Then install all dependencies from requirements.txt
  const requirementsFile = path.join(packageDir, 'requirements.txt');
  if (fs.existsSync(requirementsFile)) {
    console.log(`   Installing AI provider dependencies (OpenAI, Anthropic, Gemini, Groq, etc.)...`);
    const installDepsCmd = `${pythonCmd} -m pip install -r "${requirementsFile}" --quiet --disable-pip-version-check`;
    execSync(installDepsCmd, {
      stdio: 'pipe',
      cwd: packageDir,
      env: { ...process.env, PIP_DISABLE_PIP_VERSION_CHECK: '1' }
    });
  }
  
  console.log('✅ Python ffmcp and all AI provider dependencies installed successfully!');
  
  // Verify installation
  try {
    execSync(`${pythonCmd} -m ffmcp.cli --version 2>&1`, { stdio: 'pipe', timeout: 2000 });
    console.log('✅ Installation verified.');
  } catch (e) {
    console.warn('⚠️  Warning: Installation completed but verification failed.');
    console.warn('   You may need to restart your terminal or run:');
    console.warn(`   ${pythonCmd} -m pip install -e "${packageDir}"`);
  }
  
} catch (error) {
  console.error('❌ Error installing Python package:');
  console.error(error.message);
  console.error('');
  console.error('You can install it manually:');
  console.error(`  cd ${packageDir}`);
  console.error(`  ${pythonCmd} -m pip install -e .`);
  console.error(`  ${pythonCmd} -m pip install -r requirements.txt`);
  console.error('');
  console.error('Or install from source:');
  console.error('  git clone https://github.com/brandonhenry/ffmcp.git');
  console.error('  cd ffmcp');
  console.error(`  ${pythonCmd} -m pip install -e .`);
  console.error(`  ${pythonCmd} -m pip install -r requirements.txt`);
  process.exit(1);
}

