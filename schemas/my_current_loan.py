from pydantic import BaseModel
from datetime import date, time

class LoanSchema(BaseModel):
    loan_time: time
    next_loan_time: date
    machine_id: int
    loan_date: date
    machine_type: str

    class Config:
        from_attributes = True  # SQLAlchemy modelini otomatik olarak JSON'a çevirir
