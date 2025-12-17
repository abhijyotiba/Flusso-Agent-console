"""
Health Check Router

Provides system health status and statistics.
"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="", tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns system status and service availability.
    """
    from app.services.data_loader import get_product_database
    from app.services.gemini_service import get_gemini_service
    from app.services.freshdesk import get_freshdesk_service
    from app.core.orchestrator import get_orchestrator
    
    try:
        product_db = get_product_database()
        gemini = get_gemini_service()
        freshdesk = get_freshdesk_service()
        orchestrator = get_orchestrator()
        
        db_stats = product_db.get_stats()
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "services": {
                "database": {
                    "status": "loaded" if db_stats["loaded"] else "error",
                    "total_products": db_stats["total_products"],
                    "products_with_media": db_stats["products_with_media"],
                    "products_with_specs": db_stats["products_with_specs"]
                },
                "gemini": {
                    "status": "connected" if gemini else "disconnected"
                },
                "freshdesk": {
                    "status": "configured" if freshdesk else "not_configured"
                },
                "orchestrator": {
                    "status": "ready" if orchestrator else "not_ready"
                }
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """
    Get detailed system statistics.
    """
    from app.services.data_loader import get_product_database
    from app.core.orchestrator import get_orchestrator
    
    try:
        product_db = get_product_database()
        orchestrator = get_orchestrator()
        
        return {
            "database": product_db.get_stats(),
            "orchestrator": orchestrator.get_stats(),
            "models": {
                "available": ["flash", "reasoning"],
                "default": "flash"
            }
        }
        
    except Exception as e:
        return {
            "error": str(e)
        }
