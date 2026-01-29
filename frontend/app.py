import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8001/api"

# Page config
st.set_page_config(
    page_title="AI Visibility Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        font-size: 1.1rem;
        border-radius: 5px;
        transition: all 0.3s;
    }
    .glass-card {
        background: #f8fafc;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        padding: 15px;
        margin-bottom: 10px;
    }
    .sentiment-pro { color: #059669; font-weight: bold; margin-right: 5px; }
    .sentiment-con { color: #dc2626; font-weight: bold; margin-right: 5px; }
</style>
""", unsafe_allow_html=True)

def create_gauge_chart(score: float, title: str) -> go.Figure:
    """Create a gauge chart for score visualization"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#ffcccc'},
                {'range': [30, 60], 'color': '#fff4cc'},
                {'range': [60, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

def create_score_breakdown_chart(breakdown: Dict[str, float]) -> go.Figure:
    """Create a bar chart for score breakdown"""
    categories = list(breakdown.keys())
    scores = list(breakdown.values())
    
    # Color based on score
    colors = ['#ef4444' if s < 50 else '#fbbf24' if s < 70 else '#10b981' for s in scores]
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=scores,
            marker_color=colors,
            text=[f"{s:.1f}" for s in scores],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Score Breakdown",
        xaxis_title="Component",
        yaxis_title="Score",
        yaxis=dict(range=[0, 100]),
        height=400,
        showlegend=False
    )
    
    return fig

def fetch_competitors_from_market(product_data: Dict[str, str]) -> list:
    """Fetch top competitors from the market using the API"""
    try:
        response = requests.post(f"{API_BASE_URL}/fetch-competitors", json=product_data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch competitors: {str(e)}")
        return []

def analyze_product(product_data: Dict[str, str]) -> Dict[str, Any]:
    """Call the analyze-product API"""
    try:
        response = requests.post(f"{API_BASE_URL}/analyze-product", json=product_data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        return None

def check_market_visibility(product_data: Dict[str, str]) -> Dict[str, Any]:
    """Check where the product appears in search results"""
    try:
        response = requests.post(f"{API_BASE_URL}/market-visibility", json=product_data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Market check failed: {str(e)}")
        return None

def deep_compare_products(product: Dict, competitors: list) -> str:
    """Call the deep-compare API using Gemini URL Context"""
    try:
        payload = {"product": product, "competitors": competitors}
        response = requests.post(f"{API_BASE_URL}/deep-compare", json=payload)
        response.raise_for_status()
        return response.json().get("comparison", "Comparison unavailable.")
    except Exception as e:
        st.error(f"Deep comparison failed: {str(e)}")
        return "Failed to perform deep comparison."

def load_test_data():
    """Load Sony WH-1000XM6 test data into session state"""
    test_description = """About this item
THE BEST NOISE CANCELLATION: Powered by advanced processors and an adaptive microphone system, the WH-1000XM6 headphones deliver real-time noise cancellation for an immersive, distraction-free listening experience.

CO-CREATED WITH MASTERING AUDIO ENGINEERS: Developed in collaboration with world-renowned mastering audio engineers, these headphones deliver unparalleled sound clarity and precision. A specially designed driver with a lightweight carbon fiber dome delivers high fidelity sound, where rich vocals and every instrument remains pure and balanced. Optimized for advanced noise cancellation, the WH-1000XM6 headphones keep every frequency crisp and true to the artist's intent.

HD NOISE CANCELING PROCESSOR QN3: The HD Noise Canceling Processor QN3 is 7x faster than the QN1 (found in our WH-1000XM5 headphones), optimizing 12 microphones in real time for superior noise cancellation, sound quality, and call clarity. With more microphones than ever, we can precisely detect external noise and counteracts it with opposite soundwaves, delivering a new level of noise cancellation.

ULTRA-CLEAR CALLS, FROM ANYWHERE: A six-microphone AI-based beamforming system, intelligent noise reduction technology, and wind-resistant design, work together to isolate your voice, filter out background noise, and ensure every word comes through crisp and clear—even in the busiest environments.

COMPACT CARRYING CASE & FOLDABLE DESIGN: Crafted for durability and style, the foldable design features precision metalwork and a compact case with a magnetic closure—ready to go wherever you do.

TAILORED COMFORT, THOUGHTFULLY DESIGNED: A wider, asymmetrical headband with smooth synthetic leather ensures a pressure-free, all-day fit, while a stepless slider and seamless swivel make every adjustment effortless.

LONG BATTERY LIFE AND CONVENIENT CHARGING: With up to 30 hours of battery life, these headphones ensure you're powered for even the longest trips. When you're running low, simply plug in the USB charging cable and keep listening, with both Bluetooth and audio cable connections supported. Charge for 3 minutes and you'll get up to 3 hours of playback with an optional USB-PD compatible AC adapter.

ADAPTIVE NC OPTIMIZER: Our new Adaptive NC Optimizer intelligently adjusts to a variety of factors, including external noise, air pressure, and your wearing style, even while wearing a hat or glasses, for uninterrupted, immersive sound. This technology monitors your environment to ensure you enjoy the purest, most immersive sound, no matter where you are.

AUTO AMBIENT SOUND MODE: Our Auto Ambient Sound mode adapts to your surroundings in real time by balancing music and external sound. The multiple microphones can filter out the noise or let in what matters: announcements, conversations, or the world around you.

HIGH-RESOLUTION AUDIO: The WH-1000XM6 headphones support High-Resolution Audio and High-Resolution Audio Wireless, thanks to LDAC, our industry-adopted audio coding technology. LDAC transmits approximately three times more data than conventional Bluetooth audio for exceptional High-Resolution Audio quality.

SPECIFICATIONS COMPARISON:
- Noise Canceling: The Best Noise Canceling (12 mics)
- Battery Life: Up to 30 Hrs, Quick charging: 3 Min charge for up to 3 Hrs playback
- Calling features: AI Beamforming(6mics) + AI noise reduction, Multi device connection
- Audio features: Spatial audio upmix, Hi-Res audio compatible
- Special Features: Adaptive NC Optimizer, Foldable design, Case, Wearing detection, Touch Control"""
    
    st.session_state['p_title'] = "Sony WH-1000XM6"
    st.session_state['p_brand'] = "Sony"
    st.session_state['p_category'] = "Headphones"
    st.session_state['p_description'] = test_description
    st.session_state['p_price'] = 27611.0
    
    # Force analysis reset when loading new data
    if 'analysis' in st.session_state:
        del st.session_state['analysis']
    if 'rank_results' in st.session_state:
        del st.session_state['rank_results']

# Main App
def analyze_url(url: str):
    """Analyze a product via URL"""
    try:
        response = requests.post(f"{API_BASE_URL}/analyze-url", json={"url": url})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"URL analysis failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 AI Visibility Platform 2.0</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Automated Discovery & Open-Weight LLM Optimization</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # Sidebar Navigation
        st.title("🚀 Navigation")
        mode = st.radio("Select Mode", ["Manual Entry", "Analyze via Link"])
        
        # Common Categories
        CATEGORIES = [
            "Headphones", "Smartphones", "Laptops", "Smartwatches", 
            "Cameras", "Speakers", "Tablets", "Televisions",
            "Gaming Consoles", "Other"
        ]
        
        if mode == "Manual Entry":
            st.header("📝 Product Information")
            
            # Add Test Data Button
            if st.button("🧪 Use Test Value (Sony WH-1000XM6)", use_container_width=True, type="secondary"):
                load_test_data()
                st.rerun()
            
            
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input(
                    "Product Title", 
                    placeholder="e.g. Sony WH-1000XM5",
                    key="p_title"
                )
                brand = st.text_input(
                    "Brand", 
                    placeholder="e.g. Sony",
                    key="p_brand"
                )
            with col2:
                category_selection = st.selectbox(
                    "Category", 
                    CATEGORIES,
                    key="p_category"
                )
                if category_selection == "Other":
                    category = st.text_input("Enter custom category", key="p_custom_cat")
                else:
                    category = category_selection
            
            description = st.text_area(
                "Product Description", 
                height=150,
                placeholder="Enter a detailed description of your product...",
                key="p_description"
            )
            price = st.number_input(
                "Target Price (₹)", 
                min_value=0.0, 
                step=100.0, 
                help="Optional: Used for price-targeted benchmarking",
                key="p_price"
            )
        else:
            st.header("🔗 Analyze via Link")
            st.info("Paste an Amazon or Flipkart link to automatically fetch and analyze product visibility.")
            url = st.text_input("Product URL", placeholder="https://www.amazon.in/dp/...")
            
            if st.button("Fetch & Analyze"):
                with st.spinner("Fetching product details and analyzing..."):
                    result = analyze_url(url)
                    if result:
                        # Map result to state
                        st.session_state.scraped_product = result["scraped_data"]
                        st.session_state.analysis = result["analysis"]
                        st.success("Successfully fetched and analyzed product!")
                        # Force rerun to show results
                        st.rerun()

            # If data was fetched, show it
            if "scraped_product" in st.session_state:
                st.subheader(f"Extracted: {st.session_state.scraped_product['title']}")
                title = st.session_state.scraped_product["title"]
                description = st.session_state.scraped_product["description"]
                category = st.session_state.scraped_product["category"]
                brand = st.session_state.scraped_product["brand"]
                price = st.session_state.scraped_product.get("price", 0.0)
            else:
                title = ""
                description = ""
                category = ""
                brand = ""
                price = 0.0
        
        st.divider()
        
        st.header("⚙️ Advanced Settings")
        provider = st.selectbox("LLM Provider", ["Google Gemini", "OpenAI", "Hugging Face (Mistral)"])
        search_enabled = st.checkbox("Enable Automated Competitor Search", value=True)

    # Main area
    if not all([title, category, brand, description]):
        st.info("👈 Fill in product info to start")
        return

    product_data = {
        "title": title, 
        "description": description, 
        "category": category, 
        "brand": brand,
        "price": price if price > 0 else None
    }

    # Results Area
    if 'analysis' in st.session_state and st.session_state.analysis:
        res = st.session_state.analysis
        
        c1, c2, c3 = st.columns([1, 1, 3])
        with c1:
            # Display Product Image if available
            if res.get('product') and res['product'].get('image_url'):
                try:
                    st.image(res['product']['image_url'], use_container_width=True)
                except Exception:
                    st.info("🖼️ Image load error")
            else:
                st.info("🖼️ No image available")
        with c2:
            st.plotly_chart(create_gauge_chart(res.get('ai_visibility_score', 0), "Visibility Score"), use_container_width=True)
        with c3:
            st.subheader("💡 Improvement Hub")
            weakness = res.get('weakness_analysis', {})
            if weakness and weakness.get('missing_specs'):
                st.info(f"**Missing Details:** {', '.join(weakness['missing_specs'])}")
                st.markdown("Add these specs below to help the AI write a better description:")
                
            # Use the key directly to ensure it persistence
            user_specs = st.text_area(
                "Technical Specifications & Use Cases:", 
                value=st.session_state.get('user_specs', ""),
                placeholder="e.g. '30h battery life, Bluetooth 5.3, Leather ear cushions, 2-year warranty'",
                key="user_specs_input",
                help="The more technical data you provide, the higher your visibility score will be."
            )
            # Sync to a generic key for the optimization call
            st.session_state.user_specs = user_specs
            
            if user_specs:
                st.success("✅ Technical specs added! Ready to Optimize with AI.")
                
            # Main Product Sentiment
            if res.get('sentiment'):
                st.markdown("### 🧠 Your Product Intelligence")
                
                # New AI Search Simulation Card
                if res.get('ai_recommendation'):
                    a_rec = res['ai_recommendation']
                    with st.container(border=True):
                        st.markdown("**🔍 AI Search Simulation (Gemini Grounding)**")
                        if a_rec.get('is_recommended'):
                            st.success("✅ AI Shortlist: This product/brand appears in AI's top recommendations!")
                        else:
                            st.warning("⚠️ AI Gap: Product did not appear in AI's simulated recommendations.")
                        
                        with st.expander("Show AI Reasoning & Sources"):
                            st.markdown(a_rec.get('recommendation_text', 'No details available.'))
                            if a_rec.get('sources'):
                                st.markdown("**Sources Used:**")
                                for src in a_rec['sources']:
                                    st.markdown(f"- [{src}]({src})")
                
                col_pro, col_con = st.columns(2)
                with col_pro:
                    with st.container(border=True):
                        st.markdown("<span class='sentiment-pro'>🚀 Strengths</span>", unsafe_allow_html=True)
                        for pro in res['sentiment'].get('pros', []):
                            st.markdown(f"✅ {pro}")
                with col_con:
                    with st.container(border=True):
                        st.markdown("<span class='sentiment-con'>⚠️ Implicit Gaps</span>", unsafe_allow_html=True)
                        for con in res['sentiment'].get('cons', []):
                            # Handle common "missing info" warnings gracefully
                            if "missing" in con.lower() or "recommended" in con.lower():
                                st.markdown(f"<span style='color: #ef4444'>{con}</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"❌ {con}")

    st.divider()

    # Action Buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        analyze_btn = st.button("🔍 Refresh Analysis", use_container_width=True)
    with col2:
        fetch_comp_btn = st.button("🌐 Market Scan", use_container_width=True)
    with col3:
        # Highlight this button if analysis is done
        optimize_btn = st.button("✨ Optimize with AI", use_container_width=True, type="primary" if 'analysis' in st.session_state else "secondary")
    with col4:
        compare_btn = st.button("📊 Feature Matrix", use_container_width=True)

    # Re-run analysis if btn clicked
    if analyze_btn:
        with st.spinner("Analyzing..."):
            st.session_state.analysis = analyze_product(product_data)
            st.rerun()

    if fetch_comp_btn:
        with st.spinner("Searching Amazon & Flipkart for competitors..."):
            competitors = fetch_competitors_from_market(product_data)
            if competitors:
                st.session_state.competitors = competitors
                # Now rank against them
                payload = {"product": product_data, "competitors": competitors}
                rank_res = requests.post(f"{API_BASE_URL}/rank-products", json=payload).json()
                st.session_state.rank_results = rank_res
                st.success(f"Found and ranked against {len(competitors)} market competitors!")

    if 'rank_results' in st.session_state:
        st.header("🏆 Market Leaderboard (Top 10)")
        rank_res = st.session_state.rank_results
        all_products = rank_res['all_products']
        
        # Filter into tabs by platform
        amazon_results = [p for p in all_products if p.get('product') and ("Amazon" in (p.get('platform') or '') or "amazon" in p['product'].get('title', '').lower())]
        flipkart_results = [p for p in all_products if p.get('product') and ("Flipkart" in (p.get('platform') or '') or "flipkart" in p['product'].get('title', '').lower())]
        
        # Identity check helper
        def is_user_product(p_title, p_brand):
            # Check if brand matches AND the specific model name from the user exists in the search title
            brand_match = brand.lower() in p_brand.lower() or brand.lower() in p_title.lower()
            title_match = title.lower() in p_title.lower() or p_title.lower() in title.lower()
            return brand_match and title_match

        tab1, tab2 = st.tabs(["🛒 Amazon.in", "🛍️ Flipkart.com"])
        
        with tab1:
            if amazon_results:
                for p in amazon_results:
                    # Skip if product data is missing
                    if not p.get('product'):
                        continue
                    
                    is_user = is_user_product(p['product'].get('title', ''), p['product'].get('brand', ''))
                    
                    with st.container():
                        # Highlight user's product with a border/color
                        if is_user:
                            st.markdown('<div style="border: 2px solid #764ba2; border-radius: 10px; padding: 15px; background-color: #f3f4f6; margin-bottom: 15px;">', unsafe_allow_html=True)
                        
                        c1, c2, c3 = st.columns([1, 4, 2])
                        with c1: 
                            st.subheader(f"#{p['rank']}")
                            if is_user: st.markdown("⭐ **YOUR PRODUCT**")
                            # Market Rank Comparison
                            if p.get('market_rank'):
                                diff = p['market_rank'] - p['rank']
                                if diff > 0:
                                    st.markdown(f"<span style='color: #10b981'>▲ AI Boost: +{diff}</span>", unsafe_allow_html=True)
                                elif diff < 0:
                                    st.markdown(f"<span style='color: #ef4444'>▼ AI Lag: {diff}</span>", unsafe_allow_html=True)
                                else:
                                    st.caption("Neutral AI Gap")
                        with c2:
                            st.markdown(f"**{p['product'].get('title', 'Unknown Product')}**")
                            st.caption(f"Brand: {p['product'].get('brand', 'Unknown')}")
                            
                            # Sentiment Intelligence
                            if p.get('sentiment'):
                                with st.expander("🧠 Product Intelligence"):
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.markdown("**Pros**")
                                        for pro in p['sentiment']['pros'][:3]:
                                            st.markdown(f"<span class='sentiment-pro'>+</span> {pro}", unsafe_allow_html=True)
                                    with col_b:
                                        st.markdown("**Gaps**")
                                        for con in p['sentiment']['cons'][:2]:
                                            st.markdown(f"<span class='sentiment-con'>-</span> {con}", unsafe_allow_html=True)
                        with c3:
                            st.metric("Score", f"{p['score']:.1f}")
                            if p.get('url'):
                                st.link_button("View on Amazon", p['url'], use_container_width=True)
                                if not is_user:
                                    if st.button(f"Deep Specs Analysis vs #{p['rank']}", key=f"deep_{p['rank']}_{p['product']['title'][:10]}"):
                                        with st.spinner("Analyzing live pages via Gemini URL Context..."):
                                            comparison = deep_compare_products(res['product'], [p['product']])
                                            st.info("**AI Deep Specs Comparison:**")
                                            st.markdown(comparison)
                        
                        if is_user:
                            st.markdown('</div>', unsafe_allow_html=True)
                        st.divider()
            else:
                st.info("No direct Amazon competitors found for this query.")

        with tab2:
            if flipkart_results:
                for p in flipkart_results:
                    # Skip if product data is missing
                    if not p.get('product'):
                        continue
                    
                    is_user = is_user_product(p['product'].get('title', ''), p['product'].get('brand', ''))
                    
                    with st.container():
                        if is_user:
                            st.markdown('<div style="border: 2px solid #764ba2; border-radius: 10px; padding: 15px; background-color: #f3f4f6; margin-bottom: 15px;">', unsafe_allow_html=True)
                            
                        c1, c2, c3 = st.columns([1, 4, 2])
                        with c1: 
                            st.subheader(f"#{p['rank']}")
                            if is_user: st.markdown("⭐ **YOUR PRODUCT**")
                            # Market Rank Comparison
                            if p.get('market_rank'):
                                diff = p['market_rank'] - p['rank']
                                if diff > 0:
                                    st.markdown(f"<span style='color: #10b981'>▲ AI Boost: +{diff}</span>", unsafe_allow_html=True)
                                elif diff < 0:
                                    st.markdown(f"<span style='color: #ef4444'>▼ AI Lag: {diff}</span>", unsafe_allow_html=True)
                                else:
                                    st.caption("Neutral AI Gap")
                        with c2:
                            st.markdown(f"**{p['product'].get('title', 'Unknown Product')}**")
                            st.caption(f"Brand: {p['product'].get('brand', 'Unknown')}")
                            
                            # Sentiment Intelligence
                            if p.get('sentiment'):
                                with st.expander("🧠 Product Intelligence"):
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.markdown("**Pros**")
                                        for pro in p['sentiment']['pros'][:3]:
                                            st.markdown(f"<span class='sentiment-pro'>+</span> {pro}", unsafe_allow_html=True)
                                    with col_b:
                                        st.markdown("**Gaps**")
                                        for con in p['sentiment']['cons'][:2]:
                                            st.markdown(f"<span class='sentiment-con'>-</span> {con}", unsafe_allow_html=True)
                        with c3:
                            st.metric("Score", f"{p['score']:.1f}")
                            if p.get('url'):
                                st.link_button("View on Flipkart", p['url'], use_container_width=True)
                                if not is_user:
                                    if st.button(f"Deep Specs Analysis vs #{p['rank']}", key=f"fdeep_{p['rank']}_{p['product']['title'][:10]}"):
                                        with st.spinner("Analyzing live pages via Gemini URL Context..."):
                                            comparison = deep_compare_products(res['product'], [p['product']])
                                            st.info("**AI Deep Specs Comparison:**")
                                            st.markdown(comparison)
                        
                        if is_user:
                            st.markdown('</div>', unsafe_allow_html=True)
                        st.divider()
            else:
                st.info("No direct Flipkart competitors found for this query.")

    if compare_btn:
        with st.spinner("Analyzing market features..."):
            comp_res = requests.post(f"{API_BASE_URL}/compare-features", json=product_data).json()
            st.session_state.feature_comp = comp_res

    if 'feature_comp' in st.session_state:
        st.header("📊 Feature Comparison Matrix")
        comp = st.session_state.feature_comp
        
        # Display user's own features prominently
        st.subheader("Your Extracted Features:")
        if comp['your_features']:
            cols = st.columns(len(comp['your_features']))
            for i, f in enumerate(comp['your_features']):
                cols[i].success(f"✅ {f.title()}")
        else:
            st.warning("No clear features extracted from your description. Add keywords like 'Wireless', 'Bluetooth', or '30h battery'.")

        st.divider()
        
        for item in comp['comparison']:
            with st.expander(f"🆚 vs {item['competitor'][:60]}..."):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### Common Features")
                    if item['common_features']:
                        for f in item['common_features']: st.write(f"✅ {f}")
                    else:
                        st.write("No common features found.")
                with c2:
                    st.markdown("### Potential Gaps (Add these!)")
                    if item['missing_features']:
                        for f in item['missing_features']: 
                            st.markdown(f"<span style='color: #ef4444'>❌ {f}</span>", unsafe_allow_html=True)
                    else:
                        st.write("You cover all features found in this competitor!")

    if optimize_btn:
        with st.spinner(f"Optimizing using {provider}..."):
            specs = st.session_state.get('user_specs', "")
            
            # Map UI name to API slug
            provider_map = {
                "Google Gemini": "gemini",
                "OpenAI": "openai",
                "Hugging Face (Mistral)": "huggingface"
            }
            active_slug = provider_map.get(provider, "gemini")
            
            payload = {
                "product": product_data, 
                "additional_specs": specs,
                "target_queries": (st.session_state.analysis or {}).get('generated_queries', []) if st.session_state.get('analysis') else [],
                "provider": active_slug
            }
            opt_res = requests.post(f"{API_BASE_URL}/optimize-description", json=payload).json()
            st.session_state.opt_res = opt_res
            
    if 'opt_res' in st.session_state:
        opt = st.session_state.opt_res
        st.header("✨ Optimized Description")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Score")
            st.title(f"{opt['original_score']:.1f}")
        with col2:
            st.subheader("Optimized Score")
            st.title(f"{opt['optimized_score']:.1f}")
            st.write(f"🚀 Improvement: **+{opt['score_delta']}**")

        st.subheader("New Description")
        st.write(opt['optimized_description'])
        
        with st.expander("🎯 Improvements Made"):
            for imp in opt['improvements']:
                st.success(f"✓ {imp}")
        
        if st.button("📋 Copy for Amazon/Flipkart"):
            st.code(opt['optimized_description'])

if __name__ == "__main__":
    main()
