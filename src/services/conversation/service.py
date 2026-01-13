from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from src.models.conversation.conversation import Conversation
from src.models.user.user import User
from src.models.product.product import Product
from src.services.llm.service import LLMService, LLMServiceError
from src.services.product.service import ProductService
from .logger import ConversationLogger, ConversationLoggerError
from src.config.settings import settings


class ConversationServiceError(Exception):
    pass


class ConversationService:
    
    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        product_service: Optional[ProductService] = None,
        logger: Optional[ConversationLogger] = None
    ):
        self._llm_service = llm_service or LLMService()
        self._product_service = product_service or ProductService()
        self._logger = logger or ConversationLogger()
        self._active_conversations: Dict[str, Conversation] = {}
    
    def start_conversation(self, user: User) -> Conversation:
        try:
            conversation_id = self._generate_conversation_id()
            
            conversation = Conversation.create_new(
                conversation_id=conversation_id,
                user_persona_id=user.persona_id,
                metadata={'user_name': user.name}
            )
            
            self._active_conversations[conversation_id] = conversation
            
            if settings.sales.greeting_enabled:
                greeting = self._llm_service.generate_greeting(user)
                conversation.add_assistant_message(greeting)
            
            return conversation
            
        except Exception as e:
            raise ConversationServiceError(f"Failed to start conversation: {str(e)}")
    
    def _generate_conversation_id(self) -> str:
        return f"CONV-{uuid.uuid4().hex[:12].upper()}"
    
    def process_user_message(
        self,
        conversation: Conversation,
        user: User,
        user_message: str
    ) -> str:
        try:
            conversation.add_user_message(user_message)
            
            intent_analysis = self._llm_service.analyze_user_intent(user_message)
            
            conversation_stage = self._determine_conversation_stage(intent_analysis)
            
            available_products = self._get_relevant_products(user, intent_analysis)
            
            assistant_response = self._llm_service.generate_response(
                conversation=conversation,
                user=user,
                available_products=available_products,
                conversation_stage=conversation_stage
            )
            
            conversation.add_assistant_message(
                assistant_response,
                metadata={
                    'stage': conversation_stage,
                    'intent': intent_analysis.get('intent'),
                    'products_shown': len(available_products)
                }
            )
            
            return assistant_response
            
        except LLMServiceError as e:
            raise ConversationServiceError(f"LLM service error: {str(e)}")
        except Exception as e:
            raise ConversationServiceError(f"Failed to process user message: {str(e)}")
    
    # def process_user_message(
    #     self,
    #     conversation: Conversation,
    #     user: User,
    #     user_message: str
    # ) -> str:
    #     try:
    #         conversation.add_user_message(user_message)
            
    #         intent_analysis = self._llm_service.analyze_user_intent(user_message)
            
    #         conversation_stage = self._determine_conversation_stage(intent_analysis)
            
    #         # Get ALL products so LLM has complete inventory knowledge
    #         all_products = self._product_service.get_all_products()
            
    #         assistant_response = self._llm_service.generate_response(
    #             conversation=conversation,
    #             user=user,
    #             available_products=all_products,
    #             conversation_stage=conversation_stage
    #         )
            
    #         conversation.add_assistant_message(
    #             assistant_response,
    #             metadata={
    #                 'stage': conversation_stage,
    #                 'intent': intent_analysis.get('intent'),
    #                 'products_shown': len(all_products)
    #             }
    #         )
            
    #         return assistant_response
            
    #     except LLMServiceError as e:
    #         raise ConversationServiceError(f"LLM service error: {str(e)}")
    #     except Exception as e:
    #         raise ConversationServiceError(f"Failed to process user message: {str(e)}")

    def _determine_conversation_stage(self, intent_analysis: Dict[str, Any]) -> str:
        intent = intent_analysis.get('intent', 'unknown')
        
        stage_mapping = {
            'browsing': 'discovery',
            'asking_question': 'discovery',
            'requesting_recommendation': 'recommendation',
            'comparing_products': 'comparison',
            'ready_to_buy': 'closing',
            'objection': 'objection_handling'
        }
        
        return stage_mapping.get(intent, 'discovery')
    
    def _get_relevant_products(
        self,
        user: User,
        intent_analysis: Dict[str, Any]
    ) -> List[Product]:
        categories = intent_analysis.get('categories', [])
        budget = intent_analysis.get('budget')
        
        if categories:
            products = self._product_service.get_products_by_categories(
                categories,
                limit=settings.sales.product_recommendation_limit
            )
        else:
            products = self._product_service.get_recommendations_for_user(
                user,
                limit=settings.sales.product_recommendation_limit
            )
        
        if budget:
            from decimal import Decimal
            products = [p for p in products if p.price <= Decimal(str(budget))]
        
        return products
    
    def get_product_recommendations(
        self,
        conversation: Conversation,
        user: User,
        limit: Optional[int] = None
    ) -> str:
        try:
            recommendation_limit = limit or settings.sales.product_recommendation_limit
            
            products = self._product_service.get_recommendations_for_user(
                user,
                limit=recommendation_limit
            )
            
            response = self._llm_service.generate_product_recommendation(
                conversation=conversation,
                user=user,
                products=products
            )
            
            conversation.add_assistant_message(
                response,
                metadata={
                    'stage': 'recommendation',
                    'products_recommended': [p.product_id for p in products]
                }
            )
            
            return response
            
        except Exception as e:
            raise ConversationServiceError(f"Failed to generate recommendations: {str(e)}")
    
    def compare_products(
        self,
        conversation: Conversation,
        user: User,
        product_ids: List[str]
    ) -> str:
        try:
            products = []
            for product_id in product_ids:
                product = self._product_service.get_product_by_id(product_id)
                if product:
                    products.append(product)
            
            if not products:
                raise ConversationServiceError("No valid products found for comparison")
            
            response = self._llm_service.generate_product_comparison(
                conversation=conversation,
                user=user,
                products=products
            )
            
            conversation.add_assistant_message(
                response,
                metadata={
                    'stage': 'comparison',
                    'products_compared': product_ids
                }
            )
            
            return response
            
        except Exception as e:
            raise ConversationServiceError(f"Failed to compare products: {str(e)}")
    
    def get_similar_products(
        self,
        conversation: Conversation,
        user: User,
        product_id: str
    ) -> str:
        try:
            product = self._product_service.get_product_by_id(product_id)
            
            if not product:
                raise ConversationServiceError(f"Product not found: {product_id}")
            
            similar_products = self._product_service.get_similar_products(product, limit=3)
            
            if not similar_products:
                return "I couldn't find similar products at the moment."
            
            response = self._llm_service.generate_product_recommendation(
                conversation=conversation,
                user=user,
                products=similar_products
            )
            
            conversation.add_assistant_message(
                response,
                metadata={
                    'stage': 'recommendation',
                    'similar_to': product_id,
                    'products_shown': [p.product_id for p in similar_products]
                }
            )
            
            return response
            
        except Exception as e:
            raise ConversationServiceError(f"Failed to get similar products: {str(e)}")
    
    def end_conversation(self, conversation: Conversation) -> None:
        try:
            conversation.complete_conversation()
            
            if settings.conversation.enable_logging:
                log_path = self._logger.log_conversation(conversation)
                conversation.set_metadata_value('log_path', str(log_path))
            
            if conversation.conversation_id in self._active_conversations:
                del self._active_conversations[conversation.conversation_id]
                
        except ConversationLoggerError as e:
            raise ConversationServiceError(f"Failed to log conversation: {str(e)}")
        except Exception as e:
            raise ConversationServiceError(f"Failed to end conversation: {str(e)}")
    
    def abandon_conversation(self, conversation: Conversation) -> None:
        try:
            conversation.abandon_conversation()
            
            if settings.conversation.enable_logging:
                self._logger.log_conversation(conversation)
            
            if conversation.conversation_id in self._active_conversations:
                del self._active_conversations[conversation.conversation_id]
                
        except Exception as e:
            raise ConversationServiceError(f"Failed to abandon conversation: {str(e)}")
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return self._active_conversations.get(conversation_id)
    
    def get_active_conversations(self) -> List[Conversation]:
        return list(self._active_conversations.values())
    
    def get_conversation_summary(self, conversation: Conversation) -> Dict[str, Any]:
        messages = conversation.get_all_messages()
        user_messages = conversation.get_user_messages()
        assistant_messages = conversation.get_assistant_messages()
        
        return {
            'conversation_id': conversation.conversation_id,
            'user_persona_id': conversation.user_persona_id,
            'status': conversation.status.value,
            'started_at': conversation.started_at.isoformat(),
            'ended_at': conversation.ended_at.isoformat() if conversation.ended_at else None,
            'duration_seconds': conversation.get_duration_seconds(),
            'total_messages': conversation.message_count,
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages)
        }


