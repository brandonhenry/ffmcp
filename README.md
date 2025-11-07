# ffmcp

**ffmcp** - AI command-line tool inspired by ffmpeg. Access any AI service from the command line with a unified interface.

## Features

- 🚀 **Unified CLI**: Single command-line interface for multiple AI providers
- 🔌 **9 AI Providers**: OpenAI, Anthropic, Google Gemini, Groq, DeepSeek, Mistral AI, Together AI, Cohere, and Perplexity
- 📝 **Simple**: Works just like ffmpeg - simple, powerful, composable
- 🔧 **Configurable**: Manage API keys and settings easily
- 📊 **Streaming**: Real-time streaming support for responses
- 🎨 **Full OpenAI Support**: All OpenAI features including vision, images, audio, embeddings, and assistants
- 🧠 **Memory with Zep (Brains)**: Create brains, store/retrieve chat memory, collections, and graph
- 🤖 **Agents**: Named agents with model, instructions, brain, dynamic properties, and actions (web, images, vision, embeddings)
- 💬 **Threads**: Conversation history for both chat and agents - maintain context across multiple interactions

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ffmcp.git
cd ffmcp

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Or install with specific providers
pip install -e ".[openai]"
pip install -e ".[anthropic]"
pip install -e ".[all]"
```

**Note:** On macOS with Homebrew Python, you'll need to use a virtual environment. If you prefer system-wide installation, use `pip3` with `--user` flag or `pipx`.

## Quick Start

### 1. Configure API Keys

```bash
# Set OpenAI API key
ffmcp config -p openai -k YOUR_OPENAI_API_KEY

# Set Anthropic API key
ffmcp config -p anthropic -k YOUR_ANTHROPIC_API_KEY

# Set Google Gemini API key
ffmcp config -p gemini -k YOUR_GEMINI_API_KEY

# Set Groq API key
ffmcp config -p groq -k YOUR_GROQ_API_KEY

# Set DeepSeek API key
ffmcp config -p deepseek -k YOUR_DEEPSEEK_API_KEY

# Set Mistral AI API key
ffmcp config -p mistral -k YOUR_MISTRAL_API_KEY

# Set Together AI API key
ffmcp config -p together -k YOUR_TOGETHER_API_KEY

# Set Cohere API key
ffmcp config -p cohere -k YOUR_COHERE_API_KEY

# Set Perplexity API key
ffmcp config -p perplexity -k YOUR_PERPLEXITY_API_KEY

# Or use environment variables (provider name in uppercase)
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
export GEMINI_API_KEY=your_key
export GROQ_API_KEY=your_key
export DEEPSEEK_API_KEY=your_key
export MISTRAL_API_KEY=your_key
export TOGETHER_API_KEY=your_key
export COHERE_API_KEY=your_key
export PERPLEXITY_API_KEY=your_key
```

### 2. Generate Text

```bash
# Basic generation
ffmcp generate "Write a haiku about coding"

# With specific provider and model
ffmcp generate "Explain quantum computing" -p openai -m gpt-4
ffmcp generate "Explain quantum computing" -p gemini -m gemini-1.5-pro
ffmcp generate "Explain quantum computing" -p groq -m llama-3.1-70b-versatile
ffmcp generate "Explain quantum computing" -p deepseek -m deepseek-chat
ffmcp generate "Explain quantum computing" -p mistral -m mistral-large-latest
ffmcp generate "Explain quantum computing" -p together -m meta-llama/Llama-3-70b-chat-hf
ffmcp generate "Explain quantum computing" -p cohere -m command-r-plus
ffmcp generate "Explain quantum computing" -p perplexity -m llama-3.1-sonar-large-128k-online

# Stream the response
ffmcp generate "Tell me a story" -s

# Read from file
ffmcp generate -i prompt.txt -o output.txt

# Pipe input
echo "Summarize this" | ffmcp generate
```

### 3. Chat Mode

```bash
# Conversational chat
ffmcp chat "Hello, how are you?" -p anthropic

# With system message
ffmcp chat "What is 2+2?" -s "You are a helpful math tutor"

# Chat with thread (maintains conversation history)
ffmcp chat "Hello" -t conversation1
ffmcp chat "What did I just say?" -t conversation1  # Remembers previous messages

