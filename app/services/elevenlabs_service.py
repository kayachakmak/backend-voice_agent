from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException

from app.core.config import Settings


class ElevenLabsService:
    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.elevenlabs_api_key

    def _headers(self) -> Dict[str, str]:
        return {"xi-api-key": self.api_key}

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.BASE_URL}{path}"
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method,
                    url,
                    headers=self._headers(),
                    params=clean_params or None,
                    json=json_body,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            detail = "ElevenLabs API error"
            try:
                detail = exc.response.json().get("detail", detail)
            except Exception:
                pass
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=detail,
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to reach ElevenLabs API: {exc}",
            )

    async def list_agents(
        self,
        page_size: int = 30,
        search: Optional[str] = None,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self._request(
            "GET",
            "/convai/agents",
            params={"page_size": page_size, "search": search, "cursor": cursor},
        )

    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/convai/agents/{agent_id}")

    async def list_phone_numbers(self) -> List[Dict[str, Any]]:
        return await self._request("GET", "/convai/phone-numbers")

    async def submit_batch_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request(
            "POST",
            "/convai/batch-calling/submit",
            json_body=payload,
        )

    async def list_batch_jobs(
        self,
        limit: int = 100,
        last_doc: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self._request(
            "GET",
            "/convai/batch-calling/workspace",
            params={"limit": limit, "last_doc": last_doc},
        )

    async def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/convai/batch-calling/{batch_id}")

    async def list_conversations(
        self,
        agent_id: str,
        page_size: int = 20,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self._request(
            "GET",
            "/convai/conversations",
            params={"agent_id": agent_id, "page_size": page_size, "cursor": cursor},
        )

    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/convai/conversations/{conversation_id}")

    async def get_conversation_audio(self, conversation_id: str) -> bytes:
        """Returns raw audio bytes for a conversation recording."""
        url = f"{self.BASE_URL}/convai/conversations/{conversation_id}/audio"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, headers=self._headers())
                response.raise_for_status()
                return response.content
        except httpx.HTTPStatusError as exc:
            detail = "ElevenLabs API error"
            try:
                detail = exc.response.json().get("detail", detail)
            except Exception:
                pass
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=detail,
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to reach ElevenLabs API: {exc}",
            )

    async def cancel_batch_call(self, batch_id: str) -> Dict[str, Any]:
        return await self._request(
            "POST",
            f"/convai/batch-calling/{batch_id}/cancel",
        )
