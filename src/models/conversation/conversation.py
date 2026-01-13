from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from .schema import ConversationSchema, ConversationStatus
from .message import Message, MessageRole


@dataclass
class Conversation:
    schema: ConversationSchema
    
    def __post_init__(self):
        if not isinstance(self.schema, ConversationSchema):
            raise ValueError("Invalid conversation schema provided")
    
    @property
    def conversation_id(self) -> str:
        return self.schema.conversation_id
    
    @property
    def user_persona_id(self) -> str:
        return self.schema.user_persona_id
    
    @property
    def status(self) -> ConversationStatus:
        return self.schema.status
    
    @property
    def started_at(self) -> datetime:
        return self.schema.started_at
    
    @property
    def ended_at(self) -> Optional[datetime]:
        return self.schema.ended_at
    
    @property
    def message_count(self) -> int:
        return len(self.schema.messages)
    
    @property
    def is_active(self) -> bool:
        return self.status == ConversationStatus.ACTIVE
    
    @property
    def is_completed(self) -> bool:
        return self.status == ConversationStatus.COMPLETED
    
    def get_all_messages(self) -> List[Message]:
        return [Message(schema=msg) for msg in self.schema.messages]
    
    def get_user_messages(self) -> List[Message]:
        return [Message(schema=msg) for msg in self.schema.messages if msg.role == MessageRole.USER]
    
    def get_assistant_messages(self) -> List[Message]:
        return [Message(schema=msg) for msg in self.schema.messages if msg.role == MessageRole.ASSISTANT]
    
    def get_last_n_messages(self, n: int) -> List[Message]:
        if n <= 0:
            return []
        return [Message(schema=msg) for msg in self.schema.messages[-n:]]
    
    def get_context_window(self, window_size: int) -> List[Message]:
        messages = self.get_last_n_messages(window_size)
        return [msg for msg in messages if not msg.is_system_message()]
    
    def get_messages_for_llm(self, context_window_size: int) -> List[Dict[str, str]]:
        context_messages = self.get_context_window(context_window_size)
        return [msg.to_openai_format() for msg in context_messages]
    
    def add_message(self, message: Message) -> None:
        if not self.is_active:
            raise ValueError("Cannot add message to inactive conversation")
        self.schema.messages.append(message.schema)
    
    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        message = Message.create_user_message(content, metadata)
        self.add_message(message)
        return message
    
    def add_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        message = Message.create_assistant_message(content, metadata)
        self.add_message(message)
        return message
    
    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        message = Message.create_system_message(content, metadata)
        self.add_message(message)
        return message
    
    def complete_conversation(self) -> None:
        if not self.is_active:
            raise ValueError("Conversation is already inactive")
        self.schema.status = ConversationStatus.COMPLETED
        self.schema.ended_at = datetime.now()
    
    def abandon_conversation(self) -> None:
        if not self.is_active:
            raise ValueError("Conversation is already inactive")
        self.schema.status = ConversationStatus.ABANDONED
        self.schema.ended_at = datetime.now()
    
    def get_duration_seconds(self) -> Optional[float]:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at).total_seconds()
    
    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        return self.schema.metadata.get(key, default)
    
    def set_metadata_value(self, key: str, value: Any) -> None:
        self.schema.metadata[key] = value
    
    @classmethod
    def create_new(cls, conversation_id: str, user_persona_id: str, metadata: Optional[Dict[str, Any]] = None) -> 'Conversation':
        schema = ConversationSchema(
            conversation_id=conversation_id,
            user_persona_id=user_persona_id,
            messages=[],
            status=ConversationStatus.ACTIVE,
            started_at=datetime.now(),
            metadata=metadata or {}
        )
        return cls(schema=schema)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        schema = ConversationSchema.from_dict(data)
        return cls(schema=schema)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.schema.to_dict()
    
    def __str__(self) -> str:
        return f"Conversation {self.conversation_id} ({self.status.value}) - {self.message_count} messages"
    
    def __repr__(self) -> str:
        return f"Conversation(id={self.conversation_id}, status={self.status.value}, messages={self.message_count})"
