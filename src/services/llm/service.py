from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI, OpenAIError, APIError, APIConnectionError, RateLimitError, APITimeoutError
import time
from src.models.conversation.conversation import Conversation
from src.models.conversation.message import Message
from src.models.user.user import User
from src.models.product.product import Product
from .config import llm_config
from .prompts import SalesPromptBuilder


class LLMServiceError(Exception):
    pass


class LLMService:
    
    def __init__(self):
        self._client = self._initialize_client()
        self._prompt_builder = SalesPromptBuilder()
    
    def _initialize_client(self) -> OpenAI:
        try:
            return OpenAI(api_key=llm_config.api_key)
        except Exception as e:
            raise LLMServiceError(f"Failed to initialize OpenAI client: {str(e)}")
    
    def generate_response(
        self,
        conversation: Conversation,
        user: User,
        available_products: Optional[List[Product]] = None,
        conversation_stage: str = "discovery"
    ) -> str:
        try:
            system_prompt = self._build_system_prompt(user, available_products or [], conversation_stage)
            messages = self._prepare_messages(system_prompt, conversation)
            
            response = self._call_openai_api_with_retry(messages)
            
            return response
        except OpenAIError as e:
            raise LLMServiceError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise LLMServiceError(f"Unexpected error generating response: {str(e)}")
    
    def _build_system_prompt(
        self,
        user: User,
        available_products: List[Product],
        conversation_stage: str
    ) -> str:
        return self._prompt_builder.build_system_prompt(
            user=user,
            available_products=available_products,
            conversation_stage=conversation_stage
        )
    
    def _prepare_messages(
        self,
        system_prompt: str,
        conversation: Conversation
    ) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": system_prompt}]
        
        context_window_size = self._get_context_window_size()
        conversation_messages = conversation.get_messages_for_llm(context_window_size)
        
        messages.extend(conversation_messages)
        
        return messages
    
    def _get_context_window_size(self) -> int:
        from src.config.settings import settings
        return settings.conversation.context_window_messages
    
    def _call_openai_api(self, messages: List[Dict[str, str]]) -> str:
        api_params = llm_config.get_api_params()
        
        try:
            response = self._client.chat.completions.create(
                messages=messages,
                **api_params
            )
            
            if not response.choices:
                raise LLMServiceError("No response choices returned from OpenAI API")
            
            content = response.choices[0].message.content
            
            if not content:
                raise LLMServiceError("Empty content returned from OpenAI API")
            
            return content.strip()
            
        except RateLimitError as e:
            raise LLMServiceError(f"Rate limit exceeded: {str(e)}")
        except APITimeoutError as e:
            raise LLMServiceError(f"API request timed out: {str(e)}")
        except APIConnectionError as e:
            raise LLMServiceError(f"API connection error: {str(e)}")
        except APIError as e:
            raise LLMServiceError(f"API error: {str(e)}")
        except Exception as e:
            raise LLMServiceError(f"Unexpected API error: {str(e)}")
    
    def _call_openai_api_with_retry(self, messages: List[Dict[str, str]]) -> str:
        max_retries = llm_config.max_retries
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                return self._call_openai_api(messages)
            except LLMServiceError as e:
                last_error = str(e)
                
                if 'rate limit' in last_error.lower() and attempt < max_retries:
                    wait_time = (2 ** attempt) + (attempt * 0.5)
                    time.sleep(wait_time)
                    continue
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    raise
        
        raise LLMServiceError(f"Failed after {max_retries} attempts. Last error: {last_error}")
    
    def generate_greeting(self, user: User) -> str:
        try:
            greeting_prompt = self._prompt_builder.build_greeting_prompt(user)
            
            messages = [
                {"role": "system", "content": greeting_prompt},
                {"role": "user", "content": "Hello"}
            ]
            
            response = self._call_openai_api_with_retry(messages)
            return response
            
        except Exception as e:
            raise LLMServiceError(f"Failed to generate greeting: {str(e)}")
    
    def generate_product_recommendation(
        self,
        conversation: Conversation,
        user: User,
        products: List[Product]
    ) -> str:
        try:
            recommendation_prompt = self._prompt_builder.build_recommendation_prompt(user, products)
            
            messages = [{"role": "system", "content": recommendation_prompt}]
            
            context_messages = conversation.get_messages_for_llm(self._get_context_window_size())
            messages.extend(context_messages)
            
            response = self._call_openai_api_with_retry(messages)
            return response
            
        except Exception as e:
            raise LLMServiceError(f"Failed to generate product recommendation: {str(e)}")
    
    def generate_product_comparison(
        self,
        conversation: Conversation,
        user: User,
        products: List[Product]
    ) -> str:
        try:
            comparison_prompt = self._prompt_builder.build_comparison_prompt(user, products)
            
            messages = [{"role": "system", "content": comparison_prompt}]
            
            context_messages = conversation.get_messages_for_llm(self._get_context_window_size())
            messages.extend(context_messages)
            
            response = self._call_openai_api_with_retry(messages)
            return response
            
        except Exception as e:
            raise LLMServiceError(f"Failed to generate product comparison: {str(e)}")
    
    def analyze_user_intent(self, user_message: str) -> Dict[str, Any]:
        try:
            analysis_prompt = """Analyze the user's message and extract:
1. Intent (browsing, asking_question, requesting_recommendation, comparing_products, ready_to_buy, objection)
2. Mentioned product categories or types
3. Budget if mentioned
4. Key requirements or preferences

Respond in this exact format:
Intent: [intent]
Categories: [comma-separated list or "none"]
Budget: [amount or "not mentioned"]
Requirements: [comma-separated list or "none"]"""

            messages = [
                {"role": "system", "content": analysis_prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = self._call_openai_api_with_retry(messages)
            
            return self._parse_intent_analysis(response)
            
        except Exception as e:
            return {
                "intent": "unknown",
                "categories": [],
                "budget": None,
                "requirements": []
            }
    
    def _parse_intent_analysis(self, response: str) -> Dict[str, Any]:
        lines = response.strip().split('\n')
        result = {
            "intent": "unknown",
            "categories": [],
            "budget": None,
            "requirements": []
        }
        
        for line in lines:
            if ':' not in line:
                continue
            
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if key == "intent":
                result["intent"] = value.lower()
            elif key == "categories" and value.lower() != "none":
                result["categories"] = [cat.strip() for cat in value.split(',')]
            elif key == "budget" and value.lower() != "not mentioned":
                try:
                    budget_str = value.replace('$', '').replace(',', '').strip()
                    result["budget"] = float(budget_str)
                except ValueError:
                    pass
            elif key == "requirements" and value.lower() != "none":
                result["requirements"] = [req.strip() for req in value.split(',')]
        
        return result
    
    def validate_api_connection(self) -> bool:
        try:
            test_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
            
            response = self._client.chat.completions.create(
                model=llm_config.model,
                messages=test_messages,
                max_tokens=10
            )
            
            return bool(response.choices)
            
        except Exception:
            return False