# Thread management
ffmcp thread create conversation1
ffmcp thread list
ffmcp thread use conversation1
ffmcp thread current
ffmcp thread clear conversation1
ffmcp thread delete conversation1
```

### 4. Agents

```bash
# Create an agent (any provider, default actions enabled)
ffmcp agent create myagent -p openai -m gpt-4o-mini -i "You are a helpful assistant" --brain mybrain
ffmcp agent create gemini-agent -p gemini -m gemini-2.0-flash-exp -i "You are a helpful assistant"
ffmcp agent create groq-agent -p groq -m llama-3.1-70b-versatile -i "You are a helpful assistant"

# Create an agent with instructions from a file
ffmcp agent create myagent -p openai -m gpt-4o-mini -f instructions.txt --brain mybrain

# List and select the active agent
ffmcp agent list
ffmcp agent use myagent

# Show details
ffmcp agent show

# Thread Management (conversation history)
ffmcp agent thread create myagent thread1
ffmcp agent thread list myagent
ffmcp agent thread use myagent thread1
ffmcp agent thread current myagent
ffmcp agent thread clear myagent thread1
ffmcp agent thread delete myagent thread1

# Run the agent (uses active thread automatically)
ffmcp agent run "Plan a 3-day trip to Paris and fetch top sights"

# Run with specific thread
ffmcp agent run "Continue planning" --thread thread1

# Manage properties and actions
ffmcp agent prop set myagent timezone UTC
ffmcp agent action enable myagent web_fetch
ffmcp agent action disable myagent generate_image
```

**See [Threads: Conversation History](#threads-conversation-history) section for detailed thread documentation.**

## OpenAI Features

### Vision / Image Understanding

```bash
# Analyze images
ffmcp openai vision "What's in this image?" image1.jpg image2.png

# With custom model and options
ffmcp openai vision "Describe this" photo.jpg -m gpt-4o -t 0.5
```

### Image Generation (DALL·E)

```bash
# Generate image with DALL·E 3
ffmcp openai image "A futuristic cityscape at sunset"

# DALL·E 2 with custom size
ffmcp openai image "A cat wearing sunglasses" -m dall-e-2 --size 512x512

# High quality with natural style
ffmcp openai image "Abstract art" --quality hd --style natural

# Save URL to file
ffmcp openai image "Beautiful landscape" -o image_url.txt
```

### Audio Transcription (Whisper)

```bash
# Transcribe audio to text
ffmcp openai transcribe audio.mp3

# With language hint
ffmcp openai transcribe audio.mp3 -l es

# With prompt for better accuracy
ffmcp openai transcribe meeting.mp3 -p "This is a technical meeting about AI"

# Output as JSON with timestamps
ffmcp openai transcribe audio.mp3 --json -o transcript.json
```

### Audio Translation

```bash
# Translate audio to English
ffmcp openai translate spanish_audio.mp3

# With prompt
ffmcp openai translate audio.mp3 -p "Technical presentation"
```

### Text-to-Speech

```bash
# Convert text to speech
ffmcp openai tts "Hello, world!" output.mp3

# With custom voice and speed
ffmcp openai tts "Welcome to the future" speech.mp3 -v nova -s 1.2

# High quality model
ffmcp openai tts "Important announcement" announcement.mp3 -m tts-1-hd
```

### Embeddings

```bash
# Create embeddings
ffmcp openai embed "This is a sample text"

# With custom dimensions
ffmcp openai embed "Vectorize this" -d 256

# Output full JSON with usage stats
ffmcp openai embed "Text to embed" --json -o embeddings.json
```

### Function Calling / Tools

```bash
# Chat with function calling
# First, create a tools.json file:
cat > tools.json << EOF
[
  {
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get the current weather",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {"type": "string"}
        }
      }
    }
  }
]
EOF

# Use with chat
ffmcp openai tools "What's the weather in San Francisco?" -t tools.json
```

### Assistants API

```bash
# Create an assistant
ffmcp openai assistant create "Math Tutor" "You are a helpful math tutor"

# Create a conversation thread
ffmcp openai assistant thread -o thread_id.txt

# Add a message to thread
ffmcp openai assistant message $(cat thread_id.txt) "Solve 2x + 5 = 15"

# Run the assistant
ffmcp openai assistant run $(cat thread_id.txt) $(cat assistant_id.txt)

# Get messages from thread
ffmcp openai assistant messages $(cat thread_id.txt)

