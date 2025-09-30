from fastapi import Request
from application.lead.interfaces import ContextProvider

class ContextProvider(ContextProvider):
    def __init__(self, request: Request):
        self._request = request

    def get_idempotency_key(self) -> str:
        return self._request.headers.get("Idempotency-Key", "")