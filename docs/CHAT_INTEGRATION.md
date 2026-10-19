# Grounded chat integration plan

This PR introduces a real `POST /chat` route and tested orchestration code,
but starts in **503 fail-closed** mode until all team-owned adapters are wired.

The real application startup must supply:

1. **Authorizer** mapping authenticated session identity to owned sources,
   enforcing source-level access. A caller's session ID is not authentication.
2. **Document retriever** (Sneha) returning only authorized PDF/PPTX evidence.
3. **Video retriever** (Vansh) returning timestamp-filtered transcript segments.
4. **Model provider** (Shubhanshu, separate PR) producing an answer only from the
   curated evidence list.

The chat service adds a second defensive filter: unauthorized source IDs and
transcript segments ending after `playback_seconds` are discarded even if a
retriever accidentally returns them.

The provider result is **not** proof of correctness: grounding evaluations
and citation entailment checks must be added before calling this production-ready.
This PR attaches citation IDs from retrieved evidence and must be complemented
by proper evidence-selection quality tests.

**Important:** Multi-turn persistence, quiz endpoints and a real data-backed
source/session authorization store remain to be implemented. Do not turn on
the route using permissive placeholder adapters.
