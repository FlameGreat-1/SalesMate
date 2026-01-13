from typing import List, Optional, Callable
from src.models.user.user import User
from src.models.product.product import Product
from .formatter import CLIFormatter
from src.ui.prompts.user_prompts import UserPrompts


class MenuOption:
    
    def __init__(self, label: str, action: Callable, description: Optional[str] = None):
        self.label = label
        self.action = action
        self.description = description


class Menu:
    
    def __init__(self, title: str, options: List[MenuOption]):
        self.title = title
        self.options = options
    
    def display(self) -> None:
        option_labels = [opt.label for opt in self.options]
        print(CLIFormatter.format_menu(self.title, option_labels))
    
    def get_user_choice(self) -> int:
        return UserPrompts.get_menu_choice("Select an option", len(self.options))
    
    def execute_choice(self, choice: int) -> None:
        if 1 <= choice <= len(self.options):
            self.options[choice - 1].action()
        else:
            print(CLIFormatter.format_error("Invalid choice"))


class CLIMenu:
    
    @staticmethod
    def display_main_menu() -> int:
        options = [
            "Start New Conversation",
            "View Product Catalog",
            "View Conversation History",
            "Settings",
            "Exit"
        ]
        
        print(CLIFormatter.format_menu("Main Menu", options))
        return UserPrompts.get_menu_choice("Select an option", len(options))
    
    @staticmethod
    def display_persona_selection_menu(personas: List[User]) -> Optional[User]:
        if not personas:
            print(CLIFormatter.format_error("No personas available"))
            return None
        
        print(CLIFormatter.format_header("Select Customer Persona"))
        
        for i, persona in enumerate(personas, 1):
            print(f"\n{i}. {persona.name}")
            print(f"   Age: {persona.age} | Occupation: {persona.occupation}")
            print(f"   Tech Level: {persona.tech_savviness.value}")
            print(f"   Budget: ${persona.budget_min} - ${persona.budget_max}")
        
        print(f"\n0. Cancel")
        
        choice = UserPrompts.get_menu_choice("Select a persona", len(personas), allow_back=True)
        
        if choice == 0:
            return None
        
        return personas[choice - 1]
    
    @staticmethod
    def display_conversation_menu() -> int:
        options = [
            "Continue Conversation",
            "Get Product Recommendations",
            "View Product Details",
            "Compare Products",
            "View Conversation History",
            "End Conversation"
        ]
        
        print(CLIFormatter.format_menu("Conversation Menu", options))
        return UserPrompts.get_menu_choice("Select an option", len(options))
    
    @staticmethod
    def display_product_catalog_menu() -> int:
        options = [
            "View All Products",
            "Browse by Category",
            "Browse by Brand",
            "View Featured Products",
            "View Products on Sale",
            "Search Products",
            "Back to Main Menu"
        ]
        
        print(CLIFormatter.format_menu("Product Catalog", options))
        return UserPrompts.get_menu_choice("Select an option", len(options))
    
    @staticmethod
    def display_product_list_menu(products: List[Product], title: str = "Products") -> Optional[Product]:
        if not products:
            print(CLIFormatter.format_info("No products found"))
            return None
        
        print(CLIFormatter.format_header(title))
        print(CLIFormatter.format_product_list(products, numbered=True))
        
        print("\n0. Back")
        
        choice = UserPrompts.get_menu_choice("Select a product to view details", len(products), allow_back=True)
        
        if choice == 0:
            return None
        
        return products[choice - 1]
    
    @staticmethod
    def display_product_details_menu(product: Product) -> int:
        print(CLIFormatter.format_product_detailed(product))
        
        options = [
            "View Similar Products",
            "Add to Conversation Context",
            "Back"
        ]
        
        print("\n")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        return UserPrompts.get_menu_choice("Select an option", len(options))
    
    @staticmethod
    def display_category_selection_menu(categories: List[str]) -> Optional[str]:
        if not categories:
            print(CLIFormatter.format_error("No categories available"))
            return None
        
        print(CLIFormatter.format_header("Select Category"))
        
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category.replace('_', ' ').title()}")
        
        print("0. Cancel")
        
        choice = UserPrompts.get_menu_choice("Select a category", len(categories), allow_back=True)
        
        if choice == 0:
            return None
        
        return categories[choice - 1]
    
    @staticmethod
    def display_brand_selection_menu(brands: List[str]) -> Optional[str]:
        if not brands:
            print(CLIFormatter.format_error("No brands available"))
            return None
        
        print(CLIFormatter.format_header("Select Brand"))
        
        for i, brand in enumerate(brands, 1):
            print(f"{i}. {brand}")
        
        print("0. Cancel")
        
        choice = UserPrompts.get_menu_choice("Select a brand", len(brands), allow_back=True)
        
        if choice == 0:
            return None
        
        return brands[choice - 1]
    
    @staticmethod
    def display_settings_menu() -> int:
        options = [
            "View Current Settings",
            "Toggle Conversation Logging",
            "Change Log Format",
            "View System Information",
            "Back to Main Menu"
        ]
        
        print(CLIFormatter.format_menu("Settings", options))
        return UserPrompts.get_menu_choice("Select an option", len(options))
    
    @staticmethod
    def display_conversation_history_menu(conversation_files: List[str]) -> Optional[int]:
        if not conversation_files:
            print(CLIFormatter.format_info("No conversation history found"))
            return None
        
        print(CLIFormatter.format_header("Conversation History"))
        
        for i, filename in enumerate(conversation_files, 1):
            print(f"{i}. {filename}")
        
        print("0. Back")
        
        choice = UserPrompts.get_menu_choice("Select a conversation to view", len(conversation_files), allow_back=True)
        
        if choice == 0:
            return None
        
        return choice - 1
    
    @staticmethod
    def display_comparison_selection_menu(products: List[Product]) -> List[Product]:
        if not products:
            print(CLIFormatter.format_error("No products available for comparison"))
            return []
        
        print(CLIFormatter.format_header("Select Products to Compare"))
        print(CLIFormatter.format_info("You can select 2-4 products for comparison"))
        print(CLIFormatter.format_product_list(products, numbered=True))
        
        selected_products = []
        
        while len(selected_products) < 4:
            if selected_products:
                print(f"\nCurrently selected: {len(selected_products)} product(s)")
                for p in selected_products:
                    print(f"  • {p.name}")
            
            print("\nEnter product number (or 0 when done):")
            choice = UserPrompts.get_menu_choice("", len(products), allow_back=True)
            
            if choice == 0:
                break
            
            selected_product = products[choice - 1]
            
            if selected_product in selected_products:
                print(CLIFormatter.format_warning("Product already selected"))
                continue
            
            selected_products.append(selected_product)
            
            if len(selected_products) >= 2:
                if not UserPrompts.get_yes_no_input("Add another product?", default=False):
                    break
        
        return selected_products
    
    @staticmethod
    def confirm_exit() -> bool:
        return UserPrompts.get_yes_no_input("Are you sure you want to exit?", default=False)
    
    @staticmethod
    def confirm_end_conversation() -> bool:
        return UserPrompts.get_yes_no_input("Are you sure you want to end this conversation?", default=False)


cli_menu = CLIMenu()
