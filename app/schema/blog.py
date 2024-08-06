from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Blog(BaseModel):
    title: str
    content: str
    author_id: str = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    updated_at: Optional[datetime] = None
