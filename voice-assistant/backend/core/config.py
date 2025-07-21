import os
import json
from pathlib import Path
from typing import Dict, Optional
import logging

class ConfigManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        self.keys_path = self.base_path / "config" / "keys"
        self.settings_path = self.base_path / "config" / "settings"
        self.api_keys = {}
        self._setup_logging()
        self._load_api_keys()
    
    def _setup_logging(self):
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('voice_assistant.log'),
                    logging.StreamHandler()
                ]
            )
    
    def _load_api_keys(self):
        """Load API keys from key files"""
        key_files = {
            'openai': 'OpenAI.key',
            'claude': 'Claude.key', 
            'xai': 'XAI.key'
        }
        
        for provider, filename in key_files.items():
            key_file = self.keys_path / filename
            if key_file.exists():
                try:
                    with open(key_file, 'r') as f:
                        key = f.read().strip()
                        if key:
                            self.api_keys[provider] = key
                            self.logger.info(f"Loaded {provider} API key")
                except Exception as e:
                    self.logger.error(f"Error loading {provider} key: {e}")
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider"""
        return self.api_keys.get(provider.lower())
    
    def has_api_key(self, provider: str) -> bool:
        """Check if API key exists for provider"""
        return provider.lower() in self.api_keys
    
    def get_setting(self, key: str, default=None):
        """Get a configuration setting"""
        settings_file = self.settings_path / "config.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get(key, default)
            except Exception as e:
                self.logger.error(f"Error reading settings: {e}")
        return default

# Global config instance
config = ConfigManager()