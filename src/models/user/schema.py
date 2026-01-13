from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class AgeGroup(Enum):
    YOUNG_ADULT = "young_adult"
    MIDDLE_AGED = "middle_aged"
    SENIOR = "senior"


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class TechSavviness(Enum):
    BEGINNER = "beginner"
    MODERATE = "moderate"
    HIGH = "high"
    EXPERT = "expert"


class IncomeLevel(Enum):
    LOW = "low"
    MIDDLE = "middle"
    UPPER_MIDDLE = "upper_middle"
    HIGH = "high"


@dataclass
class LocationSchema:
    city: str
    state: str
    country: str
    
    def __post_init__(self):
        if not self.city or not self.city.strip():
            raise ValueError("City is required")
        if not self.state or not self.state.strip():
            raise ValueError("State is required")
        if not self.country or not self.country.strip():
            raise ValueError("Country is required")


@dataclass
class CommunicationStyleSchema:
    pace: str
    tone: str
    verbosity: str
    decision_making: str
    
    def __post_init__(self):
        if not self.pace or not self.pace.strip():
            raise ValueError("Communication pace is required")
        if not self.tone or not self.tone.strip():
            raise ValueError("Communication tone is required")


@dataclass
class ShoppingBehaviorSchema:
    research_depth: str
    price_sensitivity: str
    brand_loyalty: str
    impulse_buying: str
    preferred_channels: List[str]
    decision_time: str
    influences: List[str]
    
    def __post_init__(self):
        if not isinstance(self.preferred_channels, list) or len(self.preferred_channels) == 0:
            raise ValueError("Preferred channels must be a non-empty list")
        if not isinstance(self.influences, list) or len(self.influences) == 0:
            raise ValueError("Influences must be a non-empty list")


@dataclass
class TechnologyPreferencesSchema:
    comfort_level: str
    adoption_rate: str
    preferred_devices: List[str]
    learning_style: str
    frustrations: List[str]
    values: List[str]
    
    def __post_init__(self):
        if not isinstance(self.preferred_devices, list):
            raise ValueError("Preferred devices must be a list")
        if not isinstance(self.frustrations, list):
            raise ValueError("Frustrations must be a list")
        if not isinstance(self.values, list):
            raise ValueError("Values must be a list")


@dataclass
class ProductPreferencesSchema:
    categories_of_interest: List[str]
    key_features_valued: List[str]
    budget_range: Dict[str, float]
    deal_breakers: List[str]
    
    def __post_init__(self):
        if not isinstance(self.categories_of_interest, list) or len(self.categories_of_interest) == 0:
            raise ValueError("Categories of interest must be a non-empty list")
        if not isinstance(self.key_features_valued, list):
            raise ValueError("Key features valued must be a list")
        if not isinstance(self.budget_range, dict):
            raise ValueError("Budget range must be a dictionary")
        if 'min' not in self.budget_range or 'max' not in self.budget_range:
            raise ValueError("Budget range must contain 'min' and 'max' keys")
        if self.budget_range['min'] < 0 or self.budget_range['max'] < 0:
            raise ValueError("Budget values cannot be negative")
        if self.budget_range['min'] > self.budget_range['max']:
            raise ValueError("Minimum budget cannot exceed maximum budget")


@dataclass
class ConversationPatternsSchema:
    greeting_style: str
    question_frequency: str
    clarification_needs: str
    patience_level: str
    trust_building_time: str
    objection_handling: str
    
    def __post_init__(self):
        if not self.greeting_style or not self.greeting_style.strip():
            raise ValueError("Greeting style is required")


@dataclass
class DigitalBehaviorSchema:
    online_shopping_frequency: str
    preferred_contact_method: str
    social_media_usage: str
    email_usage: str
    video_call_comfort: str
    
    def __post_init__(self):
        if not self.preferred_contact_method or not self.preferred_contact_method.strip():
            raise ValueError("Preferred contact method is required")


