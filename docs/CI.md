# Continuous integration

GitHub Actions runs two independent jobs for every pull request and for pushes to `main`.

- **Frontend**: Node 22, `npm ci`, `npm run lint`, `npm run build`.
- **Backend**: Python 3.11, pinned-range development requirements, compile check, and pytest API regressions.

## Reproduce locally

```bash
npm ci
npm run lint
npm run build

python -m pip install -r backend/requirements-dev.txt
python -m compileall -q backend
python -m pytest backend/tests -q
```

No model credentials or hosted services are needed for CI. Tests use temporary local storage. Before merging, check that both jobs pass; configure branch protection in the repository settings if your plan permits it.

## Continuous delivery

This PR deliberately does **not** deploy. Deployment needs an agreed hosting target, storage lifecycle, and securely configured credentials. Do not put cloud keys in workflows or PRs.

## PR checklist

1. Link your task/issue, describe the change and affected API contracts.
2. Include reproducible test steps and examples (without secrets).
3. Confirm CI is green and existing extraction/upload flows still work.
4. Explain missing integrations, feature flags and deployment requirements accurately.
