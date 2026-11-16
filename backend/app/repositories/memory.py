from threading import RLock
from uuid import UUID

from app.domain.models import RequestRecord


class InMemoryRequestRepository:
    """Volatile repository for local development with synthetic messages only."""

    def __init__(self) -> None:
        self._records: dict[UUID, RequestRecord] = {}
        self._lock = RLock()

    def add(self, record: RequestRecord) -> RequestRecord:
        with self._lock:
            self._records[record.request_id] = record
        return record

    def get(self, request_id: UUID) -> RequestRecord | None:
        with self._lock:
            return self._records.get(request_id)

    def list(self) -> list[RequestRecord]:
        with self._lock:
            return sorted(self._records.values(), key=lambda record: record.created_at, reverse=True)


request_repository = InMemoryRequestRepository()
