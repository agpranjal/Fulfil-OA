"""Progress tracking utilities placeholder."""

from typing import Dict, Optional


class ProgressStore:
    """In-memory progress store placeholder."""

    def __init__(self):
        self._store: Dict[str, Dict[str, Optional[float]]] = {}

    def set(self, task_id: str, payload: Dict[str, Optional[float]]) -> None:
        self._store[task_id] = payload

    def get(self, task_id: str) -> Optional[Dict[str, Optional[float]]]:
        return self._store.get(task_id)


progress_store = ProgressStore()

