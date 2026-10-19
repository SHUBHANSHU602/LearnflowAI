# Upload content validation

## Existing flow

The server supports PDF, PPT, PPTX, MP4, MOV, AVI, WebM and MKV.
Upload still returns the same `stored_filename` shape as before.
Size limits and temporary cleanup behavior remain intact.

## New checks

- Reject empty files (HTTP 422).
- Reject obviously mismatched formats by file signature (HTTP 415).
- Open PDFs with PyMuPDF and reject corrupt/password-protected PDFs.
- Validate required PPTX ZIP parts and bound individual uncompressed members.
- Apply lightweight container signature checks for supported video formats.

An upload is not a promise that the video is playable or that its
captions/transcription exist. No scanning for viruses is performed.
Production deployments must add sandboxing, malware scanning, storage
quotas and authenticated file ownership.

## Test

```bash
python -m pip install -r backend/requirements-dev.txt
python -m pytest backend/tests/test_upload_validation.py -q
```

Tests validate valid and forged PDF/PPTX inputs and cleanup paths.
