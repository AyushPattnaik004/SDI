from uvicorn import run
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from pydantic import AnyHttpUrl
from starlette.middleware.cors import CORSMiddleware

from api import api_router

# from utils.file_handlers import create_folders_on_startup

app = FastAPI(title="BLS",docs_url=None,redoc_url=None)

# @app.on_event("startup")
# async def startup_event():
#     create_folders_on_startup()

app.mount("/assets", StaticFiles(directory="assets"), name="assets")
BACKEND_CORS_ORIGIN : list[AnyHttpUrl] = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in BACKEND_CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

app.include_router(api_router, prefix='/api')

secure_assets_route = APIRouter(tags=['secure_route'])
app.include_router(secure_assets_route, prefix='/secure_assets')

if __name__ == '__main__':
    run(app=app, host='0.0.0.0', port=11443, ssl_keyfile='server.key', ssl_certfile='server.crt' )
