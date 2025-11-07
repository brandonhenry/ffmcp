"""Together AI provider implementation"""
try:
    from together import Together
except ImportError:
    Together = None

from typing import List, Dict, Iterator, Optional, Any
from ffmcp.providers.base import BaseProvider


class TogetherProvider(BaseProvider):
    """Together AI provider (OpenAI-compatible)"""
    
    def __init__(self, config):
        if Together is None:
            raise ImportError("together package not installed. Install with: pip install together")
        super().__init__(config)
        self.client = Together(api_key=self.api_key)
    
    def get_provider_name(self) -> str:
        return 'together'
    
    def get_default_model(self) -> str:
        return self.config.get_default_model('together') or 'meta-llama/Llama-3-70b-chat-hf'
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Together AI"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Record token usage if available
        try:
            usage = getattr(response, 'usage', None)
            if usage:
                total = int(getattr(usage, 'total_tokens', 0) or 0)
                if total == 0:
                    pt = int(getattr(usage, 'prompt_tokens', 0) or 0)
                    ct = int(getattr(usage, 'completion_tokens', 0) or 0)
                    total = pt + ct
                if total > 0:
                    self.config.add_token_usage(self.get_provider_name(), total)
        except Exception:
            pass
        
        return response.choices[0].message.content
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate text using Together AI (streaming)"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        
        stream = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        
        total_tokens_detected = None
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            # Try to capture usage from final chunk
            try:
                usage = getattr(chunk, 'usage', None)
                if usage and getattr(usage, 'total_tokens', None) is not None:
                    total_tokens_detected = int(usage.total_tokens)
            except Exception:
                pass
        
        # Record token usage after streaming completes
        if total_tokens_detected:
            try:
                self.config.add_token_usage(self.get_provider_name(), total_tokens_detected)
            except Exception:
                pass
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with Together AI"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Record token usage if available
        try:
            usage = getattr(response, 'usage', None)
            if usage:
                total = int(getattr(usage, 'total_tokens', 0) or 0)
                if total == 0:
                    pt = int(getattr(usage, 'prompt_tokens', 0) or 0)
                    ct = int(getattr(usage, 'completion_tokens', 0) or 0)
                    total = pt + ct
                if total > 0:
                    self.config.add_token_usage(self.get_provider_name(), total)
        except Exception:
            pass
        
        return response.choices[0].message.content

