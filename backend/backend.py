from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import re
import requests

app = FastAPI(title="PC Budget Assistant API")

# Allow React frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"] to restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Knowledge base
# --------------------------
KNOWLEDGE_BASE = {
    "budget_ranges": [
        {
            "range": "$300-$500",
            "cpu": "Intel Pentium Gold or AMD Athlon",
            "gpu": "Integrated Graphics",
            "ram": "8GB DDR4",
            "storage": "256GB SSD",
            "use_case": "Basic computing, web browsing, office work"
        },
        {
            "range": "$600-$900",
            "cpu": "Intel Core i3-12100F or AMD Ryzen 5 5600",
            "gpu": "GTX 1650 or RX 6500 XT",
            "ram": "16GB DDR4",
            "storage": "500GB NVMe SSD",
            "use_case": "Gaming at 1080p, content creation, multitasking"
        },
        {
            "range": "$1000-$1500",
            "cpu": "Intel Core i5-13400F or AMD Ryzen 5 7600",
            "gpu": "RTX 4060 or RX 7600",
            "ram": "16GB DDR4/DDR5",
            "storage": "1TB NVMe SSD",
            "use_case": "High-end gaming, streaming, video editing"
        },
        {
            "range": "$1500-$2500",
            "cpu": "Intel Core i7-14700K or AMD Ryzen 7 7800X3D",
            "gpu": "RTX 4070 Super or RX 7800 XT",
            "ram": "32GB DDR5",
            "storage": "2TB NVMe Gen4 SSD",
            "use_case": "4K gaming, professional work, heavy multitasking"
        }
    ],
    "components": {
        "cpu": "The processor is the brain of your computer.",
        "gpu": "Graphics card handles visuals and gaming.",
        "ram": "Memory for running programs.",
        "storage": "SSD (Solid State Drive) is faster than HDD.",
        "motherboard": "Connects all components. Must match CPU socket.",
        "psu": "Power Supply Unit. Bronze/Gold/Platinum ratings show efficiency.",
        "case": "Houses all components. Ensure good airflow."
    },
    "tips": [
        "Check component compatibility before buying",
        "Invest more in GPU if gaming is priority",
        "Don't cheap out on PSU - it powers everything",
        "SSD for OS is essential",
        "Consider future upgradability"
    ]
}

# --------------------------
# Pydantic models
# --------------------------
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    context: str
    response: str
    timestamp: str

# --------------------------
# RAG System
# --------------------------
class RAGSystem:
    def __init__(self):
        self.knowledge_base = KNOWLEDGE_BASE

    def retrieve_context(self, query: str) -> str:
        """Retrieve context for a query"""
        query_lower = query.lower()
        context = []

        # Match budget
        budget_match = re.search(r'\$?(\d+)', query_lower)
        if budget_match:
            budget = int(budget_match.group(1))
            for b in self.knowledge_base["budget_ranges"]:
                min_b, max_b = map(int, b["range"].replace("$", "").split("-"))
                if min_b <= budget <= max_b:
                    context.append(f"Budget: {b['range']}\nCPU: {b['cpu']}\nGPU: {b['gpu']}\nRAM: {b['ram']}\nStorage: {b['storage']}\nUse Case: {b['use_case']}")

        # Match components
        for comp, desc in self.knowledge_base["components"].items():
            if comp in query_lower:
                context.append(f"{comp.upper()}: {desc}")

        # Tips
        if any(w in query_lower for w in ["tip", "advice", "recommend", "help"]):
            context.append("Tips:\n" + "\n".join(f"- {t}" for t in self.knowledge_base["tips"][:3]))

        if any(w in query_lower for w in ["option", "choice", "range", "budget"]):
            for b in self.knowledge_base["budget_ranges"]:
                context.append(f"{b['range']}: {b['use_case']}")

        return "\n\n".join(context) if context else "General PC building info available."

    def generate_response(self, query: str, context: str) -> str:
        """Simple fallback response for React frontend"""
        if "General PC building info available." in context:
            return "I can help you build PCs! Ask me about budgets like '$800' or components like 'GPU'."
        return f"Based on your question about '{query}':\n{context}"

# Initialize RAG system
rag_system = RAGSystem()

# --------------------------
# API Endpoints
# --------------------------
@app.get("/")
async def root():
    return {"message": "PC Budget Assistant API", "version": "1.0"}

@app.post("/query", response_model=QueryResponse)
async def query_pc(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    context = rag_system.retrieve_context(request.query)
    response = rag_system.generate_response(request.query, context)

    return QueryResponse(
        query=request.query,
        context=context,
        response=response,
        timestamp=datetime.now().isoformat()
    )

@app.get("/budgets")
async def get_budgets():
    return {"budgets": KNOWLEDGE_BASE["budget_ranges"]}

@app.get("/components")
async def get_components():
    return {"components": KNOWLEDGE_BASE["components"]}

@app.get("/tips")
async def get_tips():
    return {"tips": KNOWLEDGE_BASE["tips"]}
