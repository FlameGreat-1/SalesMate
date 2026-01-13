from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ConversationStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


@dataclass
class MessageSchema:
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty")
        if not isinstance(self.timestamp, datetime):
            raise ValueError("Timestamp must be a datetime object")
        if not isinstance(self.metadata, dict):
            raise ValueError("Metadata must be a dictionary")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageSchema':
        return cls(
            role=MessageRole(data['role']),
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp'],
            metadata=data.get('metadata', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'role': self.role.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    def to_openai_format(self) -> Dict[str, str]:
        return {
            'role': self.role.value,
            'content': self.content
        }


@dataclass
class ConversationSchema:
    conversation_id: str
    user_persona_id: str
    messages: List[MessageSchema]
    status: ConversationStatus
    started_at: datetime
    ended_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.conversation_id or not self.conversation_id.strip():
            raise ValueError("Conversation ID is required")
        if not self.user_persona_id or not self.user_persona_id.strip():
            raise ValueError("User persona ID is required")
        if not isinstance(self.messages, list):
            raise ValueError("Messages must be a list")
        if not isinstance(self.started_at, datetime):
            raise ValueError("Started at must be a datetime object")
        if self.ended_at is not None and not isinstance(self.ended_at, datetime):
            raise ValueError("Ended at must be a datetime object or None")
        if self.ended_at is not None and self.ended_at < self.started_at:
            raise ValueError("End time cannot be before start time")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSchema':
        messages = [MessageSchema.from_dict(msg) for msg in data.get('messages', [])]
        
        return cls(
            conversation_id=data['conversation_id'],
            user_persona_id=data['user_persona_id'],
            messages=messages,
            status=ConversationStatus(data['status']),
            started_at=datetime.fromisoformat(data['started_at']) if isinstance(data['started_at'], str) else data['started_at'],
            ended_at=datetime.fromisoformat(data['ended_at']) if data.get('ended_at') and isinstance(data['ended_at'], str) else data.get('ended_at'),
            metadata=data.get('metadata', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'conversation_id': self.conversation_id,
            'user_persona_id': self.user_persona_id,
            'messages': [msg.to_dict() for msg in self.messages],
            'status': self.status.value,
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'metadata': self.metadata
        }
