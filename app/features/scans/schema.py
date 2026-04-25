from typing import List
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class app_type(str, Enum):
    Desktop = "Desktop"
    Mobile = "Mobile"

class ScanCreate(BaseModel):
    filename: str
    file_hash: str
    file_size: int
    app_platform: app_type

class ScanResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    status: str
    prediction: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ScanHistoryResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ScanResponse]
