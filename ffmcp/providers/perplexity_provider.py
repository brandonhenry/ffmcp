"""Perplexity AI provider implementation"""
try:
    import httpx
except ImportError:
    httpx = None

from typing import List, Dict, Iterator, Optional, Any
from ffmcp.providers.base import BaseProvider
import json


class PerplexityProvider(BaseProvider):
    """Perplexity AI provider"""
    
    def __init__(self, config):
        if httpx is None:
            raise ImportError("httpx package not installed. Install with: pip install httpx")
        super().__init__(config)
        self.base_url = "https://api.perplexity.ai"
    
    def get_provider_name(self) -> str:
        return 'perplexity'
    
    def get_default_model(self) -> str:
        return self.config.get_default_model('perplexity') or 'llama-3.1-sonar-large-128k-online'
    
    def _make_request(self, messages: List[Dict[str, str]], stream: bool = False, **kwargs) -> Any:
        """Make API request to Perplexity"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if stream:
            payload["stream"] = True
        
        # For streaming, we need to return the client and response
        # For non-streaming, we can use context manager
        if stream:
            client = httpx.Client(timeout=60.0)
            response = client.post(url, headers=headers, json=payload, stream=True)
            response.raise_for_status()
            # Store client on response for cleanup
            response._client = client
            return response
        else:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Perplexity"""
        messages = [{"role": "user", "content": prompt}]
        response = self._make_request(messages, stream=False, **kwargs)
        data = response.json()
        
        # Record token usage if available
        try:
            usage = data.get('usage', {})
            if usage:
                total = int(usage.get('total_tokens', 0) or 0)
                if total == 0:
                    pt = int(usage.get('prompt_tokens', 0) or 0)
                    ct = int(usage.get('completion_tokens', 0) or 0)
                    total = pt + ct
                if total > 0:
                    self.config.add_token_usage(self.get_provider_name(), total)
        except Exception:
            pass
        
        return data['choices'][0]['message']['content']
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate text using Perplexity (streaming)"""
        messages = [{"role": "user", "content": prompt}]
        response = self._make_request(messages, stream=True, **kwargs)
        
        total_tokens_detected = None
        try:
            for line in response.iter_lines():
                if not line or not line.startswith('data: '):
                    continue
                if line == 'data: [DONE]':
                    break
                
                try:
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        if 'content' in delta:
                            yield delta['content']
                    
                    # Try to capture usage
                    if 'usage' in data:
                        usage = data['usage']
                        total = int(usage.get('total_tokens', 0) or 0)
                        if total > 0:
                            total_tokens_detected = total
                except json.JSONDecodeError:
                    continue
        finally:
            # Clean up the client
            if hasattr(response, '_client'):
                response._client.close()
        
        # Record token usage after streaming completes
        if total_tokens_detected:
            try:
                self.config.add_token_usage(self.get_provider_name(), total_tokens_detected)
            except Exception:
                pass
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with Perplexity"""
        response = self._make_request(messages, stream=False, **kwargs)
        data = response.json()
        
        # Record token usage if available
        try:
            usage = data.get('usage', {})
            if usage:
                total = int(usage.get('total_tokens', 0) or 0)
                if total == 0:
                    pt = int(usage.get('prompt_tokens', 0) or 0)
                    ct = int(usage.get('completion_tokens', 0) or 0)
                    total = pt + ct
                if total > 0:
                    self.config.add_token_usage(self.get_provider_name(), total)
        except Exception:
            pass
        
        return data['choices'][0]['message']['content']

