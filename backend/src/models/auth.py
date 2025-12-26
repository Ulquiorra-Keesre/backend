from pydantic import BaseModel, field_validator
from typing import Optional

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


@field_validator('password')
def password_length(cls, v):
    if len(v.encode('utf-8')) > 72:
        raise ValueError("Пароль не может быть длиннее 72 байт")
    return v