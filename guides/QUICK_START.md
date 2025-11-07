# Quick Setup Guide

## Installation

### Option 1: Install via pip (Recommended)

The easiest way to install ffmcp:

```bash
# Install the base package
pip install ffmcp

# Or install with specific providers
pip install ffmcp[openai]
pip install ffmcp[anthropic]
pip install ffmcp[all]
```

**Note:** On macOS with Homebrew Python, you may encounter an "externally-managed-environment" error. Use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install ffmcp
```

### Option 2: Install from Source (Development)

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/brandonhenry/ffmcp.git
cd ffmcp

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Or install with all providers
pip install -e ".[all]"
```

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

# ElevenLabs (for voiceover/TTS)
ffmcp config -p elevenlabs -k YOUR_ELEVENLABS_API_KEY
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

### Voiceover/TTS Commands
- `ffmcp voiceover create` - Create voice configuration
- `ffmcp voiceover list` - List saved voices
- `ffmcp voiceover show <name>` - Show voice details
- `ffmcp voiceover update <name>` - Update voice settings
- `ffmcp voiceover delete <name>` - Delete voice
- `ffmcp voiceover provider list --provider elevenlabs` - List provider voices
- `ffmcp voiceover provider show --provider elevenlabs <voice_id>` - Show provider voice
- `ffmcp tts <text> <output_file>` - Generate speech
- `ffmcp agent voice set <agent> <voice>` - Set agent voice
- `ffmcp agent voice remove <agent>` - Remove agent voice
- `ffmcp agent voice show <agent>` - Show agent voice

### Agent Commands
- `ffmcp agent create <name>` - Create an agent
- `ffmcp agent list|use|show|delete` - Manage agents
- `ffmcp agent run <prompt>` - Run an agent
- `ffmcp agent action enable|disable` - Manage agent actions
- `ffmcp agent thread create|list|use|clear|delete` - Manage agent threads

### Team Commands (Hierarchical)
- `ffmcp team create <name> -o <orchestrator>` - Create a team with orchestrator
- `ffmcp team create <name> -o <orchestrator> -m <member> -s <sub-team> -b <brain>` - Create hierarchical team
- `ffmcp team list|show|use|current|delete` - Manage teams
- `ffmcp team add-member|remove-member` - Manage team members
- `ffmcp team add-sub-team|remove-sub-team` - Manage sub-teams
- `ffmcp team set-orchestrator` - Set team orchestrator
- `ffmcp team run <task>` - Run a task with a team

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

# 9. Create hierarchical teams (agents working together)
ffmcp agent create ceo -p openai -m gpt-4o-mini -i "You are a CEO orchestrating teams"
ffmcp agent create researcher -p openai -m gpt-4o-mini -i "You are a researcher"
ffmcp agent create writer -p openai -m gpt-4o-mini -i "You are a writer"
ffmcp agent action enable ceo delegate_to_agent
ffmcp brain create team-brain
ffmcp team create org-team -o ceo -m researcher -m writer -b team-brain
ffmcp team run "Create a comprehensive report" --team org-team

# 10. Create nested teams (teams within teams)
ffmcp agent create research-manager -p openai -m gpt-4o-mini -i "You manage research"
ffmcp agent action enable research-manager delegate_to_agent
ffmcp team create research-sub-team -o research-manager -m researcher -b team-brain
ffmcp team create main-team -o ceo -s research-sub-team -m writer -b team-brain
ffmcp team run "Research and write a report" --team main-team

# 11. Use voiceover/TTS
ffmcp config -p elevenlabs -k YOUR_ELEVENLABS_API_KEY
ffmcp voiceover provider list --provider elevenlabs
ffmcp voiceover create my-voice --provider elevenlabs --voice-id 21m00Tcm4TlvDq8ikWAM
ffmcp tts "Hello, world!" output.mp3 --voice my-voice
ffmcp agent voice set assistant my-voice
```

## Troubleshooting

- **"Could not find a version that satisfies the requirement ffmcp"**: Make sure you're using Python 3.8+ and pip is up to date: `pip install --upgrade pip`
- **"externally-managed-environment" error**: You must use a virtual environment on macOS with Homebrew Python. Create one with `python3 -m venv venv` and activate it.
- **Command not found**: Make sure ffmcp is installed and in your PATH. If using a virtual environment, make sure it's activated.
- **API key error**: Run `ffmcp config -p openai -k YOUR_KEY`
- **Import errors**: Make sure you installed with `pip install ffmcp[all]` or `pip install -e ".[all]"` if installing from source

## Need Help?

Check the main README.md for detailed documentation and examples.

