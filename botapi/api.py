from __future__ import annotations

from botapi.errors import TelegramAPIError
from botapi.methods import Methods

from pydantic import BaseModel, Field
from typing import Dict, Any

import logging
import httpx
import orjson

log = logging.getLogger(__name__)

session = httpx.AsyncClient(timeout=120)

class BotAPI(
    BaseModel,
    Methods,
):
    class Config:
        arbitrary_types_allowed = True

    token: str
    api_url: str = "https://api.telegram.org"
    parse_mode: str = Field(default="HTML")
    
    session: httpx.AsyncClient = None

    def _compose_api_url(self, method: str) -> str:
        return f"{self.api_url}/bot{self.token}/{method}"

    @staticmethod
    def _convert_data(data: Dict) -> Dict:
        for key, value in data.items():
            if isinstance(value, BaseModel):
                data[key] = orjson.dumps(
                    value.model_dump(
                        mode="json",
                        exclude_none=True,
                    )
                ).decode("utf-8")
            elif isinstance(value, list):
                data[key] = orjson.dumps([
                    item.model_dump(
                        mode="json",
                        exclude_none=True,
                    )
                    if isinstance(item, BaseModel) else item
                    for item in value
                ]).decode("utf-8")
        return data
    
    async def _send_request(self, method: str, data: Dict) -> Any:
        converted_data = BotAPI._convert_data(data)
        request = await session.post(
            url=self._compose_api_url(method),
            data=converted_data,
        )
        response_content = request.json()
        if not response_content["ok"]:
            value = None
            if "parameters" in response_content:
                value = list(response_content["parameters"].values())[0]
            raise TelegramAPIError(
                message=response_content["description"],
                code=response_content["error_code"],
                value=value,
            )
        return response_content["result"]

