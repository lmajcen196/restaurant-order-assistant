
from fastapi import APIRouter

from app.schemas.order import ExtractRequest, AssistantResponse
from app.services.gemini import extract_order

router = APIRouter(tags=["orders"])


@router.post("/order", response_model=AssistantResponse)
async def extract(request: ExtractRequest) -> AssistantResponse:
    return await extract_order(request.text, request.menu)
