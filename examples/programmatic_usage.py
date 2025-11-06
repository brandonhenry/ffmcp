"""Example: Using ffmcp programmatically (like ffmpeg)"""
from ffmcp.providers import get_provider
from ffmcp.config import Config

# Initialize config
config = Config()

# Get a provider
provider = get_provider('openai', config)

# Generate text
result = provider.generate("Write a haiku about Python")
print(result)

# Stream generation
print("\nStreaming response:")
for chunk in provider.generate_stream("Count to 5"):
    print(chunk, end='', flush=True)
print()

# Chat with context
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"}
]
response = provider.chat(messages)
print(f"\nChat response: {response}")

