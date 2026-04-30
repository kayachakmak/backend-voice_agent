from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.core.auth import TokenPayload, get_current_user
from app.core.config import Settings, get_settings
from app.schemas.elevenlabs import (
    AgentDetailResponse,
    AgentListResponse,
    BatchDetailResponse,
    BatchJob,
    BatchJobListResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    PhoneNumberItem,
    SubmitBatchCallRequest,
    SubmitBatchCallResponse,
)
from app.services.elevenlabs_service import ElevenLabsService

router = APIRouter()


def _get_service(settings: Settings = Depends(get_settings)) -> ElevenLabsService:
    return ElevenLabsService(settings)


@router.get("/batch-calling/agents", response_model=AgentListResponse)
async def list_agents(
    page_size: int = Query(default=30, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    cursor: Optional[str] = Query(default=None),
    current_user: TokenPayload = Depends(get_current_user),
    service: ElevenLabsService = Depends(_get_service),
) -> AgentListResponse:
    data = await service.list_agents(page_size=page_size, search=search, cursor=cursor)
    return AgentListResponse.model_validate(data)


@router.get("/batch-calling/agents/{agent_id}", response_model=AgentDetailResponse)
async def get_agent(
    agent_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    service: ElevenLabsService = Depends(_get_service),
) -> AgentDetailResponse:
    data = await service.get_agent(agent_id)
    return AgentDetailResponse.model_validate(data)


@router.get("/batch-calling/phone-numbers", response_model=List[PhoneNumberItem])
async def list_phone_numbers(
    current_user: TokenPayload = Depends(get_current_user),
    service: ElevenLabsService = Depends(_get_service),
) -> List[PhoneNumberItem]:
    data = await service.list_phone_numbers()
    return [PhoneNumberItem.model_validate(item) for item in data]


@router.post("/batch-calling/submit", response_model=SubmitBatchCallResponse)
async def submit_batch_call(
    body: SubmitBatchCallRequest,
    current_user: TokenPayload = Depends(get_current_user),
    service: ElevenLabsService = Depends(_get_service),
) -> SubmitBatchCallResponse:
    payload = body.model_dump(exclude_none=True)
    recipients_out = []
    for r in body.recipients:
        entry: Dict[str, Any] = {"phone_number": r.phone_number}
        if r.dynamic_variables:
            entry["conversation_initiation_client_data"] = {
                "dynamic_variables": r.dynamic_variables,
            }
        recipients_out.append(entry)
    payload["recipients"] = recipients_out
    data = await service.submit_batch_call(payload)
    return SubmitBatchCallResponse.model_validate(data)


@router.get("/batch-calling/conversations", response_model=ConversationListResponse)
async def list_conversations(
    agent_id: str = Query(...),
    page_size: int = Query(default=20, ge=1, le=100),
    cursor: Optional[str] = Query(default=None),
    current_user: TokenPayload = Depends(get_current_user),
    service: ElevenLabsService = Depends(_get_service),
) -> ConversationListResponse:
    data = await service.list_conversations(
        agent_id=agent_id, page_size=page_size, cursor=cursor
    )
    return ConversationListResponse.model_validate(data)


@router.get("/batch-calling/jobs", response_model=BatchJobListResponse)
async def list_batch_jobs(
    limit: int = Query(default=100, ge=1, le=100),
    last_doc: Optional[str] = Query(default=None),
    current_user: TokenPayload = Depends(get_current_user),
    service: ElevenLabsService = Depends(_get_service),
) -> BatchJobListResponse:
    data = await service.list_batch_jobs(limit=limit, last_doc=last_doc)
    return BatchJobListResponse.model_validate(data)


@router.get("/batch-calling/jobs/{batch_id}", response_model=BatchDetailResponse)
async def get_batch_status(
    batch_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    service: ElevenLabsService = Depends(_get_service),
) -> BatchDetailResponse:
    data = await service.get_batch_status(batch_id)
    return BatchDetailResponse.model_validate(data)


@router.get(
    "/batch-calling/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
)
async def get_conversation(
    conversation_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    service: ElevenLabsService = Depends(_get_service),
) -> ConversationDetailResponse:
    data = await service.get_conversation(conversation_id)
    return ConversationDetailResponse.model_validate(data)


@router.get("/batch-calling/conversations/{conversation_id}/audio")
async def get_conversation_audio(
    conversation_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    service: ElevenLabsService = Depends(_get_service),
) -> Response:
    audio_bytes = await service.get_conversation_audio(conversation_id)
    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f'inline; filename="{conversation_id}.mp3"'},
    )


@router.post("/batch-calling/jobs/{batch_id}/cancel", response_model=BatchJob)
async def cancel_batch_call(
    batch_id: str,
    current_user: TokenPayload = Depends(get_current_user),
    service: ElevenLabsService = Depends(_get_service),
) -> BatchJob:
    data = await service.cancel_batch_call(batch_id)
    return BatchJob.model_validate(data)
