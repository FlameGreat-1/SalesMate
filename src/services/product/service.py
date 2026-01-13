from typing import List, Dict, Any, Optional
from decimal import Decimal
from src.models.product.product import Product
from src.models.product.schema import PriceTier
from src.models.user.user import User
from .repository import ProductRepository


class ProductService:
    
    def __init__(self, repository: Optional[ProductRepository] = None):
        self._repository = repository or ProductRepository()
    
    def get_all_products(self) -> List[Product]:
        return self._repository.get_all_products()
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        return self._repository.get_product_by_id(product_id)
    
    def search_products(
        self,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        price_tier: Optional[PriceTier] = None,
        tag: Optional[str] = None,
        available_only: bool = True
    ) -> List[Product]:
        products = self._repository.get_all_products()
        
        if available_only:
            products = [p for p in products if p.is_available]
        
        if category:
            products = [p for p in products if p.matches_category(category)]
        
        if subcategory:
            products = [p for p in products if p.matches_subcategory(subcategory)]
        
        if brand:
            products = [p for p in products if p.matches_brand(brand)]
        
        if min_price is not None or max_price is not None:
            products = [p for p in products if p.matches_price_range(min_price, max_price)]
        
        if price_tier:
            products = [p for p in products if p.matches_price_tier(price_tier)]
        
        if tag:
            products = [p for p in products if p.has_tag(tag)]
        
        return products
    
    def get_recommendations_for_user(self, user: User, limit: int = 5) -> List[Product]:
        products = self._repository.get_available_products()
        
        scored_products = []
        for product in products:
            score = self._calculate_product_score_for_user(product, user)
            scored_products.append((product, score))
        
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        return [product for product, score in scored_products[:limit]]
    
    def _calculate_product_score_for_user(self, product: Product, user: User) -> float:
        score = 0.0
        
        if product.is_within_budget(user.budget_min, user.budget_max):
            score += 10.0
            if product.price <= user.budget_sweet_spot:
                score += 5.0
        else:
            return 0.0
        
        if user.is_interested_in_category(product.category):
            score += 15.0
        
        for feature in user.key_features_valued:
            if product.has_feature_keyword(feature):
                score += 3.0
        
        if product.is_featured:
            score += 2.0
        
        if product.is_on_sale:
            score += 3.0
        
        if product.rating >= 4.5:
            score += 4.0
        elif product.rating >= 4.0:
            score += 2.0
        
        return score
    
    def get_similar_products(self, product: Product, limit: int = 3) -> List[Product]:
        all_products = self._repository.get_available_products()
        
        similar = []
        for p in all_products:
            if p.product_id == product.product_id:
                continue
            
            if p.matches_category(product.category):
                similarity_score = self._calculate_similarity_score(product, p)
                similar.append((p, similarity_score))
        
        similar.sort(key=lambda x: x[1], reverse=True)
        
        return [p for p, score in similar[:limit]]
    
    def _calculate_similarity_score(self, product1: Product, product2: Product) -> float:
        score = 0.0
        
        if product1.matches_subcategory(product2.subcategory):
            score += 10.0
        
        if product1.matches_brand(product2.brand):
            score += 5.0
        
        price_diff = abs(float(product1.price - product2.price))
        if price_diff < 50:
            score += 8.0
        elif price_diff < 100:
            score += 5.0
        elif price_diff < 200:
            score += 2.0
        
        if product1.matches_price_tier(product2.price_tier):
            score += 3.0
        
        common_tags = set(product1.tags) & set(product2.tags)
        score += len(common_tags) * 2.0
        
        return score
    
    def get_products_by_categories(self, categories: List[str], limit: Optional[int] = None) -> List[Product]:
        products = []
        for category in categories:
            category_products = self._repository.get_products_by_category(category)
            products.extend(category_products)
        
        products = [p for p in products if p.is_available]
        
        if limit:
            return products[:limit]
        return products
    
    def get_featured_products(self, limit: Optional[int] = None) -> List[Product]:
        products = self._repository.get_featured_products()
        products = [p for p in products if p.is_available]
        
        if limit:
            return products[:limit]
        return products
    
    def get_products_on_sale(self, limit: Optional[int] = None) -> List[Product]:
        products = self._repository.get_products_on_sale()
        products = [p for p in products if p.is_available]
        
        if limit:
            return products[:limit]
        return products
    
    def get_product_summary_for_llm(self, product: Product) -> str:
        return (
            f"{product.name} by {product.brand} - {product.get_formatted_price()} "
            f"({product.discount_percentage}% off, save {product.get_formatted_savings()}). "
            f"Category: {product.category}. Rating: {product.rating}/5.0 ({product.review_count} reviews). "
            f"Key features: {', '.join(product.features[:3])}. "
            f"Stock: {product.stock_status.value}."
        )
    
    def get_products_summary_for_llm(self, products: List[Product]) -> str:
        if not products:
            return "No products available."
        
        summaries = []
        for i, product in enumerate(products, 1):
            summary = f"{i}. {self.get_product_summary_for_llm(product)}"
            summaries.append(summary)
        
        return "\n".join(summaries)
    
    def get_available_categories(self) -> List[str]:
        return self._repository.get_all_categories()
    
    def get_available_brands(self) -> List[str]:
        return self._repository.get_all_brands()
