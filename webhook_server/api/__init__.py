from fastapi import APIRouter

from .aisensy_webhook import webhook_router
api_router = APIRouter()

api_router.include_router(webhook_router,prefix='/webhook')

@api_router.get("/health-check")
def health_check():
    return "sucess"

