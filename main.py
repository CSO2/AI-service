from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
import re
import requests
import os
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Product Catalog Service URL
CATALOG_SERVICE_URL = os.getenv("PRODUCT_CATALOGUE_SERVICE_URL", "http://localhost:8082")

app = FastAPI(title="AI Service", description="Dynamic PC Budget Assistant", version="2.0")

# Allow React frontend to call API
# app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["*"],
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
# )

# --------------------------
# Knowledge Base (Static Fallback + Structure)
# --------------------------
KNOWLEDGE_BASE = {
    "budget_ranges": [
        {"range": "$300-$500", "desc": "Basic computing"},
        {"range": "$600-$900", "desc": "Entry-level gaming (1080p)"},
        {"range": "$1000-$1500", "desc": "Mid-tier gaming (1440p)"},
        {"range": "$1500-$2500", "desc": "High-end gaming (4K)"}
    ],
    "components": {
        "cpu": "The processor is the brain of your computer.",
        "gpu": "Graphics card handles visuals and gaming.",
        "motherboard": "Connects all components.",
        "ram": "Memory for running programs.",
        "storage": "SSD/HDD for storing files.",
        "psu": "Power Supply Unit.",
        "case": "Computer case."
    },
    "tips": [
        "Always check socket compatibility between CPU and Motherboard.",
        "Don't cheap out on the PSU.",
        "SSDs are essential for a responsive system."
    ]
}

# --------------------------
# Dynamic Data Fetching
# --------------------------
def fetch_products_from_catalog() -> List[Dict[str, Any]]:
    """Fetch products from the Product Catalog Service."""
    try:
        response = requests.get(f"{CATALOG_SERVICE_URL}/api/products", params={"size": 100}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "content" in data:
                return data["content"]
            elif isinstance(data, list):
                return data
        return []
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return get_mock_products()

def get_mock_products() -> List[Dict[str, Any]]:
    """Fallback mock product data."""
    return [
        {"id": "1", "name": "Intel Core i9-13900K", "subcategory": "CPU", "price": 589.99, "brand": "Intel", "specs": {"socketType": "LGA1700"}},
        {"id": "2", "name": "NVIDIA GeForce RTX 4090", "subcategory": "GPU", "price": 1599.99, "brand": "NVIDIA", "specs": {"powerRequirement": "450"}},
        {"id": "3", "name": "Corsair Vengeance 32GB", "subcategory": "RAM", "price": 129.99, "brand": "Corsair", "specs": {"type": "DDR5"}},
    ]

# --------------------------
# Models
# --------------------------
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    context: str
    response: str
    timestamp: str

# Frontend compatibility models
class BuilderBotRequest(BaseModel):
    query: str

class BuildSuggestion(BaseModel):
    components: List[Any]
    totalPrice: float

class BuilderBotResponse(BaseModel):
    message: str
    buildSuggestion: BuildSuggestion

# --------------------------
# RAG System (Dynamic)
# --------------------------
class RAGSystem:
    def __init__(self):
        self.knowledge_base = KNOWLEDGE_BASE

    def retrieve_context(self, query: str) -> str:
        query_lower = query.lower()
        context = []

        # 1. Fetch Dynamic Products
        products = fetch_products_from_catalog()
        
        # Simple keyword matching for products
        relevant_products = []
        for p in products:
            p_name = p.get('name', '').lower()
            p_sub = p.get('subcategory', '').lower()
            if p_sub in query_lower or any(word in query_lower for word in p_name.split()):
                relevant_products.append(f"{p.get('name')} (${p.get('price')})")
        
        if relevant_products:
            context.append("Available Products:\n" + "\n".join(relevant_products[:5]))

        # 2. Static Knowledge Base
        if "budget" in query_lower or re.search(r'\$\d+', query):
            context.append("Budget Ranges:\n" + "\n".join([f"{b['range']}: {b['desc']}" for b in self.knowledge_base["budget_ranges"]]))
            
        for comp, desc in self.knowledge_base["components"].items():
            if comp in query_lower:
                context.append(f"{comp.upper()}: {desc}")

        if not context:
            context.append("General PC building advice available.")

        return "\n\n".join(context)

    def generate_response(self, query: str, context: str) -> str:
        if "Available Products" in context:
             return f"Based on your request, here are some options from our catalog:\n{context}\n\nWould you like me to build a PC with these?"
        
        return f"Here is some information regarding '{query}':\n{context}"

rag_system = RAGSystem()

# --------------------------
# Logic for Builder Bot (Frontend Compat)
# --------------------------
def generate_build_suggestion_logic(query: str) -> Dict[str, Any]:
    # Simplified logic reusing the dynamic fetch
    products = fetch_products_from_catalog()
    
    # Simple budget extraction
    budget = 2000
    budget_match = re.search(r'\$?(\d{3,5})', query)
    if budget_match:
        budget = int(budget_match.group(1))

    # Basic filtering logic (simplified from original logic.py)
    # real logic would be more complex, but this proves the dynamic connection
    def get_price(p): return float(p.get('price', 0))
    def get_sub(p): return p.get('subcategory', '')

    components = []
    required_types = ['CPU', 'GPU', 'Motherboard', 'RAM', 'Storage', 'PSU', 'Case']
    
    current_total = 0
    for type_ in required_types:
        # Find a product of this type consistent with budget
        # Very naive heuristic: allocate ~1/7th of budget per component (not realistic but functional)
        target_price = budget / 7 
        candidates = [p for p in products if type_ in get_sub(p) or (type_ == 'Storage' and 'SSD' in get_sub(p))]
        
        if candidates:
            # Pick one closest to target price
            chosen = min(candidates, key=lambda x: abs(get_price(x) - target_price))
            
            # Normalize for frontend
            components.append({
                "id": str(chosen.get('id')),
                "name": chosen.get('name'),
                "subcategory": chosen.get('subcategory'),
                "price": get_price(chosen),
                "brand": chosen.get('brand', ''),
                "imageUrl": chosen.get('imageUrl', '/placeholder-product.png'),
                "specs": chosen.get('specs', {})
            })
            current_total += get_price(chosen)

    return {
        "components": components,
        "totalPrice": current_total
    }

# --------------------------
# API Endpoints
# --------------------------
@app.get("/api/ai")
def root():
    return {"message": "AI Service Running", "mode": "Dynamic"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/ai/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    context = rag_system.retrieve_context(request.query)
    response = rag_system.generate_response(request.query, context)
    return QueryResponse(
        query=request.query, 
        context=context, 
        response=response, 
        timestamp=datetime.now().isoformat()
    )

# Frontend Endpoint
@app.post("/api/ai/builder-bot", response_model=BuilderBotResponse)
def builder_bot(request: BuilderBotRequest):
    # 1. Get Text Response from RAG
    context = rag_system.retrieve_context(request.query)
    text_response = rag_system.generate_response(request.query, context)
    
    # 2. Get Build Suggestion (Dynamic)
    build_data = generate_build_suggestion_logic(request.query)
    
    return BuilderBotResponse(
        message=text_response,
        buildSuggestion=BuildSuggestion(
            components=build_data['components'],
            totalPrice=build_data['totalPrice']
        )
    )

if __name__ == "__main__":
    import uvicorn
    # Clean up port 8089 user before starting? (Handled by user instructions usually, but we can try)
    uvicorn.run(app, host="0.0.0.0", port=8089)
