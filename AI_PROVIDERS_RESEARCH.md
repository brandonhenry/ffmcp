# AI Model APIs Available for CLI Integration

This document lists AI model providers with well-documented APIs that can be added to the ffmcp CLI. All providers listed below have official Python SDKs and comprehensive documentation.

## Currently Implemented

1. **OpenAI** ✅
   - Python SDK: `openai` (already in requirements.txt)
   - Documentation: https://platform.openai.com/docs
   - Models: GPT-4, GPT-3.5, DALL-E, Whisper, TTS, Embeddings
   - Features: Chat, streaming, vision, image generation, audio, embeddings, assistants API

2. **Anthropic** ✅
   - Python SDK: `anthropic` (already in requirements.txt)
   - Documentation: https://docs.anthropic.com
   - Models: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
   - Features: Chat, streaming, vision (with images)

## Recommended Additions

### 1. Google Gemini
- **Python SDK**: `google-generativeai`
- **Install**: `pip install google-generativeai`
- **Documentation**: https://ai.google.dev/docs
- **API Reference**: https://ai.google.dev/api/python
- **Models**: 
  - `gemini-2.0-flash-exp`
  - `gemini-1.5-pro`
  - `gemini-1.5-flash`
- **Features**: 
  - Chat completions with streaming
  - Vision (image understanding)
  - Function calling
  - Multimodal inputs
- **API Key**: Get from https://makersuite.google.com/app/apikey
- **Notes**: Similar interface to OpenAI, supports system instructions, temperature, max_tokens

### 2. Mistral AI
- **Python SDK**: `mistralai`
- **Install**: `pip install mistralai`
- **Documentation**: https://docs.mistral.com
- **API Reference**: https://docs.mistral.com/api/
- **Models**:
  - `mistral-large-latest`
  - `mistral-medium-latest`
  - `mistral-small-latest`
  - `pixtral-large-latest` (vision)
- **Features**:
  - Chat completions with streaming
  - Vision support
  - Function calling
  - JSON mode
- **API Key**: Get from https://console.mistral.ai/
- **Notes**: RESTful API similar to OpenAI, supports streaming, tool use

### 3. Groq
- **Python SDK**: `groq`
- **Install**: `pip install groq`
- **Documentation**: https://console.groq.com/docs
- **API Reference**: https://console.groq.com/docs/python
- **Models**:
  - `llama-3.1-70b-versatile`
  - `llama-3.1-8b-instant`
  - `mixtral-8x7b-32768`
  - `gemma2-9b-it`
- **Features**:
  - Very fast inference (optimized for speed)
  - Chat completions with streaming
  - Function calling
- **API Key**: Get from https://console.groq.com/
- **Notes**: OpenAI-compatible API, focuses on speed, supports streaming

### 4. Cohere
- **Python SDK**: `cohere`
- **Install**: `pip install cohere`
- **Documentation**: https://docs.cohere.com
- **API Reference**: https://docs.cohere.com/reference/chat
- **Models**:
  - `command-r-plus`
  - `command-r`
  - `command`
- **Features**:
  - Chat completions with streaming
  - RAG (Retrieval Augmented Generation)
  - Embeddings
  - Classification
- **API Key**: Get from https://dashboard.cohere.com/
- **Notes**: Strong for enterprise use cases, good embeddings API

### 5. Together AI
- **Python SDK**: `together`
- **Install**: `pip install together`
- **Documentation**: https://docs.together.ai
- **API Reference**: https://docs.together.ai/reference/chat-completions
- **Models**: Access to many open-source models
  - `meta-llama/Llama-3-70b-chat-hf`
  - `mistralai/Mixtral-8x7B-Instruct-v0.1`
  - `Qwen/Qwen2.5-72B-Instruct`
  - Many others
- **Features**:
  - Chat completions with streaming
  - Function calling
  - Embeddings
  - Image generation
- **API Key**: Get from https://api.together.xyz/
- **Notes**: Provides access to many open-source models, OpenAI-compatible API

