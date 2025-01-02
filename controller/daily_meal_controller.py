from typing import List
from fastapi import Depends, APIRouter,status
from sqlalchemy.orm import Session
from schemas import meal
from create_db import SessionLocal
from model.meal_db import ToDo

router = APIRouter(
    prefix="/meal",
    tags=["Meal"],
)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
@router.get("/tasks/{date}/{meal_type}", response_model=List[meal.Task])
def read_task(date: str, meal_type: str ,session:Session=Depends(get_session)):
    todo_list = session.query(ToDo).filter(ToDo.date == date,ToDo.task == meal_type).all()
    return todo_list

@router.post("/tasks/", response_model=meal.Task, status_code=status.HTTP_201_CREATED)
def create_task(task: meal.ToDoCreate, session:Session = Depends(get_session)):
    tododb = ToDo(**task.dict())

    session.add(tododb)
    session.commit()
    session.refresh(tododb)

    return tododb
