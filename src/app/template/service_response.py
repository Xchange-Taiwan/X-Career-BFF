import json
from typing import Dict, Optional, List, Union
from .client_response import ClientResponse
import httpx


class ServiceApiResponse(ClientResponse):
    code: Optional[str] = None
    msg: Optional[str] = None
    data: Optional[Union[Dict, List, bool, int, str]] = None

    @staticmethod
    def parse(response: httpx.Response = None) -> 'ServiceApiResponse':
        if response:
            parsed_data = response.json()
            code = parsed_data.get('code', '20000')
            msg = parsed_data.get('msg', 'ok')
            raw_data = parsed_data.get('data', {})
            # Ensure `data` is parsed properly
            if isinstance(raw_data, str):
                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError:
                    data = raw_data  # only a string
            else:
                data = raw_data
            return ServiceApiResponse(
                status_code=response.status_code,
                headers=response.headers,
                res_json=parsed_data,
                res_content=response.content,
                res_text=response.text,
                code=code,
                msg=msg,
                data=data
            )

        return None
