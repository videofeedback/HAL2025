import aiohttp
import json
from typing import List, Dict, Any, Optional
from .base_provider import BaseLLMProvider

class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__("Ollama", None)  # No API key needed for local
        self.base_url = base_url
        self._models = []
    
    async def chat(self, message: str, history: List[Dict[str, str]] = None, model: str = None) -> str:
        """Send chat message to Ollama"""
        try:
            model_to_use = model or self.current_model or "llama3.1:8b"
            
            # Build prompt with personality and history
            prompt = f"System: {self.get_system_prompt()}\n\n"
            
            if history:
                for turn in history:
                    if 'user' in turn and 'assistant' in turn:
                        prompt += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
            
            prompt += f"User: {message}\nAssistant:"
            
            # Make API call to Ollama
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model_to_use,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9
                        }
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '').strip()
                    else:
                        raise Exception(f"Ollama API error: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Ollama chat error: {e}")
            raise Exception(f"Ollama error: {str(e)}")
    
    async def health_check(self, model: str = None) -> bool:
        """Check Ollama service health"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check if Ollama service is running
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status != 200:
                        return False
                
                # Test with a model if specified
                if model or self.current_model:
                    test_model = model or self.current_model
                    async with session.post(
                        f"{self.base_url}/api/generate",
                        json={
                            "model": test_model,
                            "prompt": "Hello",
                            "stream": False,
                            "options": {"max_tokens": 5}
                        }
                    ) as test_response:
                        return test_response.status == 200
                
                return True
                
        except Exception as e:
            self.logger.error(f"Ollama health check failed: {e}")
            return False
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available Ollama models (cached)"""
        return self._models.copy()
    
    async def _fetch_available_models(self) -> List[Dict[str, Any]]:
        """Fetch available Ollama models from API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = []
                        for model in data.get('models', []):
                            models.append({
                                "id": model['name'],
                                "name": model['name'],
                                "available": True,
                                "cost_tier": "free",
                                "size": model.get('size', 0)
                            })
                        self._models = models
                        return models
                    else:
                        return []
        except Exception as e:
            self.logger.error(f"Error getting Ollama models: {e}")
            return []
    
    def set_model(self, model: str) -> bool:
        """Set current Ollama model"""
        # For Ollama, we'll accept any model name and try to use it
        # The actual validation happens during API calls
        self.current_model = model
        self.logger.info(f"Ollama model set to: {model}")
        return True
    
    async def initialize(self):
        """Initialize Ollama provider"""
        try:
            self.available_models = await self._fetch_available_models()
            if self.available_models:
                # Prefer llama3.1 if available, otherwise use first model
                preferred_models = ["llama3.1:8b", "llama3.1:latest", "llama3.1", "llama3"]
                for preferred in preferred_models:
                    for model in self.available_models:
                        if preferred in model['id']:
                            self.current_model = model['id']
                            break
                    if self.current_model:
                        break
                
                if not self.current_model and self.available_models:
                    self.current_model = self.available_models[0]['id']
            
            self.is_healthy = await self.health_check()
            if self.is_healthy:
                self.logger.info(f"Ollama provider initialized with {len(self.available_models)} models")
            else:
                self.logger.warning("Ollama provider health check failed")
        except Exception as e:
            self.logger.error(f"Error initializing Ollama provider: {e}")
            self.is_healthy = False