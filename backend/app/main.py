from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
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
    TrustedHostMiddleware,
    allowed_hosts=[item.strip() for item in settings.allowed_hosts.split(',') if item.strip()],
)
if settings.force_https:
    app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip() for item in settings.cors_origins.split(',')],
    allow_credentials=False,
    allow_methods=['GET', 'POST'],
    allow_headers=['Content-Type'],
)

@app.middleware('http')
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'same-origin'
    return response
app.include_router(filters_router, prefix='/api')
app.include_router(dashboard_router, prefix='/api')
app.include_router(requests_router, prefix='/api')

@app.get('/health')
def health():
    return {'status': 'ok'}
