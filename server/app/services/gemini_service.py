"""
Gemini Service - Google GenAI Wrapper

Handles all interactions with Google's Generative AI API including
chat completions and file search capabilities.
"""

import os
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types


class GeminiService:
    """
    Wrapper for Google GenAI API with support for:
    - Multiple models (flash vs pro)
    - File Search tool integration
    - Context management
    """
    
    def __init__(self, api_key: str, corpus_id: Optional[str] = None):
        """
        Initialize Gemini service.
        
        Args:
            api_key: Google API key
            corpus_id: Optional File Search store name (e.g., fileSearchStores/abc123)
        """
        self.client = genai.Client(api_key=api_key)
        self.file_search_store_name = corpus_id  # Renamed for clarity
        
        # Model configurations
        self.models = {
            "flash": "gemini-2.5-flash",
            "reasoning": "gemini-2.5-pro"
        }
        
        print("✓ Gemini service initialized")
    
    async def generate_response(
        self,
        query: str,
        context: Dict[str, Any],
        mode: str = "flash",
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate LLM response with optional context.
        
        Args:
            query: User's question
            context: Structured data (specs, media, file search results)
            mode: "flash" (fast) or "reasoning" (complex)
            system_prompt: Custom system instructions
            
        Returns:
            {
                "response": str,
                "sources": List[str],
                "model_used": str
            }
        """
        try:
            model_name = self.models.get(mode, self.models["flash"])
            
            # Build the prompt with context
            full_prompt = self._build_prompt(query, context)
            
            # Prepare configuration
            config = types.GenerateContentConfig(
                temperature=0.2 if mode == "flash" else 0.4,
                top_p=0.95,
                top_k=40,
                max_output_tokens=4096,
                system_instruction=system_prompt if system_prompt else None
            )
            
            # Generate response
            response = self.client.models.generate_content(
                model=model_name,
                contents=full_prompt,
                config=config
            )
            
            # Extract sources from context
            sources = self._extract_sources(context)
            
            return {
                "response": response.text,
                "sources": sources,
                "model_used": model_name
            }
            
        except Exception as e:
            print(f"✗ Error generating response: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def file_search(
        self,
        query: str,
        model_filter: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Execute File Search against knowledge base using Gemini file search tool (async, google-genai >=1.55.0).
        Args:
            query: Search query
            model_filter: Optional model number to filter results
            max_results: Maximum number of results to return
        Returns:
            List of document chunks with metadata
        """
        from google.genai import errors
        if not self.file_search_store_name:
            print("⚠ File Search store not configured, skipping")
            return []
        try:
            search_query = query
            if model_filter:
                search_query = f"{model_filter} {query}"
            # Use async client for file search
            aclient = self.client.aio
            response = await aclient.models.generate_content(
                model=self.models["flash"],
                contents=search_query,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[self.file_search_store_name],
                            top_k=max_results
                        )
                    )]
                )
            )
            results = []
            candidates = getattr(response, "candidates", None)
            if candidates and hasattr(candidates[0], "grounding_metadata"):
                grounding = candidates[0].grounding_metadata
                if grounding and getattr(grounding, "grounding_chunks", None):
                    for chunk in grounding.grounding_chunks[:max_results]:
                        ctx = getattr(chunk, "retrieved_context", None)
                        results.append({
                            "title": getattr(ctx, "title", "Unknown") if ctx else "Unknown",
                            "text": getattr(ctx, "text", "") if ctx else "",
                            "uri": getattr(ctx, "uri", "") if ctx else ""
                        })
            print(f"✓ File search returned {len(results)} results")
            return results
        except errors.APIError as e:
            print(f"⚠ Gemini API error: {e.code} {e.message}")
            return []
        except Exception as e:
            print(f"⚠ File search error: {e}")
            return []
    
    def _build_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Build comprehensive prompt with structured context"""
        
        prompt_parts = [f"User Query: {query}\n"]
        
        # Check if this is a general query (no product context)
        has_product = "structured" in context and context["structured"] and context["structured"].get("specs")
        
        if not has_product:
            # GENERAL QUERY: Use only file search results from policy documents
            prompt_parts.append("\n**Note:** This is a general query about company policies, programs, or procedures. Do NOT include product-specific details. Answer using ONLY the documentation excerpts below.\n")
        
        # Add structured data (specs) - only if product was found
        if "structured" in context and context["structured"]:
            structured = context["structured"]
            
            if "specs" in structured and structured["specs"]:
                prompt_parts.append("\n## Product Specifications:")
                specs = structured["specs"]
                for key, value in specs.items():
                    if key not in ['Model_NO', 'Product_Name']:
                        prompt_parts.append(f"- {key}: {value}")
            
            # FIX: Defensive check for media being a dict
            if "media" in structured and structured["media"]:
                media = structured["media"]
                
                # Ensure media is a dictionary
                if not isinstance(media, dict):
                    print(f"⚠ Warning: media is not a dict, it's a {type(media)}. Value: {media}")
                    media = {"videos": [], "images": []}
                
                # Safely access videos
                videos = media.get("videos", []) if isinstance(media, dict) else []
                if videos and isinstance(videos, list):
                    prompt_parts.append("\n## Available Videos:")
                    for video in videos:
                        if isinstance(video, dict):
                            title = video.get('title', 'Video')
                            url = video.get('url', '')
                            prompt_parts.append(f"- {title}: {url}")
                        elif isinstance(video, str):
                            prompt_parts.append(f"- Video: {video}")
                
                # Safely access images
                images = media.get("images", []) if isinstance(media, dict) else []
                if images and isinstance(images, list):
                    prompt_parts.append("\n## Available Images:")
                    for image in images:
                        if isinstance(image, dict):
                            title = image.get('title', 'Image')
                            url = image.get('url', '')
                            prompt_parts.append(f"- {title}: {url}")
                        elif isinstance(image, str):
                            prompt_parts.append(f"- Image: {image}")
            
            if "documents" in structured and structured["documents"]:
                documents = structured["documents"]
                if isinstance(documents, list):
                    prompt_parts.append("\n## Available Documents:")
                    for doc in documents:
                        if isinstance(doc, dict):
                            title = doc.get('title', 'Document')
                            doc_type = doc.get('type', 'Document')
                            url = doc.get('url', '')
                            prompt_parts.append(f"- {title} ({doc_type}): {url}")
        
        # Add unstructured data (file search results)
        if "unstructured" in context and context["unstructured"]:
            prompt_parts.append("\n## Relevant Documentation Excerpts:")
            for idx, result in enumerate(context["unstructured"], 1):
                if isinstance(result, dict):
                    prompt_parts.append(f"\n### Excerpt {idx} (from {result.get('title', 'Unknown')})")
                    prompt_parts.append(result.get('text', ''))
        
        return "\n".join(prompt_parts)
    
    def _extract_sources(self, context: Dict[str, Any]) -> List[str]:
        """Extract source references from context"""
        sources = []
        
        # From file search results
        if "unstructured" in context:
            for result in context["unstructured"]:
                if isinstance(result, dict):
                    title = result.get('title', 'Documentation')
                    page = result.get('page', '')
                    source = f"{title}"
                    if page:
                        source += f" (Page {page})"
                    if source not in sources:
                        sources.append(source)
        
        # From documents
        if "structured" in context and "documents" in context["structured"]:
            documents = context["structured"]["documents"]
            if isinstance(documents, list):
                for doc in documents:
                    if isinstance(doc, dict):
                        title = doc.get('title', '')
                        if title and title not in sources:
                            sources.append(title)
        
        return sources


# Global instance (initialized in main.py)
gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get global Gemini service instance"""
    if gemini_service is None:
        raise RuntimeError("Gemini service not initialized")
    return gemini_service