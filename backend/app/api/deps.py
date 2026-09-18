from fastapi import Request
from app.services.request_service import RequestService

def service(request: Request) -> RequestService:
    return request.app.state.request_service
