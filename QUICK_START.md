# Quick Setup Guide

## ✅ Installation Complete!

Your `ffmcp` tool is now installed and ready to use.

## Next Steps

### 1. Activate Virtual Environment (if not already active)

```bash
source venv/bin/activate
```

### 2. Configure Your API Keys

```bash
# OpenAI
ffmcp config -p openai -k YOUR_OPENAI_API_KEY

# Anthropic Claude
ffmcp config -p anthropic -k YOUR_ANTHROPIC_API_KEY

# Google Gemini
ffmcp config -p gemini -k YOUR_GEMINI_API_KEY

# Groq (ultra-fast)
ffmcp config -p groq -k YOUR_GROQ_API_KEY

# DeepSeek
ffmcp config -p deepseek -k YOUR_DEEPSEEK_API_KEY

# Mistral AI
ffmcp config -p mistral -k YOUR_MISTRAL_API_KEY

# Together AI
ffmcp config -p together -k YOUR_TOGETHER_API_KEY

# Cohere
ffmcp config -p cohere -k YOUR_COHERE_API_KEY

# Perplexity AI
ffmcp config -p perplexity -k YOUR_PERPLEXITY_API_KEY
```

Or use environment variables:
```bash
export OPENAI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here
export GEMINI_API_KEY=your_key_here
# ... etc
```

### 3. (Optional) Configure Zep for Brains/Memory

```bash
# Zep Cloud
export ZEP_CLOUD_API_KEY=your_key

# Self-hosted (if applicable)
export ZEP_BASE_URL=http://localhost:8000

# Or persist key
ffmcp config -p zep -k YOUR_ZEP_API_KEY
```

### 3. Test Basic Commands

```bash
# Test help
ffmcp --help
ffmcp openai --help

# Test text generation with different providers
ffmcp generate "Hello, world!" -p openai
ffmcp generate "Hello, world!" -p gemini
ffmcp generate "Hello, world!" -p groq
ffmcp generate "Hello, world!" -p anthropic

# List all available providers
ffmcp providers

# Test OpenAI features
ffmcp openai image "A beautiful sunset"
ffmcp openai embed "Sample text"
```

## Available Commands

### Core Commands
- `ffmcp generate` - Generate text
- `ffmcp chat` - Chat with AI (use `--thread` for conversation history)
- `ffmcp config` - Manage API keys
- `ffmcp providers` - List providers
- `ffmcp thread` - Manage chat threads (create, list, use, clear, delete)
- `ffmcp agent thread` - Manage agent threads

### OpenAI Commands
- `ffmcp openai vision` - Analyze images
- `ffmcp openai image` - Generate images (DALL·E)
- `ffmcp openai transcribe` - Transcribe audio
- `ffmcp openai translate` - Translate audio
- `ffmcp openai tts` - Text-to-speech
- `ffmcp openai embed` - Create embeddings
- `ffmcp openai tools` - Function calling
- `ffmcp openai assistant` - Manage assistants

### Brain (Zep) Commands
- `ffmcp brain create|list|use|current|delete`
- `ffmcp brain memory add|get|search|clear`
- `ffmcp brain collection create|list`
- `ffmcp brain document add|search|delete`
- `ffmcp brain graph add|get` (Zep Cloud)

## Example Workflow

```bash
# 1. Generate text with different providers
ffmcp generate "Write a haiku about coding" -p openai
ffmcp generate "Write a haiku about coding" -p gemini
ffmcp generate "Write a haiku about coding" -p groq -s  # Stream with Groq (very fast!)

# 2. Chat with conversation history (threads)
ffmcp thread create conversation1
ffmcp thread use conversation1
ffmcp chat "Hello, I'm Alice" -p openai
ffmcp chat "What's my name?" -p openai  # Remembers!

# 3. Generate an image (OpenAI only)
ffmcp openai image "A futuristic AI laboratory"

# 4. Create embeddings (OpenAI only)
ffmcp openai embed "Machine learning is fascinating" -o embeddings.json

# 5. Transcribe audio (OpenAI only)
ffmcp openai transcribe audio.mp3 -o transcript.txt

# 6. Use Brain memory (Zep)
ffmcp brain create mybrain
ffmcp brain memory add --role user --role-type user --content "Remember: favorite color is blue"
ffmcp brain memory get
ffmcp brain memory get --brain mybrain --session session-123

# 7. Try Perplexity for web-search enabled queries
ffmcp generate "What are the latest developments in AI?" -p perplexity

# 8. Use agents with threads
ffmcp agent create assistant -p openai -m gpt-4o-mini -i "You are helpful"
ffmcp agent thread create assistant project1
ffmcp agent thread use assistant project1
ffmcp agent run "Plan a project" --agent assistant
ffmcp agent run "Add details" --agent assistant  # Remembers conversation!
```

## Troubleshooting

- **Command not found**: Make sure the virtual environment is activated
- **API key error**: Run `ffmcp config -p openai -k YOUR_KEY`
- **Import errors**: Make sure you installed with `pip install -e ".[all]"`

## Need Help?

Check the main README.md for detailed documentation and examples.

