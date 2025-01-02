from pydantic import BaseModel
from enum import Enum


class MachineTypeSchema(Enum):
    NORMAL = "NORMAL"
    DRYER = "DRYER"
class StudentSign(BaseModel):
    username:str
    password:str
class StudentLogin(BaseModel):
    username:str
    password:str


class MachineLoanRequest(BaseModel):
    user_token: str
    machine_type: MachineTypeSchema
    machine_count:int
    loan_time : str

