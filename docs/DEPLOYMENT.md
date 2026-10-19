# LearnFlow AI backend deployment guide

## What this PR delivers

A reproducible FastAPI Docker image, request timing metadata, and
configuration documentation. **It does not deploy a live service**, create
cloud resources, upload secrets, or implement authentication.

## Build and start (Docker)

From the repository root:

```bash
docker build -f backend/Dockerfile -t learnflow-api:local .
docker run --rm -p 8000:8000 \
  -e LEARNFLOW_MAX_UPLOAD_SIZE_MB=100 \
  -e LEARNFLOW_CORS_ORIGINS=http://localhost:5173 \
  learnflow-api:local
curl http://localhost:8000/health
```

The expected response is `{"status":"ok"}`. The container runs as an
unprivileged user and stores temporary uploads in `backend/uploads`.
**Uploads are lost on container restart** unless durable storage is wired in.
Do not use this container for multi-user public production traffic until
authenticated source ownership, storage isolation, retention and scanning
have been implemented.

## Environment variables

- `LEARNFLOW_MAX_UPLOAD_SIZE_MB`: upload size cap (default 100).
- `LEARNFLOW_CORS_ORIGINS`: comma-separated trusted frontend origins;
  default `http://localhost:5173`. Production must set a real HTTPS origin.

Model provider keys are configured separately; never commit them.

## Future CD steps

1. Choose a cloud deployment account and budget (App Runner or other agreed
   target), supply credentials through the provider's secret store.
2. Build image after passing PR checks; push to a managed registry using OIDC
   identity, not long-lived AWS keys in GitHub.
3. Run a health and API smoke test against the deployed URL.
4. Configure persistent/object storage before supporting real student uploads.
5. Set an allowed frontend origin and arrange monitoring, retention and
   per-user source authorization.

CD is intentionally deferred until the destination is confirmed.
