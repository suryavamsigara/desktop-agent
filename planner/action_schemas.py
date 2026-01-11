from pydantic import BaseModel
from typing import Optional

class OpenAppParams(BaseModel):
    app_name: str

class TypeParams(BaseModel):
    text: str
    interval: Optional[float] = 0.05

class PressParams(BaseModel):
    key: str

class ClickParams(BaseModel):
    x: Optional[int] = None
    y: Optional[int] = None
    target: Optional[str] = None

class WaitParams(BaseModel):
    seconds: float