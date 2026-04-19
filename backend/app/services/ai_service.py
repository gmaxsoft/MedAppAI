from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.core.config import get_settings


def generate_emg_description_sync(deviations: list[dict[str, Any]], technical_payload: dict[str, Any]) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        return (
            "[Brak OPENAI_API_KEY] Szkic opisu nie został wygenerowany. "
            "Skonfiguruj klucz API, aby włączyć model GPT-4o.\n\n"
            f"Odchylenia od norm: {json.dumps(deviations, ensure_ascii=False)}\n"
            f"Dane techniczne (anonimowe): {json.dumps(technical_payload, ensure_ascii=False)}"
        )

    client = OpenAI(api_key=settings.openai_api_key)
    odchylenia_txt = json.dumps(deviations, ensure_ascii=False)
    dane_txt = json.dumps(technical_payload, ensure_ascii=False)

    prompt = (
        "Jesteś asystentem neurologa. Na podstawie poniższych wyników badań EMG "
        f"(z uwzględnieniem przekroczeń norm: {odchylenia_txt}) przygotuj profesjonalny, "
        "medyczny szkic opisu badania w języku polskim.\n\n"
        f"Dane techniczne (anonimizowane): {dane_txt}"
    )

    completion = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Jesteś asystentem klinicznym wspierającym neurologa. "
                    "Generujesz wyłącznie szkic tekstu opisu badania EMG/ENG w języku polskim. "
                    "Nie diagnozuj ostatecznie — używaj ostrożnego, profesjonalnego języka medycznego."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    choice = completion.choices[0].message.content
    return (choice or "").strip()
