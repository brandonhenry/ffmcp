"""AI provider abstraction layer"""
from typing import Dict, Type, Iterator
from ffmcp.providers.base import BaseProvider
from ffmcp.providers.openai_provider import OpenAIProvider
from ffmcp.providers.anthropic_provider import AnthropicProvider


AVAILABLE_PROVIDERS: Dict[str, Type[BaseProvider]] = {
    'openai': OpenAIProvider,
    'anthropic': AnthropicProvider,
}


def get_provider(name: str, config) -> BaseProvider:
    """Get a provider instance by name"""
    if name not in AVAILABLE_PROVIDERS:
        raise ValueError(f"Unknown provider: {name}. Available: {list(AVAILABLE_PROVIDERS.keys())}")
    
    provider_class = AVAILABLE_PROVIDERS[name]
    return provider_class(config)

