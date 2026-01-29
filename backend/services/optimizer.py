from typing import List, Optional
import os
from openai import OpenAI
from google import genai
from google.genai import types
import requests
from schemas.product import ProductInput
from core.config import settings

class OptimizerService:
    """Service for optimizing product descriptions using LLM (Updated to new SDK)"""
    
    def __init__(self):
        self.openai_client = None
        self.gemini_client = None
        self.hf_api_url = f"https://api-inference.huggingface.co/models/{settings.HF_MODEL}"
        self.hf_headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"} if settings.HF_API_KEY else {}
        
        if settings.MODEL_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        elif settings.MODEL_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            try:
                self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                print(f"Failed to initialize Gemini Client: {e}")
    
    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Call Google Gemini API using the new google-genai SDK"""
        if not self.gemini_client:
            return None
            
        try:
            config = types.GenerateContentConfig(
                temperature=settings.LLM_TEMPERATURE,
                max_output_tokens=settings.LLM_MAX_TOKENS
            )
            response = self.gemini_client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=config
            )
            return response.text.strip() if response and response.text else None
        except Exception as e:
            print(f"Gemini API call failed: {e}")
            return None

    def _call_hf_api(self, prompt: str) -> Optional[str]:
        """Call Hugging Face Inference API"""
        if not settings.HF_API_KEY:
            return None
            
        try:
            payload = {
                "inputs": f"<s>[INST] {prompt} [/INST]",
                "parameters": {
                    "max_new_tokens": settings.LLM_MAX_TOKENS,
                    "temperature": settings.LLM_TEMPERATURE
                }
            }
            response = requests.post(self.hf_api_url, headers=self.hf_headers, json=payload, timeout=20)
            response.raise_for_status()
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                # Strip the prompt if the model returns it
                if "[/INST]" in generated_text:
                    return generated_text.split("[/INST]")[-1].strip()
                return generated_text.strip()
            return None
        except Exception as e:
            print(f"HF API call failed: {e}")
            return None

    def optimize_description(
        self, 
        product: ProductInput,
        weakness_suggestions: List[str],
        target_queries: Optional[List[str]] = None,
        additional_specs: Optional[str] = None,
        provider: Optional[str] = None
    ) -> tuple[str, List[str]]:
        """
        Optimize product description using LLM (OpenAI, HF, or Gemini)
        """
        # Build optimization prompt
        prompt = self._build_optimization_prompt(product, weakness_suggestions, target_queries, additional_specs)
        
        optimized_description = None
        
        # Determine provider
        active_provider = provider or settings.MODEL_PROVIDER
        
        # Try configured provider
        if active_provider == "gemini" and settings.GEMINI_API_KEY:
            optimized_description = self._call_gemini_api(prompt)
        elif active_provider == "huggingface" and settings.HF_API_KEY:
            optimized_description = self._call_hf_api(prompt)
        elif self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert e-commerce copywriter."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS
                )
                optimized_description = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI call failed: {e}")

        # Fallback to rule-based if LLMs fail or aren't configured
        if not optimized_description:
            return self._rule_based_optimization(product, weakness_suggestions)
            
        # Extract improvements made
        improvements = self._extract_improvements(product.description, optimized_description)
        
        return optimized_description, improvements
    
    def _build_optimization_prompt(
        self,
        product: ProductInput,
        suggestions: List[str],
        target_queries: Optional[List[str]],
        additional_specs: Optional[str] = None
    ) -> str:
        """Build the optimization prompt for LLM"""
        
        prompt = f"""You are an expert AI Visibility Optimizer. Your goal is to rewrite the product description to maximize its ranking in AI-driven search engines (like Perplexity, Gemini, ChatGPT).

**Product Information:**
- Title: {product.title}
- Category: {product.category}
- Brand: {product.brand}
- Current Description: {product.description}
"""

        if additional_specs:
            prompt += f"\n**User Provided Specifications:**\n{additional_specs}\n"

        prompt += f"""
**Optimization Goals (Must Address):**
{chr(10).join(f"- {s}" for s in suggestions)}

**Strict Requirements:**
1. **LENGTH**: You MUST generate at least 400-600 words of technical, dense content. Do not stop early.
2. **SPECS**: Prioritize and integrate ALL "User Provided Specifications" listed above. They are critical.
3. **DO NOT SIMPLIFY**: Keep every technical detail from the current description and expand upon it.
4. **STRUCTURE**: Use exactly these markdown headers: '# Overview', '## Key Features', '## Technical Specifications', '## AI Search Optimization Benefits'.
5. **FORMATTING**: Use bullet points for all features and specifications.
6. **CONTENT**: If the product is '{product.title}', explain why it is the definitive choice in the '{product.category}' category.
"""
        
        if target_queries:
            prompt += f"""
**Directly answer these AI search queries within the text to ensure high visibility:**
{chr(10).join(f"- {q}" for q in target_queries)}
"""
        
        prompt += "\nProvide ONLY the detailed, optimized markdown-formatted description. No conversational filler. Start with the # Overview header."
        
        return prompt
    
    def _rule_based_optimization(
        self,
        product: ProductInput,
        suggestions: List[str]
    ) -> tuple[str, List[str]]:
        """
        Fallback rule-based optimization when LLM is not available
        """
        optimized = product.description
        improvements = []
        
        # Add category and brand if not present
        if product.category.lower() not in optimized.lower():
            optimized = f"{product.category}: {optimized}"
            improvements.append("Added category context")
        
        if product.brand.lower() not in optimized.lower():
            optimized = f"{product.brand} {optimized}"
            improvements.append("Added brand name")
        
        # Add generic improvements based on suggestions
        additions = []
        
        if any("specification" in s.lower() for s in suggestions):
            additions.append("Features high-quality materials and construction.")
            improvements.append("Added quality indicators")
        
        if any("use case" in s.lower() for s in suggestions):
            additions.append("Ideal for daily use and professional applications.")
            improvements.append("Added use case information")
        
        if any("keyword" in s.lower() for s in suggestions):
            additions.append(f"Top-rated {product.category.lower()} with premium features.")
            improvements.append("Added relevant keywords")
        
        if additions:
            optimized = f"{optimized} {' '.join(additions)}"
        
        return optimized, improvements
    
    def _extract_improvements(self, original: str, optimized: str) -> List[str]:
        """
        Extract what improvements were made
        """
        improvements = []
        
        # Length comparison
        if len(optimized) > len(original) * 1.2:
            improvements.append("Expanded description with more details")
        
        # Check for added keywords
        keywords = ["specifications", "features", "quality", "premium", "professional", "ideal for"]
        for kw in keywords:
            if kw in optimized.lower() and kw not in original.lower():
                improvements.append(f"Added '{kw}' context")
        
        if not improvements:
            improvements.append("Enhanced overall clarity and structure")
        
        return improvements

# Global instance
_optimizer_service = None

def get_optimizer_service() -> OptimizerService:
    """Get or create the global optimizer service instance"""
    global _optimizer_service
    if _optimizer_service is None:
        _optimizer_service = OptimizerService()
    return _optimizer_service
