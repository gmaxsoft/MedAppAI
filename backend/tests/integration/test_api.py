from app.models import Patient


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_login_success(client, doctor_and_headers):
    doc, _ = doctor_and_headers
    r = client.post(
        "/auth/login",
        json={"email": doc.email, "password": "haslo-testowe-123"},
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_invalid_password(client, doctor_and_headers):
    doc, _ = doctor_and_headers
    r = client.post(
        "/auth/login",
        json={"email": doc.email, "password": "złe-hasło"},
    )
    assert r.status_code == 401


def test_analyze_emg_returns_deviations_and_draft(monkeypatch, client, doctor_and_headers):
    _, headers = doctor_and_headers
    monkeypatch.setattr(
        "app.routers.analyze.generate_emg_description_sync",
        lambda deviations, technical: "Szkic testowy AI",
    )
    body = {
        "norms": {"default": {"latency_ms_max": 5.0}},
        "nerves": [{"nerve_key": "nerw_testowy", "latency_ms": 7.0}],
        "muscles": {},
    }
    r = client.post("/analyze-emg", json=body, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["ai_description_draft"] == "Szkic testowy AI"
    assert len(data["deviations"]) >= 1
    assert data["deviations"][0]["direction"] == "above"


def test_analyze_emg_requires_auth(client):
    r = client.post(
        "/analyze-emg",
        json={
            "norms": {},
            "nerves": [{"nerve_key": "n", "latency_ms": 1.0}],
            "muscles": {},
        },
    )
    assert r.status_code == 401


def test_save_examination(client, doctor_and_headers, db_session):
    _, headers = doctor_and_headers
    patient = Patient(first_name="Anna", last_name="Test", pesel=None)
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    r = client.post(
        "/examinations/",
        headers=headers,
        json={
            "patient_id": patient.id,
            "raw_emg_data": {"nerves": []},
            "norms_snapshot": {},
            "final_description": "Opis zatwierdzony",
            "status": "approved",
        },
    )
    assert r.status_code == 200
    assert r.json()["patient_id"] == patient.id
