import asyncio
import logging
from typing import Dict, List, Optional, Any
from ..core.config import config
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .ollama_provider import OllamaProvider

class ProviderManager:
    """Manages multiple LLM providers with automatic fallback"""
    
    def __init__(self):
        self.providers: Dict[str, Any] = {}
        self.current_provider = None
        self.current_model = None
        self.logger = logging.getLogger(__name__)
        self.fallback_chain = ["openai", "claude", "ollama"]
    
    async def initialize(self):
        """Initialize all available providers"""
        # Initialize OpenAI if API key available
        if config.has_api_key("openai"):
            try:
                openai_provider = OpenAIProvider(config.get_api_key("openai"))
                await openai_provider.initialize()
                self.providers["openai"] = openai_provider
                self.logger.info("OpenAI provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI: {e}")
        
        # Initialize Claude if API key available
        if config.has_api_key("claude"):
            try:
                claude_provider = ClaudeProvider(config.get_api_key("claude"))
                await claude_provider.initialize()
                self.providers["claude"] = claude_provider
                self.logger.info("Claude provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Claude: {e}")
        
        # Initialize Ollama (local, no API key needed)
        try:
            ollama_provider = OllamaProvider()
            await ollama_provider.initialize()
            if ollama_provider.is_healthy:
                self.providers["ollama"] = ollama_provider
                self.logger.info("Ollama provider initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama: {e}")
        
        # Set default provider and model
        await self._set_default_provider()
    
    async def _set_default_provider(self):
        """Set the default provider based on availability"""
        for provider_name in self.fallback_chain:
            if provider_name in self.providers:
                provider = self.providers[provider_name]
                # For Ollama, check if it has models, not just API key
                if provider_name == "ollama":
                    if provider.is_healthy and provider.get_current_model():
                        self.current_provider = provider_name
                        self.current_model = provider.get_current_model()
                        self.logger.info(f"Default provider set to: {provider_name} with model: {self.current_model}")
                        return
                else:
                    if provider.is_available():
                        self.current_provider = provider_name
                        self.current_model = provider.get_current_model()
                        self.logger.info(f"Default provider set to: {provider_name} with model: {self.current_model}")
                        return
        
        self.logger.warning("No providers available")
    
    async def chat(self, message: str, history: List[Dict[str, str]] = None, 
                   provider: str = None, model: str = None) -> Dict[str, Any]:
        """Send chat message with automatic fallback"""
        provider_to_use = provider or self.current_provider
        model_to_use = model or self.current_model
        
        # Try the specified/current provider first
        if provider_to_use and provider_to_use in self.providers:
            try:
                response = await self._try_provider(provider_to_use, message, history, model_to_use)
                if response:
                    return {
                        "text": response,
                        "provider": provider_to_use,
                        "model": model_to_use,
                        "fallback_used": False
                    }
            except Exception as e:
                self.logger.warning(f"Provider {provider_to_use} failed: {e}")
        
        # Try fallback chain
        for fallback_provider in self.fallback_chain:
            if (fallback_provider != provider_to_use and 
                fallback_provider in self.providers and 
                self.providers[fallback_provider].is_available()):
                
                try:
                    fallback_model = self.providers[fallback_provider].get_current_model()
                    response = await self._try_provider(fallback_provider, message, history, fallback_model)
                    if response:
                        self.logger.info(f"Fallback successful with {fallback_provider}")
                        return {
                            "text": response,
                            "provider": fallback_provider,
                            "model": fallback_model,
                            "fallback_used": True
                        }
                except Exception as e:
                    self.logger.warning(f"Fallback provider {fallback_provider} failed: {e}")
        
        # All providers failed
        raise Exception("All LLM providers failed")
    
    async def _try_provider(self, provider_name: str, message: str, 
                          history: List[Dict[str, str]], model: str) -> Optional[str]:
        """Try a specific provider"""
        provider = self.providers.get(provider_name)
        if not provider or not provider.is_available():
            return None
        
        return await provider.chat(message, history, model)
    
    def set_provider(self, provider_name: str, model: str = None) -> bool:
        """Set current provider and optionally model"""
        if provider_name not in self.providers:
            self.logger.error(f"Provider {provider_name} not available")
            return False
        
        provider = self.providers[provider_name]
        if not provider.is_available():
            self.logger.error(f"Provider {provider_name} not healthy")
            return False
        
        self.current_provider = provider_name
        
        if model:
            if provider.set_model(model):
                self.current_model = model
            else:
                self.current_model = provider.get_current_model()
        else:
            self.current_model = provider.get_current_model()
        
        self.logger.info(f"Provider set to {provider_name} with model {self.current_model}")
        return True
    
    def set_model(self, model: str, provider: str = None) -> bool:
        """Set model for current or specified provider"""
        provider_to_use = provider or self.current_provider
        
        if provider_to_use not in self.providers:
            self.logger.error(f"Provider {provider_to_use} not available")
            return False
        
        provider_obj = self.providers[provider_to_use]
        if provider_obj.set_model(model):
            if provider_to_use == self.current_provider:
                self.current_model = model
            self.logger.info(f"Model set to {model} for provider {provider_to_use}")
            return True
        
        return False
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        
        for name, provider in self.providers.items():
            status[name] = {
                "available": provider.is_available(),
                "current_model": provider.get_current_model(),
                "model_health": provider.is_healthy,
                "models": provider.get_available_models()
            }
        
        # Add placeholder for providers not initialized
        for provider_name in ["openai", "claude", "xai", "lm_studio", "ollama"]:
            if provider_name not in status:
                status[provider_name] = {
                    "available": False,
                    "current_model": None,
                    "model_health": False,
                    "models": []
                }
        
        return status
    
    async def health_check_all(self):
        """Perform health check on all providers"""
        tasks = []
        for name, provider in self.providers.items():
            tasks.append(self._check_provider_health(name, provider))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_provider_health(self, name: str, provider):
        """Check health of a single provider"""
        try:
            is_healthy = await provider.health_check()
            provider.is_healthy = is_healthy
            self.logger.info(f"Provider {name} health check: {'✓' if is_healthy else '✗'}")
        except Exception as e:
            provider.is_healthy = False
            self.logger.error(f"Provider {name} health check failed: {e}")

# Global provider manager instance
provider_manager = ProviderManager()