from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
import os

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key
        self.current_model = None
        self.available_models = []
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.is_healthy = False
        self._personality_prompt = self._load_personality_prompt()
    
    @abstractmethod
    async def chat(self, message: str, history: List[Dict[str, str]] = None, model: str = None) -> str:
        """Send a chat message and get response"""
        pass
    
    @abstractmethod
    async def health_check(self, model: str = None) -> bool:
        """Check if the provider and model are healthy"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models for this provider"""
        pass
    
    @abstractmethod
    def set_model(self, model: str) -> bool:
        """Set the current model for this provider"""
        pass
    
    def get_current_model(self) -> Optional[str]:
        """Get the currently selected model"""
        return self.current_model
    
    def is_available(self) -> bool:
        """Check if provider is available (has API key and is healthy)"""
        return bool(self.api_key) and self.is_healthy
    
    async def initialize(self):
        """Initialize the provider and perform health check"""
        try:
            self.available_models = self.get_available_models()
            if self.available_models:
                # Set first available model as default
                self.current_model = self.available_models[0]['id']
            
            self.is_healthy = await self.health_check()
            if self.is_healthy:
                self.logger.info(f"{self.name} provider initialized successfully")
            else:
                self.logger.warning(f"{self.name} provider health check failed")
        except Exception as e:
            self.logger.error(f"Error initializing {self.name} provider: {e}")
            self.is_healthy = False
    
    def format_conversation_history(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format conversation history for this provider (can be overridden)"""
        if not history:
            return []
        
        formatted = []
        for turn in history:
            if 'user' in turn and 'assistant' in turn:
                formatted.extend([
                    {"role": "user", "content": turn['user']},
                    {"role": "assistant", "content": turn['assistant']}
                ])
        return formatted
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        for model in self.available_models:
            if model['id'] == model_id:
                return model
        return None
    
    def _load_personality_prompt(self) -> str:
        """Load personality prompt from Personality.txt file"""
        try:
            # Get the project root directory (assuming the backend is in voice-assistant/backend/)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            personality_file = os.path.join(project_root, 'Personality.txt')
            
            if os.path.exists(personality_file):
                with open(personality_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.logger.info(f"Loaded personality prompt from {personality_file}")
                        return content
            
            # Fallback to default system prompt
            self.logger.warning(f"Personality file not found or empty at {personality_file}, using default prompt")
            return "You are a helpful AI assistant."
            
        except Exception as e:
            self.logger.error(f"Error loading personality prompt: {e}")
            return "You are a helpful AI assistant."
    
    def get_system_prompt(self) -> str:
        """Get the system prompt (personality) for the LLM"""
        return self._personality_prompt