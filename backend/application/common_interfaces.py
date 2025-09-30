from enum import Enum
from abc import abstractmethod  
from typing import Protocol
from uuid import UUID

class DBSession(Protocol):
    @abstractmethod
    async def commit(self) -> None:
        pass
    
class UUIDGenerator(Protocol):
    def __call__(self) -> UUID:
        ...