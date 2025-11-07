"""AI provider abstraction layer"""
from typing import Dict, Type, Iterator
import logging
from ffmcp.providers.base import BaseProvider
from ffmcp.providers.openai_provider import OpenAIProvider
from ffmcp.providers.anthropic_provider import AnthropicProvider


AVAILABLE_PROVIDERS: Dict[str, Type[BaseProvider]] = {
    'openai': OpenAIProvider,
    'anthropic': AnthropicProvider,
}


def get_provider(name: str, config) -> BaseProvider:
    """Get a provider instance by name"""
    logger = logging.getLogger('ffmcp.providers')
    logger.debug("get_provider called name=%s", name)
    if name not in AVAILABLE_PROVIDERS:
        raise ValueError(f"Unknown provider: {name}. Available: {list(AVAILABLE_PROVIDERS.keys())}")
    
    provider_class = AVAILABLE_PROVIDERS[name]
    logger.debug("instantiating provider class=%s", provider_class.__name__)
    instance = provider_class(config)
    logger.debug("provider instantiated class=%s", instance.__class__.__name__)
    return instance

