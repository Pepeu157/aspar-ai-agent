from __future__ import annotations

import re
from typing import Protocol

from app.domain.models import ExtractedFields, RequestClassification


class AIProvider(Protocol):
    """Provider-neutral contract for a future model or local analyzer."""

    name: str
    version: str

    def analyze(self, text: str) -> tuple[RequestClassification, ExtractedFields, list[str]]:
        """Analyze untrusted message text without adding unsupported facts."""
        ...


class LocalRulesProvider:
    """Conservative deterministic rules; this is not a real AI model."""

    name = "local-rules"
    version = "rules-v1"

    _audience = re.compile(r"\b(audi[eê]ncia|reuni[aã]o)\b", re.IGNORECASE)
    _positive_request_patterns = (
        re.compile(
            r"\b(?:solicito|solicitamos|requeiro|requeremos|pe[cç]o|pedimos|"
            r"gostaria de solicitar|gostar[ií]amos de solicitar|venho solicitar|vimos solicitar)"
            r"\b.{0,80}\b(?:audi[eê]ncia|reuni[aã]o)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:agendar|marcar|solicitar|requerer)\b.{0,50}\b(?:audi[eê]ncia|reuni[aã]o)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:audi[eê]ncia|reuni[aã]o)\b.{0,50}\b(?:solicitada|solicito|solicitamos|agendar|marcar|requeremos)\b",
            re.IGNORECASE,
        ),
    )
    _negative = re.compile(
        r"(?:\b n[aã]o\s+(?:(?:gostaria|gostar[ií]amos)\s+de\s+solicitar|"
        r"solicito|solicitamos|solicita|pretendo|pretendemos|quero|queremos|desejo|desejamos)\b"
        r"|\b(?:audi[eê]ncia|reuni[aã]o)\s+(?:de ontem|ocorreu|ocorrida|realizada|foi realizada|j[aá] realizada)\b)",
        re.IGNORECASE,
    )
    _informational_request = re.compile(
        r"\b(?:solicito|solicitamos|pe[cç]o|pedimos|requeiro|requeremos)\b"
        r".{0,80}\b(?:informa[cç][oõ]es?|esclarecimentos?|detalhes|c[oó]pia|dados)\b"
        r".{0,100}\b(?:audi[eê]ncia|reuni[aã]o)\b",
        re.IGNORECASE,
    )
    _non_scope = re.compile(
        r"\b(den[uú]ncia|reclama[cç][aã]o|recurso|pedido de informa[cç][aã]o)\b",
        re.IGNORECASE,
    )
    _technical_terms = (
        "energia elétrica", "geração", "transmissão", "distribuição", "política energética",
        "minerais críticos", "terras raras", "petróleo", "gás natural", "hidrogênio",
        "transição energética", "infraestrutura energética", "sistemas trifásicos",
    )

    @staticmethod
    def _label(text: str, *labels: str) -> str | None:
        names = "|".join(re.escape(label) for label in labels)
        match = re.search(rf"(?im)^\s*(?:{names})\s*:\s*(.*?)\s*$", text)
        value = match.group(1).strip() if match else ""
        return value or None

    @classmethod
    def _date(cls, text: str) -> str | None:
        # Only a dedicated suggestion/proposal label associates a date with the requested meeting.
        value = cls._label(text, "Data sugerida", "Data pretendida", "Data proposta")
        if not value:
            return None
        match = re.fullmatch(r"\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})\s*", value)
        if not match:
            return None
        from datetime import date

        raw = match.group(1)
        try:
            parsed = date.fromisoformat(raw) if "-" in raw else date.fromisoformat(
                f"{raw[6:10]}-{raw[3:5]}-{raw[0:2]}"
            )
        except ValueError:
            return None
        return parsed.isoformat()

    @classmethod
    def _time(cls, text: str) -> str | None:
        value = cls._label(text, "Horário sugerido", "Horário pretendido", "Horário proposto")
        if not value:
            return None
        match = re.fullmatch(r"\s*([01]?\d|2[0-3]):([0-5]\d)\s*", value)
        if not match:
            return None
        return f"{int(match.group(1)):02d}:{match.group(2)}"

    @classmethod
    def _sender(cls, text: str) -> tuple[str | None, str | None]:
        value = cls._label(text, "De", "Remetente")
        if not value:
            return None, None
        match = re.fullmatch(r"\s*(.*?)\s*<([^<>\s]+@[^<>\s]+)>\s*", value)
        if match:
            return match.group(1).strip() or None, match.group(2)
        if re.fullmatch(r"[^\s<>]+@[^\s<>]+", value):
            return None, value
        return value, None

    def analyze(self, text: str) -> tuple[RequestClassification, ExtractedFields, list[str]]:
        sender_name, sender_email = self._sender(text)
        participant_value = self._label(text, "Participantes")
        participants = (
            [item.strip() for item in re.split(r"[,;]", participant_value) if item.strip()]
            if participant_value else []
        )
        sentences = [part.strip() for part in re.split(r"[.!?\n]+", text) if part.strip()]
        positive_intent = any(
            any(pattern.search(sentence) for pattern in self._positive_request_patterns)
            and not self._negative.search(sentence)
            and not self._informational_request.search(sentence)
            for sentence in sentences
        )
        mentioned = bool(self._audience.search(text))

        if positive_intent:
            classification = RequestClassification.AUDIENCE_REQUEST
            warnings = ["Classificação por regras locais; revisão humana obrigatória."]
        elif mentioned:
            classification = RequestClassification.AMBIGUOUS
            warnings = ["A menção a audiência/reunião não confirma, por si só, uma solicitação."]
        elif self._non_scope.search(text):
            classification = RequestClassification.OUT_OF_SCOPE
            warnings = ["Conteúdo aparentemente fora do escopo de audiências."]
        else:
            classification = RequestClassification.OUT_OF_SCOPE
            warnings = ["Não foi identificada intenção explícita de solicitar audiência."]

        # Do not associate proposed dates/times unless the request itself is explicit.
        fields = ExtractedFields(
            sender_name=sender_name,
            sender_email=sender_email,
            institution=self._label(text, "Instituição"),
            subject=self._label(text, "Assunto"),
            request_summary=self._label(text, "Solicitação"),
            suggested_date=self._date(text) if positive_intent else None,
            suggested_time=self._time(text) if positive_intent else None,
            participants=participants,
            context=self._label(text, "Contexto"),
            technical_terms=[term for term in self._technical_terms if re.search(re.escape(term), text, re.IGNORECASE)],
            suggested_response=None,
        )
        return classification, fields, warnings
