"""
Orchestrator - The Brain of Agent Assist Console

Implements the linear processing pipeline:
1. EXTRACTION - Find model number in query
2. RETRIEVAL - Gather structured + unstructured data
3. SYNTHESIS - Generate comprehensive response with LLM
4. FORMATTING - Structure output for frontend
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from ..services.data_loader import ProductDatabase, ProductContext
from ..services.gemini_service import GeminiService
from .prompts import PromptsManager


class Orchestrator:
    """
    Main processing pipeline coordinator.
    
    Replaces complex ReACT loops with a deterministic 4-stage pipeline
    for speed and reliability.
    """
    
    def __init__(
        self,
        product_db: ProductDatabase,
        gemini: GeminiService,
        prompts: PromptsManager
    ):
        """
        Initialize orchestrator with required services.
        
        Args:
            product_db: Product database instance
            gemini: Gemini service instance
            prompts: Prompts manager instance
        """
        self.product_db = product_db
        self.gemini = gemini
        self.prompts = prompts
        
        print("✓ Orchestrator initialized")
    
    async def process_query(
        self,
        query: str,
        model_mode: str = "flash"
    ) -> Dict[str, Any]:
        """
        Main processing pipeline.
        
        Pipeline Stages:
        1. EXTRACTION - Extract model number from query
        2. RETRIEVAL - Retrieve data (structured + unstructured)
        3. SYNTHESIS - Synthesize with LLM
        4. FORMATTING - Format response
        
        Args:
            query: User's question
            model_mode: "flash" (fast) or "reasoning" (complex)
            
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
                "matched_product": Optional[str],
                "confidence": float,
                "timestamp": str
            }
        """
        try:
            print(f"\n{'='*60}")
            print(f"Processing Query: {query[:100]}...")
            print(f"Mode: {model_mode}")
            print(f"{'='*60}\n")
            
            # STAGE 1: EXTRACTION
            print("STAGE 1: EXTRACTION")
            product_context = self._extract_product(query)
            
            if product_context:
                print(f"✓ Found product: {product_context.model_number} "
                      f"(confidence: {product_context.matched_confidence:.2f})")
            else:
                print("ℹ No specific product identified")
            
            # STAGE 2: RETRIEVAL
            print("\nSTAGE 2: RETRIEVAL")
            retrieval_context = await self._retrieve_data(query, product_context)
            
            # STAGE 3: SYNTHESIS
            print("\nSTAGE 3: SYNTHESIS")
            llm_response = await self._synthesize_response(
                query=query,
                context=retrieval_context,
                mode=model_mode,
                product_context=product_context
            )
            
            # STAGE 4: FORMATTING
            print("\nSTAGE 4: FORMATTING")
            final_output = self._format_output(
                llm_response=llm_response,
                product_context=product_context,
                retrieval_context=retrieval_context
            )
            
            print(f"\n{'='*60}")
            print("✓ Processing complete")
            print(f"{'='*60}\n")
            
            return final_output
            
        except Exception as e:
            print(f"✗ Error in orchestrator pipeline: {e}")
            raise
    
    def _extract_product(self, query: str) -> Optional[ProductContext]:
        """
        STAGE 1: Extract product from query.
        
        Uses ProductDatabase's fuzzy/regex matching capabilities.
        """
        return self.product_db.find_product(query)
    
    async def _retrieve_data(
        self,
        query: str,
        product_context: Optional[ProductContext]
    ) -> Dict[str, Any]:
        """
        STAGE 2: Retrieve structured and unstructured data.
        
        Strategy:
        - If product found: Get specs/media + targeted file search
        - If no product: Broad file search
        """
        retrieval_context = {
            "structured": {},
            "unstructured": []
        }
        
        # Get structured data if product found
        if product_context:
            print(f"  → Retrieving structured data for {product_context.model_number}")
            retrieval_context["structured"] = {
                "specs": product_context.specs,
                "media": product_context.media,
                "documents": product_context.documents
            }
            print(f"    - Specs: {len(product_context.specs)} fields")
            print(f"    - Videos: {len(product_context.media.get('videos', []))}")
            print(f"    - Images: {len(product_context.media.get('images', []))}")
            print(f"    - Documents: {len(product_context.documents)}")
            
            # Targeted file search
            print(f"  → Performing targeted file search...")
            file_search_results = await self.gemini.file_search(
                query=query,
                model_filter=product_context.model_number,
                max_results=5
            )
        else:
            print(f"  → Performing broad file search...")
            # Broad file search
            file_search_results = await self.gemini.file_search(
                query=query,
                max_results=5
            )
        
        retrieval_context["unstructured"] = file_search_results
        print(f"    - File search results: {len(file_search_results)}")
        
        return retrieval_context
    
    async def _synthesize_response(
        self,
        query: str,
        context: Dict[str, Any],
        mode: str,
        product_context: Optional[ProductContext]
    ) -> Dict[str, Any]:
        """
        STAGE 3: Synthesize response with LLM.
        
        Combines query + structured data + unstructured data
        and sends to LLM for comprehensive response generation.
        """
        # Select appropriate system prompt
        system_prompt = self.prompts.get_synthesis_prompt()
        
        # Check if this is a troubleshooting query
        troubleshooting_keywords = ['not working', 'broken', 'leak', 'issue', 'problem', 'fix', 'repair']
        if any(keyword in query.lower() for keyword in troubleshooting_keywords):
            system_prompt = self.prompts.get_troubleshooting_prompt()
            print("  → Using troubleshooting prompt")
        
        # Check if this is a comparison query
        comparison_keywords = ['compare', 'difference', 'versus', 'vs', 'better']
        if any(keyword in query.lower() for keyword in comparison_keywords):
            system_prompt = self.prompts.get_comparison_prompt()
            print("  → Using comparison prompt")
        
        print(f"  → Generating response with {mode} model...")
        
        # Generate response
        llm_response = await self.gemini.generate_response(
            query=query,
            context=context,
            mode=mode,
            system_prompt=system_prompt
        )
        
        print(f"    - Model used: {llm_response['model_used']}")
        print(f"    - Sources: {len(llm_response['sources'])}")
        
        return llm_response
    
    def _format_output(
        self,
        llm_response: Dict[str, Any],
        product_context: Optional[ProductContext],
        retrieval_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        STAGE 4: Format final output for frontend.
        
        Structures the response with all necessary metadata
        and media assets for the UI.
        """
        print("  → Formatting final output...")
        
        # Build media assets structure
        media_assets = None
        if product_context:
            media_assets = {
                "specs": product_context.specs,
                "videos": product_context.media.get("videos", []),
                "images": product_context.media.get("images", []),
                "documents": product_context.documents
            }
        
        output = {
            "markdown_response": llm_response["response"],
            "media_assets": media_assets,
            "sources": llm_response["sources"],
            "model_used": llm_response["model_used"],
            "matched_product": product_context.model_number if product_context else None,
            "confidence": product_context.matched_confidence if product_context else 0.0,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        print(f"    - Response length: {len(output['markdown_response'])} chars")
        print(f"    - Media assets: {'Yes' if media_assets else 'No'}")
        
        return output
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "database_stats": self.product_db.get_stats(),
            "orchestrator_ready": True
        }


# Global instance (initialized in main.py)
orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    """Get global orchestrator instance"""
    if orchestrator is None:
        raise RuntimeError("Orchestrator not initialized")
    return orchestrator
