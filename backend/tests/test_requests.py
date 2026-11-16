from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create(text: str):
    return client.post("/api/v1/requests", json={"message_text": text})


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_missing_fields_are_not_invented() -> None:
    body = create("Solicito audiência para tratar de energia.").json()
    fields = body["analysis"]["extracted_fields"]
    assert body["classification"] == "audience_request"
    assert fields["sender_name"] is None
    assert fields["sender_email"] is None
    assert fields["institution"] is None
    assert fields["suggested_date"] is None
    assert fields["suggested_time"] is None
    assert fields["participants"] == []
    assert fields["suggested_response"] is None


def test_only_explicitly_labeled_date_and_time_are_associated() -> None:
    text = "Solicito audiência para discutir energia.\nData sugerida: 2026-12-10\nHorário proposto: 14:30"
    fields = create(text).json()["analysis"]["extracted_fields"]
    assert fields["suggested_date"] == "2026-12-10"
    assert fields["suggested_time"] == "14:30"


def test_incidental_historical_date_and_time_are_not_extracted() -> None:
    text = "Solicito audiência para discutir energia. Um evento ocorreu em 2022-01-03 às 12:00."
    fields = create(text).json()["analysis"]["extracted_fields"]
    assert fields["suggested_date"] is None
    assert fields["suggested_time"] is None


def test_mention_alone_is_ambiguous_not_a_request() -> None:
    body = create("A audiência será sobre energia elétrica.").json()
    assert body["classification"] == "ambiguous"
    assert body["status"] == "needs_more_info"


def test_historical_and_negative_mention_is_not_positive_request() -> None:
    historical = create("A audiência de ontem foi realizada às 10:00.").json()
    negative = create("Não solicito audiência neste momento.").json()
    assert historical["classification"] == "ambiguous"
    assert negative["classification"] == "ambiguous"
    assert historical["analysis"]["extracted_fields"]["suggested_time"] is None


def test_unrelated_request_is_out_of_scope_and_has_no_draft() -> None:
    body = create("Apresento uma reclamação sobre atendimento.").json()
    assert body["classification"] == "out_of_scope"
    assert body["status"] == "out_of_scope"
    assert body["analysis"]["extracted_fields"]["suggested_response"] is None


def test_solicitation_about_an_existing_audience_is_not_a_meeting_request() -> None:
    body = create("Solicito informações sobre a audiência realizada no mês passado.").json()
    assert body["classification"] == "ambiguous"


def test_explicit_labeled_fields_are_extracted() -> None:
    text = (
        "De: Ana Exemplo <ana@example.com>\n"
        "Instituição: Entidade Fictícia\n"
        "Participantes: Ana Exemplo, Bruno Exemplo\n"
        "Solicito audiência para tratar de energia."
    )
    body = create(text).json()
    fields = body["analysis"]["extracted_fields"]
    assert body["classification"] == "audience_request"
    assert fields["sender_name"] == "Ana Exemplo"
    assert fields["sender_email"] == "ana@example.com"
    assert fields["institution"] == "Entidade Fictícia"
    assert fields["participants"] == ["Ana Exemplo", "Bruno Exemplo"]


def test_list_get_and_not_found() -> None:
    created = create("Solicito audiência.").json()
    request_id = created["request_id"]
    assert any(item["request_id"] == request_id for item in client.get("/api/v1/requests").json())
    assert client.get(f"/api/v1/requests/{request_id}").status_code == 200
    assert client.get("/api/v1/requests/00000000-0000-0000-0000-000000000000").status_code == 404
    assert client.get("/api/v1/requests/not-a-uuid").status_code == 400


def test_blank_or_oversized_input_is_rejected() -> None:
    assert client.post("/api/v1/requests", json={"message_text": "   "}).status_code == 422
    assert client.post("/api/v1/requests", json={"message_text": "x" * 20_001}).status_code == 422
