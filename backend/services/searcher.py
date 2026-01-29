from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0 # For consistent results
from core.config import settings
from schemas.product import ProductInput

class SearchService:
    """Service for searching products and competitors online"""
    
    def __init__(self):
        self.ddgs = DDGS()
        
    def search_competitors(self, product_name: str, category: str, exclude_brand: Optional[str] = None, price: Optional[float] = None) -> List[Dict[str, str]]:
        """
        Search for top competitors specifically on Amazon and Flipkart using strict product page filtering.
        """
        results = []
        
        # Determine price ceiling for "under X" queries
        price_query_part = ""
        if price:
            # Round to nearest 1000, e.g. 27611 -> 28000
            rounded_price = int(round(price / 1000.0) * 1000)
            if rounded_price == 0: rounded_price = 1000
            price_query_part = f"under {rounded_price}"
        
        # Platforms to search
        platforms = [
            {"name": "Amazon", "site": "amazon.in", "url_patterns": ["/dp/", "/gp/product/"]},
            {"name": "Flipkart", "site": "flipkart.com", "url_patterns": ["/p/"]}
        ]
        
        for platform in platforms:
            # User Algorithm: "best {product type} under {price}"
            base_query = f"best {category}"
            if price_query_part:
                base_query += f" {price_query_part}"
            
            query = f"{base_query} site:{platform['site']}"
            print(f"Executing search: {query}")
            
            try:
                # Fetch more results to allow for filtering
                search_results = self.ddgs.text(query, region="in-en", max_results=15)
                
                platform_count = 0
                for res in search_results:
                    if platform_count >= 5: # Top 5 per platform
                        break
                        
                    url = res.get("href", "").lower()
                    title = res.get("title", "")
                    
                    # STRICT URL PATTERN CHECK
                    # Only accept URLs that look like actual product pages
                    is_product_page = False
                    for pattern in platform['url_patterns']:
                        if pattern in url:
                            is_product_page = True
                            break
                    
                    # Skip if not a product page (likely a category page like /b/ or /s)
                    if not is_product_page:
                        continue
                        
                    # Exclude user's own brand
                    if exclude_brand and exclude_brand.lower() in title.lower():
                        continue
                        
                    # Title Cleaning
                    clean_title = title
                    # Remove Platform Suffixes
                    clean_title = clean_title.replace("Amazon.in", "").replace("Flipkart.com", "").replace("Flipkart", "").replace("Amazon", "")
                    # Remove common prefixes
                    clean_title = clean_title.replace("Buy ", "").replace("Online at Best Price", "").strip()
                    # Remove separators
                    clean_title = clean_title.split("|")[0].split(":")[0].strip()
                    # Remove leading/trailing punctuation
                    clean_title = clean_title.strip(" -:.,")
                    
                    results.append({
                        "title": clean_title,
                        "url": res.get("href", ""),
                        "snippet": res.get("body", ""),
                        "platform": platform["name"]
                    })
                    platform_count += 1
                    
            except Exception as e:
                print(f"Search failed for {platform['name']}: {e}")
                
        return results

    def _deduplicate_results(self, results: List[Dict[str, str]], target_product: str) -> List[Dict[str, str]]:
        """Filter out product variants and near-duplicates"""
        seen_titles_normalized = set()
        unique_results = []
        
        target_words = set(target_product.lower().split())
        
        for res in results:
            title = res["title"].lower()
            # Remove common variant markers
            for marker in ["(black)", "(white)", "(blue)", "(green)", "(red)", " 128gb", " 256gb", " 512gb", " 8gb", " 16gb", "midnight", "starlight"]:
                title = title.replace(marker, "")
            
            # Simple content overlap check
            words = set(title.split()[:7]) # Focus on first 7 words
            words_tuple = tuple(sorted(list(words)))
            
            # IDENTITY LOCK: If it contains many words from the target product, it might be a duplicate
            overlap_with_target = len(words.intersection(target_words))
            if overlap_with_target > 2 and len(target_words) > 1:
                # If it's the target product, we only keep the FIRST occurrence found in search
                # for market rank calculation, but we'll mark it later in the UI
                pass

            if words_tuple not in seen_titles_normalized:
                seen_titles_normalized.add(words_tuple)
                unique_results.append(res)
                
        return unique_results

    def fetch_product_details(self, url: str) -> Dict[str, str]:
        """
        Attempt to fetch product details from a URL
        Note: This is a basic scraper and might be blocked by major sites
        """
        details = {"title": "", "description": "", "image_url": ""}
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.google.com/"
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            
            # 1. Image Extraction
            # Amazon
            img_tag = soup.select_one("#landingImage, #imgBlkFront, #main-image")
            if img_tag:
                details["image_url"] = img_tag.get("src") or img_tag.get("data-old-hires") or img_tag.get("data-a-dynamic-image")
                if details["image_url"] and details["image_url"].startswith("{"):
                    # Amazon dynamic image JSON
                    try:
                        import json
                        img_data = json.loads(details["image_url"])
                        details["image_url"] = list(img_data.keys())[0]
                    except: pass
            
            # Flipkart
            if not details["image_url"]:
                fk_img = soup.select_one("._396cs4, ._2r_T1_, img[src*='flipkart.com/image']")
                if fk_img:
                    details["image_url"] = fk_img.get("src")

            # 2. Improved Extraction for Amazon Bullet Points and Features
            feature_bullets = soup.select("#feature-bullets ul li span")
            if feature_bullets:
                bullets_text = " ".join([b.get_text().strip() for b in feature_bullets if len(b.get_text().strip()) > 5])
                details["description"] += f" Features: {bullets_text}"
            
            # 3. A+ Content / Product Description Section
            aplus_content = soup.select(".aplus-v2, #productDescription, .description, #aplus")
            if aplus_content:
                aplus_text = " ".join([a.get_text().strip() for a in aplus_content])
                details["description"] += f" Detail: {aplus_text[:2000]}"
            
            # 4. Clean up
            details["description"] = details["description"].strip()
            
            # Stronger Fallback for description
            if not details["description"]:
                # Try meta description
                meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
                if meta_desc:
                    details["description"] = meta_desc.get("content", "").strip()
            
            # Last resort: paragraphs
            if not details["description"] or len(details["description"]) < 50:
                details["description"] += " " + " ".join([p.get_text() for p in soup.find_all("p")[:5]]).strip()
                
            # Title
            title_tag = soup.select_one("#productTitle, ._35KyD6, h1, .B_NuCI")
            if title_tag:
                details["title"] = title_tag.get_text().strip()
            elif soup.title:
                details["title"] = soup.title.string.strip() if soup.title.string else ""
                
        except Exception as e:
            print(f"Scraping failed for {url}: {e}")
            
        return details

    def get_automated_competitors(self, product: ProductInput) -> List[ProductInput]:
        """
        Automatically find and fetch competitor data
        """
        search_results = self.search_competitors(product.title, product.category, exclude_brand=product.brand, price=product.price)
        competitors = []
        
        for i, res in enumerate(search_results, start=1):
            # For this MVP, we use the search snippet as the description 
            # if scraping is blocked or fails
            comp_desc = res["snippet"]
            
            # Clean up snippet
            if len(comp_desc) < 50:
                comp_desc = f"Top rated {product.category} from {res['title']}. {res['snippet']}"
                
            competitors.append(ProductInput(
                title=res["title"],
                description=comp_desc,
                category=product.category,
                brand="Top Competitor",
                platform=res.get("platform"),
                url=res.get("url"),
                market_rank=i
            ))
            
        return competitors

    def extract_features(self, text: str) -> List[str]:
        """Simple feature extraction from text"""
        # Look for bullet points or comma separated features
        features = []
        # Keywords that often precede features
        keywords = ["features:", "specs:", "key specs:", "highlights:", "benefits:"]
        text_lower = text.lower()
        
        for kw in keywords:
            if kw in text_lower:
                part = text_lower.split(kw)[1].split("\n")[0]
                extracted = [f.strip() for f in part.split(",") if len(f.strip()) > 3]
                features.extend(extracted[:5])
        
        # If none found, look for common tech terms
        tech_terms = ["bluetooth", "battery", "waterproof", "noise cancel", "wireless", "hd", "4k", "oled"]
        for term in tech_terms:
            if term in text_lower and term not in features:
                features.append(term)
                
        return features[:10]

# Global instance
_search_service = None

def get_search_service() -> SearchService:
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
