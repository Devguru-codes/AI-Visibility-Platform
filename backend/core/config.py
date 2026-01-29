import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    """Application configuration settings"""
    
    # API Configuration
    API_TITLE = "AI Visibility Platform"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "Analyze and optimize product discoverability for AI search engines"
    
    # ML Model Configuration
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Scoring Weights (must sum to 1.0)
    WEIGHT_SEMANTIC = 0.4
    WEIGHT_KEYWORD = 0.2
    WEIGHT_COMPLETENESS = 0.2
    WEIGHT_READABILITY = 0.2
    
    # LLM Configuration
    MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "gemini") # 'openai', 'huggingface', or 'gemini'
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL = "gpt-4o"
    HF_API_KEY: Optional[str] = os.getenv("HF_API_KEY", "")
    HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 2500
    
    # Search & Competitor Configuration
    SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "duckduckgo") # 'duckduckgo' or 'serper'
    SERPER_API_KEY: Optional[str] = os.getenv("SERPER_API_KEY", "")
    MAX_COMPETITORS = 10
    
    # AI Query Templates
    AI_QUERY_TEMPLATES = [
        "Best {category} for {use_case}",
        "Top rated {category}",
        "Affordable {category}",
        "{category} with {feature}",
        "High quality {category}",
        "Professional {category}",
        "{brand} {category} review",
    ]
    
    # Completeness Check Keywords
    COMPLETENESS_KEYWORDS = [
        "specifications", "specs", "features", "dimensions", "weight",
        "material", "color", "size", "warranty", "compatibility",
        "battery", "power", "capacity", "performance", "quality",
        "use case", "application", "suitable for", "ideal for",
        "technical", "highlights", "overview", "included", "package",
        "design", "technology", "engineered", "certified"
    ]
    
    # Readability Thresholds
    MIN_DESCRIPTION_LENGTH = 50
    MAX_DESCRIPTION_LENGTH = 5000 # Increased for long professional descriptions
    TARGET_READABILITY_SCORE = 60  # Flesch Reading Ease

    # UI Options
    COMMON_CATEGORIES = [
        "Headphones", "Smartphones", "Laptops", "Smartwatches", 
        "Cameras", "Speakers", "Tablets", "Televisions",
        "Gaming Consoles", "Kitchen Appliances", "Fitness Trackers"
    ]

settings = Settings()
