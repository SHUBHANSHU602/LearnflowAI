# LearnFlow AI

LearnFlow AI is a learning workspace being built in small milestones. The current milestone contains:

- A React + TypeScript + Vite frontend
- A Python + FastAPI backend with health, local material-upload, and text-extraction endpoints
- A homepage with a material upload interface, extraction controls, and a readable learning workspace

AI processing, transcription, summaries, OCR, and RAG are intentionally **not implemented yet**.

## Folder guide

- `src/` - The frontend source code. `App.tsx` contains the page structure, while `App.css` and `index.css` contain its styles.
- `backend/` - The Python API. `main.py` defines the FastAPI application, CORS settings, validation, upload, and extraction endpoints.
- `backend/extraction.py` - Small, separate PyMuPDF and python-pptx functions that return page- or slide-level text.
- `backend/uploads/` - Created automatically when the first upload succeeds. Local uploaded files are kept here and are ignored by Git.
- `public/` - Static files that Vite serves directly.
- `package.json` - Frontend commands and JavaScript dependencies.
- `requirements.txt` - Python backend dependencies.
- `.env.example` - Safe placeholder names for future configuration. It contains no real secrets.

The upload endpoint accepts PDF, PPT, PPTX, MP4, WebM, MOV, AVI, and MKV files up to 100 MB by default. Set `LEARNFLOW_MAX_UPLOAD_SIZE_MB` before starting the backend to change that development limit.

PDF and PPTX extraction is limited to 500 pages/slides, 2 million extracted characters, and 30 seconds per request. Legacy binary `.ppt` files can be uploaded, but `python-pptx` cannot read them; convert them to `.pptx` first.

## Prerequisites

Install these separately if they are not already installed: Node.js 20+, Python 3.10+, and Git. This project does not install software or change Windows settings for you.

## Windows PowerShell setup

Run these commands from the project folder:

```powershell
cd C:\Users\saumy\OneDrive\Desktop\LearnflowAI
npm install

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

If PowerShell blocks activation, you can run the backend with the virtual environment's Python directly instead:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

## Run both services

Open two PowerShell windows. In the first window, run the frontend:

```powershell
cd C:\Users\saumy\OneDrive\Desktop\LearnflowAI
npm run dev
```

Open the frontend at [http://localhost:5173](http://localhost:5173).

In the second window, run the backend:

```powershell
cd C:\Users\saumy\OneDrive\Desktop\LearnflowAI
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload --port 8000
```

The API is available at [http://localhost:8000](http://localhost:8000).

## Test the health endpoint

With the backend running, use this PowerShell command:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

You should receive:

```text
status
------
ok
```

You can also open [http://localhost:8000/health](http://localhost:8000/health) in a browser.

## Test a material upload

The easiest way to test the complete flow is to open [http://localhost:5173](http://localhost:5173), choose a supported file, and select **Upload material**. You can also test directly from PowerShell:

```powershell
curl.exe -X POST http://localhost:8000/materials/upload -F "file=@C:\path\to\your\sample.pdf"
```

The API returns the original filename, file type, byte size, and a generated stored filename. The generated file is saved under `backend\uploads\`; it is not publicly served by the API. Unsupported extensions return `415`, and files over the configured limit return `413`.

## Extract text from a PDF or PowerPoint

1. Upload a real `.pdf` or `.pptx` file using the browser interface.
2. After the upload succeeds, select **Extract text**.
3. The workspace displays the actual extracted text grouped by page or slide number.

The frontend calls:

```text
POST http://localhost:8000/materials/{stored_filename}/extract
```

Use the safe `stored_filename` returned by the upload endpoint; do not send a local filesystem path. The extraction endpoint returns structured records with `reference_type`, `reference_number`, `text`, and `has_text`. It rejects invalid identifiers, missing files, unsupported formats, empty documents, and extraction failures.

To test extraction directly from PowerShell after uploading:

```powershell
curl.exe -X POST http://localhost:8000/materials/REPLACE_WITH_STORED_FILENAME.pdf/extract
```

Scanned PDFs often contain images rather than selectable text. They will report that no extractable text was found because OCR is intentionally outside this milestone.

## Checks

```powershell
npm run build
npm run lint
python -m compileall backend
```
