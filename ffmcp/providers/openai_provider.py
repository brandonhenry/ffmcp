"""OpenAI provider implementation with full feature support"""
try:
    from openai import OpenAI
    import base64
    from pathlib import Path
except ImportError:
    OpenAI = None
    base64 = None
    Path = None

from typing import List, Dict, Iterator, Optional, Any, Union
from ffmcp.providers.base import BaseProvider
import json


class OpenAIProvider(BaseProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, config):
        if OpenAI is None:
            raise ImportError("openai package not installed. Install with: pip install openai")
        super().__init__(config)
        self.client = OpenAI(api_key=self.api_key)
    
    def get_provider_name(self) -> str:
        return 'openai'
    
    def get_default_model(self) -> str:
        return self.config.get_default_model('openai') or 'gpt-4o-mini'
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI"""
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
            total = getattr(usage, 'total_tokens', None) if usage else None
            if total is None and usage:
                # Fallback: sum prompt + completion
                pt = getattr(usage, 'prompt_tokens', 0)
                ct = getattr(usage, 'completion_tokens', 0)
                total = (pt or 0) + (ct or 0)
            if total:
                self.config.add_token_usage(self.get_provider_name(), int(total))
        except Exception:
            pass
        return response.choices[0].message.content
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate text using OpenAI (streaming)"""
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
            # Best-effort: capture usage when present on a chunk (SDK-dependent)
            try:
                usage = getattr(chunk, 'usage', None)
                if usage and getattr(usage, 'total_tokens', None) is not None:
                    total_tokens_detected = int(usage.total_tokens)
            except Exception:
                pass
        # After stream ends, record usage if we saw it
        if total_tokens_detected:
            try:
                self.config.add_token_usage(self.get_provider_name(), total_tokens_detected)
            except Exception:
                pass
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with OpenAI"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        tools = kwargs.get('tools')
        tool_choice = kwargs.get('tool_choice')
        
        params = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
        }
        if max_tokens:
            params['max_tokens'] = max_tokens
        if tools:
            params['tools'] = tools
        if tool_choice:
            params['tool_choice'] = tool_choice
        
        response = self.client.chat.completions.create(**params)
        # Record token usage if available
        try:
            usage = getattr(response, 'usage', None)
            total = getattr(usage, 'total_tokens', None) if usage else None
            if total is None and usage:
                pt = getattr(usage, 'prompt_tokens', 0)
                ct = getattr(usage, 'completion_tokens', 0)
                total = (pt or 0) + (ct or 0)
            if total:
                self.config.add_token_usage(self.get_provider_name(), int(total))
        except Exception:
            pass
        return response.choices[0].message.content
    
    # ========== Vision / Image Understanding ==========
    
    def vision(self, prompt: str, image_paths: List[str], **kwargs) -> str:
        """Analyze images with vision models"""
        model = kwargs.get('model', 'gpt-4o')
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        
        # Prepare image content
        image_contents = []
        for img_path in image_paths:
            path = Path(img_path)
            if not path.exists():
                raise FileNotFoundError(f"Image not found: {img_path}")
            
            # Read and encode image
            with open(path, 'rb') as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
                image_contents.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{path.suffix[1:]};base64,{image_data}"
                    }
                })
        
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                *image_contents
            ]
        }]
        
        params = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
        }
        if max_tokens:
            params['max_tokens'] = max_tokens
        
        response = self.client.chat.completions.create(**params)
        # Record token usage if available
        try:
            usage = getattr(response, 'usage', None)
            total = getattr(usage, 'total_tokens', None) if usage else None
            if total is None and usage:
                pt = getattr(usage, 'prompt_tokens', 0)
                ct = getattr(usage, 'completion_tokens', 0)
                total = (pt or 0) + (ct or 0)
            if total:
                self.config.add_token_usage(self.get_provider_name(), int(total))
        except Exception:
            pass
        return response.choices[0].message.content
    
    # ========== Image Generation (DALL·E) ==========
    
    def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate image using DALL·E"""
        model = kwargs.get('model', 'dall-e-3')
        size = kwargs.get('size', '1024x1024')
        quality = kwargs.get('quality', 'standard')
        n = kwargs.get('n', 1)
        style = kwargs.get('style', 'vivid')
        
        if model == 'dall-e-3':
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,  # DALL-E 3 only supports n=1
                style=style,
            )
            return {
                'url': response.data[0].url,
                'revised_prompt': response.data[0].revised_prompt if hasattr(response.data[0], 'revised_prompt') else None
            }
        else:  # DALL-E 2
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                n=n,
            )
            return {
                'urls': [item.url for item in response.data],
                'url': response.data[0].url  # For compatibility
            }
    
    def generate_image_variation(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """Generate image variation"""
        n = kwargs.get('n', 1)
        size = kwargs.get('size', '1024x1024')
        
        with open(image_path, 'rb') as img_file:
            response = self.client.images.create_variation(
                image=img_file,
                n=n,
                size=size,
            )
        
        return {
            'urls': [item.url for item in response.data],
            'url': response.data[0].url
        }
    
    def edit_image(self, prompt: str, image_path: str, mask_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Edit image using DALL·E"""
        n = kwargs.get('n', 1)
        size = kwargs.get('size', '1024x1024')
        
        with open(image_path, 'rb') as img_file:
            params = {
                'image': img_file,
                'prompt': prompt,
                'n': n,
                'size': size,
            }
            if mask_path:
                params['mask'] = open(mask_path, 'rb')
            
            try:
                response = self.client.images.edit(**params)
                return {
                    'urls': [item.url for item in response.data],
                    'url': response.data[0].url
                }
            finally:
                if mask_path and 'mask' in params:
                    params['mask'].close()
    
    # ========== Audio Transcription (Whisper) ==========
    
    def transcribe(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """Transcribe audio to text using Whisper"""
        model = kwargs.get('model', 'whisper-1')
        language = kwargs.get('language')
        prompt = kwargs.get('prompt')
        response_format = kwargs.get('response_format', 'json')
        temperature = kwargs.get('temperature', 0)
        timestamp_granularities = kwargs.get('timestamp_granularities', [])
        
        with open(audio_path, 'rb') as audio_file:
            params = {
                'model': model,
                'file': audio_file,
                'response_format': response_format,
                'temperature': temperature,
            }
            if language:
                params['language'] = language
            if prompt:
                params['prompt'] = prompt
            if timestamp_granularities:
                params['timestamp_granularities'] = timestamp_granularities
            
            transcript = self.client.audio.transcriptions.create(**params)
            
            if response_format == 'json':
                return {
                    'text': transcript.text,
                    'language': getattr(transcript, 'language', None),
                    'segments': getattr(transcript, 'segments', None),
                }
            return {'text': str(transcript)}
    
    def translate(self, audio_path: str, **kwargs) -> Dict[str, Any]:
        """Translate audio to English using Whisper"""
        model = kwargs.get('model', 'whisper-1')
        prompt = kwargs.get('prompt')
        response_format = kwargs.get('response_format', 'json')
        temperature = kwargs.get('temperature', 0)
        
        with open(audio_path, 'rb') as audio_file:
            params = {
                'model': model,
                'file': audio_file,
                'response_format': response_format,
                'temperature': temperature,
            }
            if prompt:
                params['prompt'] = prompt
            
            translation = self.client.audio.translations.create(**params)
            
            if response_format == 'json':
                return {
                    'text': translation.text,
                    'language': 'en',
                }
            return {'text': str(translation)}
    
    # ========== Text-to-Speech ==========
    
    def text_to_speech(self, text: str, output_path: str, **kwargs) -> str:
        """Convert text to speech"""
        model = kwargs.get('model', 'tts-1')
        voice = kwargs.get('voice', 'alloy')
        speed = kwargs.get('speed', 1.0)
        
        response = self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            speed=speed,
        )
        
        response.stream_to_file(output_path)
        return output_path
    
    # ========== Embeddings ==========
    
    def create_embedding(self, text: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
        """Create embeddings for text"""
        model = kwargs.get('model', 'text-embedding-3-small')
        dimensions = kwargs.get('dimensions')
        encoding_format = kwargs.get('encoding_format', 'float')
        
        params = {
            'model': model,
            'input': text if isinstance(text, list) else [text],
        }
        if dimensions:
            params['dimensions'] = dimensions
        if encoding_format:
            params['encoding_format'] = encoding_format
        
        response = self.client.embeddings.create(**params)
        
        result = {
            'embeddings': [item.embedding for item in response.data],
            'embedding': response.data[0].embedding if len(response.data) == 1 else None,
            'model': response.model,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'total_tokens': response.usage.total_tokens,
            }
        }
        # Count embedding tokens as well
        try:
            total = getattr(response.usage, 'total_tokens', None)
            if total:
                self.config.add_token_usage(self.get_provider_name(), int(total))
        except Exception:
            pass
        return result
    
    # ========== Function Calling / Tools ==========
    
    def chat_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict], **kwargs) -> Dict[str, Any]:
        """Chat with function calling support"""
        model = kwargs.get('model', self.get_default_model())
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens')
        tool_choice = kwargs.get('tool_choice', 'auto')
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        # Record token usage if available
        try:
            usage = getattr(response, 'usage', None)
            total = getattr(usage, 'total_tokens', None) if usage else None
            if total is None and usage:
                pt = getattr(usage, 'prompt_tokens', 0)
                ct = getattr(usage, 'completion_tokens', 0)
                total = (pt or 0) + (ct or 0)
            if total:
                self.config.add_token_usage(self.get_provider_name(), int(total))
        except Exception:
            pass
        
        message = response.choices[0].message
        result = {
            'content': message.content,
            'tool_calls': None,
        }
        
        if message.tool_calls:
            result['tool_calls'] = [
                {
                    'id': tc.id,
                    'type': tc.type,
                    'function': {
                        'name': tc.function.name,
                        'arguments': json.loads(tc.function.arguments),
                    }
                }
                for tc in message.tool_calls
            ]
        
        return result
    
    # ========== Assistants API ==========
    
    def create_assistant(self, name: str, instructions: str, **kwargs) -> Dict[str, Any]:
        """Create an AI assistant"""
        model = kwargs.get('model', 'gpt-4o-mini')
        tools = kwargs.get('tools', [])
        tool_resources = kwargs.get('tool_resources')
        temperature = kwargs.get('temperature', 1.0)
        top_p = kwargs.get('top_p')
        response_format = kwargs.get('response_format')
        
        params = {
            'name': name,
            'instructions': instructions,
            'model': model,
            'tools': tools,
            'temperature': temperature,
        }
        if tool_resources:
            params['tool_resources'] = tool_resources
        if top_p:
            params['top_p'] = top_p
        if response_format:
            params['response_format'] = response_format
        
        assistant = self.client.beta.assistants.create(**params)
        return {
            'id': assistant.id,
            'name': assistant.name,
            'model': assistant.model,
            'created_at': assistant.created_at,
        }
    
    def create_thread(self, messages: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Create a conversation thread"""
        params = {}
        if messages:
            params['messages'] = messages
        
        thread = self.client.beta.threads.create(**params)
        return {
            'id': thread.id,
            'created_at': thread.created_at,
        }
    
    def run_assistant(self, thread_id: str, assistant_id: str, **kwargs) -> Dict[str, Any]:
        """Run an assistant on a thread"""
        instructions = kwargs.get('instructions')
        tools = kwargs.get('tools')
        model = kwargs.get('model')
        stream = kwargs.get('stream', False)
        
        params = {
            'assistant_id': assistant_id,
        }
        if instructions:
            params['instructions'] = instructions
        if tools:
            params['tools'] = tools
        if model:
            params['model'] = model
        
        if stream:
            return self._stream_assistant_run(thread_id, params)
        
        run = self.client.beta.threads.runs.create(thread_id=thread_id, **params)
        return {
            'id': run.id,
            'status': run.status,
            'created_at': run.created_at,
        }
    
    def _stream_assistant_run(self, thread_id: str, params: Dict) -> Iterator[Dict]:
        """Stream assistant run"""
        stream = self.client.beta.threads.runs.create(thread_id=thread_id, stream=True, **params)
        for event in stream:
            yield {
                'event': event.event,
                'data': event.data.model_dump() if hasattr(event.data, 'model_dump') else str(event.data),
            }
    
    def add_message_to_thread(self, thread_id: str, role: str, content: str, **kwargs) -> Dict[str, Any]:
        """Add message to thread"""
        file_ids = kwargs.get('file_ids', [])
        metadata = kwargs.get('metadata', {})
        
        message = self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content,
            file_ids=file_ids,
            metadata=metadata,
        )
        return {
            'id': message.id,
            'role': message.role,
            'content': message.content[0].text.value if message.content else None,
            'created_at': message.created_at,
        }
    
    def get_thread_messages(self, thread_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get messages from thread"""
        messages = self.client.beta.threads.messages.list(thread_id=thread_id, limit=limit)
        return [
            {
                'id': msg.id,
                'role': msg.role,
                'content': msg.content[0].text.value if msg.content else None,
                'created_at': msg.created_at,
            }
            for msg in messages.data
        ]
    
    def upload_file(self, file_path: str, purpose: str = 'assistants') -> Dict[str, Any]:
        """Upload file for use with assistants"""
        with open(file_path, 'rb') as f:
            file = self.client.files.create(
                file=f,
                purpose=purpose,
            )
        return {
            'id': file.id,
            'filename': file.filename,
            'bytes': file.bytes,
            'created_at': file.created_at,
            'purpose': file.purpose,
        }

