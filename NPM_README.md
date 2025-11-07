# ffmcp - Node.js Package

**ffmcp** - AI command-line tool inspired by ffmpeg. Access any AI service from the command line with a unified interface.

## Installation

### Prerequisites

This npm package requires the Python `ffmcp` package to be installed first.

1. **Install Python ffmcp:**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/ffmcp.git
   cd ffmcp
   
   # Create a virtual environment (recommended)
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install in development mode
   pip install -e .
   ```

2. **Install npm package:**
   ```bash
   npm install ffmcp
   # or
   yarn add ffmcp
   # or
   pnpm add ffmcp
   ```

## Usage

### Command Line

After installing both packages, you can use `ffmcp` from the command line:

```bash
ffmcp generate "Write a haiku about coding"
ffmcp chat "Hello, how are you?" -p anthropic
ffmcp providers
```

### Programmatic API

```javascript
const ffmcp = require('ffmcp');

// Generate text
const result = await ffmcp.generate('Write a haiku about coding', {
  provider: 'openai',
  model: 'gpt-4',
  temperature: 0.7
});
console.log(result);

// Chat with AI
const response = await ffmcp.chat('Hello, how are you?', {
  provider: 'anthropic',
  system: 'You are a helpful assistant'
});
console.log(response);

// Stream responses
const stream = ffmcp.streamGenerate('Tell me a story', {
  provider: 'openai'
});

stream.on('data', (chunk) => {
  process.stdout.write(chunk);
});

// Configure API keys
await ffmcp.config('openai', 'your-api-key-here');

// List providers
const providers = await ffmcp.providers();
console.log(providers);

// Execute raw commands
const output = await ffmcp.raw(['agent', 'list']);
console.log(output);
```

### TypeScript Support

TypeScript definitions are included:

```typescript
import ffmcp from 'ffmcp';

const result = await ffmcp.generate('Hello', {
  provider: 'openai',
  model: 'gpt-4',
  temperature: 0.7
});
```

## Features

- 🚀 **Unified CLI**: Single command-line interface for multiple AI providers
- 🔌 **11 AI Providers**: OpenAI, Anthropic, Google Gemini, Groq, DeepSeek, Mistral AI, Together AI, Cohere, Perplexity, AI33, and AIMLAPI
- 📝 **Simple**: Works just like ffmpeg - simple, powerful, composable
- 🔧 **Configurable**: Manage API keys and settings easily
- 📊 **Streaming**: Real-time streaming support for responses
- 🎨 **Full OpenAI Support**: All OpenAI features including vision, images, audio, embeddings, and assistants
- 🧠 **Memory with Zep (Brains)**: Create brains, store/retrieve chat memory, collections, and graph
- 🤖 **Agents**: Named agents with model, instructions, brain, dynamic properties, and actions
- 👥 **Multi-Agent Teams**: Agents can work together in teams
- 💬 **Threads**: Conversation history for both chat and agents
- 🎤 **Voiceover/TTS**: Full text-to-speech support with multiple providers

## API Reference

### `ffmcp.generate(prompt, options?)`

Generate text using AI.

**Parameters:**
- `prompt` (string): The prompt to generate from
- `options` (object, optional):
  - `provider` (string): AI provider to use
  - `model` (string): Model to use
  - `temperature` (number): Temperature for generation
  - `maxTokens` (number): Maximum tokens to generate
  - `stream` (boolean): Stream the response
  - `timeout` (number): Timeout in milliseconds

**Returns:** `Promise<string>`

### `ffmcp.streamGenerate(prompt, options?)`

Generate text with streaming.

**Returns:** `ReadableStream`

### `ffmcp.chat(message, options?)`

Chat with AI.

**Parameters:**
- `message` (string): The message to send
- `options` (object, optional):
  - `provider` (string): AI provider to use
  - `model` (string): Model to use
  - `system` (string): System message
  - `thread` (string): Thread name for conversation history
  - `stream` (boolean): Stream the response

**Returns:** `Promise<string>`

### `ffmcp.streamChat(message, options?)`

Chat with streaming.

**Returns:** `ReadableStream`

### `ffmcp.config(provider, apiKey)`

Configure API keys.

**Parameters:**
- `provider` (string): Provider name
- `apiKey` (string): API key

**Returns:** `Promise<string>`

### `ffmcp.providers()`

List all available providers.

**Returns:** `Promise<string>`

### `ffmcp.raw(args, options?)`

Execute raw ffmcp command.

**Parameters:**
- `args` (string[]): Command arguments
- `options` (object, optional): Execution options

**Returns:** `Promise<string>`

### `ffmcp.streamRaw(args, options?)`

Execute raw command with streaming.

**Returns:** `ReadableStream`

## Supported AI Providers

- **OpenAI** - GPT-4, GPT-3.5, DALL·E, Whisper
- **Anthropic** - Claude 3.5 Sonnet, Claude 3 Opus
- **Google Gemini** - Gemini 2.0 Flash, Gemini 1.5 Pro
- **Groq** - Llama 3.1, Mixtral, Gemma
- **DeepSeek** - DeepSeek Chat, DeepSeek Coder
- **Mistral AI** - Mistral Large, Pixtral
- **Together AI** - Llama, Mixtral, Qwen, many more
- **Cohere** - Command R+, Command R
- **Perplexity** - Sonar Large, Sonar Pro
- **AI33** - Various models
- **AIMLAPI** - 300+ models unified API

## Examples

### Basic Generation

```javascript
const result = await ffmcp.generate('Write a Python function to calculate fibonacci');
console.log(result);
```

### Advanced Options

```javascript
const result = await ffmcp.generate('Creative story', {
  provider: 'openai',
  model: 'gpt-4',
  temperature: 0.9,
  maxTokens: 500
});
```

### Streaming

```javascript
const stream = ffmcp.streamGenerate('Tell me a story', {
  provider: 'openai'
});

stream.on('data', (chunk) => {
  process.stdout.write(chunk);
});

stream.on('end', () => {
  console.log('\nDone!');
});
```

### Chat with Thread

```javascript
// First message
await ffmcp.chat('Hello, my name is Alice', {
  provider: 'openai',
  thread: 'conversation1'
});

// Follow-up (remembers previous messages)
const response = await ffmcp.chat('What is my name?', {
  provider: 'openai',
  thread: 'conversation1'
});
console.log(response); // "Your name is Alice"
```

### Using Agents

```javascript
// Create an agent (via CLI or programmatically)
await ffmcp.raw(['agent', 'create', 'myagent', '-p', 'openai', '-m', 'gpt-4o-mini', '-i', 'You are helpful']);

// Run agent
const result = await ffmcp.raw(['agent', 'run', 'Plan a trip to Paris', '--agent', 'myagent']);
console.log(result);
```

## Requirements

- Node.js >= 14.0.0
- Python 3.8+ with ffmcp installed

## License

MIT License

## Links

- [GitHub Repository](https://github.com/yourusername/ffmcp)
- [Python Package Documentation](https://github.com/yourusername/ffmcp#readme)

