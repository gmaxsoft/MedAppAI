from app.services.anonymization import anonymize_for_llm


def test_anonymize_removes_sensitive_keys():
    payload = {
        "first_name": "Jan",
        "nerves": [{"nerve_key": "n1", "latency_ms": 3.0}],
        "patient_id": 99,
    }
    out = anonymize_for_llm(payload)
    assert "first_name" not in out
    assert "patient_id" not in out
    assert out["nerves"][0]["latency_ms"] == 3.0


def test_anonymize_scrubs_pesel_in_strings():
    payload = {"note": "PESEL 44051401359 w tekście"}
    out = anonymize_for_llm(payload)
    assert "44051401359" not in str(out)
    assert "[USUNIĘTO_PESEL]" in out["note"]