# Upload a file for the assistant
ffmcp openai assistant upload document.pdf
```

### 4. List Providers

```bash
ffmcp providers
```

This will show all available providers:
- **openai** - OpenAI GPT models (GPT-4, GPT-3.5, DALL·E, Whisper, TTS, Embeddings)
- **anthropic** - Anthropic Claude models (Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku)
- **gemini** - Google Gemini models (Gemini 2.0 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash)
- **groq** - Groq models (Llama 3.1, Mixtral, Gemma) - Ultra-fast inference
- **deepseek** - DeepSeek models (DeepSeek Chat, DeepSeek Coder) - OpenAI-compatible
- **mistral** - Mistral AI models (Mistral Large, Mistral Medium, Pixtral)
- **together** - Together AI models (Access to many open-source models like Llama, Mixtral, Qwen)
- **cohere** - Cohere models (Command R+, Command R) - Enterprise-focused
- **perplexity** - Perplexity AI models (Sonar Large, Sonar Pro) - Built-in web search

### 5. Daily Token Tracking

ffmcp automatically tracks total tokens used per UTC day across supported providers (e.g., OpenAI, Anthropic). Totals are stored in `~/.ffmcp/tokens.json`.

```bash
# Show today's total token count (UTC day)
ffmcp tokens

# Filter by provider
ffmcp tokens -p openai
ffmcp tokens -p gemini
ffmcp tokens -p groq
# ... any provider name

# Specify a date (UTC, YYYY-MM-DD)
ffmcp tokens -d 2025-11-07
```

Notes:
- The total is best-effort for streaming responses and depends on provider SDK support for usage in stream events.
- Token accounting is updated automatically on each command invocation that returns usage from the provider.

## Threads: Conversation History

ffmcp supports **threads** to maintain conversation history for both the `chat` command and `agent run` command. Threads allow you to have ongoing conversations where the AI remembers previous messages.

### Chat Threads

Chat threads are independent conversation histories that work with the `chat` command:

```bash
# Create a chat thread
ffmcp thread create conversation1

# Set it as active (optional - chat will use active thread automatically)
ffmcp thread use conversation1

# Chat with conversation history
ffmcp chat "Hello, my name is Alice" -t conversation1 -p openai
ffmcp chat "What's my name?" -t conversation1 -p openai  # Remembers!

# Or use active thread (no -t needed)
ffmcp chat "Hello" -p openai  # Uses active thread automatically
ffmcp chat "Continue" -p openai  # Remembers previous message

# With system message (saved to thread)
ffmcp chat "Solve 2+2" -s "You are a math tutor" -t math-thread
ffmcp chat "Now solve 5+5" -t math-thread  # Remembers system message

# Manage threads
ffmcp thread list                    # List all chat threads
ffmcp thread current                 # Show active thread
ffmcp thread clear conversation1     # Clear messages (keeps thread)
ffmcp thread delete conversation1    # Delete thread entirely
```

**Key Points:**
- Chat threads are **independent** from agent threads
- Each thread maintains its own conversation history
- System messages are saved to the thread on first use
- Active thread is used automatically if no thread is specified

### Agent Threads

Agent threads are tied to specific agents and maintain conversation history for agent runs:

```bash
# Create an agent
ffmcp agent create myagent -p openai -m gpt-4o-mini -i "You are helpful"

# Create a thread for the agent
ffmcp agent thread create myagent conversation1

# Set it as active (optional - agent run uses active thread automatically)
ffmcp agent thread use myagent conversation1

# Run agent with conversation history
ffmcp agent run "Plan a trip to Paris" --agent myagent
ffmcp agent run "Add a day in London" --agent myagent  # Remembers!

# Or specify thread explicitly
ffmcp agent run "Start new topic" --agent myagent --thread conversation2

# Manage agent threads
ffmcp agent thread list myagent           # List threads for agent
ffmcp agent thread current myagent        # Show active thread
ffmcp agent thread clear myagent conv1    # Clear messages
ffmcp agent thread delete myagent conv1   # Delete thread
```

**Key Points:**
- Agent threads are **tied to specific agents**
- Each agent can have multiple threads
- Each agent has its own active thread
- Tool calls and actions are saved to the thread
- Threads work seamlessly with agent actions (web fetch, image generation, etc.)

### When to Use Threads

**Use Chat Threads when:**
- You want simple conversation history with the `chat` command
- You're switching between different providers/models
- You don't need agent features (actions, tools, etc.)
- You want lightweight conversation management

**Use Agent Threads when:**
- You're using agents with actions and tools
- You want conversation history tied to a specific agent configuration
- You need multiple conversation contexts per agent
- You want to leverage agent capabilities (web search, image generation, etc.)

### Thread Management Commands

**Chat Threads:**
```bash
ffmcp thread create <name>      # Create thread
ffmcp thread list               # List all threads
ffmcp thread use <name>         # Set active thread
ffmcp thread current            # Show active thread
ffmcp thread clear <name>       # Clear messages
ffmcp thread delete <name>      # Delete thread
```

**Agent Threads:**
```bash
ffmcp agent thread create <agent> <name>    # Create thread
ffmcp agent thread list <agent>              # List threads
ffmcp agent thread use <agent> <name>        # Set active thread
ffmcp agent thread current <agent>           # Show active thread
ffmcp agent thread clear <agent> <name>      # Clear messages
ffmcp agent thread delete <agent> <name>    # Delete thread
```

### Example Workflows

**Chat Thread Workflow:**
```bash
# Create and use a thread
ffmcp thread create project-planning
ffmcp thread use project-planning

