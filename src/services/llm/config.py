from dataclasses import dataclass
from typing import Dict, Any
from src.config.settings import settings


@dataclass
class LLMConfig:
    
    @property
    def api_key(self) -> str:
        return settings.openai.api_key
    
    @property
    def model(self) -> str:
        return settings.openai.model
    
    @property
    def temperature(self) -> float:
        return settings.openai.temperature
    
    @property
    def max_tokens(self) -> int:
        return settings.openai.max_tokens
    
    @property
    def top_p(self) -> float:
        return settings.openai.top_p
    
    @property
    def frequency_penalty(self) -> float:
        return settings.openai.frequency_penalty
    
    @property
    def presence_penalty(self) -> float:
        return settings.openai.presence_penalty
    
    @property
    def timeout(self) -> int:
        return settings.openai.timeout
    
    @property
    def max_retries(self) -> int:
        return settings.openai.max_retries
    
    def get_api_params(self) -> Dict[str, Any]:
        return {
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty
        }
    
    def get_client_config(self) -> Dict[str, Any]:
        return {
            'api_key': self.api_key,
            'timeout': self.timeout,
            'max_retries': self.max_retries
        }


llm_config = LLMConfig()
