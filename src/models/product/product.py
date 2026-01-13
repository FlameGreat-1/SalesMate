from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from decimal import Decimal
from .schema import (
    ProductSchema,
    ProductPriceSchema,
    ProductStockSchema,
    ProductSpecificationSchema,
    ProductWarrantySchema,
    ProductMetadataSchema,
    StockStatus,
    PriceTier
)


@dataclass
class Product:
    schema: ProductSchema
    
    def __post_init__(self):
        if not isinstance(self.schema, ProductSchema):
            raise ValueError("Invalid product schema provided")
    
    @property
    def product_id(self) -> str:
        return self.schema.product_id
    
    @property
    def sku(self) -> str:
        return self.schema.sku
    
    @property
    def name(self) -> str:
        return self.schema.name
    
    @property
    def category(self) -> str:
        return self.schema.category
    
    @property
    def subcategory(self) -> str:
        return self.schema.subcategory
    
    @property
    def brand(self) -> str:
        return self.schema.brand
    
    @property
    def manufacturer(self) -> str:
        return self.schema.manufacturer
    
    @property
    def description(self) -> str:
        return self.schema.description
    
    @property
    def short_description(self) -> str:
        return self.schema.short_description
    
    @property
    def price(self) -> Decimal:
        return self.schema.price_info.price
    
    @property
    def original_price(self) -> Decimal:
        return self.schema.price_info.original_price
    
    @property
    def currency(self) -> str:
        return self.schema.price_info.currency
    
    @property
    def discount_percentage(self) -> int:
        return self.schema.price_info.discount_percentage
    
    @property
    def is_on_sale(self) -> bool:
        return self.schema.price_info.is_on_sale
    
    @property
    def savings(self) -> Decimal:
        return self.schema.price_info.savings
    
    @property
    def stock_status(self) -> StockStatus:
        return self.schema.stock_info.status
    
    @property
    def stock_quantity(self) -> int:
        return self.schema.stock_info.quantity
    
    @property
    def is_available(self) -> bool:
        return self.schema.stock_info.is_available
    
    @property
    def needs_reorder(self) -> bool:
        return self.schema.stock_info.needs_reorder
    
    @property
    def specifications(self) -> Dict[str, Any]:
        return self.schema.specifications.to_dict()
    
    @property
    def features(self) -> List[str]:
        return self.schema.features.copy()
    
    @property
    def included_accessories(self) -> List[str]:
        return self.schema.included_accessories.copy()
    
    @property
    def target_audience(self) -> List[str]:
        return self.schema.target_audience.copy()
    
    @property
    def use_cases(self) -> List[str]:
        return self.schema.use_cases.copy()
    
    @property
    def price_tier(self) -> PriceTier:
        return self.schema.price_tier
    
    @property
    def warranty_months(self) -> int:
        return self.schema.warranty_info.warranty_months
    
    @property
    def warranty_years(self) -> float:
        return self.schema.warranty_info.warranty_years
    
    @property
    def return_policy_days(self) -> int:
        return self.schema.warranty_info.return_policy_days
    
    @property
    def rating(self) -> float:
        return self.schema.metadata.rating
    
    @property
    def review_count(self) -> int:
        return self.schema.metadata.review_count
    
    @property
    def is_featured(self) -> bool:
        return self.schema.metadata.is_featured
    
    @property
    def is_new_arrival(self) -> bool:
        return self.schema.metadata.is_new_arrival
    
    @property
    def tags(self) -> List[str]:
        return self.schema.metadata.tags.copy()
    
    def get_specification(self, key: str, default: Any = None) -> Any:
        return self.schema.specifications.get(key, default)
    
    def matches_category(self, category: str) -> bool:
        return self.category.lower() == category.lower()
    
    def matches_subcategory(self, subcategory: str) -> bool:
        return self.subcategory.lower() == subcategory.lower()
    
    def matches_brand(self, brand: str) -> bool:
        return self.brand.lower() == brand.lower()
    
    def matches_price_range(self, min_price: Optional[Decimal] = None, max_price: Optional[Decimal] = None) -> bool:
        if min_price is not None and self.price < min_price:
            return False
        if max_price is not None and self.price > max_price:
            return False
        return True
    
    def matches_price_tier(self, tier: PriceTier) -> bool:
        return self.price_tier == tier
    
    def has_tag(self, tag: str) -> bool:
        return tag.lower() in [t.lower() for t in self.tags]
    
    def has_feature_keyword(self, keyword: str) -> bool:
        keyword_lower = keyword.lower()
        
        for feature in self.features:
            if keyword_lower in feature.lower():
                return True
        
        if keyword_lower in self.name.lower():
            return True
        
        if keyword_lower in self.description.lower():
            return True
        
        return False
    
    def is_within_budget(self, min_price: Decimal, max_price: Decimal) -> bool:
        return min_price <= self.price <= max_price

    def is_suitable_for_audience(self, audience: str) -> bool:
        return audience.lower() in [a.lower() for a in self.target_audience]
    
    def supports_use_case(self, use_case: str) -> bool:
        return use_case.lower() in [uc.lower() for uc in self.use_cases]
    
    def get_formatted_price(self) -> str:
        return f"{self.currency} {self.price:.2f}"
    
    def get_formatted_original_price(self) -> str:
        return f"{self.currency} {self.original_price:.2f}"
    
    def get_formatted_savings(self) -> str:
        return f"{self.currency} {self.savings:.2f}"
    
    def get_summary(self) -> str:
        return (
            f"{self.name} by {self.brand} - {self.get_formatted_price()} "
            f"({'On Sale' if self.is_on_sale else 'Regular Price'}) - "
            f"{self.stock_status.value.replace('_', ' ').title()}"
        )
    
    def get_detailed_info(self) -> Dict[str, Any]:
        return {
            'id': self.product_id,
            'name': self.name,
            'brand': self.brand,
            'category': self.category,
            'price': self.get_formatted_price(),
            'original_price': self.get_formatted_original_price(),
            'discount': f"{self.discount_percentage}%",
            'savings': self.get_formatted_savings(),
            'stock_status': self.stock_status.value,
            'rating': self.rating,
            'reviews': self.review_count,
            'warranty': f"{self.warranty_months} months",
            'description': self.short_description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        schema = ProductSchema.from_dict(data)
        return cls(schema=schema)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.schema.to_dict()
    
    def __str__(self) -> str:
        return self.get_summary()
    
    def __repr__(self) -> str:
        return f"Product(id={self.product_id}, name={self.name}, price={self.get_formatted_price()})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Product):
            return False
        return self.product_id == other.product_id
    
    def __hash__(self) -> int:
        return hash(self.product_id)
