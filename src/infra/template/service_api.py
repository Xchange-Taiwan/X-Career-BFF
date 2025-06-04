from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from .service_response import ServiceApiResponse


class IServiceApi(ABC):
    @abstractmethod
    async def simple_get(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[ServiceApiResponse]:
        pass
    
    # NOTE: retrun native response
    @abstractmethod
    async def get_req(self, url: str, params: Dict = None, headers: Dict = None) -> Any:
        pass

    @abstractmethod
    async def simple_post(self, url: str, json: Dict, headers: Dict = None) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def post(self, url: str, json: Dict, headers: Dict = None) -> Optional[ServiceApiResponse]:
        pass
    
    # NOTE: retrun native response
    @abstractmethod
    async def post_req(self, url: str, json: Dict, headers: Dict = None) -> Any:
        pass

    @abstractmethod
    async def simple_put(self, url: str, json: Dict = None, headers: Dict = None) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def put(self, url: str, json: Dict = None, headers: Dict = None) -> Optional[ServiceApiResponse]:
        pass

    @abstractmethod
    async def simple_delete(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[ServiceApiResponse]:
        pass
