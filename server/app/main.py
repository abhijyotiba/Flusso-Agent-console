"""
Agent Assist Console - FastAPI Main Application

Entry point for the backend server.
Initializes all services and configures the API.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Load environment variables from .env file in parent directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import services
import app.services.data_loader as data_loader_module
import app.services.gemini_service as gemini_module
import app.services.freshdesk as freshdesk_module
import app.core.orchestrator as orchestrator_module

# Import routers
from app.routers import health, api


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize all services
    - Shutdown: Cleanup resources
    """
    print("\n" + "="*60)
    print("🚀 AGENT ASSIST CONSOLE - Starting Up")
    print("="*60 + "\n")
    
    # Get configuration from environment
    google_api_key = os.getenv("GOOGLE_API_KEY")
    freshdesk_domain = os.getenv("FRESHDESK_DOMAIN")
    freshdesk_api_key = os.getenv("FRESHDESK_API_KEY")
    file_search_corpus_id = os.getenv("FILE_SEARCH_CORPUS_ID")
    data_dir = os.getenv("DATA_DIR", "data")
    
    # Validate required configuration
    if not google_api_key:
        raise RuntimeError("GOOGLE_API_KEY environment variable not set")
    
    try:
        # Initialize Product Database
        print("📊 Initializing Product Database...")
        product_db = data_loader_module.ProductDatabase(data_dir=data_dir)
        product_db.load_data()
        data_loader_module.product_db = product_db
        
        # Initialize Gemini Service
        print("\n🤖 Initializing Gemini Service...")
        gemini_service = gemini_module.GeminiService(
            api_key=google_api_key,
            corpus_id=file_search_corpus_id
        )
        gemini_module.gemini_service = gemini_service
        
        # Initialize Freshdesk Service (optional)
        if freshdesk_domain and freshdesk_api_key:
            print("\n📧 Initializing Freshdesk Service...")
            freshdesk_service = freshdesk_module.FreshdeskService(
                domain=freshdesk_domain,
                api_key=freshdesk_api_key
            )
            freshdesk_module.freshdesk_service = freshdesk_service
            
            # Validate connection
            is_valid = await freshdesk_service.validate_connection()
            if is_valid:
                print("  ✓ Freshdesk connection validated")
            else:
                print("  ⚠ Freshdesk connection validation failed")
        else:
            print("\n📧 Freshdesk Service: Not configured (optional)")
            freshdesk_module.freshdesk_service = None
        
        # Initialize Orchestrator
        print("\n🎯 Initializing Orchestrator...")
        from app.core.prompts import PromptsManager
        orchestrator = orchestrator_module.Orchestrator(
            product_db=product_db,
            gemini=gemini_service,
            prompts=PromptsManager()
        )
        orchestrator_module.orchestrator = orchestrator
        
        print("\n" + "="*60)
        print("✅ STARTUP COMPLETE - Ready to serve requests")
        print("="*60 + "\n")
        
        # Print stats
        stats = product_db.get_stats()
        print(f"📈 Database Stats:")
        print(f"   - Total Products: {stats['total_products']}")
        print(f"   - With Media: {stats['products_with_media']}")
        print(f"   - With Specs: {stats['products_with_specs']}")
        print()
        
        yield  # Server runs here
        
        # Shutdown
        print("\n🛑 Shutting down Agent Assist Console...")
        
    except Exception as e:
        print(f"\n❌ STARTUP FAILED: {e}")
        raise


# Create FastAPI application
app = FastAPI(
    title="Agent Assist Console API",
    description="Human-in-the-Loop product research assistant for support agents",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router)
app.include_router(api.router)


# Serve static files (frontend) if available
static_dir = Path(__file__).parent.parent.parent / "client"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    print(f"📁 Serving static files from: {static_dir}")


# Root endpoint
@app.get("/api")
async def root():
    """API root endpoint"""
    return {
        "message": "Agent Assist Console API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "chat": "/api/chat",
            "freshdesk": "/api/freshdesk",
            "products": "/api/products",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Development mode
        log_level="info"
    )
