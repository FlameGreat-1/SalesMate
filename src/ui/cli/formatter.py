from typing import List, Optional
from datetime import datetime
import re
import time
from src.models.product.product import Product
from src.models.user.user import User
from src.models.conversation.message import Message
from src.config.settings import settings


class CLIFormatter:
    
    BORDER_CHAR = "="
    SEPARATOR_CHAR = "-"
    BORDER_LENGTH = 80
    
    @staticmethod
    def format_header(title: str) -> str:
        border = CLIFormatter.BORDER_CHAR * CLIFormatter.BORDER_LENGTH
        padding = (CLIFormatter.BORDER_LENGTH - len(title) - 2) // 2
        centered_title = " " * padding + title + " " * padding
        
        return f"\n{border}\n{centered_title}\n{border}\n"
    
    @staticmethod
    def format_section(title: str) -> str:
        separator = CLIFormatter.SEPARATOR_CHAR * CLIFormatter.BORDER_LENGTH
        return f"\n{separator}\n{title}\n{separator}\n"
    
    @staticmethod
    def format_message(message: Message, show_timestamp: bool = True) -> str:
        role_display = {
            "user": "👤 You",
            "assistant": "SalesMate",
            "system": "System"
        }
        
        role = role_display.get(message.role.value, message.role.value.capitalize())
        
        if show_timestamp:
            timestamp = message.get_formatted_timestamp(settings.conversation.timestamp_format)
            return f"[{timestamp}] {role}: {message.content}"
        else:
            return f"{role}: {message.content}"
    
    @staticmethod
    def strip_markdown(content: str) -> str:
        clean_content = content
        clean_content = re.sub(r'^#{1,6}\s+', '', clean_content, flags=re.MULTILINE)
        clean_content = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_content)
        clean_content = re.sub(r'__(.+?)__', r'\1', clean_content)
        clean_content = re.sub(r'\*(.+?)\*', r'\1', clean_content)
        clean_content = re.sub(r'_(.+?)_', r'\1', clean_content)
        clean_content = re.sub(r'`(.+?)`', r'\1', clean_content)
        clean_content = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', clean_content)
        clean_content = re.sub(r'^\s*[-*+]\s+', '• ', clean_content, flags=re.MULTILINE)
        clean_content = re.sub(r'^\s*\d+\.\s+', '', clean_content, flags=re.MULTILINE)
        
        return clean_content
    
    @staticmethod
    def stream_assistant_message(content: str) -> None:
        print("\nSalesMate: ", end='', flush=True)
        
        clean_content = CLIFormatter.strip_markdown(content)
        
        for char in clean_content:
            print(char, end='', flush=True)
            time.sleep(0.001)
        
        print("\n")
    
    @staticmethod
    def format_assistant_message(content: str) -> str:
        return f"\nSalesMate: {content}\n"
    
    @staticmethod
    def format_user_message(content: str) -> str:
        return f"\n👤 You: {content}\n"
    
    @staticmethod
    def format_product_summary(product: Product) -> str:
        summary = f"\n{product.name}"
        summary += f"\n  Brand: {product.brand}"
        summary += f"\n  Category: {product.category}"
        summary += f"\n  Price: {product.get_formatted_price()}"
        
        if product.is_on_sale:
            summary += f" (Save {product.get_formatted_savings()} - {product.discount_percentage}% OFF!)"
        
        summary += f"\n  Rating: {product.rating}/5.0 ({product.review_count} reviews)"
        summary += f"\n  Stock: {product.stock_status.value.replace('_', ' ').title()}"
        
        return summary
    
    @staticmethod
    def format_product_detailed(product: Product) -> str:
        details = CLIFormatter.format_section(product.name)
        
        details += f"\nBrand: {product.brand}"
        details += f"\nManufacturer: {product.manufacturer}"
        details += f"\nCategory: {product.category} > {product.subcategory}"
        details += f"\nSKU: {product.sku}"
        
        details += f"\n\nPricing:"
        details += f"\n  Current Price: {product.get_formatted_price()}"
        if product.is_on_sale:
            details += f"\n  Original Price: {product.get_formatted_original_price()}"
            details += f"\n  Discount: {product.discount_percentage}%"
            details += f"\n  You Save: {product.get_formatted_savings()}"
        
        details += f"\n\nRating: {product.rating}/5.0 ({product.review_count} reviews)"
        details += f"\nStock Status: {product.stock_status.value.replace('_', ' ').title()}"
        
        details += f"\n\nDescription:\n{product.description}"
        
        details += f"\n\nKey Features:"
        for feature in product.features[:5]:
            details += f"\n  • {feature}"
        
        details += f"\n\nWarranty: {product.warranty_months} months"
        details += f"\nReturn Policy: {product.return_policy_days} days"
        
        if product.included_accessories:
            details += f"\n\nIncluded Accessories:"
            for accessory in product.included_accessories:
                details += f"\n  • {accessory}"
        
        return details
    
    @staticmethod
    def format_product_list(products: List[Product], numbered: bool = True) -> str:
        if not products:
            return "\nNo products available."
        
        result = ""
        for i, product in enumerate(products, 1):
            if numbered:
                result += f"\n{i}. {product.name}"
            else:
                result += f"\n• {product.name}"
            
            result += f"\n   {product.get_formatted_price()}"
            if product.is_on_sale:
                result += f" (Save {product.discount_percentage}%)"
            result += f" - Rating: {product.rating}/5.0"
            result += "\n"
        
        return result
    
    @staticmethod
    def format_user_profile(user: User) -> str:
        profile = CLIFormatter.format_section(f"Customer Profile: {user.name}")
        
        profile += f"\nAge: {user.age} ({user.age_group.value})"
        profile += f"\nOccupation: {user.occupation}"
        profile += f"\nTech Savviness: {user.tech_savviness.value.replace('_', ' ').title()}"
        
        profile += f"\n\nBudget Range: ${user.budget_min} - ${user.budget_max}"
        profile += f"\nPreferred Budget: ${user.budget_sweet_spot}"
        
        profile += f"\n\nInterests:"
        for interest in user.categories_of_interest[:5]:
            profile += f"\n  • {interest.replace('_', ' ').title()}"
        
        profile += f"\n\nValues:"
        for value in user.key_features_valued[:5]:
            profile += f"\n  • {value.replace('_', ' ').title()}"
        
        return profile
    
    @staticmethod
    def format_conversation_summary(summary: dict) -> str:
        result = CLIFormatter.format_section("Conversation Summary")
        
        result += f"\nConversation ID: {summary['conversation_id']}"
        result += f"\nStatus: {summary['status'].title()}"
        result += f"\nStarted: {summary['started_at']}"
        
        if summary.get('ended_at'):
            result += f"\nEnded: {summary['ended_at']}"
        
        if summary.get('duration_seconds'):
            duration = summary['duration_seconds']
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            result += f"\nDuration: {minutes}m {seconds}s"
        
        result += f"\n\nTotal Messages: {summary['total_messages']}"
        result += f"\nUser Messages: {summary['user_messages']}"
        result += f"\nAssistant Messages: {summary['assistant_messages']}"
        
        return result
    
    @staticmethod
    def format_menu(title: str, options: List[str]) -> str:
        menu = CLIFormatter.format_header(title)
        
        for i, option in enumerate(options, 1):
            menu += f"{i}. {option}\n"
        
        return menu
    
    @staticmethod
    def format_error(error_message: str) -> str:
        border = "!" * CLIFormatter.BORDER_LENGTH
        return f"\n{border}\nERROR: {error_message}\n{border}\n"
    
    @staticmethod
    def format_success(success_message: str) -> str:
        border = "✓" * CLIFormatter.BORDER_LENGTH
        return f"\n{border}\nSUCCESS: {success_message}\n{border}\n"
    
    @staticmethod
    def format_warning(warning_message: str) -> str:
        border = "⚠" * CLIFormatter.BORDER_LENGTH
        return f"\n{border}\nWARNING: {warning_message}\n{border}\n"
    
    @staticmethod
    def format_info(info_message: str) -> str:
        return f"\nℹ {info_message}\n"
    
    @staticmethod
    def clear_screen() -> None:
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def format_welcome_banner() -> str:
        app_name = settings.app.app_name
        version = settings.app.version
        
        banner = CLIFormatter.BORDER_CHAR * CLIFormatter.BORDER_LENGTH
        banner += f"\n{' ' * 20}{app_name} - AI Sales Assistant"
        banner += f"\n{' ' * 30}Version {version}"
        banner += f"\n{CLIFormatter.BORDER_CHAR * CLIFormatter.BORDER_LENGTH}\n"
        
        return banner
    
    @staticmethod
    def format_goodbye_message() -> str:
        return CLIFormatter.format_header("Thank you for using SalesMate!")


cli_formatter = CLIFormatter()
