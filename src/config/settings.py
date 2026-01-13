import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@dataclass
class OpenAIConfig:
    api_key: str
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60
    max_retries: int = 3
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        if not self.api_key.startswith(('sk-', 'sk-proj-')):
            raise ValueError("Invalid OpenAI API key format.")


@dataclass
class PathConfig:
    base_dir: Path = field(default_factory=lambda: BASE_DIR)
    data_dir: Path = field(init=False)
    products_file: Path = field(init=False)
    personas_file: Path = field(init=False)
    logs_dir: Path = field(init=False)
    conversations_dir: Path = field(init=False)
    
    def __post_init__(self):
        self.data_dir = self.base_dir / "data"
        self.products_file = self.data_dir / "products" / "products.json"
        self.personas_file = self.data_dir / "personas" / "personas.json"
        self.logs_dir = self.base_dir / "logs"
        self.conversations_dir = self.logs_dir / "conversations"
        
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self):
        self.conversations_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class ConversationConfig:
    max_history_length: int = 20
    context_window_messages: int = 10
    enable_logging: bool = True
    log_format: str = "txt"
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    session_timeout_minutes: int = 30
    
    def __post_init__(self):
        if self.max_history_length < 1:
            raise ValueError("max_history_length must be at least 1")
        if self.context_window_messages < 1:
            raise ValueError("context_window_messages must be at least 1")
        if self.log_format not in ["txt", "json", "csv"]:
            raise ValueError("log_format must be one of: txt, json, csv")


@dataclass
class SalesConfig:
    greeting_enabled: bool = True
    product_recommendation_limit: int = 50
    enable_product_comparison: bool = True
    enable_price_discussion: bool = True
    enable_upselling: bool = True
    enable_cross_selling: bool = True
    min_confidence_threshold: float = 0.6
    
    def __post_init__(self):
        if self.product_recommendation_limit < 1:
            raise ValueError("product_recommendation_limit must be at least 1")
        if not 0.0 <= self.min_confidence_threshold <= 1.0:
            raise ValueError("min_confidence_threshold must be between 0.0 and 1.0")


@dataclass
class ApplicationConfig:
    app_name: str = "SalesMate"
    version: str = "1.0.0"
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    
    def __post_init__(self):
        if self.environment not in ["development", "staging", "production"]:
            raise ValueError("environment must be one of: development, staging, production")
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("log_level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")


class Settings:
    _instance: Optional['Settings'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.app = ApplicationConfig()
        self.openai = OpenAIConfig(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
            top_p=float(os.getenv("OPENAI_TOP_P", "0.9")),
            frequency_penalty=float(os.getenv("OPENAI_FREQUENCY_PENALTY", "0.0")),
            presence_penalty=float(os.getenv("OPENAI_PRESENCE_PENALTY", "0.0")),
            timeout=int(os.getenv("OPENAI_TIMEOUT", "60")),
            max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "3"))
        )
        self.paths = PathConfig()
        self.conversation = ConversationConfig(
            max_history_length=int(os.getenv("MAX_HISTORY_LENGTH", "20")),
            context_window_messages=int(os.getenv("CONTEXT_WINDOW_MESSAGES", "10")),
            enable_logging=os.getenv("ENABLE_LOGGING", "True").lower() == "true",
            log_format=os.getenv("LOG_FORMAT", "txt"),
            timestamp_format=os.getenv("TIMESTAMP_FORMAT", "%Y-%m-%d %H:%M:%S"),
            session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
        )
        self.sales = SalesConfig(
            greeting_enabled=os.getenv("GREETING_ENABLED", "True").lower() == "true",
            product_recommendation_limit=int(os.getenv("PRODUCT_RECOMMENDATION_LIMIT", "50")),
            enable_product_comparison=os.getenv("ENABLE_PRODUCT_COMPARISON", "True").lower() == "true",
            enable_price_discussion=os.getenv("ENABLE_PRICE_DISCUSSION", "True").lower() == "true",
            enable_upselling=os.getenv("ENABLE_UPSELLING", "True").lower() == "true",
            enable_cross_selling=os.getenv("ENABLE_CROSS_SELLING", "True").lower() == "true",
            min_confidence_threshold=float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.6"))
        )
        
        self._initialized = True
    
    def get_config_dict(self) -> Dict[str, Any]:
        return {
            "app": {
                "name": self.app.app_name,
                "version": self.app.version,
                "environment": self.app.environment,
                "debug": self.app.debug,
                "log_level": self.app.log_level
            },
            "openai": {
                "model": self.openai.model,
                "temperature": self.openai.temperature,
                "max_tokens": self.openai.max_tokens,
                "top_p": self.openai.top_p,
                "frequency_penalty": self.openai.frequency_penalty,
                "presence_penalty": self.openai.presence_penalty,
                "timeout": self.openai.timeout,
                "max_retries": self.openai.max_retries
            },
            "conversation": {
                "max_history_length": self.conversation.max_history_length,
                "context_window_messages": self.conversation.context_window_messages,
                "enable_logging": self.conversation.enable_logging,
                "log_format": self.conversation.log_format,
                "session_timeout_minutes": self.conversation.session_timeout_minutes
            },
            "sales": {
                "greeting_enabled": self.sales.greeting_enabled,
                "product_recommendation_limit": self.sales.product_recommendation_limit,
                "enable_product_comparison": self.sales.enable_product_comparison,
                "enable_price_discussion": self.sales.enable_price_discussion,
                "enable_upselling": self.sales.enable_upselling,
                "enable_cross_selling": self.sales.enable_cross_selling,
                "min_confidence_threshold": self.sales.min_confidence_threshold
            }
        }
    
    def validate(self) -> bool:
        try:
            assert self.paths.products_file.exists(), f"Products file not found: {self.paths.products_file}"
            assert self.paths.personas_file.exists(), f"Personas file not found: {self.paths.personas_file}"
            assert self.paths.conversations_dir.exists(), f"Conversations directory not found: {self.paths.conversations_dir}"
            return True
        except AssertionError as e:
            raise RuntimeError(f"Configuration validation failed: {str(e)}")


settings = Settings()
