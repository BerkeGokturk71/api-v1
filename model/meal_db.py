from sqlalchemy import Column,String,Integer,Date
from create_db import Base


# Define Todo class from Base

class ToDo(Base):
    __tablename__ = 'todos'
    id = Column(Integer,primary_key=True)
    date =Column(Date,index=True)
    task = Column(String(256))
    food = Column(String(200))
    soup = Column(String(200))
    rice = Column(String(200))
    salad = Column(String(200))
    water = Column(String(200))
    bread = Column(String(200))