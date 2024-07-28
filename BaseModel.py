from pydantic import BaseModel
from typing import List, Optional, Dict
from fastapi import UploadFile

class CreateProductRequest(BaseModel):
    word: str
    meaning: str
    note: str
    user_add: str
    subject: str
    image: Optional[List[Dict[str, str]]] = None

class DeleteProductRequest(BaseModel):
    id_product: str

class UpdateProductRequest(BaseModel):
    id_product: str
    id_user_src: str
    word: Optional[str] = None
    list_id_img: Optional[str] = None
    meaning: Optional[str] = None
    note: Optional[str] = None
    user_add: Optional[str] = None
    subject: Optional[str] = None
    image: Optional[List[Dict[str, str]]] = None
    list_id_img: Optional[str] = None
class LoginUserRequest(BaseModel):
    user_name: str
    password: str

class CreateUserRequest(BaseModel):
    id_user_add: str
    user_name: str
    password: str
    role: str
    image: Optional[List[Dict[str, str]]] = None

class UpdateUserRequest(BaseModel):
    id_user_src: str
    id_user_target: str
    user_name: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None
    image: Optional[str] = None

class DeleteUserRequest(BaseModel):
    id_user_src: str
    id_user_target: str