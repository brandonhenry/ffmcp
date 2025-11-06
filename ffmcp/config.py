"""Configuration management for ffmcp"""
import os
import json
from pathlib import Path
from typing import Optional


class Config:
    """Manages configuration and API keys"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.ffmcp'
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(exist_ok=True)
        self._config = self._load_config()
    
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
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider"""
        # First check environment variable
        env_key = os.getenv(f'{provider.upper()}_API_KEY') or os.getenv(f'{provider}_API_KEY')
        if env_key:
            return env_key
        
        # Then check config file
        return self._config.get('api_keys', {}).get(provider)
    
    def set_api_key(self, provider: str, key: str):
        """Set API key for a provider"""
        if 'api_keys' not in self._config:
            self._config['api_keys'] = {}
        self._config['api_keys'][provider] = key
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

