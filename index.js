#!/usr/bin/env node

/**
 * ffmcp - Node.js wrapper for the Python ffmcp CLI tool
 * 
 * This module provides a JavaScript API to interact with the Python ffmcp CLI.
 * It requires the Python package to be installed separately.
 */

const { spawn, exec } = require('child_process');
const { promisify } = require('util');
const path = require('path');

const execAsync = promisify(exec);

/**
 * Check if Python ffmcp is installed
 */
async function checkPythonInstallation() {
  try {
    await execAsync('ffmcp --version');
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Execute a ffmcp command
 * @param {string[]} args - Command arguments
 * @param {Object} options - Execution options
 * @returns {Promise<string>} Command output
 */
async function executeCommand(args, options = {}) {
  const {
    input,
    encoding = 'utf-8',
    timeout = 300000, // 5 minutes default
    env = process.env,
  } = options;

  return new Promise((resolve, reject) => {
    const child = spawn('ffmcp', args, {
      env,
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data.toString(encoding);
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString(encoding);
    });

    if (input) {
      child.stdin.write(input);
      child.stdin.end();
    }

    const timeoutId = timeout > 0 ? setTimeout(() => {
      child.kill();
      reject(new Error(`Command timed out after ${timeout}ms`));
    }, timeout) : null;

    child.on('close', (code) => {
      if (timeoutId) clearTimeout(timeoutId);
      if (code !== 0) {
        reject(new Error(stderr || `Command failed with exit code ${code}`));
      } else {
        resolve(stdout.trim());
      }
    });

    child.on('error', (error) => {
      if (timeoutId) clearTimeout(timeoutId);
      reject(error);
    });
  });
}

/**
 * Stream a ffmcp command output
 * @param {string[]} args - Command arguments
 * @param {Object} options - Execution options
 * @returns {Promise<ReadableStream>} Stream of output chunks
 */
function streamCommand(args, options = {}) {
  const {
    input,
    encoding = 'utf-8',
    env = process.env,
  } = options;

  const child = spawn('ffmcp', args, {
    env,
    stdio: ['pipe', 'pipe', 'pipe'],
  });

  if (input) {
    child.stdin.write(input);
    child.stdin.end();
  }

  return child.stdout;
}

/**
 * Generate text using AI
 */
class FFmcp {
  constructor() {
    this._checkInstallation = null;
  }

  async _ensureInstalled() {
    if (this._checkInstallation === null) {
      this._checkInstallation = await checkPythonInstallation();
      if (!this._checkInstallation) {
        throw new Error(
          'Python ffmcp is not installed. Please install it first:\n' +
          '  pip install -e .\n' +
          'Or see https://github.com/brandonhenry/ffmcp for installation instructions.'
        );
      }
    }
    return this._checkInstallation;
  }

  /**
   * Generate text
   */
  async generate(prompt, options = {}) {
    await this._ensureInstalled();
    const args = ['generate', prompt];
    
    if (options.provider) args.push('-p', options.provider);
    if (options.model) args.push('-m', options.model);
    if (options.temperature !== undefined) args.push('-t', String(options.temperature));
    if (options.maxTokens) args.push('--max-tokens', String(options.maxTokens));
    if (options.stream) args.push('-s');

    return executeCommand(args, options);
  }

  /**
   * Generate text with streaming
   */
  streamGenerate(prompt, options = {}) {
    this._ensureInstalled().catch(() => {});
    const args = ['generate', prompt, '-s'];
    
    if (options.provider) args.push('-p', options.provider);
    if (options.model) args.push('-m', options.model);
    if (options.temperature !== undefined) args.push('-t', String(options.temperature));
    if (options.maxTokens) args.push('--max-tokens', String(options.maxTokens));

    return streamCommand(args, options);
  }

  /**
   * Chat with AI
   */
  async chat(message, options = {}) {
    await this._ensureInstalled();
    const args = ['chat', message];
    
    if (options.provider) args.push('-p', options.provider);
    if (options.model) args.push('-m', options.model);
    if (options.system) args.push('-s', options.system);
    if (options.thread) args.push('-t', options.thread);
    if (options.stream) args.push('-s');

    return executeCommand(args, options);
  }

  /**
   * Chat with streaming
   */
  streamChat(message, options = {}) {
    this._ensureInstalled().catch(() => {});
    const args = ['chat', message, '-s'];
    
    if (options.provider) args.push('-p', options.provider);
    if (options.model) args.push('-m', options.model);
    if (options.system) args.push('-s', options.system);
    if (options.thread) args.push('-t', options.thread);

    return streamCommand(args, options);
  }

  /**
   * Configure API keys
   */
  async config(provider, apiKey) {
    await this._ensureInstalled();
    return executeCommand(['config', '-p', provider, '-k', apiKey]);
  }

  /**
   * List providers
   */
  async providers() {
    await this._ensureInstalled();
    return executeCommand(['providers']);
  }

  /**
   * Execute raw command
   */
  async raw(args, options = {}) {
    await this._ensureInstalled();
    return executeCommand(args, options);
  }

  /**
   * Stream raw command
   */
  streamRaw(args, options = {}) {
    this._ensureInstalled().catch(() => {});
    return streamCommand(args, options);
  }
}

// Export singleton instance
const ffmcp = new FFmcp();

module.exports = ffmcp;
module.exports.FFmcp = FFmcp;
module.exports.executeCommand = executeCommand;
module.exports.streamCommand = streamCommand;
module.exports.checkPythonInstallation = checkPythonInstallation;

