# Agent Assist Console - Architecture & Design Document

## 📋 Executive Summary

**Project Name:** Agent Assist Console  
**Purpose:** Standalone Human-in-the-Loop dashboard for support agents to research product data when the main Flusso workflow encounters ambiguous queries, evidence conflicts, or insufficient information.

**Core Philosophy:** "Unified Context, Stateless Execution" - Prioritize speed and accuracy with a linear pipeline over complex agent loops.

---

## 🎯 Business Requirements

### Problem Statement
The main Flusso workflow may encounter scenarios where:
- Insufficient product information in ticket/query
- Evidence conflicts between data sources
- Inability to identify correct product or model number
- Ambiguous customer requests requiring human judgment

### Solution
A dedicated chatbot interface where human agents can:
1. Input product/model numbers or queries
2. Receive comprehensive product information from all data sources
3. Access direct links to manuals, specs, images, and videos
4. Choose between fast (flash) or reasoning (pro) LLM modes
5. Optionally export responses to Freshdesk tickets as private notes

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT ASSIST CONSOLE                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────────────────┐
│   FRONTEND       │         │        BACKEND               │
│   (Vanilla JS)   │◄───────►│     (FastAPI)                │
│                  │  HTTP   │                              │
│  ┌────────────┐  │         │  ┌─────────────────────────┐ │
│  │  Controls  │  │         │  │   Orchestrator          │ │
│  │  - Model   │  │         │  │   (Brain/Pipeline)      │ │
│  │  - Ticket  │  │         │  └──────────┬──────────────┘ │
│  └────────────┘  │         │             │                │
│                  │         │             ▼                │
│  ┌────────────┐  │         │  ┌─────────────────────────┐ │
│  │ Chat Area  │  │         │  │   Services              │ │
│  │ (Markdown) │  │         │  │   - Data Loader         │ │
│  └────────────┘  │         │  │   - Gemini Service      │ │
│                  │         │  │   - Freshdesk API       │ │
│  ┌────────────┐  │         │  └──────────┬──────────────┘ │
│  │ Media      │  │         │             │                │
│  │ Panel      │  │         │             ▼                │
│  │ - Specs    │  │         │  ┌─────────────────────────┐ │
│  │ - Videos   │  │         │  │   Data Sources          │ │
│  │ - PDFs     │  │         │  │   - product_media.json  │ │
│  └────────────┘  │         │  │   - product_catalog.csv │ │
└──────────────────┘         │  └─────────────────────────┘ │
                             └──────────────────────────────┘
                                        │
                                        ▼
                             ┌──────────────────────────────┐
                             │   External Services          │
                             │   - Google GenAI API         │
                             │   - Freshdesk API            │
                             └──────────────────────────────┘
