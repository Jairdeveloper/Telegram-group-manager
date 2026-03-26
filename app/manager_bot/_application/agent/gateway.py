"""Agent Gateway - Communication with external Agent service."""

import os
from typing import Any, Dict, Optional

import httpx


class AgentGateway:
    """Gateway for communicating with the external Agent service."""

    def __init__(self, agent_url: Optional[str] = None):
        self.agent_url = agent_url or os.getenv(
            "AGENT_SERVICE_URL", "http://localhost:8001"
        )
        self.client = httpx.AsyncClient(timeout=30.0)

    async def chat(
        self, message: str, session_id: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send message to the agent service."""
        try:
            response = await self.client.post(
                f"{self.agent_url}/chat",
                json={
                    "message": message,
                    "session_id": session_id,
                    "context": context or {},
                },
            )
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            return {
                "response": "Agent service unavailable",
                "confidence": 0.0,
                "sources": [],
                "error": "connection_error",
            }
        except httpx.TimeoutException:
            return {
                "response": "Agent service timeout",
                "confidence": 0.0,
                "sources": [],
                "error": "timeout",
            }
        except Exception as e:
            return {
                "response": f"Agent service error: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "error": "unknown",
            }

    async def health_check(self) -> bool:
        """Check if the agent service is available."""
        try:
            response = await self.client.get(f"{self.agent_url}/health")
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def is_available(self) -> bool:
        """Check if agent service URL is configured."""
        return self.agent_url is not None and self.agent_url != ""
