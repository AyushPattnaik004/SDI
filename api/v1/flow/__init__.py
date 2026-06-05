from fastapi import APIRouter
from .trainee import trainee_router

flow_router = APIRouter()
flow_router.include_router(trainee_router,prefix="/trainee")