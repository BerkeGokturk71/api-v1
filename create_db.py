from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#Create a sqlite engine instance
engine =create_engine("sqlite:///dormapi.db")

#Create declarative instance

Base = declarative_base()

#Create session local class from sessionmaker factory

SessionLocal = sessionmaker(bind=engine,expire_on_commit=False)
