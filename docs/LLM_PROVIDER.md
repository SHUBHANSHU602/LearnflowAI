# AI model provider gateway

`backend/llm_provider.py` exposes a `ModelProvider` protocol, allowing backend
orchestration to use any compatible implementation. The bundled adapter speaks
an OpenAI-compatible **chat completions** endpoint; not every vendor supports it.

## Configuration

Set these values **server side** (never use `VITE_` for secrets):

- `LEARNFLOW_MODEL_ENDPOINT`: HTTPS URL for a trusted provider's chat endpoint
- `LEARNFLOW_MODEL_NAME`: approved model name
- `LEARNFLOW_MODEL_API_KEY`: token for the model provider

The endpoint is trusted deployment configuration only. Do not accept it from API
requests. Configure secret values with the hosting provider's secrets system.

## Example service usage

```python
from backend.llm_provider import ProviderConfig, OpenAICompatibleProvider
provider = OpenAICompatibleProvider(ProviderConfig.from_env())
answer = await provider.answer(question, [hit.text for hit in verified_hits])
```

## Important trust boundary

The caller MUST first enforce source ownership, `allowed_source_ids`,
and watched-time filtering. Never send future video segments to the model.
The LLM is not an authority for citations: attach validated citation metadata
from the exact retrieved evidence on the server after generating the answer.

The provider adapter alone does not implement a RAG pipeline, quiz API,
grounding correctness evaluation or Bedrock-specific authentication.

## Tests

```bash
python -m pip install -r backend/requirements-dev.txt
python -m pytest backend/tests/test_llm_provider.py -q
```

No API key is needed for tests; the network is mocked.

## Runtime dependency

The production backend installs `httpx` through `backend/requirements.txt`.
The adapter is imported directly only by trusted backend code and currently
does not expose a public route on its own. When integrating it into chat,
configure a trusted HTTPS endpoint and handle provider errors as HTTP 503.

A passing mock test does **not** demonstrate an actual model account, a
production deployment, or verified answer grounding.
