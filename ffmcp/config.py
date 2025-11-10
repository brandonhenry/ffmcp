"""Configuration management for ffmcp"""
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timezone


class Config:
    """Manages configuration and API keys"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.ffmcp'
        self.config_file = self.config_dir / 'config.json'
        self.tokens_file = self.config_dir / 'tokens.json'
        self.config_dir.mkdir(exist_ok=True)
        self._config = self._load_config()
        self._tokens = self._load_tokens()
    
    def _load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)

    def _load_tokens(self) -> dict:
        """Load token usage from file"""
        if self.tokens_file.exists():
            try:
                with open(self.tokens_file, 'r') as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) else {}
            except Exception:
                return {}
        return {}

    def _save_tokens(self):
        """Save token usage to file"""
        with open(self.tokens_file, 'w') as f:
            json.dump(self._tokens, f, indent=2)
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider"""
        # First check environment variable
        env_key = os.getenv(f'{provider.upper()}_API_KEY') or os.getenv(f'{provider}_API_KEY')
        if env_key:
            return self._normalize_secret(env_key, source='env', provider=provider)
        
        # Then check config file
        cfg_key = self._config.get('api_keys', {}).get(provider)
        if cfg_key:
            return self._normalize_secret(cfg_key, source='config', provider=provider)
        return None
    
    def set_api_key(self, provider: str, key: str):
        """Set API key for a provider"""
        if 'api_keys' not in self._config:
            self._config['api_keys'] = {}
        self._config['api_keys'][provider] = self._normalize_secret(key, source='set', provider=provider)
        self._save_config()
    
    def get_default_model(self, provider: str) -> Optional[str]:
        """Get default model for a provider"""
        return self._config.get('default_models', {}).get(provider)
    
    def set_default_model(self, provider: str, model: str):
        """Set default model for a provider"""
        if 'default_models' not in self._config:
            self._config['default_models'] = {}
        self._config['default_models'][provider] = model
        self._save_config()

    # ---------------- Internal helpers ----------------
    def _normalize_secret(self, value: str, *, source: str, provider: str) -> str:
        """Normalize secrets (API keys) to avoid common copy/paste issues.

        - Strips whitespace
        - Removes matching wrapping quotes (" ' “ ” ‘ ’)
        - Replaces smart quotes with straight quotes
        - Validates ASCII-only; logs a helpful warning if non-ASCII found
        """
        logger = logging.getLogger('ffmcp.config')
        if value is None:
            return value
        original = value
        # Trim whitespace
        value = value.strip()
        # Replace smart quotes
        value = value.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
        # Remove wrapping quotes if present and matching
        if (len(value) >= 2) and ((value[0] == value[-1]) and value[0] in ('"', "'")):
            value = value[1:-1]
        # If still contains non-ASCII, warn to user
        try:
            value.encode('ascii')
        except UnicodeEncodeError:
            logger.warning(
                "API key for provider=%s from %s contains non-ASCII characters; this may break network requests.",
                provider,
                source,
            )
        # If normalization changed the value, inform at debug level
        if value != original:
            logger.debug(
                "Normalized API key for provider=%s from %s (length preserved)",
                provider,
                source,
            )
        return value

    # ---------------- Token usage helpers ----------------
    def add_token_usage(self, provider: str, tokens: int, when: Optional[datetime] = None):
        """Add token usage for a provider on a given date (UTC-based day).

        Stored structure:
        {
          "YYYY-MM-DD": { "openai": 1234, "anthropic": 567 }
        }
        """
        if tokens is None:
            return
        try:
            tokens = int(tokens)
        except Exception:
            return
        if tokens <= 0:
            return
        when = when or datetime.now(timezone.utc)
        day = when.astimezone(timezone.utc).date().isoformat()
        day_entry = self._tokens.setdefault(day, {})
        day_entry[provider] = int(day_entry.get(provider, 0)) + tokens
        self._tokens[day] = day_entry
        self._save_tokens()

    def get_token_usage(self, date_str: Optional[str] = None, provider: Optional[str] = None) -> int:
        """Get token usage count.

        - date_str: 'YYYY-MM-DD' (UTC date). Defaults to today's UTC date.
        - provider: if provided, filters to that provider; otherwise sums all providers.
        """
        if not date_str:
            date_str = datetime.now(timezone.utc).date().isoformat()
        day_entry = self._tokens.get(date_str, {})
        if provider:
            return int(day_entry.get(provider, 0) or 0)
        return int(sum(int(v or 0) for v in day_entry.values()))

    # ---------------- Zep settings ----------------
    def get_zep_settings(self) -> dict:
        """Return Zep settings: { api_key, base_url, env }.

        Values are resolved from env variables if not configured:
        - ZEP_API_KEY or ZEP_CLOUD_API_KEY
        - ZEP_BASE_URL
        - ZEP_ENV
        """
        zep_cfg = dict(self._config.get('zep', {}))
        api_key = (
            zep_cfg.get('api_key')
            or os.getenv('ZEP_API_KEY')
            or os.getenv('ZEP_CLOUD_API_KEY')
            or self.get_api_key('zep')
        )
        base_url = zep_cfg.get('base_url') or os.getenv('ZEP_BASE_URL')
        env = (zep_cfg.get('env') or os.getenv('ZEP_ENV') or 'cloud')
        return {'api_key': api_key, 'base_url': base_url, 'env': env}

    def set_zep_settings(self, *, api_key: str = None, base_url: str = None, env: str = None):
        """Persist Zep settings. Pass only the fields to update."""
        if 'zep' not in self._config:
            self._config['zep'] = {}
        if api_key is not None:
            # Also mirror into generic api_keys for convenience
            self.set_api_key('zep', api_key)
            self._config['zep']['api_key'] = self._normalize_secret(api_key, source='set', provider='zep')
        if base_url is not None:
            self._config['zep']['base_url'] = base_url.strip()
        if env is not None:
            self._config['zep']['env'] = env.strip()
        self._save_config()

    # ---------------- LEANN settings ----------------
    def get_leann_settings(self) -> dict:
        """Return LEANN settings: { index_dir }.
        
        Values are resolved from env variables if not configured:
        - LEANN_INDEX_DIR
        """
        leann_cfg = dict(self._config.get('leann', {}))
        index_dir = leann_cfg.get('index_dir') or os.getenv('LEANN_INDEX_DIR')
        return {'index_dir': index_dir}

    def set_leann_settings(self, *, index_dir: str = None):
        """Persist LEANN settings. Pass only the fields to update."""
        if 'leann' not in self._config:
            self._config['leann'] = {}
        if index_dir is not None:
            self._config['leann']['index_dir'] = index_dir.strip()
        self._save_config()

    # ---------------- Brain registry ----------------
    def list_brains(self) -> list:
        brains = self._config.get('brains', {})
        return [{'name': n, **({} if not isinstance(v, dict) else v)} for n, v in brains.items()]

    def get_brain(self, name: str) -> dict:
        brain = self._config.get('brains', {}).get(name) or {}
        # Ensure backward compatibility: default to 'zep' if backend not set
        if 'backend' not in brain:
            brain['backend'] = 'zep'
        return brain

    def create_brain(self, name: str, *, default_session_id: str = None, backend: str = "zep") -> dict:
        if not name or not name.strip():
            raise ValueError('brain name is required')
        if backend not in ("zep", "leann"):
            raise ValueError('backend must be "zep" or "leann"')
        brains = self._config.setdefault('brains', {})
        if name in brains:
            raise ValueError(f'brain already exists: {name}')
        brains[name] = {'default_session_id': default_session_id, 'backend': backend}
        self._config['active_brain'] = name
        self._save_config()
        return brains[name]

    def delete_brain(self, name: str):
        brains = self._config.get('brains', {})
        if name in brains:
            del brains[name]
            if self._config.get('active_brain') == name:
                self._config['active_brain'] = None
            self._save_config()

    def set_active_brain(self, name: Optional[str]):
        if name is not None:
            brains = self._config.get('brains', {})
            if name not in brains:
                raise ValueError(f'unknown brain: {name}')
        self._config['active_brain'] = name
        self._save_config()

    def get_active_brain(self) -> Optional[str]:
        return self._config.get('active_brain')

    # ---------------- Agent registry ----------------
    def list_agents(self) -> list:
        agents = self._config.get('agents', {})
        return [
            {
                'name': n,
                **({} if not isinstance(v, dict) else v)
            }
            for n, v in agents.items()
        ]

    def get_agent(self, name: str) -> dict:
        return self._config.get('agents', {}).get(name) or {}

    def create_agent(
        self,
        name: str,
        *,
        provider: str,
        model: str,
        instructions: Optional[str] = None,
        brain: Optional[str] = None,
        properties: Optional[dict] = None,
        actions: Optional[dict] = None,
        voice: Optional[str] = None,
    ) -> dict:
        if not name or not name.strip():
            raise ValueError('agent name is required')
        agents = self._config.setdefault('agents', {})
        if name in agents:
            raise ValueError(f'agent already exists: {name}')
        
        # Validate voice if provided
        if voice:
            voices = self._config.get('voices', {})
            if voice not in voices:
                raise ValueError(f'unknown voice: {voice}')
        
        agent_def = {
            'provider': provider,
            'model': model,
            'instructions': instructions or '',
            'brain': brain,
            'properties': properties or {},
            'actions': actions or {},
            'voice': voice,
        }
        agents[name] = agent_def
        self._config['active_agent'] = name
        self._save_config()
        return agent_def

    def delete_agent(self, name: str):
        agents = self._config.get('agents', {})
        if name in agents:
            del agents[name]
            if self._config.get('active_agent') == name:
                self._config['active_agent'] = None
            self._save_config()

    def set_active_agent(self, name: Optional[str]):
        if name is not None:
            agents = self._config.get('agents', {})
            if name not in agents:
                raise ValueError(f'unknown agent: {name}')
        self._config['active_agent'] = name
        self._save_config()

    def get_active_agent(self) -> Optional[str]:
        return self._config.get('active_agent')

    def update_agent(self, name: str, updates: dict) -> dict:
        agents = self._config.setdefault('agents', {})
        if name not in agents:
            raise ValueError(f'unknown agent: {name}')
        if not isinstance(updates, dict):
            raise ValueError('updates must be a dict')
        current = agents[name]
        current.update({k: v for k, v in updates.items() if v is not None})
        agents[name] = current
        self._save_config()
        return current

    def set_agent_property(self, name: str, key: str, value):
        agents = self._config.setdefault('agents', {})
        if name not in agents:
            raise ValueError(f'unknown agent: {name}')
        props = agents[name].setdefault('properties', {})
        props[key] = value
        self._save_config()
    
    def set_agent_voice(self, name: str, voice_name: Optional[str]):
        """Set or remove voice for an agent"""
        agents = self._config.setdefault('agents', {})
        if name not in agents:
            raise ValueError(f'unknown agent: {name}')
        
        if voice_name:
            # Validate voice exists
            voices = self._config.get('voices', {})
            if voice_name not in voices:
                raise ValueError(f'unknown voice: {voice_name}')
        
        agents[name]['voice'] = voice_name
        self._save_config()
    
    def get_agent_voice(self, name: str) -> Optional[str]:
        """Get voice name for an agent"""
        agents = self._config.get('agents', {})
        if name not in agents:
            raise ValueError(f'unknown agent: {name}')
        return agents[name].get('voice')

    def remove_agent_property(self, name: str, key: str):
        agents = self._config.setdefault('agents', {})
        if name not in agents:
            raise ValueError(f'unknown agent: {name}')
        props = agents[name].setdefault('properties', {})
        if key in props:
            del props[key]
            self._save_config()

    def enable_agent_action(self, name: str, action: str, config: Optional[dict] = None):
        agents = self._config.setdefault('agents', {})
        if name not in agents:
            raise ValueError(f'unknown agent: {name}')
        actions = agents[name].setdefault('actions', {})
        actions[action] = config if config is not None else {'enabled': True}
        self._save_config()

    def disable_agent_action(self, name: str, action: str):
        agents = self._config.setdefault('agents', {})
        if name not in agents:
            raise ValueError(f'unknown agent: {name}')
        actions = agents[name].setdefault('actions', {})
        if action in actions:
            del actions[action]
            self._save_config()

    # ---------------- Thread management ----------------
    def list_threads(self, agent_name: str) -> List[Dict[str, Any]]:
        """List all threads for an agent"""
        threads = self._config.get('threads', {}).get(agent_name, {})
        active_thread = self.get_active_thread(agent_name)
        return [
            {
                'name': name,
                'message_count': len(thread.get('messages', [])),
                'created_at': thread.get('created_at'),
                'active': name == active_thread,
            }
            for name, thread in threads.items()
        ]

    def get_thread(self, agent_name: str, thread_name: str) -> Dict:
        """Get thread data"""
        threads = self._config.get('threads', {}).get(agent_name, {})
        return threads.get(thread_name) or {}

    def create_thread(self, agent_name: str, thread_name: str) -> Dict:
        """Create a new thread for an agent"""
        if not agent_name or not agent_name.strip():
            raise ValueError('agent name is required')
        if not thread_name or not thread_name.strip():
            raise ValueError('thread name is required')
        
        # Verify agent exists
        agents = self._config.get('agents', {})
        if agent_name not in agents:
            raise ValueError(f'unknown agent: {agent_name}')
        
        threads = self._config.setdefault('threads', {})
        agent_threads = threads.setdefault(agent_name, {})
        
        if thread_name in agent_threads:
            raise ValueError(f'thread already exists: {thread_name}')
        
        thread_data = {
            'messages': [],
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        agent_threads[thread_name] = thread_data
        
        # Set as active thread for this agent
        active_threads = self._config.setdefault('active_threads', {})
        active_threads[agent_name] = thread_name
        
        self._save_config()
        return thread_data

    def delete_thread(self, agent_name: str, thread_name: str):
        """Delete a thread"""
        threads = self._config.get('threads', {}).get(agent_name, {})
        if thread_name in threads:
            del threads[thread_name]
            # If this was the active thread, clear it
            active_threads = self._config.get('active_threads', {})
            if active_threads.get(agent_name) == thread_name:
                del active_threads[agent_name]
            self._save_config()

    def set_active_thread(self, agent_name: str, thread_name: Optional[str]):
        """Set active thread for an agent"""
        if not agent_name or not agent_name.strip():
            raise ValueError('agent name is required')
        
        # Verify agent exists
        agents = self._config.get('agents', {})
        if agent_name not in agents:
            raise ValueError(f'unknown agent: {agent_name}')
        
        if thread_name is not None:
            # Verify thread exists
            threads = self._config.get('threads', {}).get(agent_name, {})
            if thread_name not in threads:
                raise ValueError(f'unknown thread: {thread_name}')
        
        active_threads = self._config.setdefault('active_threads', {})
        active_threads[agent_name] = thread_name
        self._save_config()

    def get_active_thread(self, agent_name: str) -> Optional[str]:
        """Get active thread name for an agent"""
        active_threads = self._config.get('active_threads', {})
        return active_threads.get(agent_name)

    def clear_thread(self, agent_name: str, thread_name: str):
        """Clear all messages from a thread"""
        threads = self._config.get('threads', {}).get(agent_name, {})
        if thread_name not in threads:
            raise ValueError(f'unknown thread: {thread_name}')
        threads[thread_name]['messages'] = []
        self._save_config()

    def add_thread_message(self, agent_name: str, thread_name: str, role: str, content: str):
        """Add a message to a thread"""
        threads = self._config.setdefault('threads', {})
        agent_threads = threads.setdefault(agent_name, {})
        
        if thread_name not in agent_threads:
            # Auto-create thread if it doesn't exist
            agent_threads[thread_name] = {
                'messages': [],
                'created_at': datetime.now(timezone.utc).isoformat(),
            }
        
        agent_threads[thread_name]['messages'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })
        self._save_config()

    def get_thread_messages(self, agent_name: str, thread_name: Optional[str] = None) -> List[Dict[str, str]]:
        """Get messages from a thread. If thread_name is None, uses active thread."""
        if thread_name is None:
            thread_name = self.get_active_thread(agent_name)
            if not thread_name:
                return []
        
        thread = self.get_thread(agent_name, thread_name)
        messages = thread.get('messages', [])
        # Return in format expected by chat API (role, content)
        return [
            {'role': msg.get('role'), 'content': msg.get('content', '')}
            for msg in messages
        ]

    def save_thread_messages(self, agent_name: str, thread_name: Optional[str], messages: List[Dict[str, str]]):
        """Save messages to a thread. If thread_name is None, uses active thread."""
        if thread_name is None:
            thread_name = self.get_active_thread(agent_name)
            if not thread_name:
                # Auto-create thread if none exists
                thread_name = 'default'
                self.create_thread(agent_name, thread_name)
        
        threads = self._config.setdefault('threads', {})
        agent_threads = threads.setdefault(agent_name, {})
        
        if thread_name not in agent_threads:
            agent_threads[thread_name] = {
                'messages': [],
                'created_at': datetime.now(timezone.utc).isoformat(),
            }
        
        # Convert messages to thread format and append
        for msg in messages:
            agent_threads[thread_name]['messages'].append({
                'role': msg.get('role'),
                'content': msg.get('content', ''),
                'timestamp': datetime.now(timezone.utc).isoformat(),
            })
        self._save_config()

    # ---------------- Chat thread management (not tied to agents) ----------------
    def list_chat_threads(self) -> List[Dict[str, Any]]:
        """List all chat threads"""
        threads = self._config.get('chat_threads', {})
        active_thread = self._config.get('active_chat_thread')
        return [
            {
                'name': name,
                'message_count': len(thread.get('messages', [])),
                'created_at': thread.get('created_at'),
                'active': name == active_thread,
            }
            for name, thread in threads.items()
        ]

    def get_chat_thread(self, thread_name: str) -> Dict:
        """Get chat thread data"""
        threads = self._config.get('chat_threads', {})
        return threads.get(thread_name) or {}

    def create_chat_thread(self, thread_name: str) -> Dict:
        """Create a new chat thread"""
        if not thread_name or not thread_name.strip():
            raise ValueError('thread name is required')
        
        threads = self._config.setdefault('chat_threads', {})
        
        if thread_name in threads:
            raise ValueError(f'thread already exists: {thread_name}')
        
        thread_data = {
            'messages': [],
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        threads[thread_name] = thread_data
        
        # Set as active chat thread
        self._config['active_chat_thread'] = thread_name
        
        self._save_config()
        return thread_data

    def delete_chat_thread(self, thread_name: str):
        """Delete a chat thread"""
        threads = self._config.get('chat_threads', {})
        if thread_name in threads:
            del threads[thread_name]
            # If this was the active thread, clear it
            if self._config.get('active_chat_thread') == thread_name:
                self._config['active_chat_thread'] = None
            self._save_config()

    def set_active_chat_thread(self, thread_name: Optional[str]):
        """Set active chat thread"""
        if thread_name is not None:
            # Verify thread exists
            threads = self._config.get('chat_threads', {})
            if thread_name not in threads:
                raise ValueError(f'unknown thread: {thread_name}')
        
        self._config['active_chat_thread'] = thread_name
        self._save_config()

    def get_active_chat_thread(self) -> Optional[str]:
        """Get active chat thread name"""
        return self._config.get('active_chat_thread')

    def clear_chat_thread(self, thread_name: str):
        """Clear all messages from a chat thread"""
        threads = self._config.get('chat_threads', {})
        if thread_name not in threads:
            raise ValueError(f'unknown thread: {thread_name}')
        threads[thread_name]['messages'] = []
        self._save_config()

    def add_chat_thread_message(self, thread_name: str, role: str, content: str):
        """Add a message to a chat thread"""
        threads = self._config.setdefault('chat_threads', {})
        
        if thread_name not in threads:
            # Auto-create thread if it doesn't exist
            threads[thread_name] = {
                'messages': [],
                'created_at': datetime.now(timezone.utc).isoformat(),
            }
        
        threads[thread_name]['messages'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })
        self._save_config()

    def get_chat_thread_messages(self, thread_name: Optional[str] = None) -> List[Dict[str, str]]:
        """Get messages from a chat thread. If thread_name is None, uses active thread."""
        if thread_name is None:
            thread_name = self.get_active_chat_thread()
            if not thread_name:
                return []
        
        thread = self.get_chat_thread(thread_name)
        messages = thread.get('messages', [])
        # Return in format expected by chat API (role, content)
        return [
            {'role': msg.get('role'), 'content': msg.get('content', '')}
            for msg in messages
        ]

    # ---------------- Voiceover/Voice management ----------------
    def list_voices(self) -> List[Dict[str, Any]]:
        """List all saved voice configurations"""
        voices = self._config.get('voices', {})
        return [
            {
                'name': name,
                **({} if not isinstance(v, dict) else v)
            }
            for name, v in voices.items()
        ]

    def get_voice(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a voice configuration by name"""
        voices = self._config.get('voices', {})
        return voices.get(name)

    def create_voice(
        self,
        name: str,
        provider: str,
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None,
        stability: Optional[float] = None,
        similarity_boost: Optional[float] = None,
        style: Optional[float] = None,
        use_speaker_boost: Optional[bool] = None,
        output_format: Optional[str] = None,
        description: Optional[str] = None,
        # FishAudio-specific parameters
        reference_id: Optional[str] = None,
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None,
        format: Optional[str] = None,
        prosody: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Create a new voice configuration"""
        if not name or not name.strip():
            raise ValueError('voice name is required')
        if not provider or not provider.strip():
            raise ValueError('provider is required')
        
        # For providers that require voice_id (like ElevenLabs), validate it
        if provider == 'elevenlabs' and (not voice_id or not voice_id.strip()):
            raise ValueError('voice_id is required for elevenlabs provider')
        
        # For FishAudio, either voice_id/reference_id or reference_audio is needed
        if provider == 'fishaudio' and not voice_id and not reference_id and not reference_audio:
            raise ValueError('voice_id, reference_id, or reference_audio is required for fishaudio provider')
        
        voices = self._config.setdefault('voices', {})
        if name in voices:
            raise ValueError(f'voice already exists: {name}')
        
        voice_config = {
            'provider': provider,
        }
        
        # Add voice_id if provided
        if voice_id:
            voice_config['voice_id'] = voice_id
        
        # Add optional parameters (ElevenLabs)
        if model_id is not None:
            voice_config['model_id'] = model_id
        if stability is not None:
            voice_config['stability'] = stability
        if similarity_boost is not None:
            voice_config['similarity_boost'] = similarity_boost
        if style is not None:
            voice_config['style'] = style
        if use_speaker_boost is not None:
            voice_config['use_speaker_boost'] = use_speaker_boost
        if output_format is not None:
            voice_config['output_format'] = output_format
        if description is not None:
            voice_config['description'] = description
        
        # Add FishAudio-specific parameters
        if reference_id is not None:
            voice_config['reference_id'] = reference_id
        if reference_audio is not None:
            voice_config['reference_audio'] = reference_audio
        if reference_text is not None:
            voice_config['reference_text'] = reference_text
        if format is not None:
            voice_config['format'] = format
        if prosody is not None:
            voice_config['prosody'] = prosody
        
        voices[name] = voice_config
        self._save_config()
        return voice_config

    def update_voice(self, name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a voice configuration"""
        voices = self._config.setdefault('voices', {})
        if name not in voices:
            raise ValueError(f'unknown voice: {name}')
        
        current = voices[name]
        # Update only provided fields
        for key, value in updates.items():
            if value is not None:
                current[key] = value
        
        voices[name] = current
        self._save_config()
        return current

    def delete_voice(self, name: str):
        """Delete a voice configuration"""
        voices = self._config.get('voices', {})
        if name in voices:
            del voices[name]
            # Also remove from any agents that use this voice
            agents = self._config.get('agents', {})
            for agent_name, agent_data in agents.items():
                if isinstance(agent_data, dict) and agent_data.get('voice') == name:
                    agent_data['voice'] = None
            self._save_config()
        else:
            raise ValueError(f'unknown voice: {name}')

    # ---------------- Team management ----------------
    def list_teams(self) -> List[Dict[str, Any]]:
        """List all teams"""
        teams = self._config.get('teams', {})
        return [
            {
                'name': name,
                **({} if not isinstance(v, dict) else v)
            }
            for name, v in teams.items()
        ]

    def get_team(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a team by name"""
        teams = self._config.get('teams', {})
        return teams.get(name)

    def create_team(
        self,
        name: str,
        *,
        orchestrator: str,
        members: Optional[List[str]] = None,
        sub_teams: Optional[List[str]] = None,
        shared_brain: Optional[str] = None,
        shared_thread: Optional[str] = None,
        parent_team: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new hierarchical team"""
        if not name or not name.strip():
            raise ValueError('team name is required')
        if not orchestrator or not orchestrator.strip():
            raise ValueError('orchestrator is required')
        
        members = members or []
        sub_teams = sub_teams or []
        
        # Validate orchestrator exists
        agents = self._config.get('agents', {})
        if orchestrator not in agents:
            raise ValueError(f'orchestrator agent not found: {orchestrator}')
        
        # Validate members exist
        for agent_name in members:
            if agent_name not in agents:
                raise ValueError(f'member agent not found: {agent_name}')
        
        # Validate sub-teams exist (if creating nested teams)
        teams = self._config.setdefault('teams', {})
        for sub_team_name in sub_teams:
            if sub_team_name not in teams:
                raise ValueError(f'sub-team not found: {sub_team_name}')
        
        # Validate shared brain exists if provided
        if shared_brain:
            brains = self._config.get('brains', {})
            if shared_brain not in brains:
                raise ValueError(f'shared brain not found: {shared_brain}')
        
        # Validate parent team exists if provided
        if parent_team:
            if parent_team not in teams:
                raise ValueError(f'parent team not found: {parent_team}')
        
        if name in teams:
            raise ValueError(f'team already exists: {name}')
        
        team_data = {
            'orchestrator': orchestrator,
            'members': members,
            'sub_teams': sub_teams,
            'shared_brain': shared_brain,
            'shared_thread': shared_thread,
            'parent_team': parent_team,
        }
        teams[name] = team_data
        
        # Set parent relationship for sub-teams
        for sub_team_name in sub_teams:
            sub_team_data = teams.get(sub_team_name, {})
            if sub_team_data:
                sub_team_data['parent_team'] = name
        
        # Set as active team
        self._config['active_team'] = name
        
        self._save_config()
        return team_data

    def delete_team(self, name: str):
        """Delete a team"""
        teams = self._config.get('teams', {})
        if name in teams:
            del teams[name]
            if self._config.get('active_team') == name:
                self._config['active_team'] = None
            self._save_config()
        else:
            raise ValueError(f'unknown team: {name}')

    def set_active_team(self, name: Optional[str]):
        """Set active team"""
        if name is not None:
            teams = self._config.get('teams', {})
            if name not in teams:
                raise ValueError(f'unknown team: {name}')
        self._config['active_team'] = name
        self._save_config()

    def get_active_team(self) -> Optional[str]:
        """Get active team name"""
        return self._config.get('active_team')

    def update_team(self, name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a team"""
        teams = self._config.setdefault('teams', {})
        if name not in teams:
            raise ValueError(f'unknown team: {name}')
        
        current = teams[name]
        agents = self._config.get('agents', {})
        
        # Validate orchestrator if being updated
        if 'orchestrator' in updates:
            orchestrator = updates['orchestrator']
            if orchestrator not in agents:
                raise ValueError(f'orchestrator agent not found: {orchestrator}')
        
        # Validate members if being updated
        if 'members' in updates:
            members = updates['members']
            for agent_name in members:
                if agent_name not in agents:
                    raise ValueError(f'member agent not found: {agent_name}')
        
        # Validate sub-teams if being updated
        if 'sub_teams' in updates:
            sub_teams = updates['sub_teams']
            for sub_team_name in sub_teams:
                if sub_team_name not in teams:
                    raise ValueError(f'sub-team not found: {sub_team_name}')
        
        # Validate shared_brain if being updated
        if 'shared_brain' in updates and updates['shared_brain']:
            shared_brain = updates['shared_brain']
            brains = self._config.get('brains', {})
            if shared_brain not in brains:
                raise ValueError(f'shared brain not found: {shared_brain}')
        
        # Validate parent_team if being updated
        if 'parent_team' in updates and updates['parent_team']:
            parent_team = updates['parent_team']
            if parent_team not in teams:
                raise ValueError(f'parent team not found: {parent_team}')
        
        # Update fields
        for key, value in updates.items():
            if value is not None or key in ('shared_brain', 'shared_thread', 'parent_team'):
                current[key] = value
        
        # Update parent relationships for sub-teams
        if 'sub_teams' in updates:
            # Clear old parent relationships
            old_sub_teams = current.get('sub_teams', [])
            for old_sub_team_name in old_sub_teams:
                if old_sub_team_name in teams:
                    old_sub_data = teams[old_sub_team_name]
                    if old_sub_data.get('parent_team') == name:
                        old_sub_data['parent_team'] = None
            
            # Set new parent relationships
            for sub_team_name in updates['sub_teams']:
                if sub_team_name in teams:
                    sub_team_data = teams[sub_team_name]
                    sub_team_data['parent_team'] = name
        
        teams[name] = current
        self._save_config()
        return current

    def add_member_to_team(self, team_name: str, agent_name: str):
        """Add an agent as a member to a team"""
        teams = self._config.setdefault('teams', {})
        if team_name not in teams:
            raise ValueError(f'unknown team: {team_name}')
        
        # Validate agent exists
        agents = self._config.get('agents', {})
        if agent_name not in agents:
            raise ValueError(f'agent not found: {agent_name}')
        
        team = teams[team_name]
        members = team.get('members', [])
        
        if agent_name in members:
            raise ValueError(f'agent already in team: {agent_name}')
        
        members.append(agent_name)
        team['members'] = members
        self._save_config()

    def remove_member_from_team(self, team_name: str, agent_name: str):
        """Remove an agent member from a team"""
        teams = self._config.get('teams', {})
        if team_name not in teams:
            raise ValueError(f'unknown team: {team_name}')
        
        team = teams[team_name]
        members = team.get('members', [])
        
        if agent_name not in members:
            raise ValueError(f'agent not in team: {agent_name}')
        
        members.remove(agent_name)
        team['members'] = members
        
        self._save_config()
    
    def add_sub_team_to_team(self, team_name: str, sub_team_name: str):
        """Add a sub-team to a team"""
        teams = self._config.setdefault('teams', {})
        if team_name not in teams:
            raise ValueError(f'unknown team: {team_name}')
        
        if sub_team_name not in teams:
            raise ValueError(f'sub-team not found: {sub_team_name}')
        
        team = teams[team_name]
        sub_teams = team.get('sub_teams', [])
        
        if sub_team_name in sub_teams:
            raise ValueError(f'sub-team already in team: {sub_team_name}')
        
        sub_teams.append(sub_team_name)
        team['sub_teams'] = sub_teams
        
        # Set parent relationship
        sub_team_data = teams[sub_team_name]
        sub_team_data['parent_team'] = team_name
        
        self._save_config()
    
    def remove_sub_team_from_team(self, team_name: str, sub_team_name: str):
        """Remove a sub-team from a team"""
        teams = self._config.get('teams', {})
        if team_name not in teams:
            raise ValueError(f'unknown team: {team_name}')
        
        team = teams[team_name]
        sub_teams = team.get('sub_teams', [])
        
        if sub_team_name not in sub_teams:
            raise ValueError(f'sub-team not in team: {sub_team_name}')
        
        sub_teams.remove(sub_team_name)
        team['sub_teams'] = sub_teams
        
        # Clear parent relationship
        if sub_team_name in teams:
            sub_team_data = teams[sub_team_name]
            sub_team_data['parent_team'] = None
        
        self._save_config()
    
    # Legacy methods for backward compatibility
    def add_agent_to_team(self, team_name: str, agent_name: str):
        """Legacy: Add an agent to a team (calls add_member_to_team)"""
        return self.add_member_to_team(team_name, agent_name)
    
    def remove_agent_from_team(self, team_name: str, agent_name: str):
        """Legacy: Remove an agent from a team (calls remove_member_from_team)"""
        return self.remove_member_from_team(team_name, agent_name)

