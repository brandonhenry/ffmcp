/**
 * ffmcp - Node.js wrapper for the Python ffmcp CLI tool
 */

import { Readable } from 'stream';

export interface GenerateOptions {
  provider?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
  input?: string;
  encoding?: string;
  timeout?: number;
  env?: NodeJS.ProcessEnv;
}

export interface ChatOptions {
  provider?: string;
  model?: string;
  system?: string;
  thread?: string;
  stream?: boolean;
  encoding?: string;
  timeout?: number;
  env?: NodeJS.ProcessEnv;
}

export interface ExecuteOptions {
  input?: string;
  encoding?: string;
  timeout?: number;
  env?: NodeJS.ProcessEnv;
}

export declare class FFmcp {
  /**
   * Generate text using AI
   */
  generate(prompt: string, options?: GenerateOptions): Promise<string>;

  /**
   * Generate text with streaming
   */
  streamGenerate(prompt: string, options?: GenerateOptions): Readable;

  /**
   * Chat with AI
   */
  chat(message: string, options?: ChatOptions): Promise<string>;

  /**
   * Chat with streaming
   */
  streamChat(message: string, options?: ChatOptions): Readable;

  /**
   * Configure API keys
   */
  config(provider: string, apiKey: string): Promise<string>;

  /**
   * List providers
   */
  providers(): Promise<string>;

  /**
   * Execute raw command
   */
  raw(args: string[], options?: ExecuteOptions): Promise<string>;

  /**
   * Stream raw command
   */
  streamRaw(args: string[], options?: ExecuteOptions): Readable;
}

declare const ffmcp: FFmcp;

export default ffmcp;
export { ffmcp, FFmcp };
export { executeCommand, streamCommand, checkPythonInstallation };

declare function executeCommand(
  args: string[],
  options?: ExecuteOptions
): Promise<string>;

declare function streamCommand(
  args: string[],
  options?: ExecuteOptions
): Readable;

declare function checkPythonInstallation(): Promise<boolean>;

