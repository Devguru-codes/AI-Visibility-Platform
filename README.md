# AI Visibility Platform

> **Analyze and optimize product discoverability for AI search engines**

An AI-powered platform that helps e-commerce businesses optimize their product descriptions for AI search engines like ChatGPT, Perplexity, and Gemini.

## 🎯 Problem It Solves

E-commerce products are not optimized for AI search engines. This tool analyzes how discoverable a product is by AI systems and provides actionable optimization suggestions.

## ✨ Features

- **AI Visibility Score (0-100)**: Comprehensive scoring based on 4 key components
- **Semantic Analysis**: Uses sentence-transformers for semantic similarity
- **Competitive Ranking**: Compare your product against competitors
- **LLM-Powered Optimization**: Automatically rewrite descriptions for better AI visibility
- **Weakness Detection**: Identify missing specs, keywords, and clarity issues
- **Before/After Comparison**: See the impact of optimizations

## 🏗️ Architecture

```
[ Streamlit Frontend ]
          |
          v
[ FastAPI Backend ]
          |
  ---------------------
  |   ML Services     |
  |-------------------|
  | Embedding Engine  |
  | Scoring Engine    |
  | Ranking Engine    |
  | LLM Optimizer     |
  ---------------------
```

## 🧮 Scoring Formula

```
Final Score = 
  0.4 × Semantic Relevance +
  0.2 × Keyword Coverage +
  0.2 × Completeness +
  0.2 × Readability
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-visibility-platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup environment variables:
Create a `.env` file in the root directory (use `.env.example` as a template):
```bash
cp .env.example .env
```
Fill in your `GEMINI_API_KEY` and other optional keys in the `.env` file.

### Running the Application

1. Start the FastAPI backend:
```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

2. In a new terminal, start the Streamlit frontend:
```bash
cd frontend
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📦 API Endpoints

### `POST /api/analyze-product`
Analyze a product and return AI visibility score with detailed breakdown.

**Request:**
```json
{
  "title": "Sony WH-1000XM5 Wireless Headphones",
  "description": "Premium noise cancelling headphones...",
  "category": "Headphones",
  "brand": "Sony"
}
```

**Response:**
```json
{
  "ai_visibility_score": 75.5,
  "score_breakdown": {
    "semantic_relevance": 80.2,
    "keyword_coverage": 65.0,
    "completeness": 70.5,
    "readability": 85.0
  },
  "weakness_analysis": {
    "missing_specs": ["battery life", "warranty"],
    "suggestions": ["Add more technical specifications"]
  }
}
```

### `POST /api/rank-products`
Rank your product against competitors.

### `POST /api/optimize-description`
Optimize product description using LLM.

## 🧪 Example Use Case

**Input:**
- Product: "Noise cancelling headphones"
- Description: "Good headphones for music"

**Analysis:**
- Score: 56/100
- Rank: #4 out of 8
- Missing: Battery life, use cases, compatibility

**After Optimization:**
- Score: 82/100
- Rank: #1
- Improvements: Added specifications, use cases, and relevant keywords

## 🛠️ Tech Stack

**Backend:**
- FastAPI
- Pydantic
- Uvicorn

**ML/AI:**
- sentence-transformers (all-MiniLM-L6-v2)
- scikit-learn
- textstat
- OpenAI API (optional)

**Frontend:**
- Streamlit
- Plotly

## 📁 Project Structure

```
ai-visibility-platform/
├── backend/
│   ├── main.py
│   ├── routers/
│   │   └── analyze.py
│   ├── services/
│   │   ├── embedder.py
│   │   ├── scorer.py
│   │   ├── ranker.py
│   │   └── optimizer.py
│   ├── schemas/
│   │   └── product.py
│   └── core/
│       └── config.py
├── frontend/
│   └── app.py
├── requirements.txt
└── README.md
```

## 🚀 Deployment

### Backend Deployment (Render/Railway)

1. Connect your GitHub repository
2. Set environment variables (OPENAI_API_KEY if using LLM)
3. Deploy with command: `python backend/main.py`

### Frontend Deployment (Streamlit Cloud)

1. Push to GitHub
2. Connect to Streamlit Cloud
3. Set main file path: `frontend/app.py`
4. Configure API_BASE_URL to your deployed backend

## 🎯 Future Enhancements

- [ ] CSV upload for bulk product analysis
- [ ] Chrome extension for real-time analysis
- [ ] Multi-language support
- [ ] User authentication and history
- [ ] Amazon product scraper integration

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

