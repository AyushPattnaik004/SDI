import uvicorn
from pydantic import AnyHttpUrl
from typing import List

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from webhook_server.api import api_router


app = FastAPI()




BACKEND_CORS_ORIGIN: List[AnyHttpUrl] = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in BACKEND_CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)




if __name__ == "__main__":
    uvicorn.run(app="__main__:app", host='0.0.0.0', port=8000,reload=True)
