from passlib.context import CryptContext
from fastapi import Request
from typing import Generator
from .db import  ESIC_DB

password_context=CryptContext(schemes=['bcrypt'],deprecated="auto")

def get_db(req: Request) -> Generator:
    try: 
        
        db = ESIC_DB()
        
        yield db
    
    finally:

        db.close()



__all__ = [
    password_context,
    get_db
]
