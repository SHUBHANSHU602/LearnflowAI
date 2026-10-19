"""HTTP adapter, installed in main.py with a fail-closed default."""
from fastapi import APIRouter, HTTPException
from .contracts import ChatRequest, ChatResponse
from .chat_service import GroundedChatService, AuthorizationError, ChatUnavailableError

router = APIRouter(tags=["chat"])
_service: GroundedChatService | None = None


def configure_chat_service(service: GroundedChatService) -> None:
    """Call from trusted application startup after attaching real authorizer/retrievers."""
    global _service
    _service = service


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if _service is None:
        raise HTTPException(status_code=503, detail="Chat integrations are not configured.")
    try:
        return await _service.answer(request)
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail="Requested sources are not permitted.") from exc
    except ChatUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
