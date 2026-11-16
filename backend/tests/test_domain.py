import pytest
from pydantic import ValidationError

from app.domain.models import ExtractedFields


def test_invalid_date_time_and_email_are_rejected() -> None:
    with pytest.raises(ValidationError):
        ExtractedFields(suggested_date="2026-02-31")
    with pytest.raises(ValidationError):
        ExtractedFields(suggested_time="25:61")
    with pytest.raises(ValidationError):
        ExtractedFields(sender_email="not-an-email")
