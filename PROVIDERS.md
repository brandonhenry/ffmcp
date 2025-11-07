# AI Providers Guide

ffmcp supports 11 major AI providers, each with unique strengths and use cases. This guide helps you choose the right provider for your needs.

## Available Providers

### 1. OpenAI
**Best for:** Comprehensive AI tasks, production applications

**Models:**
- `gpt-4o-mini` (default) - Fast and cost-effective
- `gpt-4o` - Most capable GPT-4 model
- `gpt-4-turbo` - High performance
- `gpt-3.5-turbo` - Legacy model

**Unique Features:**
- ✅ Vision (image understanding)
- ✅ Image generation (DALL·E 2 & 3)
- ✅ Audio transcription (Whisper)
- ✅ Text-to-speech (TTS)
- ✅ Embeddings
- ✅ Function calling
- ✅ Assistants API

**Setup:**
```bash
ffmcp config -p openai -k YOUR_OPENAI_API_KEY
```

**Example:**
```bash
ffmcp generate "Explain quantum computing" -p openai -m gpt-4o
ffmcp openai vision "What's in this image?" photo.jpg
ffmcp openai image "A futuristic city"
```

---

### 2. Anthropic Claude
**Best for:** Complex reasoning, long documents, high-quality responses

**Models:**
- `claude-3-5-sonnet-20241022` (default) - Best balance
- `claude-3-opus` - Most capable
- `claude-3-haiku` - Fastest

**Unique Features:**
- ✅ Long context windows (200K+ tokens)
- ✅ Excellent reasoning capabilities
- ✅ Vision support (with images)
- ✅ System messages

**Setup:**
```bash
ffmcp config -p anthropic -k YOUR_ANTHROPIC_API_KEY
```

**Example:**
```bash
ffmcp generate "Analyze this 50-page document" -p anthropic -m claude-3-opus
ffmcp chat "Solve this complex math problem" -p anthropic -s "You are a math expert"
```

---

### 3. Google Gemini
**Best for:** General purpose, multimodal tasks, fast responses

**Models:**
- `gemini-2.0-flash-exp` (default) - Latest experimental
- `gemini-1.5-pro` - Most capable
- `gemini-1.5-flash` - Fast and efficient

**Unique Features:**
- ✅ Multimodal capabilities
- ✅ Fast inference
- ✅ Good vision support
- ✅ System instructions

**Setup:**
```bash
ffmcp config -p gemini -k YOUR_GEMINI_API_KEY
# Get API key from: https://makersuite.google.com/app/apikey
```

**Example:**
```bash
ffmcp generate "Write a creative story" -p gemini -m gemini-1.5-pro
ffmcp chat "Explain machine learning" -p gemini
```

---

### 4. Groq
**Best for:** Speed-critical applications, real-time responses

**Models:**
- `llama-3.1-70b-versatile` (default) - Best quality
- `llama-3.1-8b-instant` - Fastest
- `mixtral-8x7b-32768` - Alternative
- `gemma2-9b-it` - Lightweight

**Unique Features:**
- ✅ Ultra-fast inference (often <1 second)
- ✅ OpenAI-compatible API
- ✅ Multiple open-source models
- ✅ Cost-effective

**Setup:**
```bash
ffmcp config -p groq -k YOUR_GROQ_API_KEY
# Get API key from: https://console.groq.com/
```

**Example:**
```bash
# Groq is incredibly fast - perfect for streaming
ffmcp generate "Tell me a joke" -p groq -s
ffmcp generate "Quick summary" -p groq -m llama-3.1-8b-instant
```

---

### 5. DeepSeek
**Best for:** Code generation, technical tasks, cost-effective

**Models:**
- `deepseek-chat` (default) - General purpose
- `deepseek-coder` - Code-focused

**Unique Features:**
- ✅ OpenAI-compatible API
- ✅ Excellent for coding tasks
- ✅ Cost-effective
- ✅ Strong technical understanding

**Setup:**
```bash
ffmcp config -p deepseek -k YOUR_DEEPSEEK_API_KEY
# Get API key from: https://platform.deepseek.com/
```

**Example:**
```bash
ffmcp generate "Write a Python function to sort a list" -p deepseek -m deepseek-coder
ffmcp chat "Explain this code: def fib(n): ..." -p deepseek
```

---

### 6. Mistral AI
**Best for:** Enterprise applications, high-quality responses

**Models:**
- `mistral-large-latest` (default) - Most capable
- `mistral-medium-latest` - Balanced
- `mistral-small-latest` - Fast
- `pixtral-large-latest` - Vision-capable

