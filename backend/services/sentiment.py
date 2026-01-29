from google import genai
from typing import List, Dict, Optional
import json
from core.config import settings
from schemas.product import ProductInput

class SentimentService:
    """Service for analyzing sentiment and extracting pros/cons from product descriptions (New SDK)"""
    
    def __init__(self):
        self.client = None
        if settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                print(f"Failed to initialize Gemini Client: {e}")
            
    def analyze_product_sentiment(self, product: ProductInput) -> Dict[str, List[str]]:
        """
        Extract Pros and Cons from product description using AI
        """
        if not self.client:
            # Fallback for no API key
            return {"pros": ["High quality features"], "cons": ["None identified"]}
            
        if not product.description or "no description available" in product.description.lower():
            if len(product.title) > 20:
                # Try analyzing just the title if it's long
                description_to_analyze = product.title
            else:
                return {
                    "pros": ["Professional Branding"],
                    "cons": ["Detailed description missing - provide more specs for better AI insights"]
                }
        else:
            description_to_analyze = product.description

        prompt = f"""
        Analyze this product and extract the top 3-5 'Pros' (Strengths) and top 1-2 'Gaps' (Implicit Gaps).
        Focus on technical specifications, quality, and user value.
        
        Product Title: {product.title}
        Context/Description: {description_to_analyze}
        
        Return the result as a JSON object with 'pros' and 'cons' keys.
        Example: {{"pros": ["30h battery", "Noise cancelling"], "cons": ["Heavy weight"]}}
        Provide ONLY the JSON and nothing else.
        """
        
        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )
            
            # Basic JSON extraction from response
            text = response.text.strip() if response and response.text else "{}"
            if "```json" in text:
                text = text.split("```json")[-1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[-1].split("```")[0].strip()
            
            # Remove any non-JSON characters if LLM adds them
            if text.startswith("json"): text = text[4:].strip()
                
            data = json.loads(text or "{}")
            return {
                "pros": data.get("pros", ["Feature rich"]),
                "cons": data.get("cons", ["Technical gaps"])
            }
        except Exception as e:
            print(f"Sentiment analysis failed: {e}")
            return {"pros": ["High product relevance"], "cons": ["Detailed specs recommended"]}

# Global instance
_sentiment_service = None

def get_sentiment_service() -> SentimentService:
    global _sentiment_service
    if _sentiment_service is None:
        _sentiment_service = SentimentService()
    return _sentiment_service
