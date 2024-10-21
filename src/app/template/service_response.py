from typing import Dict, Optional
from .client_response import ClientResponse

class ServiceApiResponse(ClientResponse):
    data: Optional[Dict] = None

    def get_data(self):
        if 'data' in self.res_json:
            return self.res_json['data']
        return None
