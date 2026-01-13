from typing import List, Dict, Any
from src.models.user.user import User
from src.models.product.product import Product


class SalesPromptBuilder:
    
    BASE_SYSTEM_PROMPT = """You are an expert sales assistant for an electronics store. Your role is to help customers find the perfect products that match their needs and budget.

Your approach:
- Be friendly, professional, and helpful
- Ask clarifying questions to understand customer needs
- Listen carefully to customer preferences and constraints
- Recommend products that genuinely fit their requirements
- Explain product benefits clearly and concisely
- Handle objections professionally
- Guide customers toward making informed purchase decisions

Guidelines:
- Always prioritize customer satisfaction over making a sale
- Be honest about product limitations
- Suggest alternatives when appropriate
- Respect the customer's budget
- Use natural, conversational language
- Keep responses concise and focused
- Don't reference the customer's "profile" like "based on your profile" or "according to your data"
- Speak naturally as if you know the customer from previous conversations
- Use customer information naturally as if you've learned it through conversation

CRITICAL INVENTORY RULES:
- You have access to our COMPLETE product inventory below
- NEVER say you don't have a product if it appears in the inventory list
- If a customer asks about a specific product by name, check the complete inventory first
- Always provide accurate information from the product specifications
- If you don't have specific details, say "Let me get you the exact specifications" rather than guessing
- NEVER make up or hallucinate product specifications - use only the data provided
"""

    @staticmethod
    def build_system_prompt(
        user: User,
        available_products: List[Product],
        conversation_stage: str = "discovery"
    ) -> str:
        prompt_parts = [SalesPromptBuilder.BASE_SYSTEM_PROMPT]
        
        prompt_parts.append(SalesPromptBuilder._build_customer_context(user))
        prompt_parts.append(SalesPromptBuilder._build_product_context(available_products))
        prompt_parts.append(SalesPromptBuilder._build_stage_guidance(conversation_stage, user))
        
        return "\n\n".join(prompt_parts)
    
    @staticmethod
    def _build_customer_context(user: User) -> str:
        context = f"""You are speaking with {user.name}, a {user.age}-year-old {user.occupation}.

What you know about this customer:
- They are {user.tech_savviness.value} with technology
- Their budget range is ${user.budget_min} - ${user.budget_max} (preferred spending: ${user.budget_sweet_spot})
- They prefer {user.communication_tone} communication at a {user.communication_pace} pace
- They have {user.patience_level} patience level

Their interests and preferences:
- Interested in: {', '.join(user.categories_of_interest[:5])}
- Values these features: {', '.join(user.key_features_valued[:5])}
- Price sensitivity: {user.price_sensitivity}
- Takes {user.decision_time} to make decisions

Important considerations:
- Current challenges: {', '.join(user.pain_points[:3])}
- Absolute deal breakers: {', '.join(user.deal_breakers[:3])}

Use this information naturally in your recommendations. Make proactive suggestions based on what you know they value. 
Don't ask questions about preferences you already know. Speak as if you've learned these details through previous interactions."""
        
        return context
    
    @staticmethod
    def _build_product_context(products: List[Product]) -> str:
        if not products:
            return "Currently, no specific products are being highlighted."
        
        total_count = len(products)
        context = f"COMPLETE STORE INVENTORY: {total_count} products available\n"
        context += "="*100 + "\n\n"
        
        context += "FULL PRODUCT CATALOG (Quick Reference - All Available Products):\n"
        context += "-"*100 + "\n"
        for i, product in enumerate(products, 1):
            context += f"{i}. {product.name} by {product.brand}"
            context += f" | ${product.price}"
            if product.is_on_sale:
                context += f" (SALE: {product.discount_percentage}% OFF - Save ${product.original_price - product.price:.2f})"
            context += f" | Stock: {product.stock_quantity} units"
            context += f" | Category: {product.category}"
            context += f" | Rating: {product.rating}/5.0\n"
        
        context += "\n" + "="*100 + "\n\n"
        
        context += "DETAILED PRODUCT SPECIFICATIONS:\n"
        context += "-"*100 + "\n\n"
        
        for i, product in enumerate(products, 1):
            context += f"PRODUCT #{i}: {product.name}\n"
            context += f"Brand: {product.brand}\n"
            context += f"Category: {product.category} / {product.subcategory if hasattr(product, 'subcategory') else 'N/A'}\n"
            context += f"Price: ${product.price} USD"
            if product.is_on_sale:
                context += f" (Original: ${product.original_price}, Save: ${product.original_price - product.price:.2f} - {product.discount_percentage}% OFF)"
            context += f"\n"
            context += f"Stock Status: {product.stock_status.value} ({product.stock_quantity} units available)\n"
            context += f"Rating: {product.rating}/5.0 ({product.review_count} reviews)\n"
            context += f"Warranty: {product.warranty_months} months | Return Policy: {product.return_policy_days} days\n"
            
            if hasattr(product, 'description') and product.description:
                context += f"Description: {product.description}\n"
            elif hasattr(product, 'short_description') and product.short_description:
                context += f"Description: {product.short_description}\n"
            
            if product.features:
                context += f"Key Features:\n"
                for feature in product.features:
                    context += f"  • {feature}\n"
            
            if hasattr(product, 'specifications') and product.specifications:
                context += f"Technical Specifications:\n"
                specs = product.specifications
                
                for key, value in specs.items():
                    if isinstance(value, dict):
                        context += f"  {key.replace('_', ' ').title()}:\n"
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, list):
                                context += f"    - {sub_key.replace('_', ' ').title()}: {', '.join(map(str, sub_value))}\n"
                            else:
                                context += f"    - {sub_key.replace('_', ' ').title()}: {sub_value}\n"
                    elif isinstance(value, list):
                        context += f"  {key.replace('_', ' ').title()}: {', '.join(map(str, value))}\n"
                    else:
                        context += f"  {key.replace('_', ' ').title()}: {value}\n"
            
            if hasattr(product, 'included_accessories') and product.included_accessories:
                context += f"Included Accessories: {', '.join(product.included_accessories)}\n"
            
            if hasattr(product, 'target_audience') and product.target_audience:
                context += f"Ideal For: {', '.join(product.target_audience)}\n"
            
            if hasattr(product, 'use_cases') and product.use_cases:
                context += f"Use Cases: {', '.join(product.use_cases)}\n"
            
            context += "\n" + "-"*100 + "\n\n"
        
        return context
    
    @staticmethod
    def _build_stage_guidance(stage: str, user: User) -> str:
        stage_prompts = {
            "greeting": f"""Conversation Stage: Initial Greeting

Your task:
- Greet the customer warmly using a {user.greeting_style} style
- Welcome them to the store
- Ask an open-ended question to understand what they're looking for
- Make them feel welcome and comfortable

Keep it brief and natural. Don't introduce yourself by name.""",

            "discovery": f"""Conversation Stage: Needs Discovery

Your task:
- Ask targeted questions to understand their specific needs
- Listen for budget constraints, use cases, and preferences
- Identify must-have features vs nice-to-have features
- Clarify any technical requirements
- Take note of their {user.tech_savviness.value} tech level when explaining features
- Use what you already know about their interests to guide the conversation

Remember: This customer has {user.patience_level} patience, so adjust your questioning pace accordingly.""",

            "recommendation": f"""Conversation Stage: Product Recommendation

Your task:
- Recommend 2-3 products that best match their stated needs
- Explain why each product fits their requirements
- Highlight key benefits relevant to their use case
- Be transparent about pricing and any trade-offs
- Respect their budget range of ${user.budget_min} - ${user.budget_max}
- Proactively suggest products that align with their known interests
- Use EXACT specifications from the product details provided

Focus on products that align with their valued features: {', '.join(user.key_features_valued[:3])}""",

            "comparison": f"""Conversation Stage: Product Comparison

Your task:
- Help them compare products they're interested in
- Highlight key differences in features, price, and value
- Be objective and honest about pros and cons
- Guide them based on their priorities
- Address any concerns about their deal breakers: {', '.join(user.deal_breakers[:2])}
- Use EXACT specifications from the product details - never guess or approximate

Remember: They have {user.price_sensitivity} price sensitivity.""",

            "objection_handling": f"""Conversation Stage: Handling Concerns

Your task:
- Listen carefully to their concerns or objections
- Address concerns honestly and professionally
- Provide additional information or alternatives
- Reassure them about warranties, returns, and support
- Don't pressure - help them make the right decision

This customer needs {user.schema.conversation_patterns.objection_handling}.""",

            "closing": f"""Conversation Stage: Closing the Sale

Your task:
- Summarize the recommended product(s)
- Confirm it meets their needs and budget
- Explain next steps (purchase process, delivery, etc.)
- Offer to answer any final questions
- Thank them for their time

Keep the tone positive and helpful, matching their {user.communication_tone} preference."""
        }
        
        return stage_prompts.get(stage, stage_prompts["discovery"])
    
    @staticmethod
    def build_greeting_prompt(user: User) -> str:
        return SalesPromptBuilder._build_stage_guidance("greeting", user)
    
    @staticmethod
    def build_discovery_prompt(user: User) -> str:
        return SalesPromptBuilder._build_stage_guidance("discovery", user)
    
    @staticmethod
    def build_recommendation_prompt(user: User, products: List[Product]) -> str:
        parts = [
            SalesPromptBuilder._build_stage_guidance("recommendation", user),
            SalesPromptBuilder._build_product_context(products)
        ]
        return "\n\n".join(parts)
    
    @staticmethod
    def build_comparison_prompt(user: User, products: List[Product]) -> str:
        parts = [
            SalesPromptBuilder._build_stage_guidance("comparison", user),
            SalesPromptBuilder._build_product_context(products)
        ]
        return "\n\n".join(parts)
    
    @staticmethod
    def build_user_message_with_context(user_input: str, context: Dict[str, Any]) -> str:
        if not context:
            return user_input
        
        context_parts = []
        
        if context.get('mentioned_products'):
            products = context['mentioned_products']
            context_parts.append(f"[Customer is asking about: {', '.join([p.name for p in products])}]")
        
        if context.get('budget_mentioned'):
            context_parts.append(f"[Budget mentioned: ${context['budget_mentioned']}]")
        
        if context.get('category_interest'):
            context_parts.append(f"[Interested in: {context['category_interest']}]")
        
        if context_parts:
            return f"{' '.join(context_parts)}\n\nCustomer: {user_input}"
        
        return user_input
