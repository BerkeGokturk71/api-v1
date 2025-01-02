from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import HTTPException
from sqlalchemy import and_, extract, func, DateTime, cast, desc
from sqlalchemy.orm import Session, joinedload
from model.model_camasir import Machine, Student, Loan, MachineHour, MachineType, Role
from schemas.camasir import MachineTypeSchema, MachineLoanRequest

scheduler = BackgroundScheduler()

def start_scheduler(db:Session):
    try:
        scheduler.add_job(machine_hours_one_to_zero, CronTrigger(hour=17, minute=46,timezone="Europe/Istanbul"), args=[db])
        scheduler.start()
    except Exception as e:
        print(e)
def machine_hours_one_to_zero(db:Session)->MachineHour:
    db.query(MachineHour).filter(MachineHour.available==0).update({MachineHour.available:1})
    print("veri tabanı güncellendi")
    db.commit()

def get_available_machine_hour_normal(db:Session)->MachineHour:
    available_machine = db.query(MachineHour).join(Machine).filter(and_(MachineHour.available==1,Machine.type == MachineTypeSchema.NORMAL.value)).order_by(MachineHour.start_time).all()
    return available_machine

def get_available_machine_hour_dryer(db:Session)->MachineHour:
    available_machine = db.query(MachineHour).join(Machine).filter(and_(MachineHour.available==1,Machine.type == MachineTypeSchema.DRYER.value)).order_by(MachineHour.start_time).all()
    return available_machine

def get_available_machine_all(db:Session)->None:
    list_machine_hour = (get_available_machine_hour_normal(db)+get_available_machine_hour_dryer(db))
    return list_machine_hour

def get_student(student_id, db: Session) -> Student:
    """Verilen ID'ye göre öğrenci sorgula."""
    student = db.query(Student).filter(Student.username == student_id).first()
    print(student.username)
    print(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    return student

def calculate_next_loan_time() -> datetime.time:
    """Ödünç alım zamanı ve bir sonraki uygun zamanı hesapla."""

    loan_date = (datetime.now()).date()
    loan_time = datetime.now().time()
    next_loan_time_obj = (datetime.now() + timedelta(weeks=1)).date()
    return loan_date,loan_time, next_loan_time_obj

def user_loan(student_id,db:Session)->Loan:
    student_loan = db.query(Loan).filter(Student.username==student_id).order_by(desc(Loan.next_loan_time)).first()
    return student_loan
def create_loan(student_id: int, machine_id: int, loan_time: datetime.time, next_loan_time: datetime.time,loan_date:datetime.time, machine_type, db: Session) -> Loan:
    """Yeni bir ödünç kaydı oluştur."""
    print(machine_type)
    new_loan = Loan(
        student_id=student_id,
        machine_id=machine_id,
        loan_time=loan_time,
        next_loan_time=next_loan_time,
        machine_type=machine_type.value,
        loan_date = loan_date
    )
    db.add(new_loan)
    db.commit()
    return new_loan

def convert_to_datetime(datetime_list, year=2024, month=1, day=1):
    result = []
    for dt in datetime_list:
        result.append(
            datetime(
                year,
                month,
                day,
                dt.get("hour", 0),
                dt.get("minute", 0),
                dt.get("second", 0)
            )
        )
    return result

datetime_list = [
    {"hour": 8, "minute": 0, "second": 0},
    {"hour": 10, "minute": 0, "second": 0},
    {"hour": 13, "minute": 0, "second": 0},
    {"hour": 15, "minute": 0, "second": 0},
    {"hour": 17, "minute": 0, "second": 0},
]
def mark_machine_hour(machine_hour_model, db: Session):
    """
    Makine saatlerini veritabanına kaydeden işlev.
    machine_hour_model: Veritabanı modeli (ör: MachineHour)
    db: SQLAlchemy Session
    """
    # Eğer makine saatleri zaten eklenmişse hata döndür
    if db.query(machine_hour_model).count() > 0:
        raise HTTPException(status_code=400, detail="Machine hours are already initialized.")
    normal_machine_ids = list(range(1, 31))
    # Kurutma makineleri (ID: 31-40)
    dryer_machine_ids = list(range(31, 41))
    # Saat listesi


    # Başlangıç zamanlarını datetime objelerine çevir
    converted_datetimes = convert_to_datetime(datetime_list)

    # Makine saatlerini veritabanına ekle
    for machine_id in normal_machine_ids + dryer_machine_ids:
        for start_time in converted_datetimes:
            end_time = start_time + timedelta(hours=1)  # Örneğin, her saat aralığı 1 saat
            new_machine_hour = machine_hour_model(
                machine_id=machine_id,
                start_time=start_time.time(),
                end_time=end_time.time(),

            )
            db.add(new_machine_hour)

    db.commit()

    return {"message": "Makine saatleri başarıyla işaretlendi."}

def current_time_smaller_than_machine_hour():
    now = datetime.now()
    return now.time()


def get_available_machine(machine_type: MachineTypeSchema, db: Session,request: MachineLoanRequest):
    current_time = current_time_smaller_than_machine_hour()
    # Enum dönüşümü: Pydantic schema'dan SQLAlchemy enum'una
    machine_type_enum = MachineType[machine_type.value]

    # 1. Makine saatlerini filtrele, sadece verilen saatten sonraki uygun makineleri al
    machines = db.query(MachineHour).join(Machine).filter(
        and_(
            Machine.type == machine_type_enum,  # Makine tipi
            MachineHour.available == True,  # Uygun olanlar
            func.time(MachineHour.start_time) > current_time
        )
    ).order_by(func.time(MachineHour.start_time)).all()
    list = []
    list.append(machines)

    if ((request.machine_count == 2) and (request.machine_type == machine_type.DRYER)):
        machine_ids = []
        available_machines = machines[:1]
        for machine_hour in available_machines:
            machine_hour.available = False  # Artık uygun değil
            machine_ids.append(machine_hour.id)  # ID'yi listeye ekle
        print(machine_ids)
        return machine_ids
    elif((request.machine_count == 2) and (request.machine_type == machine_type.NORMAL)):
        machine_ids = []
        available_machines = machines[:request.machine_count]  # İlk 2 makineyi al
        for machine_hour in available_machines:
            machine_hour.available = False  # Artık uygun değil
            machine_ids.append(machine_hour.id)  # ID'yi listeye ekle
        print(machine_ids)
        print(type(machine_ids))
        db.commit()
        return machine_ids
    elif((request.machine_count == 1) and (request.machine_type == MachineTypeSchema.NORMAL)):
        machine_ids = []
        available_machines = machines[:request.machine_count]
        for machine_hour in available_machines:
            machine_hour.available = False  # Artık uygun değil
            machine_ids.append(machine_hour.id)  # ID'yi listeye ekle
        print(machine_ids)
        return machine_ids

    elif((request.machine_count == 1) and (request.machine_type == MachineTypeSchema.DRYER)):
        machine_ids = []
        available_machines = machines[:request.machine_count]
        for machine_hour in available_machines:
             machine_hour.available = False  # Artık uygun değil
             machine_ids.append(machine_hour.id)  # ID'yi listeye ekle
        print(machine_ids)
        return machine_ids
    else:
        if not machines:
            raise HTTPException(
                status_code=404,
                detail=f"Uygun {machine_type.value} makine bulunamadı."
            )


