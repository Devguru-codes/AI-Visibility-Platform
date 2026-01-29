import re
from typing import List, Set
import textstat
from core.config import settings
from schemas.product import ProductInput, ScoreBreakdown, WeaknessAnalysis
from services.embedder import get_embedding_service

class ScoringService:
    """Service for scoring product descriptions"""
    
    def __init__(self):
        self.embedder = get_embedding_service()
        
    def generate_ai_queries(self, product: ProductInput) -> List[str]:
        """
        Generate AI search queries based on product information
        
        Args:
            product: Product input
            
        Returns:
            List of generated queries
        """
        queries = []
        
        # Use templates from config
        for template in settings.AI_QUERY_TEMPLATES:
            query = template.format(
                category=product.category,
                brand=product.brand,
                use_case="daily use",
                feature="best features"
            )
            queries.append(query)
        
        # Add specific queries
        queries.extend([
            f"{product.category}",
            f"{product.brand} {product.category}",
            f"best {product.category}",
            f"top {product.category} brands",
        ])
        
        return queries
    
    def calculate_semantic_relevance(self, product: ProductInput, queries: List[str]) -> float:
        """
        Calculate semantic relevance score with support for long descriptions
        Boosts score significantly if the product name/brand matches queries (Self-Visibility)
        """
        product_text = f"{product.title}. {product.description}"
        
        # Self-Visibility Check: If our title is highly visible in our own search, we should have 100
        # However, this is calculated against generic queries. 
        # For now, we adjust the scaling to be more generous.
        
        chunks = []
        words = product_text.split()
        chunk_size = 200 # roughly 200-300 tokens
        
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i + chunk_size]))
            
        if not chunks:
            return 0.0
            
        all_chunk_similarities = []
        for chunk in chunks:
            similarities = self.embedder.compute_similarity_batch(chunk, queries)
            all_chunk_similarities.append(sum(similarities) / len(similarities))
            
        max_similarity = max(all_chunk_similarities)
        avg_similarity = sum(all_chunk_similarities) / len(all_chunk_similarities)
        
        # Professional listings often have high technical density.
        # We use a non-linear scaling to reward high similarity.
        top_similarity = (max_similarity * 0.8) + (avg_similarity * 0.2)
        
        # Scaling: 0.6 similarity -> 100 score (highly relevant)
        score = (top_similarity / 0.6) * 100
        
        # Boost if title contains the category or brand strongly
        if product.brand.lower() in product.title.lower():
            score += 10
            
        return min(100, max(0, score))
    
    def calculate_keyword_coverage(self, product: ProductInput) -> float:
        """
        Calculate keyword coverage score
        
        Args:
            product: Product input
            
        Returns:
            Score between 0 and 100
        """
        description_lower = product.description.lower()
        
        # Check for important keywords
        important_keywords = [
            product.category.lower(),
            product.brand.lower(),
            "quality", "premium", "best", "top",
            "features", "specifications", "performance",
            "technology", "design", "professional", "benefits"
        ]
        
        # Count keyword occurrences
        found_keywords = sum(1 for kw in important_keywords if kw in description_lower)
        coverage = (found_keywords / len(important_keywords)) * 100
        
        return min(100, max(0, coverage))
    
    def calculate_completeness(self, product: ProductInput) -> float:
        """
        Calculate completeness score based on presence of key information concepts
        """
        text_to_check = f"{product.title} {product.description}".lower()
        
        # More robust concepts for technical products
        concepts = {
            "battery": ["battery", "mah", "runtime", "hours", "charging", "powered by", "h playback", "playtime"],
            "dimensions": ["mm", "cm", "inch", "x", "folded", "compact", "size", "dimensions"],
            "material": ["leather", "carbon fiber", "plastic", "metal", "aluminum", "steel", "fabric", "silicone", "premium"],
            "warranty": ["warranty", "guarantee", "year", "month", "protection"],
            "connectivity": ["bluetooth", "wireless", "nfc", "ldac", "wifi", "cable", "jack", "aux", "5.0", "5.3"],
            "performance": ["fast", "speed", "processor", "optimized", "high fidelity", "noise cancel", "hz", "khz", "anc"]
        }
        
        found_concepts = 0
        for concept, triggers in concepts.items():
            if any(trigger in text_to_check for trigger in triggers):
                found_concepts += 1
                
        # Length check: Professional listings are 1000+ words
        target_len = 2000
        length_score = min(100, (len(product.description) / target_len) * 100)
        
        # Concept variety score (the most important part)
        concept_score = (found_concepts / len(concepts)) * 100
        
        # Keyword Presence
        keyword_overlap = sum(1 for kw in settings.COMPLETENESS_KEYWORDS if kw in text_to_check)
        keyword_score = (keyword_overlap / len(settings.COMPLETENESS_KEYWORDS)) * 100
        
        # Final combined score: Break the 62 ceiling by weighting technical detail higher
        score = (concept_score * 0.7) + (keyword_score * 0.1) + (length_score * 0.2)
        
        # Bonus for structured data (bullet points)
        if "•" in product.description or "-" in product.description or ":" in product.description:
            score += 15
            
        return min(100, max(0, score))
    
    def calculate_readability(self, product: ProductInput) -> float:
        """
        Calculate e-commerce optimized readability score
        """
        description = product.description
        
        try:
            flesch_score = textstat.flesch_reading_ease(description)
            
            # Professional product listings are often technical (Flesch 30-50)
            # We don't want to penalize them too much.
            if flesch_score < 0:
                normalized_score = 10 # very hard but not 0
            elif flesch_score < 30:
                normalized_score = 40 + (flesch_score / 30) * 10 # 40-50 range
            else:
                normalized_score = 50 + ((flesch_score - 30) / 70) * 50 # 50-100 range
                
            # Bonus for professional structure (bullet points)
            if "•" in description or "-" in description or ":" in description:
                normalized_score += 10
                
        except:
            normalized_score = 50
        
        return min(100, max(0, normalized_score))
    
    def extract_features(self, title: str, description: str) -> List[str]:
        """
        Extract key features from product text using robust rule-based logic.
        Used for the 'Compare Features' table.
        """
        text = f"{title} {description}".lower()
        features = []
        
        # Feature Mapping (User complained these were missing)
        mapping = {
            "wireless": ["wireless", "cordless", "wifi", "radio frequency"],
            "bluetooth": ["bluetooth", "bt 5", "5.0", "5.1", "5.2", "5.3", "ldac"],
            "noise cancel": ["noise cancel", "anc", "digital noise", "isolation", "qn1", "qn3"],
            "fast charge": ["fast charge", "quick charge", "pd charge", "3 min", "5 min"],
            "battery life": ["hours", "h playback", "runtime", "playtime", "battery"],
            "material": ["leather", "carbon fiber", "metal", "aluminum", "fabric"],
            "design": ["folded", "swivel", "foldable", "compact", "carrying case"]
        }
        
        for feature, triggers in mapping.items():
            if any(trigger in text for trigger in triggers):
                features.append(feature)
                
        return features

    def analyze_weaknesses(self, product: ProductInput, score_breakdown: ScoreBreakdown) -> WeaknessAnalysis:
        """
        Analyze weaknesses in product description
        
        Args:
            product: Product input
            score_breakdown: Score breakdown
            
        Returns:
            Weakness analysis
        """
        missing_specs = []
        missing_keywords = []
        clarity_issues = []
        suggestions = []
        
        description_lower = product.description.lower()
        
        # Smarter Check for missing concepts
        concepts_to_check = {
            "specifications/battery": ["battery", "mah", "runtime", "hours", "charging", "powered by"],
            "dimensions/size": ["mm", "cm", "inch", "folded", "compact", "size"],
            "weight": ["weight", "grams", " kg", "lbs", "lightweight"],
            "material": ["leather", "carbon fiber", "plastic", "metal", "aluminum", "steel", "fabric", "silicone"],
            "warranty": ["warranty", "guarantee", "protection"]
        }
        
        for concept, triggers in concepts_to_check.items():
            if not any(trigger in description_lower for trigger in triggers):
                missing_specs.append(concept.split("/")[0])
        
        # Check for missing important keywords
        important_kw = ["quality", "features", "benefits", "use case"]
        for kw in important_kw:
            if kw not in description_lower:
                missing_keywords.append(kw)
        
        # Clarity issues
        if len(product.description) < settings.MIN_DESCRIPTION_LENGTH:
            clarity_issues.append("Description too short")
            suggestions.append("Expand description with more details")
        
        if score_breakdown.semantic_relevance < 50:
            suggestions.append("Add more context about product use cases and benefits")
        
        if score_breakdown.keyword_coverage < 50:
            suggestions.append(f"Include more keywords related to {product.category}")
        
        if score_breakdown.completeness < 50:
            suggestions.append("Add specifications and technical details")
        
        if score_breakdown.readability < 50:
            suggestions.append("Simplify language for better readability")
        
        return WeaknessAnalysis(
            missing_specs=missing_specs,
            missing_keywords=missing_keywords,
            clarity_issues=clarity_issues,
            suggestions=suggestions
        )
    
    def calculate_final_score(self, score_breakdown: ScoreBreakdown) -> float:
        """
        Calculate final weighted score
        
        Args:
            score_breakdown: Individual score components
            
        Returns:
            Final score between 0 and 100
        """
        final_score = (
            score_breakdown.semantic_relevance * settings.WEIGHT_SEMANTIC +
            score_breakdown.keyword_coverage * settings.WEIGHT_KEYWORD +
            score_breakdown.completeness * settings.WEIGHT_COMPLETENESS +
            score_breakdown.readability * settings.WEIGHT_READABILITY
        )
        
        return round(final_score, 2)
    
    def score_product(self, product: ProductInput) -> tuple[float, ScoreBreakdown, List[str]]:
        """
        Complete scoring of a product
        
        Args:
            product: Product input
            
        Returns:
            Tuple of (final_score, score_breakdown, generated_queries)
        """
        # Generate AI queries
        queries = self.generate_ai_queries(product)
        
        # Calculate individual scores
        semantic_score = self.calculate_semantic_relevance(product, queries)
        keyword_score = self.calculate_keyword_coverage(product)
        completeness_score = self.calculate_completeness(product)
        readability_score = self.calculate_readability(product)
        
        # Create breakdown
        score_breakdown = ScoreBreakdown(
            semantic_relevance=semantic_score,
            keyword_coverage=keyword_score,
            completeness=completeness_score,
            readability=readability_score
        )
        
        # Calculate final score
        final_score = self.calculate_final_score(score_breakdown)
        
        return final_score, score_breakdown, queries

# Global instance
_scoring_service = None

def get_scoring_service() -> ScoringService:
    """Get or create the global scoring service instance"""
    global _scoring_service
    if _scoring_service is None:
        _scoring_service = ScoringService()
    return _scoring_service
