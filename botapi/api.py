from __future__ import annotations

from botapi.errors import TelegramAPIError
from botapi.methods import Methods

from pydantic import BaseModel
from typing import Optional, Dict, Any, List

import logging
import httpx
import orjson

log = logging.getLogger(__name__)

class BotAPI(Methods):
    def __init__(
        self,
        token: str,
        api_url: str = "https://api.telegram.org",
        parse_mode: Optional[str] = None,
        session: Optional[httpx.AsyncClient] = None,
        sudoers: Optional[List[int]] = None

    ):
        self.token: str = token
        self.api_url: str = api_url
        self.parse_mode: Optional[str] = parse_mode or "HTML"
        self.session: httpx.AsyncClient = session or httpx.AsyncClient(timeout=120)
        self.sudoers: List[int] = sudoers or []

        assert isinstance(self.token, str)
        assert isinstance(self.api_url, str)
        assert isinstance(self.parse_mode, str)
        assert isinstance(self.session, httpx.AsyncClient)
        assert isinstance(self.sudoers, list)

    def _compose_api_url(self, method: str) -> str:
        return f"{self.api_url}/bot{self.token}/{method}"

    def _convert_data(self, data: Dict) -> Dict:
        for key, value in data.items():
            if isinstance(value, BaseModel):
                if hasattr(value, "parse_mode"):
                    setattr(value, "parse_mode", self.parse_mode)
                data[key] = orjson.dumps(
                    value.model_dump(
                        mode="json",
                        exclude_none=True,
                    )
                ).decode("utf-8")
            elif isinstance(value, list):
                data[key] = orjson.dumps([
                    self._convert_data(item)
                    for item in value
                ]).decode("utf-8")
        return data
    
    async def _send_request(self, method: str, data: Dict) -> Any:
        converted_data = self._convert_data(data)
        request = await self.session.post(
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

