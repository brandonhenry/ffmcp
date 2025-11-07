# Voiceover/TTS Guide

ffmcp includes a comprehensive voiceover/TTS (Text-to-Speech) system that supports multiple providers, voice configuration management, and seamless integration with agents.

## Features

- ✅ **Multiple TTS Providers** - ElevenLabs, FishAudio (more coming soon)
- ✅ **Voice Configuration Management** - Create, read, update, delete voice configs
- ✅ **Provider Voice Discovery** - List and explore available voices from providers
- ✅ **Agent Voice Integration** - Assign voices to agents for consistent TTS output
- ✅ **Flexible TTS Generation** - Use saved configs or direct parameters
- ✅ **Advanced Voice Settings** - Fine-tune stability, similarity, style, and more
- ✅ **Voice Cloning** - FishAudio supports reference audio for voice cloning
- ✅ **Multiple Output Formats** - MP3, PCM, WAV, Opus, and more
- ✅ **Programmatic API** - Use TTS functionality in Python scripts

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

**Installation:**
```bash
pip install elevenlabs
```

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

**ElevenLabs-Specific Parameters:**
- `--model-id`: Model to use (`eleven_multilingual_v2`, `eleven_turbo_v2`, `eleven_monolingual_v1`)
- `--stability`: Voice stability (0.0-1.0)
- `--similarity-boost`: Similarity to original voice (0.0-1.0)
- `--style`: Style exaggeration (0.0-1.0)
- `--use-speaker-boost`: Enable speaker boost (boolean)
- `--output-format`: Audio format (`mp3_44100_128`, `mp3_44100_192`, `pcm_16000`, `pcm_22050`, `pcm_24000`, `pcm_44100`)

### FishAudio

**Features:**
- High-quality TTS with voice cloning
- Reference audio support for custom voices
- Multiple output formats (MP3, WAV, PCM, Opus)
- Prosody control (speed and volume)
- Model-based voice selection

**Setup:**
```bash
ffmcp config -p fishaudio -k YOUR_FISHAUDIO_API_KEY
```