```

---

## 💻 Technology Stack

### Frontend
- **HTML5, CSS3, JavaScript (ES6)** - Vanilla implementation
- **Tailwind CSS** (CDN) - Utility-first styling
- **marked.js** (CDN) - Markdown to HTML conversion
- **No build tools** - Direct deployment

### Backend
- **Python 3.11+** - Runtime
- **FastAPI** - Web framework
- **Google GenAI SDK** (`google-genai`) - LLM and File Search
- **Pandas** - CSV data manipulation
- **Native JSON** - Media data handling
- **Uvicorn** - ASGI server

### Deployment
- **Docker & Docker Compose** - Containerization
- **Environment Variables** - Configuration management

---

## 📁 Project Structure

```
Agent-Assistance-Bot/
├── client/                          # FRONTEND
│   ├── index.html                   # Main UI (3-Panel Layout)
│   ├── styles.css                   # Custom styles for the frontend
│   ├── app.js                       # Application logic
│   ├── config.js                    # Frontend configuration
│   └── icons/                       # Icons and images
│       ├── favicon.ico              # Website favicon (browser tab icon)
│       └── logo.png                 # Project logo
│
├── server/                          # BACKEND
│   ├── app/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py      # Main processing pipeline
│   │   │   └── prompts.py           # System prompts for LLM
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── data_loader.py       # In-memory data management
│   │   │   ├── gemini_service.py    # Google GenAI wrapper
│   │   │   └── freshdesk.py         # Freshdesk integration
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── api.py               # Main API endpoints
│   │   │   └── health.py            # Health check endpoint
│   │   └── main.py                  # FastAPI application entry
│   ├── data/
│   │   ├── metadata_manifest.json   # Data manifest (JSON)
│   │   └── Product-2025-11-12.xlsx  # Example Excel data file
│   └── requirements.txt             # Python dependencies for backend
│
├── .env                             # Environment variables (not committed)
├── .env.example                     # Example environment template
├── Dockerfile                       # Container definition
├── nginx.conf                       # NGINX config (if used)
├── README.md                        # Setup and usage guide
├── render.yaml                      # Render.com deployment config
├── cloudbuild.yaml                  # Google Cloud Build config
├── build.sh / start.sh              # Helper scripts (optional)
├── documentation/                   # Project documentation (structure, install, etc.)
│   ├── structure_overview.md
│   └── installation_manual.md
└── ARCHITECTURE.md                  # This document
```

---

## 🔄 Core Processing Pipeline

### The Orchestrator (Linear Pipeline)

**Philosophy:** Replace complex ReACT loops with a deterministic 4-stage pipeline.

```python
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR PIPELINE                     │
└─────────────────────────────────────────────────────────────┘

    User Query
        │
        ▼
┌───────────────────┐
│  1. EXTRACTION    │  → Extract Model Number from query
│     Stage         │    using regex/fuzzy matching
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  2. RETRIEVAL     │  → IF Model Found:
│     Strategy      │    ├─ Fetch Specs from CSV
└────────┬──────────┘    ├─ Fetch Media from JSON
         │                └─ Trigger Gemini File Search (targeted)
         │             → IF No Model:
         │                └─ Trigger Gemini File Search (broad)
         ▼
┌───────────────────┐
│  3. SYNTHESIS     │  → Combine:
│     Stage         │    ├─ User Query
└────────┬──────────┘    ├─ Structured Data (specs/media)
         │                └─ Unstructured Data (file search results)
         │             → Send to LLM with comprehensive prompt
         ▼
┌───────────────────┐
│  4. FORMATTING    │  → Generate:
│     Stage         │    ├─ markdown_response (comprehensive answer)
└────────┬──────────┘    ├─ media_assets (structured JSON)
         │                └─ sources (list of references)
         ▼
    JSON Response
```

### Data Flow Example

**Scenario:** Agent asks "How do I install the GC-303-T clamp?"

1. **Extraction:** Regex finds "GC-303-T" in query
2. **Retrieval:**
   - CSV lookup: Returns specs (Price: $125.00, Finish: Polished Chrome)
   - JSON lookup: Returns media (installation video URL, spec PDF)
   - Gemini File Search: "GC-303-T installation instructions" → Returns manual excerpt
3. **Synthesis:** LLM receives:
   ```
   Query: "How do I install the GC-303-T clamp?"
   Specs: {model: "GC-303-T", price: "$125.00", finish: "Polished Chrome"}
   Media: {video: "https://...", pdf: "https://..."}
   Manual: "Step 1: Prepare the glass surface..."
   ```
4. **Formatting:** Returns structured response with answer + asset links

---

## 🧠 Backend Components

### 1. Data Loader Service (`data_loader.py`)

**Responsibilities:**
- Load data **once** at startup for performance
- Maintain in-memory cache of all product data
- Provide fast product lookup methods

**Key Class: `ProductDatabase`**

```python
class ProductDatabase:
    def __init__(self):
        self.media_data: Dict = {}      # From product_media.json
        self.catalog_df: pd.DataFrame   # From product_catalog.csv
        self.model_index: Dict = {}     # Fast lookup index
    
    def load_data(self) -> None:
        """Load JSON and CSV into memory"""
    
    def find_product(self, query: str) -> Optional[ProductContext]:
        """
        Fuzzy search for model number in query.
        Returns ProductContext with specs, media, docs.
        """
    
    def get_all_models(self) -> List[str]:
        """Return list of all known model numbers"""
