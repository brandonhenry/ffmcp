"""Google Gemini provider implementation"""
try:
    import google.generativeai as genai
except ImportError:
    genai = None

from typing import List, Dict, Iterator, Optional, Any
from ffmcp.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """Google Gemini provider"""
    
    def __init__(self, config):
        if genai is None:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        super().__init__(config)
        genai.configure(api_key=self.api_key)
        self.client = genai
    
    def get_provider_name(self) -> str:
        return 'gemini'
    
    def get_default_model(self) -> str:
        return self.config.get_default_model('gemini') or 'gemini-2.0-flash-exp'
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini"""
        model_name = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        
        model = self.client.GenerativeModel(model_name)
        generation_config = {
            'temperature': temperature,
        }
        if max_tokens:
            generation_config['max_output_tokens'] = max_tokens
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
        )
        
        # Record token usage if available
        try:
            usage = getattr(response, 'usage_metadata', None)
            if usage:
                total = int(getattr(usage, 'total_token_count', 0) or 0)
                if total > 0:
                    self.config.add_token_usage(self.get_provider_name(), total)
        except Exception:
            pass
        
        return response.text
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate text using Gemini (streaming)"""
        model_name = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        
        model = self.client.GenerativeModel(model_name)
        generation_config = {
            'temperature': temperature,
        }
        if max_tokens:
            generation_config['max_output_tokens'] = max_tokens
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            stream=True,
        )
        
        total_tokens = 0
        for chunk in response:
            if chunk.text:
                yield chunk.text
            # Try to capture usage from final chunk
            try:
                usage = getattr(chunk, 'usage_metadata', None)
                if usage:
                    total_tokens = int(getattr(usage, 'total_token_count', 0) or 0)
            except Exception:
                pass
        
        # Record token usage after streaming completes
        if total_tokens > 0:
            try:
                self.config.add_token_usage(self.get_provider_name(), total_tokens)
            except Exception:
                pass
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with Gemini"""
        model_name = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        
        # Convert messages format for Gemini
        # Gemini uses a chat session model
        model = self.client.GenerativeModel(model_name)
        
        # Extract system message if present
        system_msg = None
        chat_messages = []
        for msg in messages:
            role = msg.get('role')
            content = msg.get('content', '')
            if role == 'system':
                system_msg = content
            elif role == 'user':
                chat_messages.append({'role': 'user', 'parts': [content]})
            elif role == 'assistant':
                chat_messages.append({'role': 'model', 'parts': [content]})
        
        # Build history (all but the last message)
        history = chat_messages[:-1] if len(chat_messages) > 1 else []
        
        # Start chat with history
        chat = model.start_chat(history=history)
        
        # Send the last message
        last_content = chat_messages[-1]['parts'][0] if chat_messages else messages[-1].get('content', '')
        
        generation_config = {
            'temperature': temperature,
        }
        if max_tokens:
            generation_config['max_output_tokens'] = max_tokens
        if system_msg:
            generation_config['system_instruction'] = system_msg
        
        response = chat.send_message(
            last_content,
            generation_config=generation_config,
        )
        
        # Record token usage if available
        try:
            usage = getattr(response, 'usage_metadata', None)
            if usage:
                total = int(getattr(usage, 'total_token_count', 0) or 0)
                if total > 0:
                    self.config.add_token_usage(self.get_provider_name(), total)
        except Exception:
            pass
        
        return response.text

