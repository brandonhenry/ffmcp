# How to Use ffmcp

## Basic Setup

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Set Your API Keys
```bash
# Set OpenAI API key
ffmcp config -p openai -k sk-your-openai-api-key-here

# Set other providers
ffmcp config -p anthropic -k sk-ant-your-anthropic-key
ffmcp config -p gemini -k your-gemini-api-key
ffmcp config -p groq -k your-groq-api-key
ffmcp config -p deepseek -k your-deepseek-api-key
ffmcp config -p mistral -k your-mistral-api-key
ffmcp config -p together -k your-together-api-key
ffmcp config -p cohere -k your-cohere-api-key
ffmcp config -p perplexity -k your-perplexity-api-key

# Or use environment variables
export OPENAI_API_KEY=sk-your-openai-api-key-here
export ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
export GEMINI_API_KEY=your-gemini-api-key
# ... etc
```

## Basic Text Generation

### Simple Generation
```bash
ffmcp generate "Write a haiku about Python programming"
```

### With Options
```bash
# Use specific model
ffmcp generate "Explain quantum computing" -p openai -m gpt-4o-mini

# Stream the response (see it as it generates)
ffmcp generate "Tell me a story" -s

# Control creativity (temperature: 0.0-2.0)
ffmcp generate "Creative story" -t 0.9

# Limit response length
ffmcp generate "Summarize this" --max-tokens 100
```

### Read from File / Write to File
```bash
# Read prompt from file
ffmcp generate -i prompt.txt

# Write output to file
ffmcp generate "Write code" -o output.txt

# Both
ffmcp generate -i prompt.txt -o output.txt
```

### Pipe Input
```bash
# Pipe text into ffmcp
echo "Translate to French: Hello world" | ffmcp generate

# Chain with other commands
cat document.txt | ffmcp generate | grep "important"
```

## Chat Mode (Conversational)

```bash
# Simple chat
ffmcp chat "What is 2+2?" -p openai

# With system message (sets the AI's role)
ffmcp chat "Solve this math problem" -s "You are a helpful math tutor" -p openai

# Chat with thread (maintains conversation history)
ffmcp chat "Hello, my name is Alice" -t conversation1
ffmcp chat "What's my name?" -t conversation1  # Remembers!

# Thread management for chat
ffmcp thread create conversation1
ffmcp thread list
ffmcp thread use conversation1
ffmcp thread current
ffmcp thread clear conversation1
ffmcp thread delete conversation1
```

## Agents

```bash
# Create agent with defaults (OpenAI)
ffmcp agent create myagent -p openai -m gpt-4o-mini -i "You are a helpful assistant"

# Create agent with instructions from a file
ffmcp agent create myagent -p openai -m gpt-4o-mini -f instructions.txt

# Optionally attach a brain for memory and document search
ffmcp agent create research -p openai -m gpt-4o-mini --brain mybrain -f research_instructions.txt

# Thread Management (conversation history per agent)
# Create a thread for an agent
ffmcp agent thread create myagent conversation1

# List all threads for an agent
ffmcp agent thread list myagent

# Set active thread (agent run will use this thread)
ffmcp agent thread use myagent conversation1

# Show active thread
ffmcp agent thread current myagent

# Clear messages from a thread (keeps thread, clears history)
ffmcp agent thread clear myagent conversation1

# Delete a thread entirely
ffmcp agent thread delete myagent conversation1

# Enable/disable actions
ffmcp agent action enable myagent web_fetch
ffmcp agent action disable myagent generate_image

# Run the active agent (automatically uses active thread)
ffmcp agent use myagent
ffmcp agent run "Find and summarize today's top AI news"

# Run with specific thread
ffmcp agent run "Continue the conversation" --thread conversation1
```

## Threads: Conversation History

Threads allow you to maintain conversation history for both `chat` and `agent run` commands. This enables ongoing conversations where the AI remembers previous messages.

### Chat Threads

Chat threads work with the `chat` command and are independent of agents:

