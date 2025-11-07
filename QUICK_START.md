# Quick Setup Guide

## ✅ Installation Complete!

Your `ffmcp` tool is now installed and ready to use.

## Next Steps

### 1. Activate Virtual Environment (if not already active)

```bash
source venv/bin/activate
```

### 2. Configure Your OpenAI API Key

```bash
ffmcp config -p openai -k YOUR_OPENAI_API_KEY
```

Or set it as an environment variable:
```bash
export OPENAI_API_KEY=your_key_here
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

# Test text generation
ffmcp generate "Hello, world!" -p openai

# Test OpenAI features
ffmcp openai image "A beautiful sunset"
ffmcp openai embed "Sample text"
```

## Available Commands

### Core Commands
- `ffmcp generate` - Generate text
- `ffmcp chat` - Chat with AI
- `ffmcp config` - Manage API keys
- `ffmcp providers` - List providers

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
# 1. Generate text
ffmcp generate "Write a haiku about coding" -p openai

# 2. Generate an image
ffmcp openai image "A futuristic AI laboratory"

# 3. Create embeddings
ffmcp openai embed "Machine learning is fascinating" -o embeddings.json

# 4. Transcribe audio (if you have an audio file)
ffmcp openai transcribe audio.mp3 -o transcript.txt

# 5. Use Brain memory (Zep)
ffmcp brain create mybrain
ffmcp brain memory add --role user --role-type user --content "Remember: favorite color is blue"
ffmcp brain memory get
```

## Troubleshooting

- **Command not found**: Make sure the virtual environment is activated
- **API key error**: Run `ffmcp config -p openai -k YOUR_KEY`
- **Import errors**: Make sure you installed with `pip install -e ".[all]"`

## Need Help?

Check the main README.md for detailed documentation and examples.

