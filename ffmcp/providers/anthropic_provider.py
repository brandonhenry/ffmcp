"""Anthropic provider implementation"""
try:
    import anthropic
    import base64
    from pathlib import Path
except ImportError:
    anthropic = None
    base64 = None
    Path = None

from typing import List, Dict, Iterator, Optional, Any, Union
from ffmcp.providers.base import BaseProvider
import json


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
    
    # ========== Vision / Image Understanding ==========
    
    def vision(self, prompt: str, image_paths: List[str], **kwargs) -> str:
        """Analyze images with vision models"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 1024)
        
        # Prepare content blocks with text and images
        content_blocks = [{"type": "text", "text": prompt}]
        
        for img_path in image_paths:
            path = Path(img_path)
            if not path.exists():
                raise FileNotFoundError(f"Image not found: {img_path}")
            
            # Read and encode image
            with open(path, 'rb') as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                # Determine media type
                suffix = path.suffix[1:].lower()
                media_type_map = {
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'gif': 'image/gif',
                    'webp': 'image/webp',
                }
                media_type = media_type_map.get(suffix, 'image/jpeg')
                
                content_blocks.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_data
                    }
                })
        
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": content_blocks}],
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
    
    def vision_urls(self, prompt: str, image_urls: List[str], **kwargs) -> str:
        """Analyze images available via URLs with vision models"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 1024)
        
        # Prepare content blocks with text and image URLs
        content_blocks = [{"type": "text", "text": prompt}]
        
        for url in image_urls:
            content_blocks.append({
                "type": "image",
                "source": {
                    "type": "url",
                    "url": url
                }
            })
        
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": content_blocks}],
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
    
    # ========== Tools / Function Calling ==========
    
    def chat_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict], **kwargs) -> Dict[str, Any]:
        """Chat with function calling support"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 1024)
        tool_choice = kwargs.get('tool_choice', 'auto')
        
        # Convert messages format
        anthropic_messages = []
        system_msg = None
        
        for msg in messages:
            role = msg['role']
            if role == 'system':
                system_msg = msg['content']
                continue
            
            # Handle content - could be string or list of content blocks
            content = msg.get('content', '')
            if isinstance(content, str):
                content = [{"type": "text", "text": content}]
            elif isinstance(content, list):
                # Ensure it's in the right format
                content = [
                    {"type": "text", "text": item} if isinstance(item, str) else item
                    for item in content
                ]
            
            anthropic_messages.append({
                "role": role if role != 'assistant' else 'assistant',
                "content": content
            })
        
        # Convert tools format from OpenAI-style to Anthropic-style
        anthropic_tools = []
        for tool in tools:
            if isinstance(tool, dict):
                if 'function' in tool:
                    # OpenAI format: {"type": "function", "function": {...}}
                    func = tool['function']
                    anthropic_tools.append({
                        "name": func.get('name'),
                        "description": func.get('description', ''),
                        "input_schema": func.get('parameters', {})
                    })
                elif 'name' in tool:
                    # Already in Anthropic format
                    anthropic_tools.append(tool)
        
        params = {
            'model': model,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': anthropic_messages,
            'tools': anthropic_tools,
        }
        
        if system_msg:
            params['system'] = system_msg
        
        # Handle tool_choice
        if tool_choice and tool_choice != 'auto':
            if tool_choice == 'required':
                params['tool_choice'] = {"type": "any"}
            elif isinstance(tool_choice, dict):
                params['tool_choice'] = tool_choice
            elif isinstance(tool_choice, str):
                # Assume it's a tool name
                params['tool_choice'] = {"type": "tool", "name": tool_choice}
        
        response = self.client.messages.create(**params)
        
        # Record token usage if available
        try:
            usage = getattr(response, 'usage', None)
            if usage:
                total = int(getattr(usage, 'input_tokens', 0) or 0) + int(getattr(usage, 'output_tokens', 0) or 0)
                if total > 0:
                    self.config.add_token_usage(self.get_provider_name(), total)
        except Exception:
            pass
        
        # Extract response content
        result = {
            'content': None,
            'tool_use': None,
        }
        
        if response.content:
            # Check if there's text content
            text_parts = []
            tool_use_parts = []
            
            for item in response.content:
                # Anthropic SDK returns TextBlock and ToolUseBlock objects
                item_type = getattr(item, 'type', None)
                if item_type == 'text' or hasattr(item, 'text'):
                    text_parts.append(getattr(item, 'text', str(item)))
                elif item_type == 'tool_use' or hasattr(item, 'name'):
                    # This is a tool use block
                    tool_use_parts.append({
                        'id': getattr(item, 'id', None),
                        'name': getattr(item, 'name', None),
                        'input': getattr(item, 'input', {})
                    })
            
            if text_parts:
                result['content'] = text_parts[0] if len(text_parts) == 1 else '\n'.join(text_parts)
            
            if tool_use_parts:
                result['tool_use'] = tool_use_parts
        
        return result

