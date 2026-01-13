from typing import List, Dict, Any, Optional
from pathlib import Path
from decimal import Decimal
from src.models.product.product import Product
from src.models.product.schema import StockStatus, PriceTier
from src.utils.file_handler.json_handler import JSONHandler
from src.config.settings import settings


class ProductRepository:
    
    def __init__(self, products_file_path: Optional[Path] = None):
        self._products_file = products_file_path or settings.paths.products_file
        self._products_cache: Optional[List[Product]] = None
        self._validate_file_exists()
    
    def _validate_file_exists(self) -> None:
        if not JSONHandler.file_exists(self._products_file):
            raise FileNotFoundError(f"Products file not found: {self._products_file}")
    
    def _load_products_from_file(self) -> List[Product]:
        try:
            data = JSONHandler.read_json(self._products_file)
            products_data = data.get('products', [])
            
            if not products_data:
                raise ValueError("No products found in products file")
            
            products = []
            for product_data in products_data:
                try:
                    product = Product.from_dict(product_data)
                    products.append(product)
                except Exception as e:
                    product_id = product_data.get('product_id', 'unknown')
                    raise ValueError(f"Error loading product {product_id}: {str(e)}")
            
            return products
        except Exception as e:
            raise RuntimeError(f"Failed to load products: {str(e)}")
    
    def get_all_products(self, force_reload: bool = False) -> List[Product]:
        if self._products_cache is None or force_reload:
            self._products_cache = self._load_products_from_file()
        return self._products_cache.copy()
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        products = self.get_all_products()
        for product in products:
            if product.product_id == product_id:
                return product
        return None
    
    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        products = self.get_all_products()
        for product in products:
            if product.sku == sku:
                return product
        return None
    
    def get_products_by_category(self, category: str) -> List[Product]:
        products = self.get_all_products()
        return [p for p in products if p.matches_category(category)]
    
    def get_products_by_subcategory(self, subcategory: str) -> List[Product]:
        products = self.get_all_products()
        return [p for p in products if p.matches_subcategory(subcategory)]
    
    def get_products_by_brand(self, brand: str) -> List[Product]:
        products = self.get_all_products()
        return [p for p in products if p.matches_brand(brand)]
    
    def get_products_by_price_range(self, min_price: Optional[Decimal] = None, max_price: Optional[Decimal] = None) -> List[Product]:
        products = self.get_all_products()
        return [p for p in products if p.matches_price_range(min_price, max_price)]
    
    def get_products_by_price_tier(self, tier: PriceTier) -> List[Product]:
        products = self.get_all_products()
        return [p for p in products if p.matches_price_tier(tier)]
    
    def get_available_products(self) -> List[Product]:
        products = self.get_all_products()
        return [p for p in products if p.is_available]
    
    def get_featured_products(self) -> List[Product]:
        products = self.get_all_products()
        return [p for p in products if p.is_featured]
    
    def get_new_arrivals(self) -> List[Product]:
        products = self.get_all_products()
        return [p for p in products if p.is_new_arrival]
    
    def get_products_on_sale(self) -> List[Product]:
        products = self.get_all_products()
        return [p for p in products if p.is_on_sale]
    
    def get_products_by_tag(self, tag: str) -> List[Product]:
        products = self.get_all_products()
        return [p for p in products if p.has_tag(tag)]
    
    def get_products_for_audience(self, audience: str) -> List[Product]:
        products = self.get_all_products()
        return [p for p in products if p.is_suitable_for_audience(audience)]
    
    def get_products_by_use_case(self, use_case: str) -> List[Product]:
        products = self.get_all_products()
        return [p for p in products if p.supports_use_case(use_case)]
    
    def get_all_categories(self) -> List[str]:
        products = self.get_all_products()
        categories = set(p.category for p in products)
        return sorted(list(categories))
    
    def get_all_brands(self) -> List[str]:
        products = self.get_all_products()
        brands = set(p.brand for p in products)
        return sorted(list(brands))
    
    def get_product_count(self) -> int:
        return len(self.get_all_products())
    
    def reload_products(self) -> None:
        self._products_cache = None
        self.get_all_products(force_reload=True)
