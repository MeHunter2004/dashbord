from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_filters import router as filters_router
from app.api.routes_requests import router as requests_router
from app.core.config import settings
from app.repositories.excel_repository import ExcelRequestRepository
from app.services.request_service import RequestService

@asynccontextmanager
async def lifespan(app: FastAPI):
    repository = ExcelRequestRepository(settings.excel_file_path, settings.excel_sheet_name)
    app.state.request_service = RequestService(repository)
    yield

app = FastAPI(title='Request Monitoring Dashboard API', version='0.1.0', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip() for item in settings.cors_origins.split(',')],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(filters_router, prefix='/api')
app.include_router(dashboard_router, prefix='/api')
app.include_router(requests_router, prefix='/api')

@app.get('/health')
def health():
    return {'status': 'ok'}
