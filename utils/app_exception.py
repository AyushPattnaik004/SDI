from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder
from fastapi import Request,Header
from typing import Annotated, Union

class AppException(StarletteHTTPException):
    '''
        `status` = `fastapi.status`
    '''
    def __init__(self,status_code: int,req: Request = None, message: str = None, data: Annotated[dict , list[dict]] = None, headers: dict= None) -> None:
        detail = {
            "status": 0,
            "data": []
        }
        if message or message.strip() == "":
            detail["message"] = message
        if data or data != {} or data != [{}]:
            detail["data"] = data
        
        super().__init__(status_code, jsonable_encoder(detail), headers)