```

**ProductContext Schema:**
```python
@dataclass
class ProductContext:
    model_number: str
    specs: Dict[str, Any]          # Price, Finish, Dimensions, etc.
    media: Dict[str, List[str]]    # videos, images
    documents: Dict[str, List[str]] # manuals, spec_sheets, installation_guides
    matched_confidence: float       # 0.0-1.0 match confidence
```

---

### 2. Gemini Service (`gemini_service.py`)

**Responsibilities:**
- Abstract all Google GenAI API interactions
- Support multiple models (flash vs pro)
- Handle File Search tool calls
- Manage context windows and token limits

**Key Methods:**

```python
class GeminiService:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.file_search_corpus_id = None  # Set from env
    
    async def generate_response(
        self, 
        query: str, 
        context: Dict, 
        mode: str = "flash",
        system_prompt: str = None
    ) -> Dict:
        """
        Generate LLM response with optional File Search.
        
        Args:
            query: User's question
            context: Structured data (specs, media)
            mode: "flash" (gemini-2.5-flash) or "reasoning" (gemini-2.5-pro)
            system_prompt: Custom system instructions
        
        Returns:
            {
                "response": str,
                "sources": List[str],
                "model_used": str
            }
        """
    
    async def file_search(
        self, 
        query: str, 
        model_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Execute File Search against knowledge base.
        
        Args:
            query: Search query
            model_filter: Optional model number to filter results
        
        Returns:
            List of document chunks with metadata
        """
```

---

### 3. Freshdesk Service (`freshdesk.py`)

**Responsibilities:**
- Post formatted notes to Freshdesk tickets
- Handle authentication and error handling

```python
class FreshdeskService:
    def __init__(self, domain: str, api_key: str):
        self.base_url = f"https://{domain}.freshdesk.com/api/v2"
        self.api_key = api_key
    
    async def add_private_note(
        self, 
        ticket_id: str, 
        note_html: str
    ) -> Dict:
        """
        Add private note to ticket.
        
        Returns:
            {
                "success": bool,
                "note_id": str,
                "error": Optional[str]
            }
        """
```

---

### 4. Orchestrator (`orchestrator.py`)

**The Brain:** Coordinates all services in a linear pipeline.

```python
class Orchestrator:
    def __init__(
        self, 
        product_db: ProductDatabase,
        gemini: GeminiService,
        prompts: PromptsManager
    ):
        self.product_db = product_db
        self.gemini = gemini
        self.prompts = prompts
    
    async def process_query(
        self, 
        query: str, 
        model_mode: str = "flash"
    ) -> Dict:
        """
        Main processing pipeline.
        
        Pipeline:
        1. Extract model number from query
        2. Retrieve data (structured + unstructured)
        3. Synthesize with LLM
        4. Format response
        
        Returns:
            {
                "markdown_response": str,
                "media_assets": {
                    "specs": {...},
                    "videos": [...],
                    "images": [...],
                    "documents": [...]
                },
                "sources": [str],
                "model_used": str,
                "matched_product": Optional[str]
            }
        """
```

**Pipeline Implementation:**

```python
async def process_query(self, query: str, model_mode: str) -> Dict:
    # Stage 1: EXTRACTION
    product_context = self.product_db.find_product(query)
    
    # Stage 2: RETRIEVAL
    if product_context:
        # Targeted search
        file_search_results = await self.gemini.file_search(
            query=query,
            model_filter=product_context.model_number
        )
        structured_data = {
            "specs": product_context.specs,
            "media": product_context.media,
            "documents": product_context.documents
        }
    else:
        # Broad search
        file_search_results = await self.gemini.file_search(query)
        structured_data = {}
    
    # Stage 3: SYNTHESIS
    combined_context = self._build_context(
        query=query,
        structured=structured_data,
        unstructured=file_search_results
    )
    
    system_prompt = self.prompts.get_synthesis_prompt()
    llm_response = await self.gemini.generate_response(
        query=query,
        context=combined_context,
        mode=model_mode,
        system_prompt=system_prompt
    )
    
    # Stage 4: FORMATTING
    return self._format_output(
        llm_response=llm_response,
        product_context=product_context,
        sources=file_search_results
    )
```

---

### 5. Prompts Manager (`prompts.py`)

**Purpose:** Centralize all system prompts for maintainability.

```python
class PromptsManager:
    @staticmethod
    def get_synthesis_prompt() -> str:
        """System prompt for main LLM synthesis"""
        return """You are a product support expert assistant.
        
        Your role: Provide comprehensive, accurate answers about products 
        using the context provided.
        
        Guidelines:
        - Prioritize structured data (specs, media) when available
        - Reference manual excerpts for technical details
        - Always cite sources at the end
        - Use clear, professional language
        - Format responses in Markdown
        - If information is missing, state it clearly
        
        Structure your response:
        1. Direct answer to the question
        2. Relevant technical specifications
        3. Installation/usage steps (if applicable)
        4. Related resources and media links
        5. Sources
        """
    
    @staticmethod
    def get_extraction_prompt() -> str:
        """Prompt for model number extraction (if using LLM)"""
```

---

## 🎨 Frontend Components

### Layout Architecture

**3-Panel Dashboard Design:**

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT ASSIST CONSOLE                      │
├─────────────┬────────────────────────┬──────────────────────┤
│   SIDEBAR   │      CHAT AREA         │    MEDIA PANEL       │
│   (20%)     │        (50%)           │      (30%)           │
│             │                        │                      │
│ ┌─────────┐ │  ┌──────────────────┐ │  ┌────────────────┐ │
│ │ Model   │ │  │ User: How to...  │ │  │ SPECIFICATIONS │ │
│ │ Switch  │ │  └──────────────────┘ │  ├────────────────┤ │
│ │ ○ Flash │ │                        │  │ Model: GC-303  │ │
│ │ ● Pro   │ │  ┌──────────────────┐ │  │ Price: $125    │ │
│ └─────────┘ │  │ AI: Here's how...│ │  │ Finish: Chrome │ │
│             │  │ [Markdown]       │ │  └────────────────┘ │
│ ┌─────────┐ │  └──────────────────┘ │                      │
│ │ Ticket  │ │                        │  ┌────────────────┐ │
│ │ #12345  │ │  [Input Box]          │  │ VIDEOS         │ │
│ │         │ │                        │  ├────────────────┤ │
│ │ Export  │ │                        │  │ 🎥 Install...  │ │
│ └─────────┘ │                        │  │ 🎥 Maintain... │ │
│             │                        │  └────────────────┘ │
│             │                        │                      │
│             │                        │  ┌────────────────┐ │
│             │                        │  │ DOCUMENTS      │ │
│             │                        │  ├────────────────┤ │
│             │                        │  │ 📄 Manual.pdf  │ │
│             │                        │  │ 📄 Specs.pdf   │ │
│             │                        │  └────────────────┘ │
└─────────────┴────────────────────────┴──────────────────────┘
```

---

### State Management (`app.js`)

**Minimal State Pattern:**

```javascript
const AppState = {
    // Configuration
    config: {
        apiBaseUrl: 'http://localhost:8000',
        modelMode: 'flash'  // or 'reasoning'
    },
    // Chat data
    chat: {
        messages: [],       // [{role: 'user'|'assistant', content: str}]
        isLoading: false
    },
    // Current context
    context: {
        currentAssets: null,  // Media assets from latest response
        matchedProduct: null, // Model number if found
        sources: []           // Source references
    },
    // Freshdesk
    freshdesk: {
        ticketId: null
    }
};
```

**Static File Serving and Favicon:**

- The backend (FastAPI) is configured to serve all files in the `client/` directory as static files, including `index.html`, CSS, JS, and images.
- The favicon (`/favicon.ico`) is served from `client/icons/favicon.ico` via a dedicated FastAPI route, so browsers display the correct icon in the tab.
---

## 🆕 Notable Recent Changes

- **Static file serving**: The backend now serves the frontend directly from the `client/` directory, making deployment and local development easier.
- **Favicon support**: `/favicon.ico` is now served from the correct location, eliminating browser 404 errors.
- **Documentation folder**: Added `documentation/` with beginner-friendly guides for structure and installation.
- **Updated data files**: Data files are now in Excel and JSON format, with a manifest for easier management.
- **Environment example**: `.env.example` is provided for easy setup of environment variables.

---

**Key Functions:**

```javascript
// API Communication
async function sendQuery(query) {
    const response = await fetch(`${apiBaseUrl}/chat`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            query: query,
            model_mode: AppState.config.modelMode
        })
    });
    return await response.json();
}

// UI Rendering
function renderMessage(message) {
    // Use marked.parse() for markdown
    const html = marked.parse(message.content);
    // Append to chat area
}

function renderMediaPanel(assets) {
    // Update right panel with specs, videos, documents
    // DO NOT render in chat bubbles - separate panel only
}

// Freshdesk Integration
async function exportToFreshdesk() {
    const latestAIMessage = getLatestAIMessage();
    const formattedNote = formatForFreshdesk(latestAIMessage);
    
    await fetch(`${apiBaseUrl}/freshdesk`, {
        method: 'POST',
        body: JSON.stringify({
            ticket_id: AppState.freshdesk.ticketId,
            formatted_note: formattedNote
        })
    });
}
```

---

## 🔌 API Specification

### Endpoints

#### 1. POST `/api/chat`

**Purpose:** Main query processing endpoint.

**Request:**
```json
{
    "query": "How do I install the GC-303-T clamp?",
    "model_mode": "flash"  // or "reasoning"
}
```

**Response:**
```json
{
    "markdown_response": "# Installation Guide for GC-303-T\n\n...",
    "media_assets": {
        "specs": {
            "model_number": "GC-303-T",
            "price": "$125.00",
            "finish": "Polished Chrome",
            "dimensions": "3\" x 2\""
        },
        "videos": [
            {
                "title": "Installation Guide",
                "url": "https://youtube.com/...",
                "thumbnail": "https://..."
            }
        ],
        "images": [
            {
                "title": "Product View",
                "url": "https://..."
            }
        ],
        "documents": [
            {
                "title": "Installation Manual",
                "type": "installation_guide",
                "url": "https://..."
            },
            {
                "title": "Specification Sheet",
                "type": "spec_sheet",
                "url": "https://..."
            }
        ]
    },
    "sources": [
        "Installation Manual (Page 5)",
        "Product Specification Sheet"
    ],
    "model_used": "gemini-2.5-flash",
    "matched_product": "GC-303-T",
    "timestamp": "2025-12-16T10:30:00Z"
}
```

**Error Response:**
```json
{
    "error": "Error message",
    "detail": "Detailed error information",
    "timestamp": "2025-12-16T10:30:00Z"
}
```

---

#### 2. POST `/api/freshdesk`

**Purpose:** Export response to Freshdesk ticket.

**Request:**
```json
{
    "ticket_id": "12345",
    "formatted_note": "<div>...</div>"
}
```

**Response:**
```json
{
    "success": true,
    "note_id": "98765",
    "ticket_id": "12345",
    "timestamp": "2025-12-16T10:30:00Z"
}
```

---

#### 3. GET `/health`

**Purpose:** Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "services": {
        "database": "loaded",
        "gemini": "connected",
        "freshdesk": "configured"
    }
}
```

---

## 🗄️ Data Sources

### 1. Product Media JSON (`product_media.json`)

**Structure:**
```json
{
    "GC-303-T": {
        "model_number": "GC-303-T",
        "product_name": "Hole In Glass Clamp",
        "videos": [
            {
                "title": "Installation Guide",
                "url": "https://youtube.com/watch?v=...",
                "thumbnail": "https://img.youtube.com/...",
                "type": "installation"
            }
        ],
        "images": [
            {
                "title": "Product Main View",
                "url": "https://example.com/images/gc-303-t-main.jpg",
                "type": "product_view"
            }
        ],
        "documents": [
            {
                "title": "Installation Manual",
                "url": "https://example.com/docs/gc-303-t-install.pdf",
                "type": "installation_guide"
            },
            {
                "title": "Specification Sheet",
                "url": "https://example.com/docs/gc-303-t-specs.pdf",
                "type": "spec_sheet"
            }
        ]
    }
}
```

---

### 2. Product Catalog CSV (`product_catalog.csv`)

**Columns:**
- `Model_NO` (Primary Key)
- `Product_Name`
- `Price`
- `Finish`
- `Dimensions`
- `Material`
- `Weight`
- `Category`
- `Subcategory`

**Example:**
```csv
Model_NO,Product_Name,Price,Finish,Dimensions,Material,Weight,Category,Subcategory
GC-303-T,Hole In Glass Clamp,125.00,Polished Chrome,3" x 2",Brass,0.5 lbs,Clamps,Glass
```

---

## 🚀 Deployment Architecture

### Docker Compose Setup

```yaml
version: '3.8'

services:
  backend:
    build: ./server
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - FRESHDESK_DOMAIN=${FRESHDESK_DOMAIN}
      - FRESHDESK_API_KEY=${FRESHDESK_API_KEY}
    volumes:
      - ./server/data:/app/data
    
  frontend:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./client:/usr/share/nginx/html
    depends_on:
      - backend
```

---

## 🔐 Security Considerations

1. **API Keys:** Store in environment variables, never commit to repo
2. **CORS:** Configure FastAPI CORS middleware for frontend origin
3. **Rate Limiting:** Implement rate limiting on API endpoints
4. **Input Validation:** Sanitize all user inputs
5. **Freshdesk Auth:** Use secure API key storage
6. **HTTPS:** Use HTTPS in production

---

## 📊 Performance Optimizations

1. **Data Loading:** Load CSV/JSON once at startup into memory
2. **Async Processing:** Use async/await throughout backend
3. **Caching:** Cache frequently accessed product data
4. **Lazy Loading:** Load media assets on-demand in frontend
5. **Debouncing:** Debounce user input to reduce API calls

---

## 🧪 Testing Strategy

### Backend Tests
- Unit tests for each service
- Integration tests for orchestrator pipeline
- Mock external API calls (Gemini, Freshdesk)

### Frontend Tests
- DOM manipulation tests
- API integration tests
- UI interaction tests

---

## 📈 Future Enhancements

1. **Multi-tenant Support:** Support multiple Freshdesk accounts
2. **Analytics Dashboard:** Track query patterns and agent usage
3. **Feedback Loop:** Allow agents to rate response quality
4. **Advanced Search:** Support natural language product discovery
5. **Conversation History:** Persist chat sessions
6. **File Upload:** Allow agents to upload product images for analysis

---

## 🔄 Development Workflow

### Phase 1: Foundation (Day 1-2)
- ✅ Scaffold directory structure
- ✅ Create mock data files
- ✅ Implement data loader service
- ✅ Basic FastAPI setup

### Phase 2: Core Services (Day 3-4)
- ✅ Implement Gemini service
- ✅ Implement Freshdesk service
- ✅ Build orchestrator pipeline
- ✅ Create API endpoints

### Phase 3: Frontend (Day 5-6)
- ✅ Build HTML layout
- ✅ Implement JavaScript logic
- ✅ Style with Tailwind
- ✅ Integrate with backend

### Phase 4: Deployment (Day 7)
- ✅ Docker containerization
- ✅ Environment configuration
- ✅ Testing and debugging
- ✅ Documentation

---

## 📚 References

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Google GenAI Python SDK:** https://github.com/googleapis/python-genai
- **Tailwind CSS:** https://tailwindcss.com/
- **marked.js:** https://marked.js.org/
- **Freshdesk API:** https://developers.freshdesk.com/api/

---

## 👥 Support & Maintenance

**Primary Developer:** Coding Agent  
**Last Updated:** December 16, 2025  
**Version:** 1.0.0

---

*This architecture document serves as the single source of truth for the Agent Assist Console project. All implementation decisions should align with the principles and patterns outlined here.*
