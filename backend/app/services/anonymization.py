from __future__ import annotations

import copy
import re
from typing import Any

_SENSITIVE_KEYS = frozenset(
    {
        "first_name",
        "last_name",
        "imie",
        "nazwisko",
        "pesel",
        "patient_name",
        "fullname",
        "full_name",
        "phone",
        "telefon",
        "email",
        "address",
        "adres",
        "nip",
        "patient_id",
    }
)

_PESEL_RE = re.compile(r"\b\d{11}\b")


def _scrub_string(s: str) -> str:
    out = _PESEL_RE.sub("[USUNIĘTO_PESEL]", s)
    return out


def anonymize_for_llm(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Usuwa dane identyfikujące przed wysłaniem do zewnętrznego API (RODO).
    Zostają wyłącznie dane techniczne badania.
    """
    data = copy.deepcopy(payload)

    def walk(obj: Any) -> Any:
        if isinstance(obj, dict):
            cleaned: dict[str, Any] = {}
            for k, v in obj.items():
                lk = str(k).lower()
                if lk in _SENSITIVE_KEYS:
                    continue
                cleaned[k] = walk(v)
            return cleaned
        if isinstance(obj, list):
            return [walk(x) for x in obj]
        if isinstance(obj, str):
            return _scrub_string(obj)
        return obj

    return walk(data)
