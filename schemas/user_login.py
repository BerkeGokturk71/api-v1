from pydantic import BaseModel
from datetime import date
from typing import Optional


class SignUpSchema(BaseModel):
    date:date
    username:str
    password:str
class LoginSchema(BaseModel):
    username:str
    password:str
    class Config:
        orm_mode:True

class Settings(BaseModel):
    authjwt_secret_key :str='ffcd8e1c0463235b4d0f98e85c2f49fb702bd2cc7482561976dcfa9a612aba0f'