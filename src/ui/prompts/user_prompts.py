from typing import Optional, List
from src.utils.validators.input_validator import InputValidator


class UserPrompts:
    
    @staticmethod
    def get_user_input(prompt: str, allow_empty: bool = False) -> str:
        while True:
            user_input = input(f"\n{prompt}\n> ").strip()
            
            if allow_empty or not InputValidator.is_empty(user_input):
                return user_input
            
            print("Input cannot be empty. Please try again.")
    
    @staticmethod
    def get_yes_no_input(prompt: str, default: Optional[bool] = None) -> bool:
        default_text = ""
        if default is True:
            default_text = " [Y/n]"
        elif default is False:
            default_text = " [y/N]"
        else:
            default_text = " [y/n]"
        
        while True:
            user_input = input(f"\n{prompt}{default_text}\n> ").strip()
            
            if InputValidator.is_empty(user_input) and default is not None:
                return default
            
            result = InputValidator.validate_yes_no(user_input)
            
            if result is not None:
                return result
            
            print("Please enter 'y' for yes or 'n' for no.")
    
    @staticmethod
    def get_menu_choice(prompt: str, max_option: int, allow_back: bool = False) -> int:
        back_text = " (or 0 to go back)" if allow_back else ""
        
        while True:
            user_input = input(f"\n{prompt}{back_text}\n> ").strip()
            
            if allow_back and user_input == "0":
                return 0
            
            choice = InputValidator.validate_menu_choice(user_input, max_option)
            
            if choice is not None:
                return choice
            
            print(f"Please enter a number between 1 and {max_option}.")
    
    @staticmethod
    def get_numeric_input(
        prompt: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> float:
        range_text = ""
        if min_value is not None and max_value is not None:
            range_text = f" ({min_value} - {max_value})"
        elif min_value is not None:
            range_text = f" (minimum: {min_value})"
        elif max_value is not None:
            range_text = f" (maximum: {max_value})"
        
        while True:
            user_input = input(f"\n{prompt}{range_text}\n> ").strip()
            
            if not InputValidator.is_numeric(user_input):
                print("Please enter a valid number.")
                continue
            
            value = float(user_input)
            
            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}.")
                continue
            
            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}.")
                continue
            
            return value
    
    @staticmethod
    def get_integer_input(
        prompt: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> int:
        range_text = ""
        if min_value is not None and max_value is not None:
            range_text = f" ({min_value} - {max_value})"
        elif min_value is not None:
            range_text = f" (minimum: {min_value})"
        elif max_value is not None:
            range_text = f" (maximum: {max_value})"
        
        while True:
            user_input = input(f"\n{prompt}{range_text}\n> ").strip()
            
            if not InputValidator.is_integer(user_input):
                print("Please enter a valid integer.")
                continue
            
            value = int(user_input)
            
            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}.")
                continue
            
            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}.")
                continue
            
            return value
    
    @staticmethod
    def get_choice_from_list(prompt: str, choices: List[str], allow_cancel: bool = False) -> Optional[str]:
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice}")
        
        if allow_cancel:
            print("0. Cancel")
        
        max_option = len(choices)
        
        while True:
            user_input = input("\n> ").strip()
            
            if allow_cancel and user_input == "0":
                return None
            
            choice_num = InputValidator.validate_menu_choice(user_input, max_option)
            
            if choice_num is not None:
                return choices[choice_num - 1]
            
            print(f"Please enter a number between 1 and {max_option}.")
    
    @staticmethod
    def confirm_action(action: str) -> bool:
        return UserPrompts.get_yes_no_input(f"Are you sure you want to {action}?", default=False)
    
    @staticmethod
    def press_enter_to_continue(message: str = "Press Enter to continue...") -> None:
        input(f"\n{message}")
    
    @staticmethod
    def get_conversation_message() -> str:
        user_input = input("\n👤 You: ").strip()
        
        while InputValidator.is_empty(user_input):
            print("Input cannot be empty. Please try again.")
            user_input = input("\n👤 You: ").strip()
        
        return user_input
    
    @staticmethod
    def get_multiline_input(prompt: str, end_marker: str = "END") -> str:
        print(f"\n{prompt}")
        print(f"(Type '{end_marker}' on a new line when finished)\n")
        
        lines = []
        while True:
            line = input()
            if line.strip().upper() == end_marker:
                break
            lines.append(line)
        
        return "\n".join(lines).strip()


user_prompts = UserPrompts()
