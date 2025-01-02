from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from config.create_db_camasir import  auto_create_db
from middleware.log import RateLimitingMiddleware
from controller import user_controller,loan_controller,daily_meal_controller
from schemas.user_login import Settings

auto_create_db()
app = FastAPI()
app.add_middleware(RateLimitingMiddleware)
app.include_router(user_controller.router)
app.include_router(loan_controller.router)
app.include_router(daily_meal_controller.router)

@AuthJWT.load_config
def get_config():
    return Settings()



"""
@app.post("/initialize-machines")
def initialize_machines(db: Session = Depends(get_camasir_session)):
    # Zaten makine varsa yeniden ekleme yapma
    if db.query(Machine).count() > 0:
        raise HTTPException(status_code=400, detail="Machines are already initialized.")

    # Normal makineler
    for i in range(1, 31):
        machine = Machine(type=MachineType.NORMAL, number=i)
        db.add(machine)
    # Kurutmalı makineler
    for i in range(1, 11):
        machine = Machine(type=MachineType.DRYER, number=i)
        db.add(machine)

    db.commit()
    return {"message": "30 Normal ve 10 Kurutmalı makine başarıyla oluşturuldu."}

@app.post("/initialize-machine-hours")
def initialize_machine_hours(db: Session = Depends(get_camasir_session)):
    return mark_machine_hour(MachineHour, db)
    
"""