"""Upload routes."""

from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Dict
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import get_settings
from app.schemas import UploadStatus
from app.services.progress import progress_store
from app.tasks.importer import import_products_task

router = APIRouter(prefix="/upload", tags=["upload"])

MAX_ROWS = 500_000


def _count_rows(file_path: Path) -> int:
    """Count data rows in CSV file."""
    with file_path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return sum(1 for _ in reader)


async def _save_upload(upload_file: UploadFile, temp_dir: Path) -> Path:
    """Persist uploaded file to a temporary path."""
    temp_dir.mkdir(parents=True, exist_ok=True)
    filename = upload_file.filename or "upload.csv"
    temp_path = temp_dir / f"{uuid4()}_{filename}"

    with temp_path.open("wb") as buffer:
        while True:
            chunk = await upload_file.read(1024 * 1024)
            if not chunk:
                break
            buffer.write(chunk)
    return temp_path


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def upload_csv(file: UploadFile = File(...)) -> Dict[str, str]:
    """Accept CSV file and enqueue background import."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are accepted.")

    settings = get_settings()
    temp_dir = Path(settings.temp_upload_dir)
    temp_path = await _save_upload(file, temp_dir)

    try:
        total_rows = _count_rows(temp_path)
    except Exception:
        os.remove(temp_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSV file.")

    if total_rows > MAX_ROWS:
        os.remove(temp_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV exceeds max allowed rows ({MAX_ROWS}).",
        )

    task = import_products_task.delay(str(temp_path), total_rows)
    progress_store.update_progress(task.id, processed=0, total=total_rows, message="Queued")

    return {"task_id": task.id}


@router.get("/status/{task_id}", response_model=UploadStatus)
def upload_status(task_id: str) -> UploadStatus:
    """Return background upload progress."""
    payload = progress_store.get(task_id)
    if not payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    payload.pop("error", None)
    return UploadStatus(**payload)
