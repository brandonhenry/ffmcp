"""Configuration management for ffmcp"""
import os
import json
from pathlib import Path
from typing import Optional
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

    # ---------------- Brain registry ----------------
    def list_brains(self) -> list:
        brains = self._config.get('brains', {})
        return [{'name': n, **({} if not isinstance(v, dict) else v)} for n, v in brains.items()]

    def get_brain(self, name: str) -> dict:
        return self._config.get('brains', {}).get(name) or {}

    def create_brain(self, name: str, *, default_session_id: str = None) -> dict:
        if not name or not name.strip():
            raise ValueError('brain name is required')
        brains = self._config.setdefault('brains', {})
        if name in brains:
            raise ValueError(f'brain already exists: {name}')
        brains[name] = {'default_session_id': default_session_id}
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

