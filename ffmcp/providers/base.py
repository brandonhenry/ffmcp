"""Base provider interface"""
from abc import ABC, abstractmethod
from typing import List, Dict, Iterator, Optional, Any


class BaseProvider(ABC):
    """Base class for AI providers"""
    
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
    def get_default_model(self) -> str:
        """Return the default model for this provider"""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt"""
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate text from a prompt (streaming)"""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with AI using message history"""
        pass

