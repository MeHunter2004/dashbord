from fastapi import APIRouter, Depends
from app.api.deps import service
from app.schemas.common import PagePayload
from app.services.request_service import RequestService
router = APIRouter(prefix='/requests', tags=['requests'])

@router.post('/search')
def search_requests(payload: PagePayload, svc: RequestService = Depends(service)):
    return svc.requests(payload)