**Unique Features:**
- ✅ High-quality responses
- ✅ Vision support (Pixtral)
- ✅ Function calling
- ✅ JSON mode

**Setup:**
```bash
ffmcp config -p mistral -k YOUR_MISTRAL_API_KEY
# Get API key from: https://console.mistral.ai/
```

**Example:**
```bash
ffmcp generate "Write a professional email" -p mistral -m mistral-large-latest
ffmcp chat "Analyze this business proposal" -p mistral
```

---

### 7. Together AI
**Best for:** Access to many open-source models, experimentation

**Models:**
- `meta-llama/Llama-3-70b-chat-hf` (default)
- `mistralai/Mixtral-8x7B-Instruct-v0.1`
- `Qwen/Qwen2.5-72B-Instruct`
- Many more open-source models

**Unique Features:**
- ✅ Access to 100+ open-source models
- ✅ OpenAI-compatible API
- ✅ Cost-effective
- ✅ Great for experimentation

**Setup:**
```bash
ffmcp config -p together -k YOUR_TOGETHER_API_KEY
# Get API key from: https://api.together.xyz/
```

**Example:**
```bash
ffmcp generate "Explain transformers" -p together -m meta-llama/Llama-3-70b-chat-hf
ffmcp generate "Write code" -p together -m Qwen/Qwen2.5-72B-Instruct
```

---

### 8. Cohere
**Best for:** Enterprise applications, RAG, embeddings

**Models:**
- `command-r-plus` (default) - Most capable
- `command-r` - Balanced
- `command` - Legacy

**Unique Features:**
- ✅ Excellent for RAG (Retrieval Augmented Generation)
- ✅ Strong embeddings API
- ✅ Enterprise-focused features
- ✅ Good for business applications

**Setup:**
```bash
ffmcp config -p cohere -k YOUR_COHERE_API_KEY
# Get API key from: https://dashboard.cohere.com/
```

**Example:**
```bash
ffmcp generate "Summarize this business report" -p cohere -m command-r-plus
ffmcp chat "Answer based on this context: ..." -p cohere
```

---

### 9. Perplexity AI
**Best for:** Research, real-time information, web search

**Models:**
- `llama-3.1-sonar-large-128k-online` (default) - With web search
- `llama-3.1-sonar-small-128k-online` - Faster
- `sonar-pro` - Alternative

**Unique Features:**
- ✅ Built-in web search
- ✅ Real-time information
- ✅ Citations in responses
- ✅ Great for research queries

**Setup:**
```bash
ffmcp config -p perplexity -k YOUR_PERPLEXITY_API_KEY
# Get API key from: https://www.perplexity.ai/settings/api
```

**Example:**
```bash
# Perplexity can search the web for current information
ffmcp generate "What are the latest AI developments in 2024?" -p perplexity
ffmcp generate "Current weather in San Francisco" -p perplexity
```

---

### 10. AIMLAPI
**Best for:** Access to 300+ AI models through a unified API, experimentation with multiple models

**Models:**
- `gpt-4o` (default) - OpenAI GPT-4o
- `gpt-4o-mini` - OpenAI GPT-4o Mini
- `gpt-4-turbo` - OpenAI GPT-4 Turbo
- `claude-3-5-sonnet-20241022` - Anthropic Claude 3.5 Sonnet
- `claude-3-opus` - Anthropic Claude 3 Opus
- `gemini-2.0-flash-exp` - Google Gemini 2.0 Flash
- `gemini-1.5-pro` - Google Gemini 1.5 Pro
- `llama-3.1-70b-versatile` - Meta Llama 3.1 70B
- `mistral-large-latest` - Mistral Large
- `deepseek-chat` - DeepSeek Chat
- And 290+ more models from various providers

**Unique Features:**
- ✅ Unified API for 300+ AI models
- ✅ OpenAI-compatible API format
- ✅ Access to models from multiple providers
- ✅ Vision support (with compatible models)
- ✅ Image generation (DALL·E models)
- ✅ Audio transcription (Whisper models)
- ✅ Text-to-speech (TTS models)
- ✅ Embeddings (embedding models)
- ✅ Function calling / tools
- ✅ Assistants API support
- ✅ Single API key for all models

**Setup:**
```bash
ffmcp config -p aimlapi -k YOUR_AIMLAPI_API_KEY
# Get API key from: https://aimlapi.com/app/sign-up/
```

