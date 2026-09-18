from fastapi import APIRouter, Depends
from app.api.deps import service
from app.schemas.common import FilterPayload
from app.services.request_service import RequestService
router = APIRouter(prefix='/dashboard', tags=['dashboard'])

@router.post('/kpis')
def kpis(payload: FilterPayload, svc: RequestService = Depends(service)):
    return svc.kpis(payload)

@router.post('/charts')
def charts(payload: FilterPayload, svc: RequestService = Depends(service)):
    return svc.charts(payload)