### 6. Perplexity AI
- **Python SDK**: `perplexityai` (or direct HTTP)
- **Install**: `pip install perplexityai` (or use `httpx`/`requests`)
- **Documentation**: https://docs.perplexity.ai
- **API Reference**: https://docs.perplexity.ai/reference/post_chat_completions
- **Models**:
  - `llama-3.1-sonar-large-128k-online`
  - `llama-3.1-sonar-small-128k-online`
  - `sonar-pro`
  - `sonar`
- **Features**:
  - Chat completions with streaming
  - Real-time web search integration
  - Citations in responses
- **API Key**: Get from https://www.perplexity.ai/settings/api
- **Notes**: Unique feature is built-in web search, returns citations

### 7. DeepSeek
- **Python SDK**: `deepseek` (or OpenAI-compatible)
- **Install**: Can use OpenAI SDK with different base URL
- **Documentation**: https://api-docs.deepseek.com
- **API Reference**: https://api-docs.deepseek.com/chat-completion
- **Models**:
  - `deepseek-chat`
  - `deepseek-coder`
- **Features**:
  - Chat completions with streaming
  - OpenAI-compatible API
  - Strong for coding tasks
- **API Key**: Get from https://platform.deepseek.com/
- **Notes**: OpenAI-compatible, can reuse OpenAI provider code with different base URL

### 8. Meta Llama (via Replicate or Together)
- **Note**: Meta doesn't provide direct API, but models available via:
  - **Replicate**: `replicate` SDK
  - **Together AI**: See Together AI above
  - **Hugging Face Inference API**: `huggingface_hub`
- **Models**: Llama 3, Llama 2, Code Llama
- **Documentation**: 
  - Replicate: https://replicate.com/docs
  - Hugging Face: https://huggingface.co/docs/api-inference

### 9. Hugging Face Inference API
- **Python SDK**: `huggingface_hub`
- **Install**: `pip install huggingface_hub`
- **Documentation**: https://huggingface.co/docs/api-inference
- **Models**: Thousands of models available
- **Features**:
  - Text generation
  - Text classification
  - Question answering
  - Image generation
  - Many other tasks
- **API Key**: Get from https://huggingface.co/settings/tokens
- **Notes**: Access to many open-source models, different API structure

### 10. xAI (Grok)
- **Python SDK**: `xai` (or direct HTTP)
- **Install**: May need to use HTTP client directly
- **Documentation**: https://docs.x.ai
- **Models**: `grok-beta`
- **Features**: Chat completions
- **API Key**: Get from https://console.x.ai/
- **Notes**: Newer API, may need custom implementation

## Implementation Priority

Based on popularity, documentation quality, and API similarity:

1. **High Priority** (OpenAI-compatible APIs, easy to implement):
   - **Google Gemini** - Very popular, well-documented, similar to OpenAI
   - **Groq** - OpenAI-compatible, very fast
   - **DeepSeek** - OpenAI-compatible, can reuse OpenAI code

2. **Medium Priority** (Similar APIs, good documentation):
   - **Mistral AI** - Popular, well-documented
   - **Together AI** - Access to many models
   - **Cohere** - Enterprise-focused, good features

3. **Lower Priority** (Unique features or different API structure):
   - **Perplexity AI** - Unique web search feature
   - **Hugging Face** - Different API structure, many models
   - **xAI** - Newer, less documentation

## Implementation Notes

All providers should implement the `BaseProvider` interface with:
- `generate()` - Simple text generation
- `generate_stream()` - Streaming text generation
- `chat()` - Chat with message history

Optional features to consider:
- Vision/image understanding
- Function calling/tools
- Embeddings
- Audio (transcription, TTS)

## Testing Strategy

For each provider:
1. Check official Python SDK documentation
2. Verify API key authentication method
3. Test basic chat completion
4. Test streaming
5. Test error handling
6. Verify token usage tracking (if available)

## References

- OpenAI API: https://platform.openai.com/docs
- Anthropic API: https://docs.anthropic.com
- Google Gemini: https://ai.google.dev/docs
- Mistral AI: https://docs.mistral.com
- Groq: https://console.groq.com/docs
- Cohere: https://docs.cohere.com
- Together AI: https://docs.together.ai
- Perplexity: https://docs.perplexity.ai
- DeepSeek: https://api-docs.deepseek.com

