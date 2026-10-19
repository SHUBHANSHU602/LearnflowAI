"""Fail-closed orchestration for grounded, watched-time lesson Q&A.

Document/video retrievers are separate team-owned adapters. The service cannot
produce an answer unless a trusted authorizer and retrievers are wired in.
"""
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol

from .contracts import ChatRequest, ChatResponse, RetrievalHit, SourceType
from .llm_provider import ModelProvider, ProviderError


class AuthorizationError(PermissionError):
    pass


class ChatUnavailableError(RuntimeError):
    pass


class SourceAuthorizer(Protocol):
    async def ensure_allowed(self, session_id: str, source_ids: list[str]) -> None: ...


class EvidenceRetriever(Protocol):
    async def retrieve_documents(self, question: str, allowed_source_ids: list[str]) -> list[RetrievalHit]: ...
    async def retrieve_video(self, question: str, video_source_id: str, playback_seconds: float) -> list[RetrievalHit]: ...


REFUSAL = "I cannot answer that from the material available at your current lesson position."


@dataclass
class GroundedChatService:
    authorizer: SourceAuthorizer
    retriever: EvidenceRetriever
    provider: ModelProvider

    async def answer(self, request: ChatRequest) -> ChatResponse:
        # IDs sent by the browser are never proof of ownership.
        await self.authorizer.ensure_allowed(request.session_id, request.allowed_source_ids)
        try:
            hits = await self.retriever.retrieve_documents(request.question, request.allowed_source_ids)
            if request.video_source_id is not None:
                video_hits = await self.retriever.retrieve_video(
                    request.question, request.video_source_id, request.playback_seconds
                )
                hits = [*hits, *video_hits]
        except Exception as exc:
            raise ChatUnavailableError("Evidence retrieval unavailable.") from exc

        valid = []
        for hit in hits:
            c = hit.citation
            if c.source_id not in request.allowed_source_ids:
                continue
            if c.source_type == SourceType.VIDEO:
                # No video evidence is accepted without explicit current position.
                if (request.video_source_id != c.source_id or request.playback_seconds is None
                        or c.end_seconds is None or c.end_seconds > request.playback_seconds):
                    continue
            valid.append(hit)
        if not valid:
            return ChatResponse(session_id=request.session_id, answer=REFUSAL, grounded=False, citations=[])

        valid = valid[:8]
        try:
            answer = await self.provider.answer(request.question, [h.text for h in valid])
        except ProviderError as exc:
            raise ChatUnavailableError("Answer generation unavailable.") from exc
        # Citations are constructed from returned evidence, not accepted from LLM text.
        return ChatResponse(session_id=request.session_id, answer=answer, grounded=True,
                            citations=[h.citation for h in valid])
