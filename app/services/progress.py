"""Progress tracking utilities."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from threading import Lock
from typing import Dict, Optional


@dataclass
class ProgressRecord:
    status: str  # processing | completed | error
    processed: int
    total: int
    percent: float
    message: Optional[str] = None
    error: Optional[str] = None

    def as_dict(self) -> Dict[str, Optional[float]]:
        """Return serializable representation."""
        return asdict(self)


class ProgressStore:
    """Thread-safe in-memory progress store."""

    def __init__(self):
        self._store: Dict[str, ProgressRecord] = {}
        self._lock = Lock()

    def set(self, task_id: str, record: ProgressRecord) -> None:
        with self._lock:
            self._store[task_id] = record

    def get(self, task_id: str) -> Optional[Dict[str, Optional[float]]]:
        with self._lock:
            record = self._store.get(task_id)
            return record.as_dict() if record else None

    def update_progress(
        self, task_id: str, processed: int, total: int, message: str
    ) -> None:
        percent = round((processed / total) * 100, 2) if total else 0.0
        record = ProgressRecord(
            status="processing", processed=processed, total=total, percent=percent, message=message
        )
        self.set(task_id, record)

    def mark_complete(self, task_id: str, processed: int, total: int) -> None:
        percent = 100.0 if total else 0.0
        record = ProgressRecord(
            status="completed", processed=processed, total=total, percent=percent, message="Completed"
        )
        self.set(task_id, record)

    def mark_error(self, task_id: str, processed: int, total: int, error: str) -> None:
        percent = round((processed / total) * 100, 2) if total else 0.0
        record = ProgressRecord(
            status="error", processed=processed, total=total, percent=percent, message="Error", error=error
        )
        self.set(task_id, record)


progress_store = ProgressStore()
