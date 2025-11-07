# Voiceover/TTS Guide

ffmcp includes a comprehensive voiceover/TTS (Text-to-Speech) system that supports multiple providers, voice configuration management, and seamless integration with agents.

## Features

- ✅ **Multiple TTS Providers** - ElevenLabs (more coming soon)
- ✅ **Voice Configuration Management** - Create, read, update, delete voice configs
- ✅ **Provider Voice Discovery** - List and explore available voices from providers
- ✅ **Agent Voice Integration** - Assign voices to agents for consistent TTS output
- ✅ **Flexible TTS Generation** - Use saved configs or direct parameters
- ✅ **Advanced Voice Settings** - Fine-tune stability, similarity, style, and more
- ✅ **Multiple Output Formats** - MP3, PCM, and more

## Quick Start

### 1. Configure API Key

```bash
# Set ElevenLabs API key
ffmcp config -p elevenlabs -k YOUR_ELEVENLABS_API_KEY

# Or use environment variable
export ELEVENLABS_API_KEY=your_key
```

### 2. Discover Available Voices

```bash
# List all voices from ElevenLabs
ffmcp voiceover provider list --provider elevenlabs

# Show details of a specific voice
ffmcp voiceover provider show --provider elevenlabs 21m00Tcm4TlvDq8ikWAM
```

### 3. Create a Voice Configuration

```bash
# Simple voice configuration
ffmcp voiceover create my-voice \
  --provider elevenlabs \
  --voice-id 21m00Tcm4TlvDq8ikWAM \
  --description "My favorite voice"
```

### 4. Generate Speech

```bash
# Using saved voice configuration
ffmcp tts "Hello, world!" output.mp3 --voice my-voice
```

## Voice Configuration Management

### Create Voice Configuration

Create a named voice configuration that stores provider, voice ID, and settings:

```bash
# Basic configuration
ffmcp voiceover create my-voice \
  --provider elevenlabs \
  --voice-id 21m00Tcm4TlvDq8ikWAM

# With all settings
ffmcp voiceover create narrator \
  --provider elevenlabs \
  --voice-id pNInz6obpgDQGcFmaJgB \
  --model-id eleven_multilingual_v2 \
  --stability 0.5 \
  --similarity-boost 0.75 \
  --style 0.0 \
  --use-speaker-boost \
  --output-format mp3_44100_128 \
  --description "Narrator voice for stories"
```

**Required Parameters:**
- `--provider` / `-p`: TTS provider name (e.g., `elevenlabs`)
- `--voice-id`: Voice ID from the provider

**Optional Parameters:**
- `--model-id`: TTS model (e.g., `eleven_multilingual_v2`, `eleven_turbo_v2`)
- `--stability`: Voice stability (0.0-1.0, default: 0.5)
- `--similarity-boost`: Similarity to original voice (0.0-1.0, default: 0.75)
- `--style`: Style exaggeration (0.0-1.0, default: 0.0)
- `--use-speaker-boost` / `--no-speaker-boost`: Enable speaker boost (default: enabled)
- `--output-format`: Audio format (e.g., `mp3_44100_128`, `pcm_16000`)
- `--description`: Human-readable description

### List Voice Configurations

```bash
# List all saved voices
ffmcp voiceover list
```

Output shows: `voice-name (provider:voice_id) - description`

### Show Voice Details

```bash
# Show full voice configuration
ffmcp voiceover show my-voice
```

### Update Voice Configuration

```bash
# Update specific settings
ffmcp voiceover update my-voice --stability 0.6 --similarity-boost 0.8

# Update multiple settings
ffmcp voiceover update narrator \
  --stability 0.7 \
  --style 0.2 \
  --description "Updated narrator voice"
```

### Delete Voice Configuration

```bash
# Delete a voice (also removes from agents using it)
ffmcp voiceover delete my-voice
```

## Provider Voice Discovery

### List Provider Voices

Explore available voices directly from TTS providers:

```bash
# List all voices from ElevenLabs
ffmcp voiceover provider list --provider elevenlabs
```

Output format: `voice_id: voice_name [category] - description`

### Show Provider Voice Details

```bash
# Get detailed information about a provider voice
ffmcp voiceover provider show --provider elevenlabs 21m00Tcm4TlvDq8ikWAM
```

## Text-to-Speech Generation

### Using Saved Voice Configuration

