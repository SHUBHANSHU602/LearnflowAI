import asyncio
from dataclasses import dataclass
import pytest

from backend.contracts import ChatRequest, Citation, RetrievalHit
from backend.chat_service import GroundedChatService, AuthorizationError, REFUSAL


class Authorizer:
    async def ensure_allowed(self, session_id, source_ids):
        if "private" in source_ids:
            raise AuthorizationError("private source")


class Retriever:
    async def retrieve_documents(self, question, allowed_source_ids):
        return [
            RetrievalHit(citation=Citation(source_id="doc1", source_type="pdf", chunk_id="d1", page=3),
                         text="Allowed earlier slides"),
            RetrievalHit(citation=Citation(source_id="private", source_type="pdf", chunk_id="p1", page=7),
                         text="SECRET"),
        ]

    async def retrieve_video(self, question, video_source_id, playback_seconds):
        return [
            RetrievalHit(citation=Citation(source_id="video1", source_type="video",
                                          chunk_id="v1", start_seconds=5, end_seconds=10),
                         text="Prior lesson"),
            RetrievalHit(citation=Citation(source_id="video1", source_type="video",
                                          chunk_id="v2", start_seconds=50, end_seconds=60),
                         text="Future lesson"),
        ]


class Provider:
    def __init__(self):
        self.evidence = None

    async def answer(self, question, evidence):
        self.evidence = evidence
        return "Summary from provided context"


def test_excludes_future_and_unpermitted_sources():
    provider = Provider()
    service = GroundedChatService(Authorizer(), Retriever(), provider)
    request = ChatRequest(session_id="s1", question="What happened?", allowed_source_ids=["doc1","video1"],
                          video_source_id="video1", playback_seconds=30)
    result = asyncio.run(service.answer(request))
    assert result.grounded
    assert [c.chunk_id for c in result.citations] == ["d1", "v1"]
    assert provider.evidence == ["Allowed earlier slides", "Prior lesson"]


def test_backward_seek_filters_previously_visible_video():
    provider = Provider()
    service = GroundedChatService(Authorizer(), Retriever(), provider)
    request = ChatRequest(session_id="s1", question="What?", allowed_source_ids=["video1"],
                          video_source_id="video1", playback_seconds=2)
    result = asyncio.run(service.answer(request))
    assert result.grounded is False
    assert result.answer == REFUSAL
    assert provider.evidence is None


def test_requires_authorizer():
    service = GroundedChatService(Authorizer(), Retriever(), Provider())
    request = ChatRequest(session_id="s1", question="What?", allowed_source_ids=["private"])
    with pytest.raises(AuthorizationError):
        asyncio.run(service.answer(request))
