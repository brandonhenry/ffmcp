"""Cohere provider implementation"""
try:
    import cohere
except ImportError:
    cohere = None

from typing import List, Dict, Iterator, Optional, Any
from ffmcp.providers.base import BaseProvider


class CohereProvider(BaseProvider):
    """Cohere provider"""
    
    def __init__(self, config):
        if cohere is None:
            raise ImportError("cohere package not installed. Install with: pip install cohere")
        super().__init__(config)
        self.client = cohere.Client(api_key=self.api_key)
    
    def get_provider_name(self) -> str:
        return 'cohere'
    
    def get_default_model(self) -> str:
        return self.config.get_default_model('cohere') or 'command-r-plus'
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Cohere"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        
        response = self.client.chat(
            model=model,
            message=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Record token usage if available
        try:
            usage = getattr(response, 'meta', {}).get('tokens', {})
            if usage:
                total = int(usage.get('total_tokens', 0) or 0)
                if total == 0:
                    pt = int(usage.get('input_tokens', 0) or 0)
                    ct = int(usage.get('output_tokens', 0) or 0)
                    total = pt + ct
                if total > 0:
                    self.config.add_token_usage(self.get_provider_name(), total)
        except Exception:
            pass
        
        return response.text
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate text using Cohere (streaming)"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        
        stream = self.client.chat_stream(
            model=model,
            message=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        total_tokens_detected = None
        for event in stream:
            if event.event_type == 'text-generation':
                if hasattr(event, 'text'):
                    yield event.text
            # Try to capture usage from final event
            try:
                if hasattr(event, 'meta') and event.meta:
                    usage = event.meta.get('tokens', {})
                    if usage:
                        total_tokens_detected = int(usage.get('total_tokens', 0) or 0)
            except Exception:
                pass
        
        # Record token usage after streaming completes
        if total_tokens_detected:
            try:
                self.config.add_token_usage(self.get_provider_name(), total_tokens_detected)
            except Exception:
                pass
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with Cohere"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        
        # Cohere chat API expects chat_history and message
        # Convert messages format
        chat_history = []
        user_message = None
        
        for msg in messages:
            role = msg.get('role')
            content = msg.get('content', '')
            if role == 'user':
                if user_message is None:
                    user_message = content
                else:
                    # Add previous user message and this one to history
                    chat_history.append({"role": "USER", "message": user_message})
                    chat_history.append({"role": "CHATBOT", "message": content})
                    user_message = None
            elif role == 'assistant':
                if user_message:
                    chat_history.append({"role": "USER", "message": user_message})
                    chat_history.append({"role": "CHATBOT", "message": content})
                    user_message = None
                else:
                    # This shouldn't happen, but handle it
                    if chat_history:
                        chat_history[-1]["message"] = content
        
        # If we have a pending user message, use it
        if user_message is None and messages:
            user_message = messages[-1].get('content', '')
        
        response = self.client.chat(
            model=model,
            message=user_message or '',
            chat_history=chat_history if chat_history else None,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Record token usage if available
        try:
            usage = getattr(response, 'meta', {}).get('tokens', {})
            if usage:
                total = int(usage.get('total_tokens', 0) or 0)
                if total == 0:
                    pt = int(usage.get('input_tokens', 0) or 0)
                    ct = int(usage.get('output_tokens', 0) or 0)
                    total = pt + ct
                if total > 0:
                    self.config.add_token_usage(self.get_provider_name(), total)
        except Exception:
            pass
        
        return response.text

