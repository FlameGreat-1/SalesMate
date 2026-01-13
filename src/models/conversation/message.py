from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from .schema import MessageSchema, MessageRole


@dataclass
class Message:
    schema: MessageSchema
    
    def __post_init__(self):
        if not isinstance(self.schema, MessageSchema):
            raise ValueError("Invalid message schema provided")
    
    @property
    def role(self) -> MessageRole:
        return self.schema.role
    
    @property
    def content(self) -> str:
        return self.schema.content
    
    @property
    def timestamp(self) -> datetime:
        return self.schema.timestamp
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return self.schema.metadata.copy()
    
    def is_from_user(self) -> bool:
        return self.role == MessageRole.USER
    
    def is_from_assistant(self) -> bool:
        return self.role == MessageRole.ASSISTANT
    
    def is_system_message(self) -> bool:
        return self.role == MessageRole.SYSTEM
    
    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        return self.schema.metadata.get(key, default)
    
    def get_formatted_timestamp(self, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
        return self.timestamp.strftime(format_string)
    
    def get_display_format(self) -> str:
        role_display = self.role.value.capitalize()
        timestamp_display = self.get_formatted_timestamp()
        return f"[{timestamp_display}] {role_display}: {self.content}"
    
    def to_openai_format(self) -> Dict[str, str]:
        return self.schema.to_openai_format()
    
    @classmethod
    def create_system_message(cls, content: str, metadata: Optional[Dict[str, Any]] = None) -> 'Message':
        schema = MessageSchema(
            role=MessageRole.SYSTEM,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        return cls(schema=schema)
    
    @classmethod
    def create_user_message(cls, content: str, metadata: Optional[Dict[str, Any]] = None) -> 'Message':
        schema = MessageSchema(
            role=MessageRole.USER,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        return cls(schema=schema)
    
    @classmethod
    def create_assistant_message(cls, content: str, metadata: Optional[Dict[str, Any]] = None) -> 'Message':
        schema = MessageSchema(
            role=MessageRole.ASSISTANT,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        return cls(schema=schema)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        schema = MessageSchema.from_dict(data)
        return cls(schema=schema)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.schema.to_dict()
    
    def __str__(self) -> str:
        return self.get_display_format()
    
    def __repr__(self) -> str:
        return f"Message(role={self.role.value}, content={self.content[:50]}...)"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Message):
            return False
        return (self.role == other.role and 
                self.content == other.content and 
                self.timestamp == other.timestamp)
    
    def __hash__(self) -> int:
        return hash((self.role.value, self.content, self.timestamp))
