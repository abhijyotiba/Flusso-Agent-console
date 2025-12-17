# 🤖 Agent Assist Console

> **Human-in-the-Loop Product Research Dashboard for Support Agents**

A standalone chatbot interface that helps support agents research product information when the main Flusso workflow encounters ambiguous queries, evidence conflicts, or insufficient data.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Agent Assist Console is designed to bridge the gap when automated workflows can't provide definitive answers. It provides:

- **Intelligent Product Search** - Automatically identifies model numbers in queries
- **Multi-Source Data Retrieval** - Combines specifications, manuals, images, and videos
- **Dual LLM Modes** - Fast responses or complex reasoning
- **Freshdesk Integration** - Export research directly to tickets
- **Rich Media Panel** - Side-by-side view of product resources

### When to Use This Tool

✅ Model number unclear or ambiguous  
✅ Evidence conflicts between data sources  
✅ Need comprehensive product information  
✅ Installation or troubleshooting guidance needed  
✅ Comparing multiple products

---

## ✨ Features

### 🔍 Intelligent Search
- Automatic model number extraction using regex and fuzzy matching
- Supports multiple model formats (GC-303-T, 10.FGC.4003CP, etc.)
- Confidence scoring for matches

### 🧠 Dual LLM Modes
- **⚡ Flash Mode** - Fast responses (2-3s) for straightforward queries
- **🧠 Reasoning Mode** - Deep analysis (5-10s) for complex questions

### 📚 Multi-Source Data
- **CSV Catalog** - Product specifications, pricing, dimensions
- **JSON Media** - Videos, images, installation guides
- **Google GenAI File Search** - Documentation and manuals

### 🎨 Modern UI
- **3-Panel Layout** - Controls | Chat | Media
- **Markdown Support** - Rich formatted responses
- **Responsive Design** - Works on desktop and tablet
- **Real-time Updates** - Dynamic media panel

### 📧 Freshdesk Integration
- Export research results as private notes
- Formatted HTML output
- One-click ticket updates

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                AGENT ASSIST CONSOLE                  │
└─────────────────────────────────────────────────────┘

┌──────────────┐         ┌─────────────────────────┐
│   FRONTEND   │◄───────►│        BACKEND          │
│  Vanilla JS  │  HTTP   │       FastAPI           │
│              │         │                         │
│  • Chat UI   │         │  ┌───────────────────┐  │
│  • Controls  │         │  │  Orchestrator     │  │
│  • Media     │         │  │  (Pipeline)       │  │
│    Panel     │         │  └────────┬──────────┘  │
└──────────────┘         │           │             │
                         │  ┌────────▼──────────┐  │
                         │  │    Services       │  │
                         │  │  • Data Loader    │  │
                         │  │  • Gemini AI      │  │
                         │  │  • Freshdesk      │  │
                         │  └────────┬──────────┘  │
                         │           │             │
                         │  ┌────────▼──────────┐  │
                         │  │  Data Sources     │  │
                         │  │  • product_       │  │
                         │  │    catalog.csv    │  │
                         │  │  • product_       │  │
                         │  │    media.json     │  │
                         │  └───────────────────┘  │
                         └─────────────────────────┘
```

### Processing Pipeline

```
User Query → EXTRACTION → RETRIEVAL → SYNTHESIS → FORMATTING
                ↓             ↓            ↓           ↓
           Model Number   Structured   LLM with   JSON Response
           Detection      + Unstructured Context  + Media Assets
                          Data
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google GenAI API Key
- (Optional) Freshdesk account for integration

### 1. Clone and Setup

```bash
cd "c:\Users\abhishek jyotiba\OneDrive\Desktop\Flusso workflow\Agent-Assistance-Bot"
```

### 2. Configure Environment

```bash
# Copy environment template
copy .env.example .env

# Edit .env and add your API keys
notepad .env
```

Required configuration:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

Optional configuration:
```env
FRESHDESK_DOMAIN=your_company
FRESHDESK_API_KEY=your_freshdesk_api_key
FILE_SEARCH_CORPUS_ID=your_corpus_id
```

### 3. Install Dependencies

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
cd server
pip install -r requirements.txt
cd ..
```

### 4. Run the Application

```powershell
# Start backend server
cd server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open another terminal:

```powershell
# Serve frontend (simple HTTP server)
cd client
python -m http.server 3000
```