# Have a conversation
ffmcp chat "I want to build a web app" -p openai
ffmcp chat "What technologies should I use?" -p openai
ffmcp chat "Tell me more about React" -p openai

# Switch to different thread
ffmcp thread create personal-chat
ffmcp thread use personal-chat
ffmcp chat "What's the weather like?" -p openai  # Fresh conversation
```

**Agent Thread Workflow:**
```bash
# Create agent and thread
ffmcp agent create assistant -p openai -m gpt-4o-mini -i "You are helpful"
ffmcp agent thread create assistant project-a
ffmcp agent thread use assistant project-a

# Run agent with conversation history
ffmcp agent run "Research React best practices" --agent assistant
ffmcp agent run "Find examples of React hooks" --agent assistant  # Uses web_fetch action

# Create another thread for different project
ffmcp agent thread create assistant project-b
ffmcp agent thread use assistant project-b
ffmcp agent run "Research Python frameworks" --agent assistant  # Fresh conversation
```

## Zep Memory (Brains)

**Note:** Brains (Zep) are separate from threads. Threads maintain conversation history locally, while Brains provide advanced memory features including semantic search, document storage, and graph relationships. You can use both together - agents can have threads for conversation history AND a brain for long-term memory and document search.

### Setup

```bash
# Configure Zep (Cloud)
export ZEP_CLOUD_API_KEY=your_key

# Optional for self-hosted
export ZEP_BASE_URL=http://localhost:8000

# Or persist settings
ffmcp config -p zep -k YOUR_ZEP_API_KEY
```

### Brains

```bash
# Create and use a brain
ffmcp brain create mybrain
ffmcp brain current
ffmcp brain list
ffmcp brain use mybrain
```

### Memory

```bash
# Add a message to memory
ffmcp brain memory add --role user --role-type user --content "Who was Octavia Butler?"

# Get memory context
ffmcp brain memory get

# Get memory for a specific brain and session
ffmcp brain memory get --brain mybrain --session session-123

# Search memory
ffmcp brain memory search "Octavia"

# Clear memory for session
ffmcp brain memory clear
```

Notes:
- Omitting `--brain` uses the active brain (set with `ffmcp brain use`).
- Omitting `--session` defaults to the brain’s `default_session_id` (if set) or the brain name.

### Collections & Documents

```bash
# Create a namespaced collection under the brain
ffmcp brain collection create knowledge --description "KB for mybrain"

# Add a document
ffmcp brain document add knowledge --text "Zep is a memory platform for LLM apps" --id doc1

# Search documents
ffmcp brain document search knowledge "memory platform"
```

### Graph (Zep Cloud)

```bash
# Add JSON data to user graph
echo '{"projects": {"alpha": {"status": "in progress"}}}' | \
  ffmcp brain graph add user-123 --type json --input -

# Get user graph
ffmcp brain graph get user-123
```

## Usage Examples

### Basic Text Generation

```bash
ffmcp generate "Write a Python function to calculate fibonacci"
```

### Advanced Options

```bash
ffmcp generate "Creative story" \
  -p openai \
  -m gpt-4 \
  -t 0.9 \
  --max-tokens 500 \
  -s
```

### File Processing

```bash
# Process a file
ffmcp generate -i input.txt -o output.txt

# Chain operations
cat data.txt | ffmcp generate | grep "important" > filtered.txt
```

### Integration in Scripts

```bash
#!/bin/bash
RESULT=$(ffmcp generate "Translate to French: Hello world" -p openai)
echo "Translation: $RESULT"
```

### Complete Workflow Example

```bash
# 1. Transcribe audio
ffmcp openai transcribe meeting.mp3 -o transcript.txt

# 2. Summarize transcript
ffmcp generate -i transcript.txt -o summary.txt

# 3. Generate image based on summary
ffmcp openai image "$(cat summary.txt | head -c 100)"

