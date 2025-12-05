# 🤖 AI Service

> AI-powered PC build suggestions and chat assistant for the CS02 E-Commerce Platform

## 📋 Overview

The AI Service provides intelligent PC build recommendations and a conversational chat assistant. It uses Google's Gemini AI (optional) with fallback to rule-based responses for generating contextual PC build suggestions based on user budgets and requirements.

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.11 |
| Framework | FastAPI | Latest |
| Server | Uvicorn | Latest |
| Validation | Pydantic | Latest |
| HTTP Client | Requests | Latest |
| AI Integration | Google Generative AI (Gemini) | Optional |

## 🚀 API Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/health` | No | Health check endpoint |
| `POST` | `/chat` | No | Chat with AI assistant |
| `POST` | `/builder-bot` | No | Get AI-generated PC build suggestions |

### Request/Response Examples

#### Health Check
```bash
GET /health
```
```json
{
  "status": "healthy"
}
```

#### Chat Endpoint
```bash
POST /chat
Content-Type: application/json

{
  "message": "What's the best GPU for gaming?"
}
```
```json
{
  "response": "For gaming, I'd recommend..."
}
```

#### Builder Bot
```bash
POST /builder-bot
Content-Type: application/json

{
  "budget": 1500,
  "use_case": "gaming",
  "preferences": {
    "brand": "any",
    "rgb": true
  }
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `USE_GEMINI` | No | `false` | Enable Google Gemini AI integration |
| `GEMINI_API_KEY` | No* | - | Google AI API key (*required if USE_GEMINI=true) |
| `CATALOG_SERVICE_URL` | No | `http://localhost:8082` | Product Catalogue Service URL |
| `PORT` | No | `8089` | Service port |

### Docker Configuration

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8089
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8089"]
```

## 📦 Dependencies

```txt
fastapi
uvicorn
pydantic
requests
google-generativeai  # Optional for Gemini integration
```

## 🏃 Running the Service

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8089 --reload

# Or run directly
python main.py
```

### Docker

```bash
# Build image
docker build -t cs02-ai-service .

# Run container
docker run -p 8089:8089 \
  -e USE_GEMINI=false \
  -e CATALOG_SERVICE_URL=http://product-catalogue-service:8082 \
  cs02-ai-service
```

## 🔌 Service Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| Product Catalogue Service | Fetch real product data for recommendations | Yes |
| Google Gemini API | Enhanced AI responses | No (falls back to rule-based) |

## ✅ Features - Completion Status

| Feature | Status | Notes |
|---------|--------|-------|
| Health check endpoint | ✅ Complete | Returns service status |
| Chat response generation | ✅ Complete | Responds to user queries |
| PC build suggestions by budget | ✅ Complete | Budget-aware recommendations |
| Gemini AI integration | ✅ Complete | Optional enhancement |
| Fallback to rule-based responses | ✅ Complete | Works without Gemini |
| Product catalog integration | ✅ Complete | Fetches real products |
| Natural language parsing | ✅ Complete | Understands user intent |

### **Overall Completion: 100%** ✅

## ❌ Not Implemented / Future Enhancements

| Feature | Priority | Notes |
|---------|----------|-------|
| Conversation history/memory | Low | Stateless by design |
| Multiple LLM providers | Low | Currently Gemini only |
| Fine-tuned PC building model | Medium | Could improve recommendations |
| Caching for product data | Low | Could improve performance |

## 📁 Project Structure

```
AI-service/
├── main.py              # FastAPI application entry point
├── logic.py             # Business logic and AI processing
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
└── README.md           # This file
```

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:8089/health

# Test chat endpoint
curl -X POST http://localhost:8089/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me build a gaming PC"}'

# Test builder bot
curl -X POST http://localhost:8089/builder-bot \
  -H "Content-Type: application/json" \
  -d '{"budget": 2000, "use_case": "gaming"}'
```

## 🔗 Related Services

- [API Gateway](../api-gateway/README.md) - Routes `/api/ai/*` to this service
- [Product Catalogue Service](../product-catalogue-service/README.md) - Provides product data

## 📝 Notes

- The service is **stateless** - no database required
- Falls back gracefully if Gemini API is unavailable
- Mock data is used when Product Catalogue is unreachable
- Runs on port **8089** by default