@dataclass
class UserSchema:
    persona_id: str
    name: str
    age: int
    age_group: AgeGroup
    gender: Gender
    occupation: str
    location: LocationSchema
    income_level: IncomeLevel
    tech_savviness: TechSavviness
    education: str
    marital_status: str
    household_size: int
    personality_traits: List[str]
    communication_style: CommunicationStyleSchema
    shopping_behavior: ShoppingBehaviorSchema
    technology_preferences: TechnologyPreferencesSchema
    interests_hobbies: List[str]
    pain_points: List[str]
    goals_motivations: List[str]
    product_preferences: ProductPreferencesSchema
    typical_questions: List[str]
    conversation_patterns: ConversationPatternsSchema
    purchase_triggers: List[str]
    digital_behavior: DigitalBehaviorSchema
    
    def __post_init__(self):
        if not self.persona_id or not self.persona_id.strip():
            raise ValueError("Persona ID is required")
        if not self.name or not self.name.strip():
            raise ValueError("Name is required")
        if self.age < 0 or self.age > 120:
            raise ValueError("Age must be between 0 and 120")
        if self.household_size < 1:
            raise ValueError("Household size must be at least 1")
        if not isinstance(self.personality_traits, list) or len(self.personality_traits) == 0:
            raise ValueError("Personality traits must be a non-empty list")
        if not isinstance(self.interests_hobbies, list):
            raise ValueError("Interests and hobbies must be a list")
        if not isinstance(self.pain_points, list):
            raise ValueError("Pain points must be a list")
        if not isinstance(self.goals_motivations, list):
            raise ValueError("Goals and motivations must be a list")
        if not isinstance(self.typical_questions, list):
            raise ValueError("Typical questions must be a list")
        if not isinstance(self.purchase_triggers, list):
            raise ValueError("Purchase triggers must be a list")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSchema':
        location = LocationSchema(
            city=data['location']['city'],
            state=data['location']['state'],
            country=data['location']['country']
        )
        
        communication_style = CommunicationStyleSchema(
            pace=data['communication_style']['pace'],
            tone=data['communication_style']['tone'],
            verbosity=data['communication_style']['verbosity'],
            decision_making=data['communication_style']['decision_making']
        )
        
        shopping_behavior = ShoppingBehaviorSchema(
            research_depth=data['shopping_behavior']['research_depth'],
            price_sensitivity=data['shopping_behavior']['price_sensitivity'],
            brand_loyalty=data['shopping_behavior']['brand_loyalty'],
            impulse_buying=data['shopping_behavior']['impulse_buying'],
            preferred_channels=data['shopping_behavior']['preferred_channels'],
            decision_time=data['shopping_behavior']['decision_time'],
            influences=data['shopping_behavior']['influences']
        )
        
        technology_preferences = TechnologyPreferencesSchema(
            comfort_level=data['technology_preferences']['comfort_level'],
            adoption_rate=data['technology_preferences']['adoption_rate'],
            preferred_devices=data['technology_preferences']['preferred_devices'],
            learning_style=data['technology_preferences']['learning_style'],
            frustrations=data['technology_preferences']['frustrations'],
            values=data['technology_preferences']['values']
        )
        
        product_preferences = ProductPreferencesSchema(
            categories_of_interest=data['product_preferences']['categories_of_interest'],
            key_features_valued=data['product_preferences']['key_features_valued'],
            budget_range=data['product_preferences']['budget_range'],
            deal_breakers=data['product_preferences']['deal_breakers']
        )
        
        conversation_patterns = ConversationPatternsSchema(
            greeting_style=data['conversation_patterns']['greeting_style'],
            question_frequency=data['conversation_patterns']['question_frequency'],
            clarification_needs=data['conversation_patterns']['clarification_needs'],
            patience_level=data['conversation_patterns']['patience_level'],
            trust_building_time=data['conversation_patterns']['trust_building_time'],
            objection_handling=data['conversation_patterns']['objection_handling']
        )
        
        digital_behavior = DigitalBehaviorSchema(
            online_shopping_frequency=data['digital_behavior']['online_shopping_frequency'],
            preferred_contact_method=data['digital_behavior']['preferred_contact_method'],
            social_media_usage=data['digital_behavior']['social_media_usage'],
            email_usage=data['digital_behavior']['email_usage'],
            video_call_comfort=data['digital_behavior']['video_call_comfort']
        )
        
        return cls(
            persona_id=data['persona_id'],
            name=data['name'],
            age=data['age'],
            age_group=AgeGroup(data['age_group']),
            gender=Gender(data['gender']),
            occupation=data['occupation'],
            location=location,
            income_level=IncomeLevel(data['income_level']),
            tech_savviness=TechSavviness(data['tech_savviness']),
            education=data['education'],
            marital_status=data['marital_status'],
            household_size=data['household_size'],
            personality_traits=data['personality_traits'],
            communication_style=communication_style,
            shopping_behavior=shopping_behavior,
            technology_preferences=technology_preferences,
            interests_hobbies=data['interests_hobbies'],
            pain_points=data['pain_points'],
            goals_motivations=data['goals_motivations'],
            product_preferences=product_preferences,
            typical_questions=data['typical_questions'],
            conversation_patterns=conversation_patterns,
            purchase_triggers=data['purchase_triggers'],
            digital_behavior=digital_behavior
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'persona_id': self.persona_id,
            'name': self.name,
            'age': self.age,
            'age_group': self.age_group.value,
            'gender': self.gender.value,
            'occupation': self.occupation,
            'tech_savviness': self.tech_savviness.value,
            'income_level': self.income_level.value,
            'personality_traits': self.personality_traits,
            'interests_hobbies': self.interests_hobbies,
            'pain_points': self.pain_points,
            'goals_motivations': self.goals_motivations,
            'typical_questions': self.typical_questions,
            'purchase_triggers': self.purchase_triggers
        }
