import openai
from typing import List, Dict, Any, Optional
from .base_provider import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider for GPT models"""
    
    def __init__(self, api_key: str):
        super().__init__("OpenAI", api_key)
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self._models = [
            {"id": "gpt-4o", "name": "GPT-4o", "available": True, "cost_tier": "high"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "available": True, "cost_tier": "low"},
            {"id": "o3-mini", "name": "o3-mini", "available": False, "cost_tier": "medium"}  # Requires special access
        ]
    
    async def chat(self, message: str, history: List[Dict[str, str]] = None, model: str = None) -> str:
        """Send chat message to OpenAI"""
        try:
            model_to_use = model or self.current_model or "gpt-4o"
            
            # Build messages array with personality prompt
            messages = [{"role": "system", "content": self.get_system_prompt()}]
            
            # Add conversation history
            if history:
                messages.extend(self.format_conversation_history(history))
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"OpenAI chat error: {e}")
            raise Exception(f"OpenAI error: {str(e)}")
    
    async def health_check(self, model: str = None) -> bool:
        """Check OpenAI API health"""
        try:
            model_to_test = model or self.current_model or "gpt-3.5-turbo"
            
            response = await self.client.chat.completions.create(
                model=model_to_test,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            return bool(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"OpenAI health check failed: {e}")
            return False
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available OpenAI models"""
        return self._models.copy()
    
    def set_model(self, model: str) -> bool:
        """Set current OpenAI model"""
        for model_info in self._models:
            if model_info['id'] == model and model_info['available']:
                self.current_model = model
                self.logger.info(f"OpenAI model set to: {model}")
                return True
        
        self.logger.warning(f"OpenAI model not available: {model}")
        return False