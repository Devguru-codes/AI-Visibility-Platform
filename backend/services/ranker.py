from typing import List
from schemas.product import ProductInput, RankedProduct
from services.scorer import get_scoring_service

class RankingService:
    """Service for ranking products against competitors"""
    
    def __init__(self):
        self.scorer = get_scoring_service()
    
    def rank_products(self, products: List[ProductInput]) -> List[RankedProduct]:
        """
        Rank multiple products by their AI visibility scores
        
        Args:
            products: List of products to rank
            
        Returns:
            List of ranked products sorted by score (highest first)
        """
        # Score all products
        scored_products = []
        for product in products:
            score, _, _ = self.scorer.score_product(product)
            scored_products.append((product, score))
        
        # Sort by score (descending)
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        # Create ranked products
        from services.sentiment import get_sentiment_service
        sentiment_service = get_sentiment_service()
        
        ranked = []
        for rank, (product, score) in enumerate(scored_products, start=1):
            # Only analyze sentiment for top products to save time/tokens if needed
            # For now, we analyze all since we usually have < 10
            sentiment_data = sentiment_service.analyze_product_sentiment(product)
            
            ranked.append(RankedProduct(
                product=product,
                score=score,
                rank=rank,
                market_rank=product.market_rank,
                platform=product.platform,
                url=product.url,
                sentiment=sentiment_data
            ))
        
        return ranked
    
    def rank_against_competitors(
        self, 
        user_product: ProductInput, 
        competitors: List[ProductInput]
    ) -> tuple[RankedProduct, List[RankedProduct]]:
        """
        Rank user's product against competitors
        
        Args:
            user_product: User's product
            competitors: List of competitor products
            
        Returns:
            Tuple of (user's ranked product, all ranked products)
        """
        # Combine all products
        all_products = [user_product] + competitors
        
        # Rank them
        ranked = self.rank_products(all_products)
        
        # Find user's product in rankings
        user_ranked = next(r for r in ranked if r.product == user_product)
        
        return user_ranked, ranked

# Global instance
_ranking_service = None

def get_ranking_service() -> RankingService:
    """Get or create the global ranking service instance"""
    global _ranking_service
    if _ranking_service is None:
        _ranking_service = RankingService()
    return _ranking_service
