
from pydantic import BaseModel, Field


class MenuItem(BaseModel):
    id: str
    naziv: str
    kategorija: str
    cijena_eur: float
    bez_mesa: bool


class ExtractRequest(BaseModel):
    text: str
    menu: list[MenuItem]


class OrderItem(BaseModel):
    id: str
    quantity: int = Field(gt=0)


class UnavailableItem(BaseModel):
    text: str
    quantity: int = Field(gt=0)


class Order(BaseModel):
    items: list[OrderItem]
    unavailable: list[UnavailableItem]


class MenuAnswer(BaseModel):
    message: str
    suggested_ids: list[str]


class AssistantResponse(BaseModel):
    order: Order | None
    answer: MenuAnswer | None
