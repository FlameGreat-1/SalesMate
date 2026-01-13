from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from decimal import Decimal
from .schema import (
    UserSchema,
    LocationSchema,
    CommunicationStyleSchema,
    ShoppingBehaviorSchema,
    TechnologyPreferencesSchema,
    ProductPreferencesSchema,
    ConversationPatternsSchema,
    DigitalBehaviorSchema,
    AgeGroup,
    Gender,
    TechSavviness,
    IncomeLevel
)


@dataclass
class User:
    schema: UserSchema
    
    def __post_init__(self):
        if not isinstance(self.schema, UserSchema):
            raise ValueError("Invalid user schema provided")
    
    @property
    def persona_id(self) -> str:
        return self.schema.persona_id
    
    @property
    def name(self) -> str:
        return self.schema.name
    
    @property
    def age(self) -> int:
        return self.schema.age
    
    @property
    def age_group(self) -> AgeGroup:
        return self.schema.age_group
    
    @property
    def gender(self) -> Gender:
        return self.schema.gender
    
    @property
    def occupation(self) -> str:
        return self.schema.occupation
    
    @property
    def tech_savviness(self) -> TechSavviness:
        return self.schema.tech_savviness
    
    @property
    def income_level(self) -> IncomeLevel:
        return self.schema.income_level
    
    @property
    def personality_traits(self) -> List[str]:
        return self.schema.personality_traits.copy()
    
    @property
    def interests_hobbies(self) -> List[str]:
        return self.schema.interests_hobbies.copy()
    
    @property
    def pain_points(self) -> List[str]:
        return self.schema.pain_points.copy()
    
    @property
    def goals_motivations(self) -> List[str]:
        return self.schema.goals_motivations.copy()
    
    @property
    def communication_pace(self) -> str:
        return self.schema.communication_style.pace
    
    @property
    def communication_tone(self) -> str:
        return self.schema.communication_style.tone
    
    @property
    def price_sensitivity(self) -> str:
        return self.schema.shopping_behavior.price_sensitivity
    
    @property
    def decision_time(self) -> str:
        return self.schema.shopping_behavior.decision_time
    
    @property
    def shopping_influences(self) -> List[str]:
        return self.schema.shopping_behavior.influences.copy()
    
    @property
    def categories_of_interest(self) -> List[str]:
        return self.schema.product_preferences.categories_of_interest.copy()
    
    @property
    def key_features_valued(self) -> List[str]:
        return self.schema.product_preferences.key_features_valued.copy()
    
    @property
    def budget_min(self) -> Decimal:
        return Decimal(str(self.schema.product_preferences.budget_range['min']))
    
    @property
    def budget_max(self) -> Decimal:
        return Decimal(str(self.schema.product_preferences.budget_range['max']))
    
    @property
    def budget_sweet_spot(self) -> Decimal:
        return Decimal(str(self.schema.product_preferences.budget_range.get('sweet_spot', 
                                                                             self.schema.product_preferences.budget_range['max'])))
    
    @property
    def deal_breakers(self) -> List[str]:
        return self.schema.product_preferences.deal_breakers.copy()
    
    @property
    def typical_questions(self) -> List[str]:
        return self.schema.typical_questions.copy()
    
    @property
    def purchase_triggers(self) -> List[str]:
        return self.schema.purchase_triggers.copy()
    
    @property
    def patience_level(self) -> str:
        return self.schema.conversation_patterns.patience_level
    
    @property
    def greeting_style(self) -> str:
        return self.schema.conversation_patterns.greeting_style
    
    def is_interested_in_category(self, category: str) -> bool:
        return category.lower() in [c.lower() for c in self.categories_of_interest]
    
    def values_feature(self, feature: str) -> bool:
        return feature.lower() in [f.lower() for f in self.key_features_valued]
    
    def is_within_budget(self, price: Decimal) -> bool:
        return self.budget_min <= price <= self.budget_max
    
    def is_deal_breaker(self, attribute: str) -> bool:
        return attribute.lower() in [db.lower() for db in self.deal_breakers]
    
    def get_persona_context_for_llm(self) -> str:
        return (
            f"Customer Profile: {self.name}, {self.age} years old, {self.occupation}. "
            f"Tech savviness: {self.tech_savviness.value}. "
            f"Communication style: {self.communication_tone} tone, {self.communication_pace} pace. "
            f"Shopping behavior: {self.price_sensitivity} price sensitivity, {self.decision_time} decision time. "
            f"Key interests: {', '.join(self.categories_of_interest[:3])}. "
            f"Budget range: ${self.budget_min}-${self.budget_max}. "
            f"Values: {', '.join(self.key_features_valued[:5])}. "
            f"Pain points: {', '.join(self.pain_points[:3])}."
        )
    
    def get_conversation_guidelines(self) -> Dict[str, str]:
        return {
            'pace': self.communication_pace,
            'tone': self.communication_tone,
            'patience': self.patience_level,
            'greeting_style': self.greeting_style,
            'verbosity': self.schema.communication_style.verbosity
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        schema = UserSchema.from_dict(data)
        return cls(schema=schema)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.schema.to_dict()
    
    def __str__(self) -> str:
        return f"{self.name} ({self.age_group.value}, {self.occupation})"
    
    def __repr__(self) -> str:
        return f"User(persona_id={self.persona_id}, name={self.name})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.persona_id == other.persona_id
    
    def __hash__(self) -> int:
        return hash(self.persona_id)
