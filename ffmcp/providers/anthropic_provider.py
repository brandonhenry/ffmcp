"""Anthropic provider implementation"""
try:
    import anthropic
except ImportError:
    anthropic = None

from typing import List, Dict, Iterator
from ffmcp.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, config):
        if anthropic is None:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        super().__init__(config)
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def get_provider_name(self) -> str:
        return 'anthropic'
    
    def get_default_model(self) -> str:
        return self.config.get_default_model('anthropic') or 'claude-3-5-sonnet-20241022'
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Anthropic"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 1024)
        
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        # Record token usage if available
        try:
            usage = getattr(response, 'usage', None)
            if usage:
                total = int(getattr(usage, 'input_tokens', 0) or 0) + int(getattr(usage, 'output_tokens', 0) or 0)
                if total > 0:
                    self.config.add_token_usage(self.get_provider_name(), total)
        except Exception:
            pass
        return response.content[0].text
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate text using Anthropic (streaming)"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 1024)
        
        with self.client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield text
            # After streaming completes, try to fetch final message to get usage
            try:
                final = stream.get_final_response() if hasattr(stream, 'get_final_response') else getattr(stream, 'final_message', None)
                usage = getattr(final, 'usage', None)
                if usage:
                    total = int(getattr(usage, 'input_tokens', 0) or 0) + int(getattr(usage, 'output_tokens', 0) or 0)
                    if total > 0:
                        self.config.add_token_usage(self.get_provider_name(), total)
            except Exception:
                pass
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with Anthropic"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 1024)
        
        # Convert messages format if needed
        anthropic_messages = []
        for msg in messages:
            role = msg['role']
            if role == 'system':
                # Anthropic handles system messages differently
                continue
            anthropic_messages.append({
                "role": role if role != 'assistant' else 'assistant',
                "content": msg['content']
            })
        
        # Extract system message if present
        system_msg = None
        for msg in messages:
            if msg.get('role') == 'system':
                system_msg = msg['content']
                break
        
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=anthropic_messages,
            system=system_msg,
        )
        # Record token usage if available
        try:
            usage = getattr(response, 'usage', None)
            if usage:
                total = int(getattr(usage, 'input_tokens', 0) or 0) + int(getattr(usage, 'output_tokens', 0) or 0)
                if total > 0:
                    self.config.add_token_usage(self.get_provider_name(), total)
        except Exception:
            pass
        return response.content[0].text