**Example:**
```bash
# Use GPT-4o through AIMLAPI
ffmcp generate "Explain quantum computing" -p aimlapi -m gpt-4o

# Use Claude through AIMLAPI
ffmcp generate "Analyze this document" -p aimlapi -m claude-3-5-sonnet-20241022

# Use Gemini through AIMLAPI
ffmcp generate "Write a story" -p aimlapi -m gemini-2.0-flash-exp

# Vision with AIMLAPI
ffmcp aimlapi vision "What's in this image?" photo.jpg

# Image generation with AIMLAPI
ffmcp aimlapi image "A futuristic city"
```

---

### By Use Case

| Use Case | Recommended Provider |
|----------|---------------------|
| **General purpose** | OpenAI, Gemini, Groq, AIMLAPI |
| **Code generation** | DeepSeek, OpenAI, AIMLAPI |
| **Speed critical** | Groq |
| **Long documents** | Anthropic Claude |
| **Image understanding** | OpenAI, Anthropic, Gemini, AIMLAPI |
| **Image generation** | OpenAI (DALL·E), AIMLAPI |
| **Audio transcription** | OpenAI (Whisper), AIMLAPI |
| **Web search** | Perplexity |
| **Enterprise** | Cohere, Mistral |
| **Experimentation** | Together AI, AIMLAPI |
| **Cost-effective** | Groq, Together AI, DeepSeek |
| **Multiple models** | AIMLAPI |

### By Speed

1. **Groq** - Fastest (often <1 second)
2. **Gemini Flash** - Very fast
3. **OpenAI GPT-4o-mini** - Fast
4. **DeepSeek** - Fast
5. **Mistral Small** - Fast
6. **Together AI** - Variable (depends on model)
7. **AIMLAPI** - Variable (depends on selected model)
8. **Anthropic Claude** - Moderate
9. **Cohere** - Moderate
10. **Perplexity** - Slower (due to web search)

### By Cost

1. **Groq** - Very affordable
2. **Together AI** - Affordable
3. **DeepSeek** - Affordable
4. **OpenAI GPT-4o-mini** - Moderate
5. **Gemini** - Moderate
6. **Mistral** - Moderate
7. **AIMLAPI** - Variable (depends on selected model)
8. **Cohere** - Moderate-High
9. **Anthropic Claude** - Higher
10. **OpenAI GPT-4o** - Higher
11. **Perplexity** - Higher (includes web search)

## Provider Comparison

| Feature | OpenAI | Anthropic | Gemini | Groq | DeepSeek | Mistral | Together | Cohere | Perplexity | AIMLAPI |
|---------|--------|-----------|--------|------|----------|---------|----------|--------|------------|---------|
| Chat | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Streaming | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Vision | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅* |
| Image Gen | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅* |
| Audio | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅* |
| Embeddings | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅* |
| Web Search | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| Speed | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Cost | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

*Feature availability depends on the selected model

## Tips

1. **Try multiple providers** - Different providers excel at different tasks
2. **Use Groq for speed** - When you need fast responses
3. **Use Perplexity for research** - When you need current information
4. **Use OpenAI for features** - When you need vision, images, or audio
5. **Use Anthropic for quality** - When you need the best reasoning
6. **Use Together AI for experimentation** - Try different open-source models
7. **Use AIMLAPI for variety** - Access 300+ models through a single API
8. **Check token usage** - Monitor costs with `ffmcp tokens`

## Getting API Keys

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **Groq**: https://console.groq.com/
- **DeepSeek**: https://platform.deepseek.com/
- **Mistral AI**: https://console.mistral.ai/
- **Together AI**: https://api.together.xyz/
- **Cohere**: https://dashboard.cohere.com/
- **Perplexity**: https://www.perplexity.ai/settings/api
- **AIMLAPI**: https://aimlapi.com/app/sign-up/

## Examples

### Compare Providers
```bash
# Same prompt, different providers
ffmcp generate "Explain quantum computing" -p openai
ffmcp generate "Explain quantum computing" -p gemini
ffmcp generate "Explain quantum computing" -p groq
ffmcp generate "Explain quantum computing" -p anthropic
ffmcp generate "Explain quantum computing" -p aimlapi -m gpt-4o
ffmcp generate "Explain quantum computing" -p aimlapi -m claude-3-5-sonnet-20241022
```

### Speed Test
```bash
time ffmcp generate "Quick summary" -p groq
time ffmcp generate "Quick summary" -p openai
time ffmcp generate "Quick summary" -p gemini
```

### Research Query
```bash
# Perplexity searches the web automatically
ffmcp generate "Latest news about AI" -p perplexity
```

### Code Generation
```bash
# DeepSeek is great for code
ffmcp generate "Write a Python REST API" -p deepseek -m deepseek-coder
```

