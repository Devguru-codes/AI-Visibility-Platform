from google import genai
from google.genai import types
from typing import List, Dict, Optional
import json
from core.config import settings
from schemas.product import ProductInput

class IntelligenceService:
    """Advanced AI Intelligence Service using the new google-genai SDK for Grounding and Intelligence"""
    
    def __init__(self):
        self.client = None
        if settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                print(f"Failed to initialize Gemini Client: {e}")
            
    def simulate_ai_recommendation(self, product: ProductInput, price: Optional[float] = None) -> Dict:
        """
        Simulate an AI recommendation using Google Search Grounding (New SDK).
        """
        if not self.client:
             return {"recommendation_text": "AI Client unavailable.", "is_recommended": False, "found_brand": False, "found_product": False, "sources": []}

        region = "India"
        price_context = f"under ₹{price}" if price else ""
        
        prompt = f"Recommend 5 top products for {product.category} in {region} {price_context}. Check specifically for '{product.brand}' and '{product.title}'."
        
        try:
            # Setup Grounding Tool using new SDK types
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            config = types.GenerateContentConfig(tools=[grounding_tool])
            
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=config
            )
            
            text = response.text or "No response text available."
            found_brand = product.brand.lower() in text.lower()
            found_product = product.title.lower() in text.lower()
            
            # Extract sources from new grounding metadata structure
            sources = []
            if response.candidates and response.candidates[0].grounding_metadata:
                metadata = response.candidates[0].grounding_metadata
                if metadata.grounding_chunks:
                    for chunk in metadata.grounding_chunks:
                        if chunk.web and chunk.web.uri:
                            sources.append(chunk.web.uri)
            
            return {
                "recommendation_text": text,
                "is_recommended": found_brand or found_product,
                "found_brand": found_brand,
                "found_product": found_product,
                "sources": list(set(sources))
            }
        except Exception as e:
            print(f"AI Recommendation Simulation failed: {e}")
            # Robust Fallback to 1.5-flash without grounding if the latest model/tool fails
            try:
                fallback_res = self.client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                )
                fallback_text = fallback_res.text or ""
                return {
                    "recommendation_text": fallback_text + f"\n\n(Grounding failed: {str(e)})",
                    "is_recommended": product.brand.lower() in fallback_text.lower(),
                    "found_brand": product.brand.lower() in fallback_text.lower(),
                    "found_product": product.title.lower() in fallback_text.lower(),
                    "sources": []
                }
            except:
                return {
                    "recommendation_text": f"Simulation failed: {str(e)}",
                    "is_recommended": False,
                    "found_brand": False,
                    "found_product": False,
                    "sources": []
                }

    def deep_compare_competitors(self, user_url: str, competitor_urls: List[str]) -> str:
        """
        Perform deep competitor comparison using Gemini (New SDK).
        """
        if not self.client:
            return "AI Client unavailable."
            
        if not competitor_urls:
            return "No competitor URLs provided for comparison."
            
        target_urls = competitor_urls[:2]
        urls_str = ", ".join([user_url] + target_urls)
        
        prompt = f"""
        Analyze and compare the products at these URLs: {urls_str}
        Perform a deep technical comparison of their specs, features, and overall value.
        Highlight which one is superior for professional use and why.
        """
        
        try:
            # Using grounding even for comparison to ensure model visits the URLs
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            config = types.GenerateContentConfig(tools=[grounding_tool])
            
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=config
            )
            return response.text or "Comparison failed to generate text."
        except Exception as e:
            print(f"Deep comparison failed: {e}")
            return f"Comparison failed: {str(e)}"

# Global instance
_intelligence_service = None

def get_intelligence_service() -> IntelligenceService:
    global _intelligence_service
    if _intelligence_service is None:
        _intelligence_service = IntelligenceService()
    return _intelligence_service