### 5. Access the Application

Open your browser:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📦 Installation

### Development Setup

1. **Backend Setup**

```powershell
cd server

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload
```

2. **Frontend Setup**

The frontend is static HTML/CSS/JS. Simply serve the `client` directory:

```powershell
cd client
python -m http.server 3000
```

Or use any static file server (Live Server extension in VS Code, etc.)

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | ✅ Yes | Google GenAI API key |
| `FILE_SEARCH_CORPUS_ID` | ❌ No | File Search corpus for manuals |
| `FRESHDESK_DOMAIN` | ❌ No | Freshdesk subdomain |
| `FRESHDESK_API_KEY` | ❌ No | Freshdesk API key |
| `DATA_DIR` | ❌ No | Data directory path (default: `data`) |
| `HOST` | ❌ No | Server host (default: `0.0.0.0`) |
| `PORT` | ❌ No | Server port (default: `8000`) |

### Data Sources

#### 1. Product Catalog CSV (`server/data/product_catalog.csv`)

Required columns:
- `Model_NO` - Product model number (primary key)
- `Product_Name` - Product name
- `Price` - List price
- `Finish` - Product finish
- `Dimensions` - Product dimensions
- `Material` - Material composition
- `Weight` - Product weight
- `Category` - Product category
- `Subcategory` - Product subcategory

#### 2. Product Media JSON (`server/data/product_media.json`)

Structure:
```json
{
  "MODEL_NUMBER": {
    "model_number": "MODEL_NUMBER",
    "product_name": "Product Name",
    "videos": [
      {
        "title": "Video Title",
        "url": "https://...",
        "type": "installation|tutorial|lifestyle"
      }
    ],
    "images": [
      {
        "title": "Image Title",
        "url": "https://...",
        "type": "product_view|lifestyle|technical"
      }
    ],
    "documents": [
      {
        "title": "Document Title",
        "url": "https://...",
        "type": "installation_guide|spec_sheet|manual"
      }
    ]
  }
}
```

---

## 📖 Usage

### Basic Usage

1. **Select LLM Mode**
   - ⚡ **Flash Mode** - For quick lookups and straightforward questions
   - 🧠 **Reasoning Mode** - For complex comparisons and troubleshooting

2. **Enter Your Query**
   ```
   How do I install the GC-303-T clamp?
   What are the specs for model 10.FGC.4003CP?
   Compare GC-303-T and 10.FGC.4003CP
   ```

3. **Review Results**
   - Chat area shows the comprehensive response
   - Media panel displays product resources
   - Sources are cited at the bottom

4. **Export to Freshdesk** (Optional)
   - Enter ticket ID in the sidebar
   - Click "Export to Ticket"
   - Response is added as a private note

### Query Examples

**Product Lookup:**
```
What is model GC-303-T?
Tell me about 10.FGC.4003CP
```

**Installation:**
```
How do I install the glass clamp GC-303-T?
Installation steps for model 10.FGC.4003CP
```

**Specifications:**
```
What are the specifications for GC-303-T?
Dimensions and material of model 10.FGC.4003CP
```

**Comparison:**
```
Compare GC-303-T and 10.FGC.4003CP
What's the difference between these clamps?
```

**Troubleshooting:**
```
GC-303-T is leaking, how to fix?
Installation issues with 10.FGC.4003CP
```

---

## 🔌 API Documentation

### Endpoints

#### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": {"status": "loaded", "total_products": 10},
    "gemini": {"status": "connected"},
    "freshdesk": {"status": "configured"}
  }
}
```

#### Chat Query
```http
POST /api/chat
Content-Type: application/json

{
  "query": "How do I install GC-303-T?",
  "model_mode": "flash"
}
```

Response:
```json
{
  "markdown_response": "# Installation Guide...",
  "media_assets": {
    "specs": {...},
    "videos": [...],
    "images": [...],
    "documents": [...]
  },
  "sources": ["Installation Manual", "Spec Sheet"],
  "model_used": "gemini-2.0-flash-exp",
  "matched_product": "GC-303-T",
  "confidence": 1.0,
  "timestamp": "2025-12-16T10:30:00Z"
}
```

#### Export to Freshdesk
```http
POST /api/freshdesk
Content-Type: application/json

