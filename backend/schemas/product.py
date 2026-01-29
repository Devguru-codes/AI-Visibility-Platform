from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ProductInput(BaseModel):
    """Input schema for product analysis"""
    title: str = Field(..., min_length=1, description="Product title")
    description: str = Field(..., min_length=10, description="Product description")
    category: str = Field(..., min_length=1, description="Product category")
    brand: str = Field(..., min_length=1, description="Product brand")
    platform: Optional[str] = None
    url: Optional[str] = None
    market_rank: Optional[int] = None
    image_url: Optional[str] = None
    price: Optional[float] = Field(None, description="Product price for competitive benchmarking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sony WH-1000XM5 Wireless Headphones",
                "description": "Premium noise cancelling headphones with 30-hour battery life",
                "category": "Headphones",
                "brand": "Sony"
            }
        }

class ScoreBreakdown(BaseModel):
    """Detailed score breakdown"""
    semantic_relevance: float = Field(..., ge=0, le=100)
    keyword_coverage: float = Field(..., ge=0, le=100)
    completeness: float = Field(..., ge=0, le=100)
    readability: float = Field(..., ge=0, le=100)

class WeaknessAnalysis(BaseModel):
    """Analysis of product description weaknesses"""
    missing_specs: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    clarity_issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

class SentimentResult(BaseModel):
    """Pros and Cons extracted from a product"""
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)

class AnalysisResult(BaseModel):
    """Complete analysis result for a product"""
    product: ProductInput
    ai_visibility_score: float = Field(..., ge=0, le=100, description="Overall AI visibility score")
    score_breakdown: ScoreBreakdown
    weakness_analysis: WeaknessAnalysis
    generated_queries: List[str] = Field(default_factory=list, description="AI queries used for analysis")
    sentiment: Optional[SentimentResult] = None
    ai_recommendation: Optional[Dict] = Field(None, description="AI recommendation simulation results")

class RankingRequest(BaseModel):
    """Request to rank product against competitors"""
    product: ProductInput
    competitors: List[ProductInput] = Field(..., min_length=1, description="Competitor products")

class RankedProduct(BaseModel):
    """Product with its ranking information"""
    product: ProductInput
    score: float
    rank: int # AI Visibility Rank
    market_rank: Optional[int] = None # Original Marketplace Rank
    platform: Optional[str] = None
    url: Optional[str] = None
    sentiment: Optional[SentimentResult] = None

class RankingResult(BaseModel):
    """Result of product ranking"""
    your_product: RankedProduct
    all_products: List[RankedProduct]
    total_products: int

class OptimizationRequest(BaseModel):
    """Request to optimize product description"""
    product: ProductInput
    target_queries: Optional[List[str]] = Field(default=None, description="Specific queries to optimize for")
    additional_specs: Optional[str] = Field(default=None, description="Additional user-provided specifications")
    provider: Optional[str] = Field(default="gemini", description="LLM provider to use")

class OptimizationResult(BaseModel):
    """Result of description optimization"""
    original_product: ProductInput
    optimized_description: str
    original_score: float
    optimized_score: float
    improvements: List[str] = Field(default_factory=list)
    score_delta: float

class URLRequest(BaseModel):
    """Request to analyze a product via URL"""
    url: str = Field(..., description="Amazon or Flipkart product URL")

class URLAnalysisResult(BaseModel):
    """Result of product analysis via URL"""
    scraped_data: ProductInput
    analysis: AnalysisResult
