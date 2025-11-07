"""Base TTS/Voiceover provider interface"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class BaseTTSProvider(ABC):
    """Base class for TTS/Voiceover providers"""
    
    def __init__(self, config):
        self.config = config
        self.api_key = config.get_api_key(self.get_provider_name())
        if not self.api_key:
            raise ValueError(f"API key not configured for {self.get_provider_name()}. "
                           f"Set it with: ffmcp config -p {self.get_provider_name()} -k YOUR_KEY")
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name"""
        pass
    
    @abstractmethod
    def text_to_speech(self, text: str, output_path: str, voice_id: Optional[str] = None, **kwargs) -> str:
        """Convert text to speech and save to file
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            voice_id: Voice ID to use (optional, some providers support reference audio instead)
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Path to the saved audio file
        """
        pass
    
    @abstractmethod
    def list_voices(self) -> List[Dict[str, Any]]:
        """List available voices from the provider
        
        Returns:
            List of voice dictionaries with at least 'id' and 'name' keys
        """
        pass
    
    def get_voice(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get details about a specific voice
        
        Args:
            voice_id: Voice ID to retrieve
        
        Returns:
            Voice dictionary or None if not found
        """
        voices = self.list_voices()
        for voice in voices:
            if voice.get('id') == voice_id:
                return voice
        return None

