import os
import uuid
from dataclasses import dataclass

from fastapi import UploadFile
from fastapi.responses import FileResponse, Response

from app.config import settings


@dataclass
class SavedObject:
    storage_mode: str
    storage_key: str
    filename: str
    content_type: str


class StorageService:
    """
    Disk mode (now):
      - saves into DISK_STORAGE_PATH
      - storage_key = relative filename within disk storage directory

    S3 mode (later):
      - storage_key = object key in bucket
      - download returns a redirect to signed URL (or streams file)
    """

    def __init__(self):
        self.mode = (settings.storage_mode or "disk").strip().lower()

    def save_upload(self, upload: UploadFile) -> SavedObject:
        if self.mode == "disk":
            return self._save_disk(upload)
        if self.mode == "s3":
            return self._save_s3(upload)
        raise ValueError(f"Unsupported STORAGE_MODE: {self.mode}")

    def save_bytes(self, *, data: bytes, filename: str, content_type: str) -> SavedObject:
        if self.mode == "disk":
            return self._save_disk_bytes(data=data, filename=filename, content_type=content_type)
        if self.mode == "s3":
            return self._save_s3_bytes(data=data, filename=filename, content_type=content_type)
        raise ValueError(f"Unsupported STORAGE_MODE: {self.mode}")

    def download_response(self, storage_mode: str, storage_key: str, filename: str) -> Response:
        storage_mode = (storage_mode or "disk").strip().lower()
        if storage_mode == "disk":
            return self._download_disk(storage_key, filename)
        if storage_mode == "s3":
            return self._download_s3(storage_key, filename)
        raise ValueError(f"Unsupported storage_mode: {storage_mode}")

    # ---------- DISK ----------
    def _ensure_disk_dir(self):
        os.makedirs(settings.disk_storage_path, exist_ok=True)

    def _save_disk(self, upload: UploadFile) -> SavedObject:
        self._ensure_disk_dir()
        ext = os.path.splitext(upload.filename or "")[1].lower()
        safe_name = f"{uuid.uuid4().hex}{ext}"
        abs_path = os.path.join(settings.disk_storage_path, safe_name)

        with open(abs_path, "wb") as f:
            f.write(upload.file.read())

        return SavedObject(
            storage_mode="disk",
            storage_key=safe_name,
            filename=upload.filename or safe_name,
            content_type=(upload.content_type or "application/octet-stream"),
        )

    def _save_disk_bytes(self, *, data: bytes, filename: str, content_type: str) -> SavedObject:
        self._ensure_disk_dir()
        ext = os.path.splitext(filename)[1].lower()
        safe_name = f"{uuid.uuid4().hex}{ext}"
        abs_path = os.path.join(settings.disk_storage_path, safe_name)

        with open(abs_path, "wb") as f:
            f.write(data)

        return SavedObject(
            storage_mode="disk",
            storage_key=safe_name,
            filename=filename,
            content_type=content_type,
        )

    def _download_disk(self, storage_key: str, filename: str) -> Response:
        abs_path = os.path.join(settings.disk_storage_path, storage_key)
        return FileResponse(
            abs_path,
            media_type="application/octet-stream",
            filename=filename,
        )

    # ---------- S3 / R2 (later) ----------
    def _save_s3(self, upload: UploadFile) -> SavedObject:
        raise NotImplementedError("S3 storage not configured yet. Keep STORAGE_MODE=disk for now.")

    def _download_s3(self, storage_key: str, filename: str) -> Response:
        raise NotImplementedError("S3 downloads not configured yet. Keep STORAGE_MODE=disk for now.")

    def _save_s3_bytes(self, *, data: bytes, filename: str, content_type: str) -> SavedObject:
        raise NotImplementedError("S3 storage not configured yet. Keep STORAGE_MODE=disk for now.")


storage = StorageService()
