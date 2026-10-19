"""Lightweight signature and container validation for local material uploads.

Not antivirus scanning or complete media decoding. File types are checked before
the API marks upload successful. Existing extraction is unchanged.
"""
from pathlib import Path
from zipfile import ZipFile, BadZipFile
import pymupdf

OLE = bytes.fromhex("D0CF11E0A1B11AE1")
EBML = bytes.fromhex("1A45DFA3")


def validate_upload_content(path: Path, extension: str) -> None:
    with path.open("rb") as stream:
        header = stream.read(4096)
    if not header:
        raise ValueError("Uploaded file is empty.")

    if extension == ".pdf":
        if not header.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF signature.")
        try:
            with pymupdf.open(path) as doc:
                if not doc.page_count or doc.needs_pass:
                    raise ValueError("PDF is empty or password protected.")
        except (pymupdf.EmptyFileError, pymupdf.FileDataError) as exc:
            raise ValueError("PDF is corrupt.") from exc
    elif extension == ".pptx":
        if not header.startswith(b"PK"):
            raise ValueError("Invalid PPTX signature.")
        try:
            with ZipFile(path) as archive:
                names = set(archive.namelist())
                if not {"[Content_Types].xml", "ppt/presentation.xml"}.issubset(names):
                    raise ValueError("Invalid PPTX container contents.")
                for info in archive.infolist():
                    if info.file_size > 100 * 1024 * 1024:
                        raise ValueError("PPTX archive member exceeds safe size limit.")
        except BadZipFile as exc:
            raise ValueError("Corrupt PPTX archive.") from exc
    elif extension == ".ppt":
        if not header.startswith(OLE):
            raise ValueError("Invalid legacy PPT signature.")
    elif extension == ".avi":
        if len(header) < 12 or header[:4] != b"RIFF" or header[8:12] != b"AVI ":
            raise ValueError("Invalid AVI container.")
    elif extension in {".mp4", ".mov"}:
        brands = (b"ftyp",) if extension == ".mp4" else (b"ftyp", b"moov", b"mdat", b"wide")
        if len(header) < 12 or header[4:8] not in brands:
            raise ValueError("Invalid MP4/MOV container.")
    elif extension == ".mkv":
        if not header.startswith(EBML):
            raise ValueError("Invalid MKV container.")
    elif extension == ".webm":
        if not header.startswith(EBML) or b"webm" not in header:
            raise ValueError("Invalid WebM container.")
    else:
        raise ValueError("Unsupported content type.")
