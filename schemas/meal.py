from pydantic import BaseModel
from typing import Optional
from datetime import date
class ToDoCreate(BaseModel):
    date: date
    task:str
    food:str
    soup:str
    rice:str
    salad:str
    water:Optional[str] = "500 ml Su"
    bread:Optional[str] ="Çeyrek Ekmek"
class Task(BaseModel):
    date:date
    id:int
    task : str
    food:str
    soup:str
    rice: str
    salad: str
    water: Optional[str] = "500 ml Su"
    bread: Optional[str] = "Çeyrek Ekmek"

    class Config:
        orm_mode = True