**Get API Key:**
1. Sign up at [FishAudio](https://fish.audio) or your FishAudio provider
2. Navigate to API settings
3. Create a new API key

**Installation:**
```bash
pip install fish-audio-sdk
```

**FishAudio-Specific Parameters:**
- `--reference-id`: Voice model/reference ID (alternative to voice-id)
- `--reference-audio`: Path to reference audio file for voice cloning
- `--reference-text`: Text corresponding to reference audio (helps with cloning quality)
- `--format`: Output format (`mp3`, `wav`, `pcm`, `opus`)
- `--prosody-speed`: Speech speed multiplier (e.g., 1.0 = normal, 1.5 = faster)
- `--prosody-volume`: Volume adjustment (typically 0 = normal)

**Creating a FishAudio Voice Configuration:**

```bash
# Using a model/reference ID
ffmcp voiceover create fish-voice \
  --provider fishaudio \
  --reference-id my-model-id \
  --format mp3 \
  --prosody-speed 1.0 \
  --description "FishAudio voice"

# Using reference audio for voice cloning
ffmcp voiceover create cloned-voice \
  --provider fishaudio \
  --reference-audio /path/to/reference.wav \
  --reference-text "This is a sample of the voice I want to clone" \
  --format wav \
  --prosody-speed 1.0 \
  --description "Cloned voice from audio"
```

**Using FishAudio for TTS:**

```bash
# With saved voice configuration
ffmcp tts "Hello from FishAudio" output.mp3 --voice fish-voice

# Direct usage with reference ID
ffmcp tts "Direct FishAudio usage" output.mp3 \
  --provider fishaudio \
  --reference-id my-model-id \
  --format mp3

# Using reference audio for one-time cloning
ffmcp tts "This will sound like the reference" output.mp3 \
  --provider fishaudio \
  --reference-audio /path/to/reference.wav \
  --reference-text "Reference text" \
  --format wav \
  --prosody-speed 1.2
```

**FishAudio Voice Cloning Tips:**
- Use high-quality reference audio (clear, minimal background noise)
- Provide accurate `reference-text` matching the audio content
- Reference audio should be at least 3-5 seconds for best results
- Supported audio formats: WAV, MP3, FLAC
- For best cloning quality, use 16kHz or higher sample rate

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
- For FishAudio, ensure reference audio file exists and is readable

### FishAudio Reference Audio Issues

**Error:** `Reference audio file not found` or cloning quality issues

**Solution:**
- Ensure reference audio file path is correct and file exists
- Use high-quality audio files (WAV, MP3, FLAC)
- Provide accurate `reference-text` matching the audio content
- Reference audio should be at least 3-5 seconds for best results
- Check file permissions: `chmod 644 /path/to/reference.wav`

### API Rate Limits

**Error:** Rate limit exceeded or quota errors

**Solution:**
- Implement delays between requests: `sleep 1` between calls
- Use batch processing with rate limiting
- Check your provider's API quota/limits
- Consider upgrading your API plan if needed

### Audio File Not Generated

**Error:** No error but file doesn't exist

**Solution:**
- Check output directory permissions
- Ensure sufficient disk space
- Verify output path is writable: `touch output.mp3` (should succeed)
- Check for silent failures in provider logs

## Programmatic Usage

You can use ffmcp's TTS functionality programmatically in Python scripts:

### Basic Programmatic TTS

```python
from ffmcp.voiceover import get_tts_provider
from ffmcp.config import Config

# Initialize config
config = Config()

# Get a TTS provider
tts_provider = get_tts_provider('elevenlabs', config)

# Generate speech
output_path = tts_provider.text_to_speech(
    text="Hello, this is a programmatic TTS example",
    output_path="output.mp3",
    voice_id="21m00Tcm4TlvDq8ikWAM",
    model_id="eleven_multilingual_v2",
    stability=0.5,
    similarity_boost=0.75,
    style=0.0,
    use_speaker_boost=True,
    output_format="mp3_44100_128"
)

print(f"Audio saved to: {output_path}")
```

### Using Saved Voice Configurations Programmatically

```python
from ffmcp.voiceover import get_tts_provider
from ffmcp.config import Config

config = Config()

# Get saved voice configuration
voice_config = config.get_voice('my-voice')
if not voice_config:
    raise ValueError("Voice 'my-voice' not found")

# Get provider
provider_name = voice_config['provider']
tts_provider = get_tts_provider(provider_name, config)

# Build parameters from saved config
kwargs = {}
if 'model_id' in voice_config:
    kwargs['model_id'] = voice_config['model_id']
if 'stability' in voice_config:
    kwargs['stability'] = voice_config['stability']
if 'similarity_boost' in voice_config:
    kwargs['similarity_boost'] = voice_config['similarity_boost']
if 'style' in voice_config:
    kwargs['style'] = voice_config['style']
if 'use_speaker_boost' in voice_config:
    kwargs['use_speaker_boost'] = voice_config['use_speaker_boost']
if 'output_format' in voice_config:
    kwargs['output_format'] = voice_config['output_format']

# Generate speech
output_path = tts_provider.text_to_speech(
    text="Using saved voice configuration",
    output_path="output.mp3",
    voice_id=voice_config.get('voice_id'),
    **kwargs
)
```

### Listing Available Voices Programmatically

```python
from ffmcp.voiceover import get_tts_provider
from ffmcp.config import Config

config = Config()

# Get provider
tts_provider = get_tts_provider('elevenlabs', config)

# List all voices
voices = tts_provider.list_voices()

print("Available voices:")
for voice in voices:
    print(f"  {voice['id']}: {voice['name']}")
    if 'description' in voice:
        print(f"    Description: {voice['description']}")

# Get specific voice details
voice_details = tts_provider.get_voice('21m00Tcm4TlvDq8ikWAM')
if voice_details:
    print(f"\nVoice details: {voice_details}")
```

### FishAudio Programmatic Usage

```python
from ffmcp.voiceover import get_tts_provider
from ffmcp.config import Config

config = Config()

# Get FishAudio provider
tts_provider = get_tts_provider('fishaudio', config)

# Using reference ID
output_path = tts_provider.text_to_speech(
    text="Hello from FishAudio",
    output_path="output.mp3",
    voice_id="my-model-id",  # or use reference_id in kwargs
    format="mp3",
    prosody={"speed": 1.0, "volume": 0}
)

# Using reference audio for voice cloning
output_path = tts_provider.text_to_speech(
    text="This will sound like the reference audio",
    output_path="cloned.mp3",
    reference_audio="/path/to/reference.wav",
    reference_text="This is the reference text",
    format="wav",
    prosody={"speed": 1.2, "volume": 0}
)
```

### Batch Processing with Error Handling

```python
from ffmcp.voiceover import get_tts_provider
from ffmcp.config import Config
import os

config = Config()
tts_provider = get_tts_provider('elevenlabs', config)

texts = [
    "First audio clip",
    "Second audio clip",
    "Third audio clip"
]

output_dir = "audio_output"
os.makedirs(output_dir, exist_ok=True)

for i, text in enumerate(texts, 1):
    try:
        output_path = tts_provider.text_to_speech(
            text=text,
            output_path=f"{output_dir}/clip_{i}.mp3",
            voice_id="21m00Tcm4TlvDq8ikWAM"
        )
        print(f"✓ Generated: {output_path}")
    except Exception as e:
        print(f"✗ Error generating clip {i}: {e}")
```

### Integrating with Agent Responses

```python
from ffmcp.voiceover import get_tts_provider
from ffmcp.config import Config
from ffmcp.agents import Agent

config = Config()

# Create and run agent
agent = Agent(
    config=config,
    name="assistant",
    provider="openai",
    model="gpt-4o-mini",
    instructions="You are a helpful assistant"
)

# Get agent response
response = agent.run("Explain quantum computing in simple terms")

# Get agent's voice configuration
voice_name = config.get_agent_voice("assistant")
if voice_name:
    voice_config = config.get_voice(voice_name)
    
    # Generate TTS from response
    tts_provider = get_tts_provider(voice_config['provider'], config)
    
    output_path = tts_provider.text_to_speech(
        text=response,
        output_path="agent_response.mp3",
        voice_id=voice_config.get('voice_id'),
        **{k: v for k, v in voice_config.items() 
           if k not in ['provider', 'voice_id', 'name', 'description']}
    )
    
    print(f"Agent response audio: {output_path}")
```

## Advanced Usage

### Batch TTS Generation

```bash
# Generate multiple files
for text in "Hello" "World" "Test"; do
  ffmcp tts "$text" "${text}.mp3" --voice my-voice
done

# Process text file line by line
counter=1
while IFS= read -r line; do
  ffmcp tts "$line" "output_${counter}.mp3" --voice my-voice
  counter=$((counter + 1))
done < input.txt
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

# FishAudio formats
ffmcp tts "WAV format" output.wav \
  --provider fishaudio \
  --reference-id my-model \
  --format wav
```

### Voice Settings Experimentation

```bash
# Test different stability settings
for stability in 0.3 0.5 0.7 0.9; do
  ffmcp tts "Stability test: $stability" "stability_${stability}.mp3" \
    --voice my-voice \
    --stability $stability
done

# Compare different voices
for voice_id in "21m00Tcm4TlvDq8ikWAM" "pNInz6obpgDQGcFmaJgB" "ErXwobaYiN019PkySvjV"; do
  ffmcp tts "Testing voice" "voice_${voice_id}.mp3" \
    --provider elevenlabs \
    --voice-id "$voice_id"
done
```

### Text Preprocessing for Better TTS

```bash
# Clean text before TTS
text="Hello, world! This is a test."
cleaned=$(echo "$text" | tr -d ',' | tr '!' '.')
ffmcp tts "$cleaned" output.mp3 --voice my-voice

# Split long text into chunks
echo "Long text here..." | split -l 100 - chunk_
for chunk in chunk_*; do
  ffmcp tts "$(cat $chunk)" "${chunk}.mp3" --voice my-voice
done
```

### Integration with Shell Scripts

```bash
#!/bin/bash
# Script to convert agent responses to speech

AGENT_NAME="assistant"
VOICE_NAME="assistant-voice"

# Get agent response
response=$(ffmcp agent run "Tell me a joke" --agent "$AGENT_NAME")

# Generate audio
timestamp=$(date +%Y%m%d_%H%M%S)
ffmcp tts "$response" "response_${timestamp}.mp3" --voice "$VOICE_NAME"

echo "Audio saved: response_${timestamp}.mp3"
```

### Performance Optimization

**For batch processing:**
- Use `eleven_turbo_v2` model for faster generation (ElevenLabs)
- Consider using lower quality formats for testing (`mp3_44100_128`)
- Process files in parallel if your API limits allow

**For quality:**
- Use `eleven_multilingual_v2` for best quality (ElevenLabs)
- Use `mp3_44100_192` or PCM formats for highest quality
- Increase stability for consistent narration (0.7-0.9)
- Use speaker boost for clarity

**For voice cloning (FishAudio):**
- Use high-quality reference audio (16kHz+ sample rate)
- Provide accurate reference text
- Use longer reference audio (5+ seconds) for better results

## Best Practices

### Voice Selection
- **Narration**: Use higher stability (0.7-0.9) for consistent, professional narration
- **Character voices**: Use lower stability (0.3-0.5) with higher style (0.2-0.4) for expressive characters
- **Educational content**: Use speaker boost enabled for clarity
- **Creative content**: Experiment with style parameter for more expressive output

### Configuration Management
- Create named voice configurations for common use cases
- Use descriptive names: `narrator-male`, `character-female`, `announcer`
- Document voice configurations with descriptions
- Version control your voice configurations by exporting them

### Performance Tips
- Cache frequently used voice configurations
- Use appropriate quality settings (lower for testing, higher for production)
- Batch process multiple texts in a single script
- Monitor API usage to avoid rate limits

### Quality Optimization
- Pre-process text: remove special characters, normalize punctuation
- Break long texts into sentences for better prosody
- Use SSML-like formatting if your provider supports it
- Test different voices for your specific use case

### Integration Patterns
- Store voice configurations alongside your project
- Use environment variables for API keys
- Implement error handling and retries
- Log TTS generation for debugging

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

See existing `elevenlabs_provider.py` and `fishaudio_provider.py` for reference implementations.

## API Reference

### BaseTTSProvider Interface

All TTS providers implement the `BaseTTSProvider` interface:

```python
class BaseTTSProvider(ABC):
    def get_provider_name(self) -> str:
        """Return the provider name"""
        pass
    
    def text_to_speech(
        self, 
        text: str, 
        output_path: str, 
        voice_id: Optional[str] = None, 
        **kwargs
    ) -> str:
        """Convert text to speech and save to file"""
        pass
    
    def list_voices(self) -> List[Dict[str, Any]]:
        """List available voices from the provider"""
        pass
    
    def get_voice(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get details about a specific voice"""
        pass
```

### Config Methods for Voice Management

```python
from ffmcp.config import Config

config = Config()

# Create voice
config.create_voice(
    name="my-voice",
    provider="elevenlabs",
    voice_id="21m00Tcm4TlvDq8ikWAM",
    # ... other parameters
)

# List voices
voices = config.list_voices()

# Get voice
voice = config.get_voice("my-voice")

# Update voice
config.update_voice("my-voice", {"stability": 0.7})

# Delete voice
config.delete_voice("my-voice")

# Agent voice management
config.set_agent_voice("assistant", "my-voice")
voice_name = config.get_agent_voice("assistant")
config.set_agent_voice("assistant", None)  # Remove voice
```

## Additional Resources

- [ElevenLabs Documentation](https://elevenlabs.io/docs)
- [FishAudio Documentation](https://fish.audio/docs)
- [ffmcp GitHub Repository](https://github.com/yourusername/ffmcp)
- [Voice Configuration Examples](./examples/voice_configs.json) (if available)

