from pydantic import BaseModel, Field
from typing import List, Optional, Any

class TelegramParameter(BaseModel):
    name: str
    type: Any
    is_required: bool
    literal: Optional[str] = Field(default=None)

class TelegramType(BaseModel):
    name: str
    description: str
    anchor_link: str
    parameters: List[TelegramParameter]
    children: List[str] = Field(default_factory=list)
    is_empty: bool = Field(default=False)

    @property
    def adapter_name(self):
        return f"_{self.name}Adapter"

class TelegramMethod(BaseModel):
    name: str
    description: str
    anchor_link: str
    return_type: Any
    parameters: List[TelegramParameter]