```bash
# Create a thread
ffmcp thread create conversation1

# Set as active (optional - chat uses active thread automatically)
ffmcp thread use conversation1

# Chat with history
ffmcp chat "Hello, I'm Alice" -t conversation1 -p openai
ffmcp chat "What's my name?" -t conversation1 -p openai  # Remembers!

# Use active thread (no -t flag needed)
ffmcp chat "Hello" -p openai
ffmcp chat "Continue" -p openai  # Automatically uses active thread

# System messages are saved to thread
ffmcp chat "Solve this" -s "You are a math tutor" -t math-thread
ffmcp chat "Another problem" -t math-thread  # Remembers system message

# Manage threads
ffmcp thread list
ffmcp thread current
ffmcp thread clear conversation1
ffmcp thread delete conversation1
```

**Chat Thread Commands:**
- `ffmcp thread create <name>` - Create a new thread
- `ffmcp thread list` - List all threads
- `ffmcp thread use <name>` - Set active thread
- `ffmcp thread current` - Show active thread
- `ffmcp thread clear <name>` - Clear messages (keeps thread)
- `ffmcp thread delete <name>` - Delete thread

### Agent Threads

Agent threads are tied to specific agents and maintain conversation history for agent runs:

```bash
# Create agent and thread
ffmcp agent create myagent -p openai -m gpt-4o-mini -i "You are helpful"
ffmcp agent thread create myagent conversation1

# Set active thread (optional - agent run uses active thread automatically)
ffmcp agent thread use myagent conversation1

# Run agent with conversation history
ffmcp agent run "Plan a trip" --agent myagent
ffmcp agent run "Add details" --agent myagent  # Remembers!

# Specify thread explicitly
ffmcp agent run "New topic" --agent myagent --thread conversation2

# Manage threads
ffmcp agent thread list myagent
ffmcp agent thread current myagent
ffmcp agent thread clear myagent conversation1
ffmcp agent thread delete myagent conversation1
```

**Agent Thread Commands:**
- `ffmcp agent thread create <agent> <name>` - Create thread for agent
- `ffmcp agent thread list <agent>` - List threads for agent
- `ffmcp agent thread use <agent> <name>` - Set active thread
- `ffmcp agent thread current <agent>` - Show active thread
- `ffmcp agent thread clear <agent> <name>` - Clear messages
- `ffmcp agent thread delete <agent> <name>` - Delete thread

### Differences: Chat Threads vs Agent Threads

| Feature | Chat Threads | Agent Threads |
|---------|--------------|---------------|
| **Command** | `ffmcp chat` | `ffmcp agent run` |
| **Tied to** | None (independent) | Specific agent |
| **Actions/Tools** | No | Yes (if agent has actions) |
| **System Messages** | Saved to thread | From agent instructions |
| **Use Case** | Simple conversations | Agent-powered workflows |

### Tips

1. **Use chat threads** for simple conversations without agent features
2. **Use agent threads** when you need agent actions (web search, image generation, etc.)
3. **Active threads** are used automatically - no need to specify `-t` or `--thread` every time
4. **Multiple threads** let you switch between different conversation contexts
5. **Clear vs Delete**: `clear` removes messages but keeps the thread; `delete` removes the thread entirely

## OpenAI Features

### 🖼️ Image Generation (DALL·E)

```bash
# Generate an image
ffmcp openai image "A futuristic cityscape at sunset"

# DALL·E 2 (cheaper, faster)
ffmcp openai image "A cat wearing sunglasses" -m dall-e-2

# High quality
ffmcp openai image "Abstract art" --quality hd

# Natural style (vs vivid)
ffmcp openai image "Portrait" --style natural

# Save URL to file
ffmcp openai image "Beautiful landscape" -o image_url.txt
```

### 👁️ Vision / Image Analysis

```bash
# Analyze a single image
ffmcp openai vision "What's in this image?" photo.jpg

# Analyze multiple images
ffmcp openai vision "Compare these images" img1.jpg img2.png

# With custom model
ffmcp openai vision "Describe this" photo.jpg -m gpt-4o
```

### 🎤 Audio Transcription (Whisper)

```bash
# Basic transcription
ffmcp openai transcribe audio.mp3

# With language hint (for better accuracy)
ffmcp openai transcribe spanish_audio.mp3 -l es

# With prompt (helps with technical terms, names, etc.)
ffmcp openai transcribe meeting.mp3 -p "This is a technical meeting about AI"

# Get JSON output with timestamps
ffmcp openai transcribe audio.mp3 --json -o transcript.json

# Save to file
ffmcp openai transcribe audio.mp3 -o transcript.txt
```