{
  "ticket_id": "12345",
  "formatted_note": "<div>...</div>"
}
```

### Interactive API Documentation

FastAPI provides interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🛠️ Development

### Project Structure

```
Agent-Assistance-Bot/
├── client/                     # Frontend
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── server/                     # Backend
│   ├── app/
│   │   ├── core/              # Orchestrator, Prompts
│   │   ├── services/          # Data Loader, Gemini, Freshdesk
│   │   ├── routers/           # API endpoints
│   │   └── main.py
│   ├── data/
│   │   ├── product_catalog.csv
│   │   └── product_media.json
│   └── requirements.txt
├── ARCHITECTURE.md            # Detailed architecture
├── docker-compose.yml
└── README.md
```

### Adding New Features

#### 1. Add New Data Source

Edit `server/app/services/data_loader.py`:
```python
def load_new_data_source(self):
    # Load your data
    pass
```

#### 2. Add New Prompt Template

Edit `server/app/core/prompts.py`:
```python
@staticmethod
def get_new_prompt() -> str:
    return """Your prompt here"""
```

#### 3. Add New API Endpoint

Edit `server/app/routers/api.py`:
```python
@router.post("/new-endpoint")
async def new_endpoint():
    pass
```

### Running Tests

```powershell
# Backend tests
cd server
pytest

# With coverage
pytest --cov=app tests/
```

---

## 🚢 Deployment

### Docker Deployment

1. **Build Images**
```bash
docker-compose build
```

2. **Start Services**
```bash
docker-compose up -d
```

3. **Check Status**
```bash
docker-compose ps
docker-compose logs -f backend
```

### Production Considerations

1. **Security**
   - Use HTTPS in production
   - Set strong API keys
   - Configure CORS properly
   - Enable rate limiting

2. **Performance**
   - Use production ASGI server (Gunicorn + Uvicorn)
   - Enable caching for product data
   - Use CDN for frontend assets
   - Monitor API usage

3. **Monitoring**
   - Setup logging aggregation
   - Monitor API response times
   - Track LLM usage and costs
   - Setup health check alerts

### Environment-Specific Settings

**Development:**
```env
DEBUG=true
RELOAD=true
LOG_LEVEL=debug
```

**Production:**
```env
DEBUG=false
RELOAD=false
LOG_LEVEL=info
WORKERS=4
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Backend Won't Start

**Error:** `GOOGLE_API_KEY environment variable not set`

**Solution:**
```powershell
# Check .env file exists
cat .env

# Make sure it contains:
GOOGLE_API_KEY=your_key_here

# Restart server
```

#### 2. No Products Found

**Error:** Products not showing in searches

**Solution:**
```powershell
# Check data files exist
ls server/data/

# Should see:
# product_catalog.csv
# product_media.json

# Check database stats
curl http://localhost:8000/stats
```

#### 3. CORS Errors

**Error:** `Access-Control-Allow-Origin` errors in browser

**Solution:**
Edit `server/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. Freshdesk Export Fails

**Error:** Export button doesn't work

**Solution:**
```powershell
# Check Freshdesk configuration
curl http://localhost:8000/health

# Verify environment variables
echo $env:FRESHDESK_DOMAIN
echo $env:FRESHDESK_API_KEY

# Test Freshdesk API directly
curl -u "YOUR_API_KEY:X" https://YOUR_DOMAIN.freshdesk.com/api/v2/tickets?per_page=1
```

### Debug Mode

Enable debug logging:

```python
# server/app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

View detailed logs:
```powershell
# Watch logs in real-time
docker-compose logs -f backend
```

---

## 📚 Additional Resources

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system architecture
- [Google GenAI Documentation](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Freshdesk API Documentation](https://developers.freshdesk.com/api/)

---

## 🤝 Contributing

### Development Workflow

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

### Code Style

- **Python**: Follow PEP 8
- **JavaScript**: Use ES6+ features
- **Documentation**: Update README for new features

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👥 Support

For questions or issues:
1. Check this README
2. Review ARCHITECTURE.md
3. Check API documentation at `/docs`
4. Review application logs

---

## 🎉 Acknowledgments

Built for the Flusso Support Team to enhance customer service efficiency.

**Key Technologies:**
- FastAPI - Modern Python web framework
- Google GenAI - Advanced language models
- Tailwind CSS - Utility-first CSS framework
- Marked.js - Markdown parser

---

**Version:** 1.0.0  
**Last Updated:** December 16, 2025  
**Status:** Production Ready ✅
