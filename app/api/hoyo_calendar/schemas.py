from pydantic import BaseModel


class GameInfo(BaseModel):
    name: str


class GameListResponse(BaseModel):
    total: int
    items: list[GameInfo]


class EventTypeInfo(BaseModel):
    name: str


class EventTypeListResponse(BaseModel):
    total: int
    items: list[EventTypeInfo]


class EventListResponse(BaseModel):
    total: int
    items: list[dict]
    offset: int
    limit: int
