"""
Freshdesk Service - Freshdesk API Integration

Handles posting private notes to Freshdesk tickets.
"""

import aiohttp
from typing import Dict, Optional


class FreshdeskService:
    """
    Freshdesk API wrapper for ticket operations.
    
    Primarily used to post private notes with research results
    from the Agent Assist Console to specific tickets.
    """
    
    def __init__(self, domain: str, api_key: str):
        """
        Initialize Freshdesk service.
        
        Args:
            domain: Freshdesk subdomain (e.g., 'yourcompany' or 'yourcompany.freshdesk.com')
            api_key: Freshdesk API key
        """
        # FIX: Clean the domain to ensure no double .freshdesk.com
        domain = domain.replace("https://", "").replace("http://", "")
        if domain.endswith(".freshdesk.com"):
            domain = domain.replace(".freshdesk.com", "")
        
        self.base_url = f"https://{domain}.freshdesk.com/api/v2"
        self.api_key = api_key
        self.auth = aiohttp.BasicAuth(api_key, 'X')  # Freshdesk uses API key as username
        
        print(f"✓ Freshdesk service initialized for domain: {domain}")
    
    async def add_private_note(
        self,
        ticket_id: str,
        note_html: str,
        notify_agents: bool = False
    ) -> Dict[str, any]:
        """
        Add a private note to a Freshdesk ticket.
        
        Args:
            ticket_id: Freshdesk ticket ID
            note_html: HTML formatted note content
            notify_agents: Whether to notify agents about the note
            
        Returns:
            {
                "success": bool,
                "note_id": Optional[str],
                "error": Optional[str]
            }
        """
        try:
            url = f"{self.base_url}/tickets/{ticket_id}/notes"
            
            payload = {
                "body": note_html,
                "private": True,
                "notify_emails": [] if not notify_agents else None
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    auth=self.auth,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status in [200, 201]:
                        data = await response.json()
                        return {
                            "success": True,
                            "note_id": str(data.get("id")),
                            "error": None
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "note_id": None,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "note_id": None,
                "error": str(e)
            }
    
    async def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """
        Get ticket details (for validation).
        
        Args:
            ticket_id: Freshdesk ticket ID
            
        Returns:
            Ticket data or None if not found
        """
        try:
            url = f"{self.base_url}/tickets/{ticket_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, auth=self.auth) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
                    
        except Exception as e:
            print(f"✗ Error fetching ticket {ticket_id}: {e}")
            return None
    
    async def validate_connection(self) -> bool:
        """
        Validate Freshdesk API connection.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Try to fetch tickets (with limit 1) as a connection test
            url = f"{self.base_url}/tickets?per_page=1"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, auth=self.auth) as response:
                    return response.status == 200
                    
        except Exception as e:
            print(f"✗ Freshdesk connection validation failed: {e}")
            return False


# Global instance (initialized in main.py)
freshdesk_service: Optional[FreshdeskService] = None


def get_freshdesk_service() -> Optional[FreshdeskService]:
    """Get global Freshdesk service instance (may be None if not configured)"""
    return freshdesk_service
