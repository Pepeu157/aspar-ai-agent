from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.domain.models import (
    AIAnalysis,
    ActorType,
    AuditEvent,
    AuditEventType,
    RequestClassification,
    RequestCreate,
    RequestRecord,
    RequestStatus,
)
from app.repositories.memory import request_repository
from app.services.ai import AIProvider, LocalRulesProvider

router = APIRouter(prefix="/api/v1/requests", tags=["requests"])
provider: AIProvider = LocalRulesProvider()


def _status_for(classification: RequestClassification) -> RequestStatus:
    if classification == RequestClassification.AUDIENCE_REQUEST:
        return RequestStatus.AWAITING_REVIEW
    if classification == RequestClassification.AMBIGUOUS:
        return RequestStatus.NEEDS_MORE_INFO
    return RequestStatus.OUT_OF_SCOPE


@router.post("", response_model=RequestRecord, status_code=status.HTTP_201_CREATED)
def create_request(payload: RequestCreate) -> RequestRecord:
    request_id = uuid4()
    now = datetime.now(timezone.utc)
    classification, extracted_fields, warnings = provider.analyze(payload.message_text)
    analysis = AIAnalysis(
        provider=provider.name,
        provider_version=provider.version,
        classification=classification,
        extracted_fields=extracted_fields,
        warnings=warnings,
        created_at=now,
    )
    history = [
        AuditEvent(
            request_id=request_id,
            event_type=AuditEventType.CREATED,
            actor_type=ActorType.SYSTEM,
            details={"source": "local_api"},
            created_at=now,
        ),
        AuditEvent(
            request_id=request_id,
            event_type=AuditEventType.ANALYZED,
            actor_type=ActorType.AI,
            details={"provider": provider.name, "classification": classification.value},
            created_at=now,
        ),
    ]
    return request_repository.add(
        RequestRecord(
            request_id=request_id,
            message_text=payload.message_text,
            classification=classification,
            status=_status_for(classification),
            analysis=analysis,
            history=history,
            created_at=now,
            updated_at=now,
        )
    )


@router.get("", response_model=list[RequestRecord])
def list_requests() -> list[RequestRecord]:
    return request_repository.list()


@router.get("/{request_id}", response_model=RequestRecord)
def get_request(request_id: str) -> RequestRecord:
    from uuid import UUID

    try:
        parsed_id = UUID(request_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid request ID") from exc
    record = request_repository.get(parsed_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return record
