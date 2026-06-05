from fastapi import APIRouter
from .v1 import v1_router

api_routerr = APIRouter()

api_routerr.include_router(v1_router,prefix="/v1")