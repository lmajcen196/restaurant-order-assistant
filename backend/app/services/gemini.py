import json
from urllib.parse import quote

import httpx
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.config import settings
from app.core.prompts import ORDER_PROMPT
from app.schemas.order import MenuItem, AssistantResponse


async def extract_order(text: str, menu: list[MenuItem]) -> AssistantResponse:
    if not settings.gemini_api_key:
        raise HTTPException(503, "Gemini ključ nije postavljen. Dodajte GEMINI_API_KEY u backend/.env.")
    menu_data = [item.model_dump() for item in menu]
    user_message = (
        f"JELOVNIK:\n"
        f"{json.dumps(menu_data, ensure_ascii=False)}"
        f"TRANSKRIPT:\n{text}"
    )

    payload = {
        "systemInstruction": {"parts": [{"text": ORDER_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
            "responseJsonSchema": AssistantResponse.model_json_schema(),
        },
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{quote(settings.gemini_model, safe='')}:generateContent",
                headers={"x-goog-api-key": settings.gemini_api_key}, json=payload,
            )
        response.raise_for_status()
        candidates = response.json().get("candidates", [])
        parts = candidates[0]["content"]["parts"] if candidates else []
        output = "".join(part.get("text", "") for part in parts if not part.get("thought"))
        
        
        
        
        result = AssistantResponse.model_validate_json(output)

        valid_ids = {item.id for item in menu}

        # Provjera narudžbe
        if result.order is not None:
            for item in result.order.items:
                if item.id not in valid_ids:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Nepostojeći proizvod: {item.id}"
                    )

        # Provjera preporuka
        if result.answer is not None:
            result.answer.suggested_ids = [
                item_id
                for item_id in result.answer.suggested_ids
                if item_id in valid_ids
            ]

        # Ako nema ni narudžbe ni odgovora
        if result.order is None and result.answer is None:
            raise HTTPException(
                status_code=422,
                detail="Nisu pronađeni narudžba ni pitanje."
            )

        return result


    except httpx.TimeoutException as exc:
        raise HTTPException(504, "Gemini nije odgovorio na vrijeme. Pokušajte ponovno.") from exc
    
    except httpx.HTTPStatusError as exc:
        print("GEMINI STATUS:", exc.response.status_code)
        print("GEMINI ERROR:", exc.response.text)

        raise HTTPException(
            status_code=502,
            detail="Gemini API poziv nije uspio. Provjerite backend terminal."
        ) from exc

    except (httpx.RequestError, ValidationError, ValueError, KeyError, IndexError, TypeError) as exc:
        raise HTTPException(502, "Nije dobiven valjan rezultat od Geminija. Pokušajte ponovno.") from exc
