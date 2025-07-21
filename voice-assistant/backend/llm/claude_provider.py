import anthropic
from typing import List, Dict, Any, Optional
from .base_provider import BaseLLMProvider

class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str):
        super().__init__("Claude", api_key)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self._models = [
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "available": True, "cost_tier": "high"},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "available": True, "cost_tier": "low"},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "available": False, "cost_tier": "high"}  # Limited availability
        ]
    
    async def chat(self, message: str, history: List[Dict[str, str]] = None, model: str = None) -> str:
        """Send chat message to Claude"""
        try:
            model_to_use = model or self.current_model or "claude-3-5-sonnet-20241022"
            
            # Build messages array (Claude format)
            messages = []
            
            # Add conversation history
            if history:
                for turn in history:
                    if 'user' in turn and 'assistant' in turn:
                        messages.extend([
                            {"role": "user", "content": turn['user']},
                            {"role": "assistant", "content": turn['assistant']}
                        ])
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Make API call with personality prompt
            response = await self.client.messages.create(
                model=model_to_use,
                max_tokens=1000,
                messages=messages,
                system=self.get_system_prompt()
            )
            
            return response.content[0].text
            
        except Exception as e:
            self.logger.error(f"Claude chat error: {e}")
            raise Exception(f"Claude error: {str(e)}")
    
    async def health_check(self, model: str = None) -> bool:
        """Check Claude API health"""
        try:
            model_to_test = model or self.current_model or "claude-3-haiku-20240307"
            
            response = await self.client.messages.create(
                model=model_to_test,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}],
                system=self.get_system_prompt()
            )
            
            return bool(response.content[0].text)
            
        except Exception as e:
            self.logger.error(f"Claude health check failed: {e}")
            return False
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available Claude models"""
        return self._models.copy()
    
    def set_model(self, model: str) -> bool:
        """Set current Claude model"""
        for model_info in self._models:
            if model_info['id'] == model and model_info['available']:
                self.current_model = model
                self.logger.info(f"Claude model set to: {model}")
                return True
        
        self.logger.warning(f"Claude model not available: {model}")
        return False