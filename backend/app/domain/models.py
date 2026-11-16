from datetime import date, datetime, time, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RequestClassification(StrEnum):
    AUDIENCE_REQUEST = "audience_request"
    AMBIGUOUS = "ambiguous"
    OUT_OF_SCOPE = "out_of_scope"


class RequestStatus(StrEnum):
    RECEIVED = "received"
    IN_ANALYSIS = "in_analysis"
    AWAITING_REVIEW = "awaiting_review"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    RESPONDED = "responded"
    DISCARDED = "discarded"
    NEEDS_MORE_INFO = "needs_more_info"
    OUT_OF_SCOPE = "out_of_scope"


class ReviewAction(StrEnum):
    EDITED = "edited"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUESTED_MORE_INFO = "requested_more_info"


class ActorType(StrEnum):
    SYSTEM = "system"
    AI = "ai"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class AuditEventType(StrEnum):
    CREATED = "created"
    ANALYZED = "analyzed"
    HUMAN_EDITED = "human_edited"
    HUMAN_APPROVED = "human_approved"
    HUMAN_REJECTED = "human_rejected"
    STATUS_CHANGED = "status_changed"


class ExtractedFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sender_name: str | None = None
    sender_email: EmailStr | None = None
    institution: str | None = None
    subject: str | None = None
    request_summary: str | None = None
    suggested_date: str | None = None
    suggested_time: str | None = None
    participants: list[str] = Field(default_factory=list)
    context: str | None = None
    technical_terms: list[str] = Field(default_factory=list)
    suggested_response: str | None = None

    @field_validator("sender_name", "institution", "subject", "request_summary", "context")
    @classmethod
    def normalize_optional_string(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        return value.strip()

    @field_validator("participants", "technical_terms")
    @classmethod
    def normalize_list(cls, values: list[str]) -> list[str]:
        return [value.strip() for value in values if value.strip()]

    @field_validator("suggested_date")
    @classmethod
    def valid_iso_date(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("suggested_date must be a valid ISO date") from exc
        return value

    @field_validator("suggested_time")
    @classmethod
    def valid_time(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            time.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("suggested_time must be a valid time") from exc
        return value


class AIAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    analysis_id: UUID = Field(default_factory=uuid4)
    provider: str = "local-rules"
    provider_version: str = "rules-v1"
    classification: RequestClassification
    extracted_fields: ExtractedFields = Field(default_factory=ExtractedFields)
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HumanReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_id: UUID = Field(default_factory=uuid4)
    reviewer_id: str
    action: ReviewAction
    comments: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    event_type: AuditEventType
    actor_type: ActorType
    actor_id: str | None = None
    details: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message_text: str = Field(min_length=1, max_length=20_000)

    @field_validator("message_text")
    @classmethod
    def reject_blank_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("message_text must not be blank")
        return normalized


class RequestRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: UUID = Field(default_factory=uuid4)
    message_text: str = Field(min_length=1, max_length=20_000)
    classification: RequestClassification
    status: RequestStatus
    analysis: AIAnalysis
    human_reviews: list[HumanReview] = Field(default_factory=list)
    history: list[AuditEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("message_text")
    @classmethod
    def reject_blank_record_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message_text must not be blank")
        return value.strip()
