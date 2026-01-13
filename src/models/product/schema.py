from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum


class StockStatus(Enum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    LOW_STOCK = "low_stock"
    DISCONTINUED = "discontinued"
    PRE_ORDER = "pre_order"


class PriceTier(Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    PREMIUM = "premium"
    LUXURY = "luxury"


@dataclass
class ProductSpecificationSchema:
    raw_specifications: Dict[str, Any]
    
    def __post_init__(self):
        if not isinstance(self.raw_specifications, dict):
            raise ValueError("Specifications must be a dictionary")
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.raw_specifications.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.raw_specifications.copy()


@dataclass
class ProductPriceSchema:
    price: Decimal
    original_price: Decimal
    currency: str
    discount_percentage: int
    
    def __post_init__(self):
        if self.price <= 0:
            raise ValueError("Price must be greater than 0")
        if self.original_price <= 0:
            raise ValueError("Original price must be greater than 0")
        if self.price > self.original_price:
            raise ValueError("Price cannot be greater than original price")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a valid 3-letter ISO code")
        if not 0 <= self.discount_percentage <= 100:
            raise ValueError("Discount percentage must be between 0 and 100")
    
    @property
    def savings(self) -> Decimal:
        return self.original_price - self.price
    
    @property
    def is_on_sale(self) -> bool:
        return self.discount_percentage > 0


@dataclass
class ProductStockSchema:
    status: StockStatus
    quantity: int
    reorder_level: int
    
    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        if self.reorder_level < 0:
            raise ValueError("Reorder level cannot be negative")
        
        if self.quantity == 0 and self.status != StockStatus.OUT_OF_STOCK:
            self.status = StockStatus.OUT_OF_STOCK
        elif 0 < self.quantity <= self.reorder_level and self.status == StockStatus.IN_STOCK:
            self.status = StockStatus.LOW_STOCK
    
    @property
    def is_available(self) -> bool:
        return self.status in [StockStatus.IN_STOCK, StockStatus.LOW_STOCK]
    
    @property
    def needs_reorder(self) -> bool:
        return self.quantity <= self.reorder_level


@dataclass
class ProductMetadataSchema:
    rating: float
    review_count: int
    release_date: str
    is_featured: bool
    is_new_arrival: bool
    tags: List[str]
    
    def __post_init__(self):
        if not 0.0 <= self.rating <= 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0")
        if self.review_count < 0:
            raise ValueError("Review count cannot be negative")
        if not isinstance(self.tags, list):
            raise ValueError("Tags must be a list")
        
        try:
            datetime.strptime(self.release_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Release date must be in YYYY-MM-DD format")


@dataclass
class ProductWarrantySchema:
    warranty_months: int
    return_policy_days: int
    
    def __post_init__(self):
        if self.warranty_months < 0:
            raise ValueError("Warranty months cannot be negative")
        if self.return_policy_days < 0:
            raise ValueError("Return policy days cannot be negative")
    
    @property
    def warranty_years(self) -> float:
        return round(self.warranty_months / 12, 1)


@dataclass
class ProductSchema:
    product_id: str
    sku: str
    name: str
    category: str
    subcategory: str
    brand: str
    manufacturer: str
    description: str
    short_description: str
    price_info: ProductPriceSchema
    stock_info: ProductStockSchema
    specifications: ProductSpecificationSchema
    features: List[str]
    included_accessories: List[str]
    target_audience: List[str]
    use_cases: List[str]
    price_tier: PriceTier
    warranty_info: ProductWarrantySchema
    metadata: ProductMetadataSchema
    
    def __post_init__(self):
        if not self.product_id or not self.product_id.strip():
            raise ValueError("Product ID is required")
        if not self.sku or not self.sku.strip():
            raise ValueError("SKU is required")
        if not self.name or not self.name.strip():
            raise ValueError("Product name is required")
        if not self.category or not self.category.strip():
            raise ValueError("Category is required")
        if not self.brand or not self.brand.strip():
            raise ValueError("Brand is required")
        if not self.description or len(self.description) < 10:
            raise ValueError("Description must be at least 10 characters")
        if not isinstance(self.features, list) or len(self.features) == 0:
            raise ValueError("Features must be a non-empty list")
        if not isinstance(self.target_audience, list) or len(self.target_audience) == 0:
            raise ValueError("Target audience must be a non-empty list")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductSchema':
        price_info = ProductPriceSchema(
            price=Decimal(str(data['price'])),
            original_price=Decimal(str(data['original_price'])),
            currency=data['currency'],
            discount_percentage=data['discount_percentage']
        )
        
        stock_info = ProductStockSchema(
            status=StockStatus(data['stock_status']),
            quantity=data['stock_quantity'],
            reorder_level=data['reorder_level']
        )
        
        specifications = ProductSpecificationSchema(
            raw_specifications=data['specifications']
        )
        
        warranty_info = ProductWarrantySchema(
            warranty_months=data['warranty_months'],
            return_policy_days=data['return_policy_days']
        )
        
        metadata = ProductMetadataSchema(
            rating=data['rating'],
            review_count=data['review_count'],
            release_date=data['release_date'],
            is_featured=data['is_featured'],
            is_new_arrival=data['is_new_arrival'],
            tags=data['tags']
        )
        
        return cls(
            product_id=data['product_id'],
            sku=data['sku'],
            name=data['name'],
            category=data['category'],
            subcategory=data['subcategory'],
            brand=data['brand'],
            manufacturer=data['manufacturer'],
            description=data['description'],
            short_description=data['short_description'],
            price_info=price_info,
            stock_info=stock_info,
            specifications=specifications,
            features=data['features'],
            included_accessories=data['included_accessories'],
            target_audience=data['target_audience'],
            use_cases=data['use_cases'],
            price_tier=PriceTier(data['price_tier']),
            warranty_info=warranty_info,
            metadata=metadata
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'product_id': self.product_id,
            'sku': self.sku,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'brand': self.brand,
            'manufacturer': self.manufacturer,
            'description': self.description,
            'short_description': self.short_description,
            'price': float(self.price_info.price),
            'original_price': float(self.price_info.original_price),
            'currency': self.price_info.currency,
            'discount_percentage': self.price_info.discount_percentage,
            'stock_status': self.stock_info.status.value,
            'stock_quantity': self.stock_info.quantity,
            'specifications': self.specifications.to_dict(),
            'features': self.features,
            'included_accessories': self.included_accessories,
            'target_audience': self.target_audience,
            'use_cases': self.use_cases,
            'price_tier': self.price_tier.value,
            'warranty_months': self.warranty_info.warranty_months,
            'return_policy_days': self.warranty_info.return_policy_days,
            'rating': self.metadata.rating,
            'review_count': self.metadata.review_count,
            'tags': self.metadata.tags
        }