### 🌍 Audio Translation

```bash
# Translate any audio to English
ffmcp openai translate spanish_audio.mp3

# With prompt
ffmcp openai translate audio.mp3 -p "Technical presentation"
```

### 🔊 Text-to-Speech

```bash
# Convert text to speech
ffmcp openai tts "Hello, world!" output.mp3

# Choose voice (alloy, echo, fable, onyx, nova, shimmer)
ffmcp openai tts "Welcome" speech.mp3 -v nova

# Adjust speed (0.25 to 4.0)
ffmcp openai tts "Important announcement" announcement.mp3 -s 1.2

# High quality model
ffmcp openai tts "Professional narration" narration.mp3 -m tts-1-hd
```

### 📊 Embeddings

```bash
# Create embeddings (for semantic search, similarity, etc.)
ffmcp openai embed "This is sample text"

# Custom dimensions
ffmcp openai embed "Vectorize this" -d 256

# Get full JSON with usage stats
ffmcp openai embed "Text to embed" --json -o embeddings.json

# Save to file
ffmcp openai embed "Important text" -o vectors.json
```

### 🔧 Function Calling / Tools

```bash
# First, create a tools.json file
cat > tools.json << 'EOF'
[
  {
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get the current weather in a location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA"
          }
        },
        "required": ["location"]
      }
    }
  }
]
EOF

# Use function calling
ffmcp openai tools "What's the weather in San Francisco?" -t tools.json
```

### 🤖 Assistants API

```bash
# Create an assistant
ffmcp openai assistant create "Math Tutor" "You are a helpful math tutor" -o assistant_id.txt

# Create a conversation thread
ffmcp openai assistant thread -o thread_id.txt

# Add a message to the thread
ffmcp openai assistant message $(cat thread_id.txt) "Solve 2x + 5 = 15"

# Run the assistant
ffmcp openai assistant run $(cat thread_id.txt) $(cat assistant_id.txt)

# Get all messages from thread
ffmcp openai assistant messages $(cat thread_id.txt)

# Upload a file for the assistant to use
ffmcp openai assistant upload document.pdf
```

## 🧠 Brains (Zep Memory)

**Note:** Brains are separate from threads. Threads maintain conversation history locally, while Brains provide advanced memory features including semantic search, document storage, and graph relationships. You can use both together - agents can have threads for conversation history AND a brain for long-term memory and document search.

### Setup Zep
```bash
# Zep Cloud (recommended)
export ZEP_CLOUD_API_KEY=your_key

# Self-hosted Zep (optional)
export ZEP_BASE_URL=http://localhost:8000

# Or persist the API key
ffmcp config -p zep -k YOUR_ZEP_API_KEY
```

### Create and Use a Brain
```bash
# Create a brain and set it active
ffmcp brain create mybrain

# Show active brain
ffmcp brain current

# List brains
ffmcp brain list

# Switch active brain
ffmcp brain use mybrain
```

### Chat Memory
```bash
# Add a message to memory (session defaults to brain name)
ffmcp brain memory add --role user --role-type user --content "Who was Octavia Butler?"

# Get memory context
ffmcp brain memory get

# Get memory for a specific named brain
ffmcp brain memory get --brain mybrain

# Get memory for a specific session within a brain
ffmcp brain memory get --brain mybrain --session session-123

# Semantic search over memory
ffmcp brain memory search "Octavia"

# Clear memory for the session
ffmcp brain memory clear
```

Notes:
- If you omit `--brain`, the active brain is used (`ffmcp brain use <name>`).
- If you omit `--session`, it defaults to the brain’s `default_session_id` (if set) or the brain name.

### Collections & Documents
```bash
# Create a collection (namespaced as mybrain::knowledge)
ffmcp brain collection create knowledge --description "KB for mybrain"

# Add a document
ffmcp brain document add knowledge --text "Zep is a memory platform for LLM apps" --id doc1

# Search documents
ffmcp brain document search knowledge "memory platform"
```

