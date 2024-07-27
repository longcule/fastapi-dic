from pydantic import BaseModel
from typing import List, Optional, Dict
from fastapi import UploadFile

class ProductCreateRequest(BaseModel):
    word: str
    meaning: str
    note: str
    user_add: str
    subject: str
    image: Optional[List[Dict[str, str]]] = None

class UserLoginRequest(BaseModel):
    user_name: str
    password: str