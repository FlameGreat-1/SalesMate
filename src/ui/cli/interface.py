from typing import Optional, List
from pathlib import Path
from src.models.user.user import User
from src.models.conversation.conversation import Conversation
from src.models.product.product import Product
from src.services.conversation.service import ConversationService, ConversationServiceError
from src.services.product.service import ProductService
from src.services.product.repository import ProductRepository
from src.utils.file_handler.json_handler import JSONHandler
from src.config.settings import settings
from .menu import CLIMenu
from .formatter import CLIFormatter
from src.ui.prompts.user_prompts import UserPrompts


class CLIInterfaceError(Exception):
    pass


class CLIInterface:
    
    def __init__(self):
        self._conversation_service = ConversationService()
        self._product_service = ProductService()
        self._current_conversation: Optional[Conversation] = None
        self._current_user: Optional[User] = None
        self._personas: List[User] = []
        self._running = True
    
    def start(self) -> None:
        try:
            self._initialize()
            self._display_welcome()
            self._main_loop()
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            self._shutdown()
        except Exception as e:
            print(CLIFormatter.format_error(f"Fatal error: {str(e)}"))
            self._shutdown()
    
    def _initialize(self) -> None:
        try:
            self._load_personas()
            settings.validate()
        except Exception as e:
            raise CLIInterfaceError(f"Initialization failed: {str(e)}")
    
    def _load_personas(self) -> None:
        try:
            personas_data = JSONHandler.read_json(settings.paths.personas_file)
            personas_list = personas_data.get('personas', [])
            
            self._personas = [User.from_dict(persona_data) for persona_data in personas_list]
            
            if not self._personas:
                raise CLIInterfaceError("No personas found in personas file")
                
        except Exception as e:
            raise CLIInterfaceError(f"Failed to load personas: {str(e)}")
    
    def _display_welcome(self) -> None:
        CLIFormatter.clear_screen()
        print(CLIFormatter.format_welcome_banner())
        print(CLIFormatter.format_info("Welcome to your AI-powered sales assistant!"))
        UserPrompts.press_enter_to_continue()
    
    def _main_loop(self) -> None:
        while self._running:
            try:
                CLIFormatter.clear_screen()
                choice = CLIMenu.display_main_menu()
                
                if choice == 1:
                    self._start_new_conversation()
                elif choice == 2:
                    self._view_product_catalog()
                elif choice == 3:
                    self._view_conversation_history()
                elif choice == 4:
                    self._view_settings()
                elif choice == 5:
                    self._exit_application()
                    
            except Exception as e:
                print(CLIFormatter.format_error(f"An error occurred: {str(e)}"))
                UserPrompts.press_enter_to_continue()
    
    def _start_new_conversation(self) -> None:
        CLIFormatter.clear_screen()
        
        selected_user = CLIMenu.display_persona_selection_menu(self._personas)
        
        if not selected_user:
            return
        
        self._current_user = selected_user
        
        try:
            self._current_conversation = self._conversation_service.start_conversation(selected_user)
            
            print(CLIFormatter.format_success(f"Conversation started with {selected_user.name}"))
            print(CLIFormatter.format_user_profile(selected_user))
            UserPrompts.press_enter_to_continue()
            
            if settings.sales.greeting_enabled:
                greeting_messages = self._current_conversation.get_assistant_messages()
                if greeting_messages:
                    CLIFormatter.clear_screen()
                    CLIFormatter.stream_assistant_message(greeting_messages[-1].content)
            
            self._conversation_loop()
            
        except ConversationServiceError as e:
            print(CLIFormatter.format_error(f"Failed to start conversation: {str(e)}"))
            UserPrompts.press_enter_to_continue()
    
    def _conversation_loop(self) -> None:
        while self._current_conversation and self._current_conversation.is_active:
            try:
                user_input = UserPrompts.get_conversation_message()
                
                if user_input.lower() in ['exit', 'quit', 'end']:
                    if CLIMenu.confirm_end_conversation():
                        self._end_conversation()
                        break
                    continue
                
                if user_input.lower() == 'menu':
                    self._handle_conversation_menu()
                    continue
                
                print(CLIFormatter.format_info("Processing..."))
                
                response = self._conversation_service.process_user_message(
                    self._current_conversation,
                    self._current_user,
                    user_input
                )
                
                CLIFormatter.stream_assistant_message(response)
                
            except ConversationServiceError as e:
                print(CLIFormatter.format_error(f"Error processing message: {str(e)}"))
            except KeyboardInterrupt:
                if CLIMenu.confirm_end_conversation():
                    self._end_conversation()
                    break
    
    def _handle_conversation_menu(self) -> None:
        CLIFormatter.clear_screen()
        choice = CLIMenu.display_conversation_menu()
        
        if choice == 1:
            return
        elif choice == 2:
            self._get_product_recommendations()
        elif choice == 3:
            self._view_product_details_in_conversation()
        elif choice == 4:
            self._compare_products_in_conversation()
        elif choice == 5:
            self._view_current_conversation_history()
        elif choice == 6:
            if CLIMenu.confirm_end_conversation():
                self._end_conversation()
    
    def _get_product_recommendations(self) -> None:
        try:
            print(CLIFormatter.format_info("Generating personalized recommendations..."))
            
            response = self._conversation_service.get_product_recommendations(
                self._current_conversation,
                self._current_user
            )
            
            CLIFormatter.stream_assistant_message(response)
            UserPrompts.press_enter_to_continue()
            
        except Exception as e:
            print(CLIFormatter.format_error(f"Failed to get recommendations: {str(e)}"))
            UserPrompts.press_enter_to_continue()
    
    def _view_product_details_in_conversation(self) -> None:
        products = self._product_service.get_recommendations_for_user(self._current_user, limit=10)
        
        selected_product = CLIMenu.display_product_list_menu(products, "Available Products")
        
        if selected_product:
            CLIFormatter.clear_screen()
            print(CLIFormatter.format_product_detailed(selected_product))
            UserPrompts.press_enter_to_continue()
    
    def _compare_products_in_conversation(self) -> None:
        products = self._product_service.get_recommendations_for_user(self._current_user, limit=10)
        
        selected_products = CLIMenu.display_comparison_selection_menu(products)
        
        if len(selected_products) < 2:
            print(CLIFormatter.format_warning("Please select at least 2 products to compare"))
            UserPrompts.press_enter_to_continue()
            return
        
        try:
            product_ids = [p.product_id for p in selected_products]
            
            response = self._conversation_service.compare_products(
                self._current_conversation,
                self._current_user,
                product_ids
            )
            
            CLIFormatter.clear_screen()
            CLIFormatter.stream_assistant_message(response)
            UserPrompts.press_enter_to_continue()
            
        except Exception as e:
            print(CLIFormatter.format_error(f"Failed to compare products: {str(e)}"))
            UserPrompts.press_enter_to_continue()
    
    def _view_current_conversation_history(self) -> None:
        if not self._current_conversation:
            return
        
        CLIFormatter.clear_screen()
        print(CLIFormatter.format_header("Conversation History"))
        
        messages = self._current_conversation.get_all_messages()
        for message in messages:
            if not message.is_system_message():
                print(CLIFormatter.format_message(message))
        
        UserPrompts.press_enter_to_continue()
    
    def _end_conversation(self) -> None:
        if self._current_conversation:
            try:
                self._conversation_service.end_conversation(self._current_conversation)
                
                summary = self._conversation_service.get_conversation_summary(self._current_conversation)
                
                CLIFormatter.clear_screen()
                print(CLIFormatter.format_success("Conversation ended successfully"))
                print(CLIFormatter.format_conversation_summary(summary))
                
                self._current_conversation = None
                self._current_user = None
                
                UserPrompts.press_enter_to_continue()
                
            except Exception as e:
                print(CLIFormatter.format_error(f"Error ending conversation: {str(e)}"))
                UserPrompts.press_enter_to_continue()
    
    def _view_product_catalog(self) -> None:
        while True:
            CLIFormatter.clear_screen()
            choice = CLIMenu.display_product_catalog_menu()
            
            if choice == 1:
                self._view_all_products()
            elif choice == 2:
                self._browse_by_category()
            elif choice == 3:
                self._browse_by_brand()
            elif choice == 4:
                self._view_featured_products()
            elif choice == 5:
                self._view_products_on_sale()
            elif choice == 6:
                self._search_products()
            elif choice == 7:
                break
    
    def _view_all_products(self) -> None:
        products = self._product_service.get_all_products()
        self._display_product_list(products, "All Products")
    
    def _browse_by_category(self) -> None:
        categories = self._product_service.get_available_categories()
        selected_category = CLIMenu.display_category_selection_menu(categories)
        
        if selected_category:
            products = self._product_service.search_products(category=selected_category)
            self._display_product_list(products, f"Products in {selected_category.title()}")
    
    def _browse_by_brand(self) -> None:
        brands = self._product_service.get_available_brands()
        selected_brand = CLIMenu.display_brand_selection_menu(brands)
        
        if selected_brand:
            products = self._product_service.search_products(brand=selected_brand)
            self._display_product_list(products, f"Products by {selected_brand}")
    
    def _view_featured_products(self) -> None:
        products = self._product_service.get_featured_products()
        self._display_product_list(products, "Featured Products")
    
    def _view_products_on_sale(self) -> None:
        products = self._product_service.get_products_on_sale()
        self._display_product_list(products, "Products on Sale")
    
    def _search_products(self) -> None:
        print(CLIFormatter.format_info("Search functionality - Enter search criteria"))
        UserPrompts.press_enter_to_continue()
    
    def _display_product_list(self, products: List[Product], title: str) -> None:
        while True:
            selected_product = CLIMenu.display_product_list_menu(products, title)
            
            if not selected_product:
                break
            
            self._display_product_details(selected_product)
    
    def _display_product_details(self, product: Product) -> None:
        CLIFormatter.clear_screen()
        print(CLIFormatter.format_product_detailed(product))
        UserPrompts.press_enter_to_continue()
    
    def _view_conversation_history(self) -> None:
        log_files = self._conversation_service._logger.get_all_conversation_logs()
        
        if not log_files:
            print(CLIFormatter.format_info("No conversation history found"))
            UserPrompts.press_enter_to_continue()
            return
        
        file_names = [f.name for f in log_files]
        
        selected_index = CLIMenu.display_conversation_history_menu(file_names)
        
        if selected_index is not None:
            self._display_conversation_log(log_files[selected_index])
    
    def _display_conversation_log(self, log_file: Path) -> None:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            CLIFormatter.clear_screen()
            print(content)
            UserPrompts.press_enter_to_continue()
            
        except Exception as e:
            print(CLIFormatter.format_error(f"Failed to read log file: {str(e)}"))
            UserPrompts.press_enter_to_continue()
    
    def _view_settings(self) -> None:
        while True:
            CLIFormatter.clear_screen()
            choice = CLIMenu.display_settings_menu()
            
            if choice == 1:
                self._display_current_settings()
            elif choice == 2:
                self._toggle_conversation_logging()
            elif choice == 3:
                self._change_log_format()
            elif choice == 4:
                self._display_system_information()
            elif choice == 5:
                break
    
    def _display_current_settings(self) -> None:
        CLIFormatter.clear_screen()
        print(CLIFormatter.format_header("Current Settings"))
        
        config = settings.get_config_dict()
        
        for section, values in config.items():
            print(f"\n{section.upper()}:")
            for key, value in values.items():
                print(f"  {key}: {value}")
        
        UserPrompts.press_enter_to_continue()
    
    def _toggle_conversation_logging(self) -> None:
        current_status = settings.conversation.enable_logging
        print(f"\nConversation logging is currently: {'ENABLED' if current_status else 'DISABLED'}")
        print(CLIFormatter.format_warning("Note: This setting cannot be changed at runtime"))
        UserPrompts.press_enter_to_continue()
    
    def _change_log_format(self) -> None:
        print(f"\nCurrent log format: {settings.conversation.log_format}")
        print(CLIFormatter.format_warning("Note: This setting cannot be changed at runtime"))
        UserPrompts.press_enter_to_continue()
    
    def _display_system_information(self) -> None:
        CLIFormatter.clear_screen()
        print(CLIFormatter.format_header("System Information"))
        
        print(f"\nApplication: {settings.app.app_name}")
        print(f"Version: {settings.app.version}")
        print(f"Environment: {settings.app.environment}")
        print(f"Debug Mode: {settings.app.debug}")
        
        print(f"\nLLM Model: {settings.openai.model}")
        print(f"Temperature: {settings.openai.temperature}")
        
        print(f"\nTotal Products: {self._product_service._repository.get_product_count()}")
        print(f"Total Personas: {len(self._personas)}")
        
        UserPrompts.press_enter_to_continue()
    
    def _exit_application(self) -> None:
        if CLIMenu.confirm_exit():
            self._shutdown()
    
    def _shutdown(self) -> None:
        if self._current_conversation and self._current_conversation.is_active:
            print(CLIFormatter.format_warning("Active conversation detected"))
            if UserPrompts.get_yes_no_input("Save conversation before exiting?", default=True):
                self._end_conversation()
        
        CLIFormatter.clear_screen()
        print(CLIFormatter.format_goodbye_message())
        self._running = False
