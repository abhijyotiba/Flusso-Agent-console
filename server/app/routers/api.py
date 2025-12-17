"""
Main API Router

Handles chat queries and Freshdesk integration.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api", tags=["api"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat query request"""
    model_config = {"protected_namespaces": ()}
    
    query: str = Field(..., min_length=1, max_length=2000, description="User query")
    model_mode: str = Field(default="flash", pattern="^(flash|reasoning)$", description="LLM mode")


class ChatResponse(BaseModel):
    """Chat query response"""
    model_config = {"protected_namespaces": ()}
    
    markdown_response: str
    media_assets: Optional[Dict[str, Any]] = None
    sources: list = []
    model_used: str
    matched_product: Optional[str] = None
    confidence: float = 0.0
    timestamp: str


class FreshdeskRequest(BaseModel):
    """Freshdesk note request"""
    ticket_id: str = Field(..., description="Freshdesk ticket ID")
    formatted_note: str = Field(..., description="HTML formatted note content")


class FreshdeskResponse(BaseModel):
    """Freshdesk note response"""
    success: bool
    note_id: Optional[str] = None
    ticket_id: str
    error: Optional[str] = None
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Process chat query through orchestrator pipeline.
    
    This is the main endpoint for product research queries.
    
    Args:
        request: ChatRequest with query and model_mode
        
    Returns:
        ChatResponse with comprehensive answer and media assets
    """
    from ..core.orchestrator import get_orchestrator
    
    try:
        orchestrator = get_orchestrator()
        
        # Process query through pipeline
        result = await orchestrator.process_query(
            query=request.query,
            model_mode=request.model_mode
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        print(f"✗ Error processing chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.post("/freshdesk", response_model=FreshdeskResponse)
async def export_to_freshdesk(request: FreshdeskRequest) -> FreshdeskResponse:
    """
    Export research results to Freshdesk ticket as private note.
    
    Args:
        request: FreshdeskRequest with ticket_id and formatted note
        
    Returns:
        FreshdeskResponse with success status
    """
    from ..services.freshdesk import get_freshdesk_service
    from datetime import datetime
    
    try:
        freshdesk = get_freshdesk_service()
        
        if not freshdesk:
            raise HTTPException(
                status_code=503,
                detail="Freshdesk service not configured. Set FRESHDESK_DOMAIN and FRESHDESK_API_KEY."
            )
        
        # Add note to ticket
        result = await freshdesk.add_private_note(
            ticket_id=request.ticket_id,
            note_html=request.formatted_note
        )
        
        return FreshdeskResponse(
            success=result["success"],
            note_id=result.get("note_id"),
            ticket_id=request.ticket_id,
            error=result.get("error"),
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ Error exporting to Freshdesk: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting to Freshdesk: {str(e)}"
        )


@router.get("/products")
async def list_products(
    category: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    List available products.
    
    Optional category filter for browsing products.
    
    Args:
        category: Optional category filter
        limit: Maximum number of results
        
    Returns:
        List of products
    """
    from ..services.data_loader import get_product_database
    
    try:
        product_db = get_product_database()
        
        if category:
            products = product_db.search_by_category(category)
        else:
            models = product_db.get_all_models()
            products = [{"model_number": model} for model in models[:limit]]
        
        return {
            "products": products[:limit],
            "total": len(products),
            "limit": limit
        }
        
    except Exception as e:
        print(f"✗ Error listing products: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing products: {str(e)}"
        )


@router.get("/product/{model_number}")
async def get_product_details(model_number: str) -> Dict[str, Any]:
    """
    Get detailed information for a specific product.
    
    Args:
        model_number: Product model number
        
    Returns:
        Product details with specs and media
    """
    from ..services.data_loader import get_product_database
    
    try:
        product_db = get_product_database()
        
        product = product_db.get_product_by_model(model_number)
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product not found: {model_number}"
            )
        
        return product.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ Error getting product details: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting product details: {str(e)}"
        )
