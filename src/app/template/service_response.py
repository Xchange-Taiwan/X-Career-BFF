import json
from typing import Dict, Optional
from .client_response import ClientResponse
import httpx


class ServiceApiResponse(ClientResponse):
    data: Optional[Dict] = None

    @staticmethod
    def parse(response: httpx.Response = None) -> 'ServiceApiResponse':
        if response:
            return ServiceApiResponse(
                status_code=response.status_code,
                headers=response.headers,
                res_json=response.json(),
                res_content=response.content,
                res_text=response.text,
                data=json.loads(response.json().get('data', {}))
            )

        return None
