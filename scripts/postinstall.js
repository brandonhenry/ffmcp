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

// Use virtual environment approach to avoid externally-managed-environment error
const os = require('os');
const venvPath = path.join(os.homedir(), '.ffmcp-venv');
const venvPython = path.join(venvPath, process.platform === 'win32' ? 'Scripts\\python.exe' : 'bin/python');

// Check if Python ffmcp is already installed (either in venv or system)
let ffmcpInstalled = false;
try {
  execSync(`${pythonCmd} -m ffmcp.cli --version 2>&1`, { stdio: 'pipe', timeout: 2000 });
  ffmcpInstalled = true;
} catch (e) {
  // Check venv
  if (fs.existsSync(venvPython)) {
    try {
      execSync(`"${venvPython}" -m ffmcp.cli --version 2>&1`, { stdio: 'pipe', timeout: 2000 });
      ffmcpInstalled = true;
    } catch (e2) {
      // Not in venv either
    }
  }
}

if (ffmcpInstalled) {
  console.log('✅ Python ffmcp is already installed.');
  process.exit(0);
}

// Create virtual environment if it doesn't exist
if (!fs.existsSync(venvPath)) {
  console.log(`   Creating virtual environment at ${venvPath}...`);
  try {
    execSync(`${pythonCmd} -m venv "${venvPath}"`, { stdio: 'pipe' });
  } catch (error) {
    console.error('❌ Error creating virtual environment:');
    console.error(error.message);
    console.error('');
    console.error('Trying fallback: installing with --break-system-packages flag...');
    
    // Fallback: try with --break-system-packages and --user
    try {
      const pipFlags = '--user --break-system-packages --quiet --disable-pip-version-check';
      execSync(`${pythonCmd} -m pip install -e "${packageDir}" ${pipFlags}`, {
        stdio: 'pipe',
        cwd: packageDir,
        env: { ...process.env, PIP_DISABLE_PIP_VERSION_CHECK: '1' }
      });
      
      const requirementsFile = path.join(packageDir, 'requirements.txt');
      if (fs.existsSync(requirementsFile)) {
        execSync(`${pythonCmd} -m pip install -r "${requirementsFile}" ${pipFlags}`, {
          stdio: 'pipe',
          cwd: packageDir,
          env: { ...process.env, PIP_DISABLE_PIP_VERSION_CHECK: '1' }
        });
      }
      
      console.log('✅ Python ffmcp installed successfully (using --break-system-packages)!');
      process.exit(0);
    } catch (fallbackError) {
      console.error('❌ Fallback installation also failed.');
      console.error('Please install manually or use pipx:');
      console.error('  brew install pipx');
      console.error('  pipx install git+https://github.com/brandonhenry/ffmcp.git');
      process.exit(1);
    }
  }
}

// Install into virtual environment
try {
  console.log(`   Installing Python package and all AI provider dependencies...`);
  
  // Install package
  const installPackageCmd = `"${venvPython}" -m pip install -e "${packageDir}" --quiet --disable-pip-version-check`;
  execSync(installPackageCmd, {
    stdio: 'pipe',
    cwd: packageDir,
    env: { ...process.env, PIP_DISABLE_PIP_VERSION_CHECK: '1' }
  });
  
  // Install dependencies
  const requirementsFile = path.join(packageDir, 'requirements.txt');
  if (fs.existsSync(requirementsFile)) {
    console.log(`   Installing AI provider dependencies (OpenAI, Anthropic, Gemini, Groq, etc.)...`);
    const installDepsCmd = `"${venvPython}" -m pip install -r "${requirementsFile}" --quiet --disable-pip-version-check`;
    execSync(installDepsCmd, {
      stdio: 'pipe',
      cwd: packageDir,
      env: { ...process.env, PIP_DISABLE_PIP_VERSION_CHECK: '1' }
    });
  }
  
  console.log('✅ Python ffmcp and all AI provider dependencies installed successfully!');
  console.log(`   Virtual environment: ${venvPath}`);
  
  // Verify installation
  try {
    execSync(`"${venvPython}" -m ffmcp.cli --version 2>&1`, { stdio: 'pipe', timeout: 2000 });
    console.log('✅ Installation verified.');
  } catch (e) {
    console.warn('⚠️  Warning: Installation completed but verification failed.');
  }
  
} catch (error) {
  console.error('❌ Error installing Python package:');
  console.error(error.message);
  console.error('');
  console.error('You can install it manually:');
  console.error(`  ${pythonCmd} -m venv ~/.ffmcp-venv`);
  console.error(`  source ~/.ffmcp-venv/bin/activate`);
  console.error(`  pip install -e "${packageDir}"`);
  console.error(`  pip install -r "${path.join(packageDir, 'requirements.txt')}"`);
  process.exit(1);
}

