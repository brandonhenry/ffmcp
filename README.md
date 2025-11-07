# ffmcp

**ffmcp** - AI command-line tool inspired by ffmpeg. Access any AI service from the command line with a unified interface.

## Features

- 🚀 **Unified CLI**: Single command-line interface for multiple AI providers
- 🔌 **Modular**: Easy to add new AI providers
- 📝 **Simple**: Works just like ffmpeg - simple, powerful, composable
- 🔧 **Configurable**: Manage API keys and settings easily
- 📊 **Streaming**: Real-time streaming support for responses
- 🎨 **Full OpenAI Support**: All OpenAI features including vision, images, audio, embeddings, and assistants
- 🧠 **Memory with Zep (Brains)**: Create brains, store/retrieve chat memory, collections, and graph

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

# Or use environment variables
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
```

### 2. Generate Text

```bash
# Basic generation
ffmcp generate "Write a haiku about coding"

# With specific provider and model
ffmcp generate "Explain quantum computing" -p openai -m gpt-4

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
```

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

### 5. Daily Token Tracking

ffmcp automatically tracks total tokens used per UTC day across supported providers (e.g., OpenAI, Anthropic). Totals are stored in `~/.ffmcp/tokens.json`.

```bash
# Show today's total token count (UTC day)
ffmcp tokens

# Filter by provider (openai or anthropic)
ffmcp tokens -p openai

# Specify a date (UTC, YYYY-MM-DD)
ffmcp tokens -d 2025-11-07
```

Notes:
- The total is best-effort for streaming responses and depends on provider SDK support for usage in stream events.
- Token accounting is updated automatically on each command invocation that returns usage from the provider.

## Zep Memory (Brains)

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
│       ├── openai_provider.py  # Full OpenAI implementation
│       └── anthropic_provider.py
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
- [ ] More AI providers (Google Gemini, Cohere, etc.)
- [x] Image generation support
- [x] Audio transcription/translation
- [ ] Batch processing
- [ ] Plugin system for custom providers
- [ ] Python API for programmatic use
- [x] Advanced features (function calling, tool use, etc.)

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License

