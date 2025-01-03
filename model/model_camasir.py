from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Time, Boolean, Date
import enum
from sqlalchemy.orm import relationship, declarative_base

BaseCamasir = declarative_base()
class MachineType(enum.Enum):
    NORMAL = "Normal"
    DRYER = "Dryer"


class Role(BaseCamasir):
    __tablename__ = "roles"
    id = Column(Integer,primary_key=True)
    name = Column(String,unique=True)
    students = relationship("Student",back_populates="role")

class Student(BaseCamasir):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    role_id = Column(String,ForeignKey("roles.id"))
    username = Column(String, nullable=False)
    password = Column(String(20), nullable=False)
    verified = Column(Boolean,default=False)
    date = Column(Date, index=True)
    role = relationship("Role",back_populates="students")
    loans = relationship("Loan", back_populates="student")

class Machine(BaseCamasir):
    __tablename__ = "machine"
    id = Column(Integer, primary_key=True)
    type = Column(Enum(MachineType), nullable=False)
    number = Column(Integer, nullable=False)  # Makine numarası
    hours = relationship("MachineHour", back_populates="machine")
    loans = relationship("Loan", back_populates="machine")

class Loan(BaseCamasir):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    machine_id = Column(Integer, ForeignKey("machine.id"), nullable=False)
    loan_time = Column(Time, nullable=False)  # Ödünç alma saati
    loan_date = Column(Date,nullable=True)
    next_loan_time = Column(Date,nullable=True) # Bir sonraki çamaşır atım tarihi
    machine_type = Column(Enum(MachineType), nullable=False)  # Makine türü

    student = relationship("Student", back_populates="loans")
    machine = relationship("Machine", back_populates="loans")

class MachineHour(BaseCamasir):
    __tablename__ = "machine_hours"
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machine.id"), nullable=False)
    start_time = Column(Time, nullable=False)  # Başlangıç saati
    available = Column(Boolean, default=True)
    end_time = Column(Time, nullable=False)  # Bitiş saati

    machine = relationship("Machine", back_populates="hours")