```bash
# Simple usage with saved voice
ffmcp tts "Hello, this is a test" output.mp3 --voice my-voice

# Override specific settings
ffmcp tts "Custom settings test" output.mp3 \
  --voice my-voice \
  --stability 0.7 \
  --similarity-boost 0.9
```

### Using Provider Directly

```bash
# Use provider and voice ID directly (no saved config needed)
ffmcp tts "Direct voice usage" output.mp3 \
  --provider elevenlabs \
  --voice-id 21m00Tcm4TlvDq8ikWAM

# With all parameters
ffmcp tts "Full control" output.mp3 \
  --provider elevenlabs \
  --voice-id 21m00Tcm4TlvDq8ikWAM \
  --model-id eleven_multilingual_v2 \
  --stability 0.5 \
  --similarity-boost 0.75 \
  --style 0.0 \
  --use-speaker-boost \
  --output-format mp3_44100_128
```

### TTS Parameters

**Required:**
- `text`: Text to convert to speech
- `output_file`: Path to save audio file
- Either `--voice` (saved config) OR `--provider` + `--voice-id` (direct)

**Optional (can override saved config):**
- `--model-id`: TTS model ID
- `--stability`: Voice stability (0.0-1.0)
- `--similarity-boost`: Similarity boost (0.0-1.0)
- `--style`: Style exaggeration (0.0-1.0)
- `--use-speaker-boost` / `--no-speaker-boost`: Speaker boost
- `--output-format`: Audio output format

## Agent Voice Integration

Associate voices with agents for consistent TTS output when generating speech from agent responses.

### Create Agent with Voice

```bash
# Create agent and assign voice at creation
ffmcp agent create assistant \
  -p openai \
  -m gpt-4o-mini \
  -i "You are a helpful assistant" \
  --voice my-voice
```

### Set Voice for Existing Agent

```bash
# Assign voice to existing agent
ffmcp agent voice set assistant my-voice
```

### Show Agent Voice

```bash
# Check which voice an agent uses
ffmcp agent voice show assistant
```

### Remove Voice from Agent

```bash
# Remove voice association
ffmcp agent voice remove assistant
```

**Note:** When a voice is deleted, it's automatically removed from all agents using it.

## Voice Parameters Explained

### Stability (0.0-1.0)
- **Lower values (0.0-0.3)**: More variation, expressive, less consistent
- **Higher values (0.7-1.0)**: More consistent, stable, less variation
- **Default**: 0.5 (balanced)

### Similarity Boost (0.0-1.0)
- **Lower values**: Less similar to original voice
- **Higher values**: More similar to original voice
- **Default**: 0.75

### Style (0.0-1.0)
- **Lower values**: More neutral, less exaggerated
- **Higher values**: More style exaggeration, expressive
- **Default**: 0.0

### Speaker Boost
- **Enabled**: Enhances clarity and intelligibility
- **Disabled**: More natural, less processed
- **Default**: Enabled

### Output Formats

Common formats for ElevenLabs:
- `mp3_44100_128` - MP3, 44.1kHz, 128kbps (default)
- `mp3_44100_192` - MP3, 44.1kHz, 192kbps (higher quality)
- `pcm_16000` - PCM, 16kHz
- `pcm_22050` - PCM, 22.05kHz
- `pcm_24000` - PCM, 24kHz
- `pcm_44100` - PCM, 44.1kHz

### Model IDs

Common ElevenLabs models:
- `eleven_multilingual_v2` - Multilingual model (default)
- `eleven_turbo_v2` - Faster, optimized model
- `eleven_monolingual_v1` - English-only model

## Supported Providers

### ElevenLabs

**Features:**
- High-quality multilingual TTS
- Voice cloning support
- Multiple voice models
- Advanced voice settings
- Multiple output formats

**Setup:**
```bash
ffmcp config -p elevenlabs -k YOUR_ELEVENLABS_API_KEY
```

**Get API Key:**
1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Navigate to Profile → API Keys
3. Create a new API key

**Common Voice IDs:**
- `21m00Tcm4TlvDq8ikWAM` - Rachel (English, female)
- `AZnzlk1XvdvUeBnXmlld` - Domi (English, female)
- `EXAVITQu4vr4xnSDxMaL` - Bella (English, female)
- `ErXwobaYiN019PkySvjV` - Antoni (English, male)
- `MF3mGyEYCl7XYWbV9V6O` - Elli (English, female)
- `TxGEqnHWrfWFTfGW9XjX` - Josh (English, male)
- `VR6AewLTigWG4xSOukaG` - Arnold (English, male)
- `pNInz6obpgDQGcFmaJgB` - Adam (English, male)
- `yoZ06aMxZJJ28mfd3POQ` - Sam (English, male)