### Graph (Zep Cloud only)
```bash
# Add JSON data to a user's graph
echo '{"projects":{"alpha":{"status":"in progress"}}}' | \
  ffmcp brain graph add user-123 --type json --input -

# Get graph data
ffmcp brain graph get user-123
```

## Real-World Examples

### Example 1: Transcribe and Summarize a Meeting
```bash
# Step 1: Transcribe audio
ffmcp openai transcribe meeting.mp3 -o transcript.txt

# Step 2: Summarize transcript
ffmcp generate -i transcript.txt -o summary.txt -p openai
```

### Example 2: Generate Image from Text Description
```bash
# Generate image
ffmcp openai image "A futuristic AI laboratory with holographic displays" -o image_url.txt

# Get the URL
cat image_url.txt
```

### Example 3: Create Embeddings for Search
```bash
# Create embeddings for multiple documents
for file in *.txt; do
    ffmcp openai embed "$(cat $file)" -o "${file%.txt}_embedding.json"
done
```

### Example 4: Batch Process Files
```bash
# Process all text files
for file in *.txt; do
    ffmcp generate -i "$file" -o "${file%.txt}_processed.txt" -p openai
done
```

### Example 5: Interactive Script
```bash
#!/bin/bash
echo "Enter your prompt:"
read PROMPT
ffmcp generate "$PROMPT" -p openai -s
```

## Common Options

### Provider Selection
```bash
-p openai      # Use OpenAI (default)
-p anthropic   # Use Anthropic Claude
-p gemini      # Use Google Gemini
-p groq        # Use Groq (ultra-fast)
-p deepseek    # Use DeepSeek
-p mistral     # Use Mistral AI
-p together    # Use Together AI
-p cohere      # Use Cohere
-p perplexity  # Use Perplexity AI (with web search)
```

### Model Selection
```bash
# OpenAI
-m gpt-4o-mini           # OpenAI default
-m gpt-4o                # More capable

# Anthropic
-m claude-3-5-sonnet     # Anthropic default
-m claude-3-opus         # Most capable

# Gemini
-m gemini-2.0-flash-exp   # Gemini default
-m gemini-1.5-pro        # More capable

# Groq
-m llama-3.1-70b-versatile  # Groq default
-m mixtral-8x7b-32768    # Alternative

# DeepSeek
-m deepseek-chat         # DeepSeek default
-m deepseek-coder        # Code-focused

# Mistral
-m mistral-large-latest  # Mistral default
-m pixtral-large-latest  # Vision-capable

# Together
-m meta-llama/Llama-3-70b-chat-hf  # Together default
-m mistralai/Mixtral-8x7B-Instruct-v0.1  # Alternative

# Cohere
-m command-r-plus        # Cohere default
-m command-r             # Alternative

# Perplexity
-m llama-3.1-sonar-large-128k-online  # Perplexity default
-m sonar-pro             # Alternative
```

### Output Control
```bash
-o output.txt    # Write to file
-s               # Stream (real-time)
--json           # JSON output (for some commands)
```

### Generation Parameters
```bash
-t 0.7           # Temperature (0.0-2.0, creativity)
--max-tokens 500 # Limit response length
```

## Getting Help

```bash
# General help
ffmcp --help

# Command-specific help
ffmcp generate --help
ffmcp openai --help
ffmcp openai image --help

# List providers
ffmcp providers
```

## Tips

1. **Always activate venv first**: `source venv/bin/activate`
2. **Use streaming** (`-s`) for long responses to see progress
3. **Save API keys** in config: `ffmcp config -p openai -k YOUR_KEY`
4. **Pipe commands** together for complex workflows
5. **Use `-o` flag** to save outputs for later use
6. **Check help** for each command: `ffmcp COMMAND --help`

## Troubleshooting

- **"Could not find a version that satisfies the requirement ffmcp"**: This package is not on PyPI. Install from source using `pip install -e .` from the project directory.
- **"externally-managed-environment" error**: You must use a virtual environment on macOS with Homebrew Python. Create one with `python3 -m venv venv` and activate it.
- **"Command not found"**: Activate venv with `source venv/bin/activate`
- **"API key not configured"**: Run `ffmcp config -p openai -k YOUR_KEY`
- **"Module not found"**: Install with `pip install -e ".[all]"`
- **Permission errors**: Make sure venv is activated

