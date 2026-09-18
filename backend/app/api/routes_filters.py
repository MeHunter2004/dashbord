from fastapi import APIRouter, Depends
from app.api.deps import service
from app.services.request_service import RequestService
router = APIRouter(tags=['filters'])

@router.get('/filters/options')
def filter_options(svc: RequestService = Depends(service)):
    return svc.options()