**Note:** Voice IDs may vary. Use `ffmcp voiceover provider list --provider elevenlabs` to see available voices.

## Example Workflows

### Workflow 1: Basic TTS Usage

```bash
# 1. Configure API key
ffmcp config -p elevenlabs -k YOUR_KEY

# 2. Discover voices
ffmcp voiceover provider list --provider elevenlabs

# 3. Create voice config
ffmcp voiceover create narrator \
  --provider elevenlabs \
  --voice-id 21m00Tcm4TlvDq8ikWAM

# 4. Generate speech
ffmcp tts "Welcome to the future" welcome.mp3 --voice narrator
```

### Workflow 2: Agent with Voice

```bash
# 1. Create voice configuration
ffmcp voiceover create assistant-voice \
  --provider elevenlabs \
  --voice-id pNInz6obpgDQGcFmaJgB \
  --stability 0.6 \
  --similarity-boost 0.8

# 2. Create agent with voice
ffmcp agent create assistant \
  -p openai \
  -m gpt-4o-mini \
  -i "You are a helpful assistant" \
  --voice assistant-voice

# 3. Generate text with agent
ffmcp agent run "Explain quantum computing" --agent assistant > response.txt

# 4. Convert response to speech
ffmcp tts "$(cat response.txt)" response.mp3 --voice assistant-voice
```

### Workflow 3: Multiple Voices for Different Use Cases

```bash
# Create different voices for different purposes
ffmcp voiceover create narrator \
  --provider elevenlabs \
  --voice-id 21m00Tcm4TlvDq8ikWAM \
  --stability 0.7 \
  --description "For narration"

ffmcp voiceover create character \
  --provider elevenlabs \
  --voice-id pNInz6obpgDQGcFmaJgB \
  --stability 0.4 \
  --style 0.3 \
  --description "For character voices"

# Use appropriate voice for each use case
ffmcp tts "Once upon a time..." story.mp3 --voice narrator
ffmcp tts "Hello, I'm a character!" character.mp3 --voice character
```

## Troubleshooting

### API Key Not Found

**Error:** `API key not configured for elevenlabs`

**Solution:**
```bash
ffmcp config -p elevenlabs -k YOUR_ELEVENLABS_API_KEY
```

### Voice Not Found

**Error:** `Unknown voice: my-voice`

**Solution:**
- Check voice exists: `ffmcp voiceover list`
- Create voice: `ffmcp voiceover create my-voice --provider elevenlabs --voice-id VOICE_ID`

### Provider Voice Not Found

**Error:** `Voice 'voice_id' not found`

**Solution:**
- List available voices: `ffmcp voiceover provider list --provider elevenlabs`
- Verify voice ID is correct

### Import Error

**Error:** `elevenlabs package not installed`

**Solution:**
```bash
pip install elevenlabs
```

### Invalid Voice Parameters

**Error:** Parameter validation errors

**Solution:**
- Stability, similarity-boost, style must be between 0.0 and 1.0
- Check provider documentation for valid model IDs and output formats

## Advanced Usage

### Batch TTS Generation

```bash
# Generate multiple files
for text in "Hello" "World" "Test"; do
  ffmcp tts "$text" "${text}.mp3" --voice my-voice
done
```

### Custom Output Formats

```bash
# High-quality MP3
ffmcp tts "High quality" output.mp3 \
  --voice my-voice \
  --output-format mp3_44100_192

# PCM format for processing
ffmcp tts "PCM format" output.pcm \
  --voice my-voice \
  --output-format pcm_44100
```

### Voice Settings Experimentation

```bash
# Test different stability settings
for stability in 0.3 0.5 0.7 0.9; do
  ffmcp tts "Stability test: $stability" "stability_${stability}.mp3" \
    --voice my-voice \
    --stability $stability
done
```

## Future Providers

The voiceover system is designed to support multiple TTS providers. Planned additions include:

- Google Cloud Text-to-Speech
- Amazon Polly
- Azure Cognitive Services Speech
- OpenAI TTS (via existing OpenAI provider)

## Contributing

To add a new TTS provider:

1. Create a provider file in `ffmcp/voiceover/` (e.g., `google_provider.py`)
2. Inherit from `BaseTTSProvider` and implement required methods
3. Register in `ffmcp/voiceover/__init__.py`

See existing `elevenlabs_provider.py` for reference implementation.

