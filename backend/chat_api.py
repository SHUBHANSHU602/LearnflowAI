"""HTTP endpoint for AI chat. Defaults to 503 until securely configured."""
from fastapi import APIRouter, HTTPException, Request

from .contracts import ChatRequest, ChatResponse
from .chat_service import (
    AuthorizationError,
    ChatUnavailableError,
    GroundedChatService,
)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    service: GroundedChatService | None = getattr(
        request.app.state, "chat_service", None
    )
    if service is None:
        raise HTTPException(
            status_code=503, detail="Chat integrations are not configured."
        )
    try:
        return await service.answer(payload)
    except AuthorizationError as exc:
        raise HTTPException(
            status_code=403, detail="Requested sources are not permitted."
        ) from exc
    except ChatUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
