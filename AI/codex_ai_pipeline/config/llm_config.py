from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class LLMConfig:
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p
        }
