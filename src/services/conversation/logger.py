import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from src.models.conversation.conversation import Conversation
from src.config.settings import settings


class ConversationLoggerError(Exception):
    pass


class ConversationLogger:
    
    def __init__(self, log_directory: Optional[Path] = None):
        self._log_directory = log_directory or settings.paths.conversations_dir
        self._ensure_log_directory_exists()
    
    def _ensure_log_directory_exists(self) -> None:
        try:
            self._log_directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ConversationLoggerError(f"Failed to create log directory: {str(e)}")
    
    def log_conversation(self, conversation: Conversation) -> Path:
        if not settings.conversation.enable_logging:
            raise ConversationLoggerError("Conversation logging is disabled in settings")
        
        log_format = settings.conversation.log_format
        
        if log_format == "txt":
            return self._log_as_text(conversation)
        elif log_format == "json":
            return self._log_as_json(conversation)
        elif log_format == "csv":
            return self._log_as_csv(conversation)
        else:
            raise ConversationLoggerError(f"Unsupported log format: {log_format}")
    
    def _generate_log_filename(self, conversation: Conversation, extension: str) -> str:
        timestamp = conversation.started_at.strftime("%Y%m%d_%H%M%S")
        return f"conversation_{conversation.conversation_id}_{timestamp}.{extension}"
    
    def _log_as_text(self, conversation: Conversation) -> Path:
        try:
            filename = self._generate_log_filename(conversation, "txt")
            filepath = self._log_directory / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self._format_conversation_header(conversation))
                f.write("\n" + "=" * 80 + "\n\n")
                
                messages = conversation.get_all_messages()
                for message in messages:
                    f.write(message.get_display_format())
                    f.write("\n\n")
                
                f.write("=" * 80 + "\n")
                f.write(self._format_conversation_footer(conversation))
            
            return filepath
            
        except Exception as e:
            raise ConversationLoggerError(f"Failed to log conversation as text: {str(e)}")
    
    def _log_as_json(self, conversation: Conversation) -> Path:
        try:
            filename = self._generate_log_filename(conversation, "json")
            filepath = self._log_directory / filename
            
            conversation_data = conversation.to_dict()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            raise ConversationLoggerError(f"Failed to log conversation as JSON: {str(e)}")
    
    def _log_as_csv(self, conversation: Conversation) -> Path:
        try:
            import csv
            
            filename = self._generate_log_filename(conversation, "csv")
            filepath = self._log_directory / filename
            
            messages = conversation.get_all_messages()
            
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                writer.writerow(['Conversation ID', conversation.conversation_id])
                writer.writerow(['User Persona ID', conversation.user_persona_id])
                writer.writerow(['Status', conversation.status.value])
                writer.writerow(['Started At', conversation.started_at.isoformat()])
                if conversation.ended_at:
                    writer.writerow(['Ended At', conversation.ended_at.isoformat()])
                writer.writerow([])
                
                writer.writerow(['Timestamp', 'Role', 'Content'])
                
                for message in messages:
                    writer.writerow([
                        message.timestamp.isoformat(),
                        message.role.value,
                        message.content
                    ])
            
            return filepath
            
        except Exception as e:
            raise ConversationLoggerError(f"Failed to log conversation as CSV: {str(e)}")
    
    def _format_conversation_header(self, conversation: Conversation) -> str:
        header = f"CONVERSATION LOG\n"
        header += f"Conversation ID: {conversation.conversation_id}\n"
        header += f"User Persona ID: {conversation.user_persona_id}\n"
        header += f"Status: {conversation.status.value}\n"
        header += f"Started: {conversation.started_at.strftime(settings.conversation.timestamp_format)}\n"
        
        if conversation.ended_at:
            header += f"Ended: {conversation.ended_at.strftime(settings.conversation.timestamp_format)}\n"
            duration = conversation.get_duration_seconds()
            if duration:
                header += f"Duration: {duration:.2f} seconds\n"
        
        header += f"Total Messages: {conversation.message_count}\n"
        
        return header
    
    def _format_conversation_footer(self, conversation: Conversation) -> str:
        footer = f"\nConversation Status: {conversation.status.value}\n"
        
        if conversation.ended_at:
            footer += f"Ended at: {conversation.ended_at.strftime(settings.conversation.timestamp_format)}\n"
        
        return footer
    
    def load_conversation_from_json(self, filepath: Path) -> Conversation:
        try:
            if not filepath.exists():
                raise FileNotFoundError(f"Conversation log not found: {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return Conversation.from_dict(data)
            
        except Exception as e:
            raise ConversationLoggerError(f"Failed to load conversation from JSON: {str(e)}")
    
    def get_all_conversation_logs(self, extension: Optional[str] = None) -> list[Path]:
        try:
            if extension:
                pattern = f"conversation_*.{extension}"
            else:
                pattern = "conversation_*.*"
            
            return sorted(self._log_directory.glob(pattern))
            
        except Exception as e:
            raise ConversationLoggerError(f"Failed to retrieve conversation logs: {str(e)}")
    
    def delete_conversation_log(self, filepath: Path) -> bool:
        try:
            if filepath.exists():
                filepath.unlink()
                return True
            return False
            
        except Exception as e:
            raise ConversationLoggerError(f"Failed to delete conversation log: {str(e)}")



