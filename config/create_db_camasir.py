from typing import Generator
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from model.model_camasir import BaseCamasir


#Create a sqlite engine instance
engineCamasir =create_engine("sqlite:///loan.db",echo=True)

#Create session local class from sessionmaker factory
SessionLocalCamasir = sessionmaker(bind=engineCamasir, expire_on_commit=False)

def create_db()->None:
    BaseCamasir.metadata.create_all(engineCamasir)

def get_db() ->Generator[Session,Any,None]:
    session = SessionLocalCamasir()  # Bir oturum oluştur
    try:
        yield session  # Oturumu döndür
    finally:
        session.close()

def auto_create_db():
    try:
        con = engineCamasir.connect()
        create_db()
        con.close()
    except Exception as e:
        tmp_engine = create_engine("sqlite:///loan.db",echo=True)
        with tmp_engine.begin() as session:
            session.exec_driver_sql(f"CREATE DATABASE `loan`")

            create_db()









