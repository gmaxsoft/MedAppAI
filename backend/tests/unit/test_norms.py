from app.services.norms import check_norms


def test_check_norms_detects_latency_above_max():
    norms = {"ne1": {"latency_ms_max": 4.0}}
    nerves = [{"nerve_key": "ne1", "latency_ms": 5.5}]
    out = check_norms(nerves, norms)
    assert len(out) == 1
    assert out[0]["parameter"] == "latency_ms"
    assert out[0]["direction"] == "above"
    assert out[0]["value"] == 5.5


def test_check_norms_detects_amplitude_below_min():
    norms = {"ne1": {"amplitude_mv_min": 3.0}}
    nerves = [{"nerve_key": "ne1", "amplitude_mv": 1.2}]
    out = check_norms(nerves, norms)
    assert len(out) == 1
    assert out[0]["direction"] == "below"


def test_check_norms_uses_default_when_nerve_missing():
    norms = {"default": {"latency_ms_max": 10.0}}
    nerves = [{"nerve_key": "unknown", "latency_ms": 12.0}]
    out = check_norms(nerves, norms, default_norms=norms["default"])
    assert len(out) == 1


def test_check_norms_skips_none_values():
    norms = {"n": {"latency_ms_max": 1.0}}
    nerves = [{"nerve_key": "n", "latency_ms": None}]
    assert check_norms(nerves, norms) == []
