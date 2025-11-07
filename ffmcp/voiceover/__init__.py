"""TTS/Voiceover provider abstraction layer"""
from typing import Dict, Type
import logging
from ffmcp.voiceover.base import BaseTTSProvider
from ffmcp.voiceover.elevenlabs_provider import ElevenLabsProvider
from ffmcp.voiceover.fishaudio_provider import FishAudioProvider


AVAILABLE_TTS_PROVIDERS: Dict[str, Type[BaseTTSProvider]] = {
    'elevenlabs': ElevenLabsProvider,
    'fishaudio': FishAudioProvider,
}


def get_tts_provider(name: str, config) -> BaseTTSProvider:
    """Get a TTS provider instance by name"""
    logger = logging.getLogger('ffmcp.voiceover')
    logger.debug("get_tts_provider called name=%s", name)
    if name not in AVAILABLE_TTS_PROVIDERS:
        raise ValueError(f"Unknown TTS provider: {name}. Available: {list(AVAILABLE_TTS_PROVIDERS.keys())}")
    
    provider_class = AVAILABLE_TTS_PROVIDERS[name]
    logger.debug("instantiating TTS provider class=%s", provider_class.__name__)
    instance = provider_class(config)
    logger.debug("TTS provider instantiated class=%s", instance.__class__.__name__)
    return instance

