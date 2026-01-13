import re
from typing import Optional, List
from decimal import Decimal, InvalidOperation


class InputValidator:
    
    @staticmethod
    def is_empty(value: str) -> bool:
        return not value or not value.strip()
    
    @staticmethod
    def is_valid_length(value: str, min_length: int = 1, max_length: Optional[int] = None) -> bool:
        if InputValidator.is_empty(value):
            return False
        length = len(value.strip())
        if length < min_length:
            return False
        if max_length is not None and length > max_length:
            return False
        return True
    
    @staticmethod
    def is_numeric(value: str) -> bool:
        if InputValidator.is_empty(value):
            return False
        try:
            float(value.strip())
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_integer(value: str) -> bool:
        if InputValidator.is_empty(value):
            return False
        try:
            int(value.strip())
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_positive_number(value: str) -> bool:
        if not InputValidator.is_numeric(value):
            return False
        return float(value.strip()) > 0
    
    @staticmethod
    def is_in_range(value: str, min_value: float, max_value: float) -> bool:
        if not InputValidator.is_numeric(value):
            return False
        num = float(value.strip())
        return min_value <= num <= max_value
    
    @staticmethod
    def is_valid_choice(value: str, valid_choices: List[str], case_sensitive: bool = False) -> bool:
        if InputValidator.is_empty(value):
            return False
        cleaned_value = value.strip()
        if case_sensitive:
            return cleaned_value in valid_choices
        return cleaned_value.lower() in [choice.lower() for choice in valid_choices]
    
    @staticmethod
    def sanitize_input(value: str) -> str:
        if InputValidator.is_empty(value):
            return ""
        return value.strip()
    
    @staticmethod
    def validate_yes_no(value: str) -> Optional[bool]:
        if InputValidator.is_empty(value):
            return None
        cleaned = value.strip().lower()
        if cleaned in ['y', 'yes', 'yeah', 'yep', 'sure', 'ok', 'okay']:
            return True
        if cleaned in ['n', 'no', 'nope', 'nah']:
            return False
        return None
    
    @staticmethod
    def validate_menu_choice(value: str, max_option: int) -> Optional[int]:
        if not InputValidator.is_integer(value):
            return None
        choice = int(value.strip())
        if 1 <= choice <= max_option:
            return choice
        return None
    
    @staticmethod
    def validate_price(value: str) -> Optional[Decimal]:
        if InputValidator.is_empty(value):
            return None
        try:
            price = Decimal(value.strip())
            if price < 0:
                return None
            return price
        except InvalidOperation:
            return None
    
    @staticmethod
    def contains_only_alphanumeric(value: str, allow_spaces: bool = False) -> bool:
        if InputValidator.is_empty(value):
            return False
        pattern = r'^[a-zA-Z0-9\s]+$' if allow_spaces else r'^[a-zA-Z0-9]+$'
        return bool(re.match(pattern, value.strip()))
    
    @staticmethod
    def validate_non_empty(value: str, field_name: str = "Input") -> str:
        if InputValidator.is_empty(value):
            raise ValueError(f"{field_name} cannot be empty")
        return value.strip()
    
    @staticmethod
    def validate_length(value: str, min_length: int, max_length: int, field_name: str = "Input") -> str:
        cleaned = InputValidator.validate_non_empty(value, field_name)
        if not InputValidator.is_valid_length(cleaned, min_length, max_length):
            raise ValueError(f"{field_name} must be between {min_length} and {max_length} characters")
        return cleaned
    
    @staticmethod
    def validate_numeric_input(value: str, field_name: str = "Input") -> float:
        if not InputValidator.is_numeric(value):
            raise ValueError(f"{field_name} must be a valid number")
        return float(value.strip())
    
    @staticmethod
    def validate_integer_input(value: str, field_name: str = "Input") -> int:
        if not InputValidator.is_integer(value):
            raise ValueError(f"{field_name} must be a valid integer")
        return int(value.strip())
    
    @staticmethod
    def validate_range_input(value: str, min_value: float, max_value: float, field_name: str = "Input") -> float:
        num = InputValidator.validate_numeric_input(value, field_name)
        if not min_value <= num <= max_value:
            raise ValueError(f"{field_name} must be between {min_value} and {max_value}")
        return num
