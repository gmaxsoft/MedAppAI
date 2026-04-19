from __future__ import annotations

from typing import Any

# Mapuje pole pomiaru -> (klucz normy dla górnej granicy, kierunek odchylenia przy przekroczeniu)
_UPPER_LIMIT_SUFFIX = "_max"
_LOWER_LIMIT_SUFFIX = "_min"


def _param_field_to_norm_keys(field: str) -> tuple[str | None, str | None]:
    """Zwraca (upper_norm_key, lower_norm_key) dla pola pomiaru."""
    upper = f"{field}{_UPPER_LIMIT_SUFFIX}"
    lower = f"{field}{_LOWER_LIMIT_SUFFIX}"
    return upper, lower


def check_norms(
    nerves: list[dict[str, Any]],
    norms_by_nerve: dict[str, Any],
    default_norms: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Porównuje parametry z normami. Flaga odchylenia, gdy:
    - wartość > *_max
    - wartość < *_min
    """
    deviations: list[dict[str, Any]] = []
    default_norms = default_norms or {}

    measure_fields = (
        "latency_ms",
        "amplitude_mv",
        "f_wave_latency_ms",
        "conduction_velocity_m_s",
    )

    for nerve in nerves:
        key = str(nerve.get("nerve_key") or "").strip()
        nerve_norms = norms_by_nerve.get(key) or default_norms
        if not isinstance(nerve_norms, dict):
            nerve_norms = {}

        for field in measure_fields:
            value = nerve.get(field)
            if value is None:
                continue
            try:
                val = float(value)
            except (TypeError, ValueError):
                continue

            upper_key, lower_key = _param_field_to_norm_keys(field)
            upper = nerve_norms.get(upper_key)
            lower = nerve_norms.get(lower_key)

            if upper is not None:
                try:
                    limit = float(upper)
                except (TypeError, ValueError):
                    limit = None
                if limit is not None and val > limit:
                    deviations.append(
                        {
                            "nerve_key": key,
                            "parameter": field,
                            "value": val,
                            "limit": limit,
                            "limit_type": "max",
                            "direction": "above",
                        }
                    )

            if lower is not None:
                try:
                    limit = float(lower)
                except (TypeError, ValueError):
                    limit = None
                if limit is not None and val < limit:
                    deviations.append(
                        {
                            "nerve_key": key,
                            "parameter": field,
                            "value": val,
                            "limit": limit,
                            "limit_type": "min",
                            "direction": "below",
                        }
                    )

    return deviations
