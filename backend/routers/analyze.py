from fastapi import APIRouter, HTTPException
from schemas.product import (
    ProductInput, AnalysisResult, RankingRequest, RankingResult,
    OptimizationRequest, OptimizationResult, URLRequest, URLAnalysisResult
)
from services.scorer import get_scoring_service
from services.ranker import get_ranking_service
from services.optimizer import get_optimizer_service
from services.searcher import get_search_service
from services.intelligence import get_intelligence_service
from typing import List

router = APIRouter(prefix="/api", tags=["analysis"])

# Service instances
scorer = get_scoring_service()
ranker = get_ranking_service()
optimizer = get_optimizer_service()

@router.post("/analyze-product", response_model=AnalysisResult)
async def analyze_product(product: ProductInput):
    """
    Analyze a product and return AI visibility score with detailed breakdown
    
    Args:
        product: Product information
        
    Returns:
        Complete analysis result with scores and weakness analysis
    """
    try:
        # Score the product
        final_score, score_breakdown, queries = scorer.score_product(product)
        
        # Analyze weaknesses
        weakness_analysis = scorer.analyze_weaknesses(product, score_breakdown)
        
        # Analyze sentiment
        from services.sentiment import get_sentiment_service
        sentiment_service = get_sentiment_service()
        sentiment = sentiment_service.analyze_product_sentiment(product)
        
        # 4. New: AI Recommendation Simulation (Grounding)
        intelligence = get_intelligence_service()
        ai_recommendation = intelligence.simulate_ai_recommendation(product, product.price)
        
        # New logic: Factor AI Recommendation into score
        if ai_recommendation.get('is_recommended'):
            final_score = min(100, final_score + 10) # 10 point bonus for being recommended by AI
        
        return AnalysisResult(
            product=product,
            ai_visibility_score=final_score,
            score_breakdown=score_breakdown,
            weakness_analysis=weakness_analysis,
            generated_queries=queries[:5],  # Return top 5 queries
            sentiment=sentiment,
            ai_recommendation=ai_recommendation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/rank-products", response_model=RankingResult)
async def rank_products(request: RankingRequest):
    """
    Rank user's product against competitors
    
    Args:
        request: Ranking request with product and competitors
        
    Returns:
        Ranking result with user's rank and full leaderboard
    """
    try:
        # Rank against competitors
        user_ranked, all_ranked = ranker.rank_against_competitors(
            request.product,
            request.competitors
        )
        
        return RankingResult(
            your_product=user_ranked,
            all_products=all_ranked,
            total_products=len(all_ranked)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")

@router.post("/optimize-description", response_model=OptimizationResult)
async def optimize_description(request: OptimizationRequest):
    """
    Optimize product description for better AI visibility
    
    Args:
        request: Optimization request with product and optional target queries
        
    Returns:
        Optimization result with before/after comparison
    """
    try:
        # Get original score
        original_score, original_breakdown, _ = scorer.score_product(request.product)
        
        # Get weakness suggestions
        weakness_analysis = scorer.analyze_weaknesses(request.product, original_breakdown)
        
        # Optimize description
        optimized_desc, improvements = optimizer.optimize_description(
            request.product,
            weakness_analysis.suggestions,
            request.target_queries,
            request.additional_specs,
            request.provider
        )
        
        # Create optimized product and score it
        optimized_product = ProductInput(
            title=request.product.title,
            description=optimized_desc,
            category=request.product.category,
            brand=request.product.brand
        )
        
        optimized_score, _, _ = scorer.score_product(optimized_product)
        
        return OptimizationResult(
            original_product=request.product,
            optimized_description=optimized_desc,
            original_score=original_score,
            optimized_score=optimized_score,
            improvements=improvements,
            score_delta=round(optimized_score - original_score, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.post("/fetch-competitors", response_model=List[ProductInput])
async def fetch_competitors(product: ProductInput):
    """
    Automatically search and fetch top competitors from the market
    """
    try:
        search_service = get_search_service()
        competitors = search_service.get_automated_competitors(product)
        return competitors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch competitors: {str(e)}")

@router.post("/market-visibility")
async def check_market_visibility(product: ProductInput):
    """
    Check where the product appears in search results for key queries
    """
    try:
        search_service = get_search_service()
        # Logic to check if product.brand or product.title appears in top results
        results = search_service.search_competitors(product.title, product.category)
        
        found_at = -1
        for i, res in enumerate(results):
            if product.brand.lower() in res['title'].lower() or product.brand.lower() in res['url'].lower():
                found_at = i + 1
                break
                
        return {
            "query": f"{product.title} {product.category}",
            "position": found_at if found_at > 0 else "Not found in top results",
            "top_results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market visibility check failed: {str(e)}")

@router.post("/compare-features")
async def compare_features(product: ProductInput):
    """
    Compare product features with top market competitors
    """
    try:
        search_service = get_search_service()
        competitors = search_service.get_automated_competitors(product)
        
        # Use scorer's improved extraction logic
        user_features = scorer.extract_features(product.title, product.description)
        comparison = []
        
        for comp in competitors:
            comp_features = scorer.extract_features(comp.title, comp.description)
            comparison.append({
                "competitor": comp.title,
                "common_features": list(set(user_features) & set(comp_features)),
                "missing_features": list(set(comp_features) - set(user_features)),
                "unique_features": list(set(user_features) - set(comp_features))
            })
            
        return {
            "your_features": user_features,
            "comparison": comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature comparison failed: {str(e)}")

@router.post("/analyze-url", response_model=URLAnalysisResult)
async def analyze_url(request: URLRequest):
    """
    Scrape a product from a URL and analyze its AI visibility
    """
    try:
        search_service = get_search_service()
        scraped_details = search_service.fetch_product_details(request.url)
        
        if not scraped_details["title"] and not scraped_details["description"]:
            raise HTTPException(status_code=400, detail="Could not extract any product information from this URL. Please ensure it's a valid Amazon or Flipkart product page.")
        
        if not scraped_details.get("title") or len(scraped_details["title"]) < 2:
            scraped_details["title"] = "Unknown Product"
            
        if not scraped_details.get("description") or len(scraped_details["description"]) < 10:
            scraped_details["description"] = "No detailed description available for this product page."
            
        # Try to guess brand and category if possible, or use defaults
        brand = "Extracted Brand"
        # Basic brand extraction from title
        if " " in scraped_details["title"]:
            brand = scraped_details["title"].split(" ")[0]
            
        product = ProductInput(
            title=scraped_details["title"],
            description=scraped_details["description"],
            category="Extracted Category",
            brand=brand,
            image_url=scraped_details.get("image_url")
        )
        
        # Now analyze it
        analysis = await analyze_product(product)
        
        return URLAnalysisResult(
            scraped_data=product,
            analysis=analysis
        )
    except HTTPException:
        # Re-raise HTTPExceptions (like the 400 we raise above)
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL analysis failed: {str(e)}")

@router.post("/deep-compare")
async def deep_compare(request: RankingRequest):
    """
    Perform deep technical comparison of products using Gemini URL Context
    """
    try:
        intelligence = get_intelligence_service()
        user_url = request.product.url or ""
        comp_urls = [c.url for c in request.competitors if c.url]
        
        if not user_url or not comp_urls:
            return {"comparison": "Missing URLs for deep comparison."}
            
        comparison_text = intelligence.deep_compare_competitors(user_url, comp_urls)
        return {"comparison": comparison_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deep comparison failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Visibility Platform"}
