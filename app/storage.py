# app/storage.py
import os
import uuid
from pathlib import Path

UPLOAD_DIR = Path("storage/uploads")

def ensure_storage():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_upload(original_filename: str, data: bytes) -> str:
    ensure_storage()
    ext = ""
    if "." in original_filename:
        ext = "." + original_filename.split(".")[-1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / safe_name
    path.write_bytes(data)
    return safe_name

def file_path(filename: str) -> Path:
    return UPLOAD_DIR / filename