# 4. Create embeddings for search
ffmcp openai embed "$(cat transcript.txt)" -o embeddings.json
```

## Supported AI Providers

ffmcp supports 9 major AI providers, each with their own strengths:

| Provider | Models | Key Features | Best For |
|----------|--------|-------------|----------|
| **OpenAI** | GPT-4, GPT-3.5, DALL·E, Whisper | Full feature set (vision, images, audio, embeddings) | Comprehensive AI tasks |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus | Long context, high quality | Complex reasoning, long documents |
| **Google Gemini** | Gemini 2.0 Flash, Gemini 1.5 Pro | Multimodal, fast | General purpose, vision tasks |
| **Groq** | Llama 3.1, Mixtral, Gemma | Ultra-fast inference | Speed-critical applications |
| **DeepSeek** | DeepSeek Chat, DeepSeek Coder | OpenAI-compatible, coding-focused | Code generation, technical tasks |
| **Mistral AI** | Mistral Large, Pixtral | High quality, vision support | Enterprise applications |
| **Together AI** | Llama, Mixtral, Qwen, many more | Access to many open-source models | Experimentation, cost-effective |
| **Cohere** | Command R+, Command R | Enterprise features, RAG | Business applications, embeddings |
| **Perplexity** | Sonar Large, Sonar Pro | Built-in web search, citations | Research, real-time information |

### Default Models

Each provider has a sensible default model:
- OpenAI: `gpt-4o-mini`
- Anthropic: `claude-3-5-sonnet-20241022`
- Gemini: `gemini-2.0-flash-exp`
- Groq: `llama-3.1-70b-versatile`
- DeepSeek: `deepseek-chat`
- Mistral: `mistral-large-latest`
- Together: `meta-llama/Llama-3-70b-chat-hf`
- Cohere: `command-r-plus`
- Perplexity: `llama-3.1-sonar-large-128k-online`

You can override defaults with the `-m` flag or set a custom default:
```bash
ffmcp config set-default-model gemini gemini-1.5-pro
```

## Architecture

```
ffmcp/
├── ffmcp/
│   ├── __init__.py
│   ├── cli.py              # Main CLI interface
│   ├── config.py           # Configuration management
│   └── providers/
│       ├── __init__.py
│       ├── base.py         # Base provider interface
│       ├── openai_provider.py      # Full OpenAI implementation
│       ├── anthropic_provider.py   # Anthropic Claude
│       ├── gemini_provider.py      # Google Gemini
│       ├── groq_provider.py        # Groq
│       ├── deepseek_provider.py    # DeepSeek
│       ├── mistral_provider.py     # Mistral AI
│       ├── together_provider.py    # Together AI
│       ├── cohere_provider.py      # Cohere
│       └── perplexity_provider.py  # Perplexity AI
├── setup.py
├── requirements.txt
└── README.md
```

## OpenAI Features Supported

- ✅ **Chat Completions** - GPT-4, GPT-3.5, GPT-4o models
- ✅ **Vision** - Image understanding with GPT-4 Vision
- ✅ **DALL·E** - Image generation (DALL·E 2 & 3)
- ✅ **Whisper** - Audio transcription and translation
- ✅ **Text-to-Speech** - TTS-1 and TTS-1-HD models
- ✅ **Embeddings** - Text embeddings for semantic search
- ✅ **Function Calling** - Tools and function calling support
- ✅ **Assistants API** - Create and manage AI assistants
- ✅ **Streaming** - Real-time streaming for all text generation

## Adding New Providers

To add a new AI provider:

1. Create a new file in `ffmcp/providers/` (e.g., `cohere_provider.py`)
2. Inherit from `BaseProvider` and implement required methods
3. Register it in `ffmcp/providers/__init__.py`

Example:

```python
from ffmcp.providers.base import BaseProvider

class CohereProvider(BaseProvider):
    def get_provider_name(self) -> str:
        return 'cohere'
    
    def generate(self, prompt: str, **kwargs) -> str:
        # Implementation
        pass
    # ... implement other methods
```

## Roadmap

- [x] OpenAI full feature support
- [x] Multiple AI providers (9 providers supported!)
- [x] Image generation support
- [x] Audio transcription/translation
- [ ] Batch processing
- [ ] Plugin system for custom providers
- [ ] Python API for programmatic use
- [x] Advanced features (function calling, tool use, etc.)
- [ ] Provider-specific features (Gemini vision, Cohere RAG, etc.)

## Provider Documentation

For detailed information about each provider, see [PROVIDERS.md](PROVIDERS.md) (if available) or run:
```bash
ffmcp providers
```

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License

