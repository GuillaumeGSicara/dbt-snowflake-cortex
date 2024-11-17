from enum import Enum
from pydantic import BaseModel
from typing import List, Optional


class ContentType(str, Enum):
    SQL = "sql"
    TEXT = "text"
    SUGGESTIONS = "suggestions"


class ContentItem(BaseModel):
    type: ContentType
    text: Optional[str] = None
    sql: Optional[str] = None
    confidence: Optional[float] = None
    suggestions: Optional[List[str]] = None
    statement: Optional[str] = None


class Message(BaseModel):
    content: List[ContentItem]
    role: str


class ResponseModel(BaseModel):
    message: Message
    request_id: str
