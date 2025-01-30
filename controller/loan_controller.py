from fastapi import Depends, HTTPException, APIRouter
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from sqlalchemy.orm import Session
from camasir.camasir_function import get_student, get_available_machine, calculate_next_loan_time, create_loan, \
    user_loan, start_scheduler, scheduler, get_available_machine_all, user_current_loan, user_latest_loan
from config.create_db_camasir import get_db
from model.model_camasir import Student
from schemas.camasir import MachineLoanRequest, MachineTypeSchema
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from schemas.my_current_loan import LoanSchema

router = APIRouter(
    prefix="/loan",
    tags=["Loan"],
)

@router.on_event("startup")
def startup_event():
    db = next(get_db())
    start_scheduler(db)
@router.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@router.get("/my_next_loan")
def my_next_loan(Authorize: AuthJWT = Depends(),db:Session=Depends(get_db)):
    try:
        Authorize.jwt_required()

    except AuthJWTException as e:
        raise HTTPException(status_code=401, detail="Yetkilendirme hatası")
    student_id = Authorize.get_jwt_subject()
    student = get_student(student_id, db)
    user_loan_info = user_loan(student_id=student_id,db=db)
    return {
        "message": "Makine başarıyla ödünç alındı.",
        "student_id": student.id,
        "machine_id":str(user_loan_info.machine_id),
        "loan_date":str(user_loan_info.loan_date) ,
        "next_loan_time": str(user_loan_info.next_loan_time)
    }
@router.get("/my_current_loan", response_model=list[LoanSchema])
def my_current_loan(Authorize:AuthJWT=Depends(),db:Session=Depends(get_db)):
    try:
        Authorize.jwt_required()

    except AuthJWTException as e:
        raise HTTPException(status_code=401, detail="Yetkilendirme hatası")
    student_id = Authorize.get_jwt_subject()
    student = user_current_loan(student_id, db)
    return jsonable_encoder(student)
@router.get("/my_latest_loan", response_model=list[LoanSchema])
def my_current_loan(Authorize:AuthJWT=Depends(),db:Session=Depends(get_db)):
    try:
        Authorize.jwt_required()

    except AuthJWTException as e:
        raise HTTPException(status_code=401, detail="Yetkilendirme hatası")
    student_id = Authorize.get_jwt_subject()
    student = user_latest_loan(student_id, db)
    return jsonable_encoder(student)

@router.get("/get_available_machine_hour")
def available_machine(db:Session=Depends((get_db))):
    get_available_machine_all(db)
    return JSONResponse(content=jsonable_encoder(get_available_machine_all(db)))

@router.post("/loan-machine")
def loan_machine(request: MachineLoanRequest, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    try:
        Authorize.jwt_required()

    except AuthJWTException as e:
        raise HTTPException(status_code=401, detail="Yetkilendirme hatası")
    #Bu alanda kontrol etmek lazım veriyi ancak ilk veriyi loan-checkera yönlendirip dogruysa buraya yönlendirmemiz lazım
    """camasirController(request=request)"""

        # Öğrenciyi getir
    student_id = Authorize.get_jwt_subject()
    student = get_student(student_id, db)
    current_date =calculate_next_loan_time()[0]
    print("curent_date",current_date)
    # Eğer makine sayısı birden fazla ise
    if ((request.machine_count == 2 and(current_date >= user_loan(student_id=student_id,db=db).next_loan_time))):
        # Birden fazla makine ödünç alınıyor
        return loan_multiple_machines(student, request, db)
    elif ((request.machine_count == 1) and(current_date >= user_loan(student_id=student_id,db=db).next_loan_time)):
        return loan_single_machine(student, request, db)
    else:
        raise HTTPException(status_code=400,detail="2 den fazla makine veya Alım tarihi dışındasınız")


def loan_single_machine(student: Student, request: MachineLoanRequest, db: Session):
    """
    Tek bir makine ödünç alındığında yapılacak işlemler
    """
    if request.machine_type == MachineTypeSchema.NORMAL:
        available_machines = get_available_machine(request.machine_type, db,request)  # Uygun makineyi getir
        print("buraya",available_machines)
        loan_date,loan_time, next_loan_time = calculate_next_loan_time()  # Ödünç alma süresi hesapla
        create_loan(student_id=student.id, machine_id=available_machines[0], loan_time=loan_time,loan_date=loan_date, next_loan_time=next_loan_time, machine_type=request.machine_type, db=db)  # Loan kaydını oluştur
        return {
            "message": "Makine başarıyla ödünç alındı.",
            "student_id": student.username,
            "machine_id": available_machines[0],
            "next_loan_time": str(next_loan_time)
        }
    else:
        available_machines = get_available_machine(request.machine_type, db, request)  # Uygun makineyi getir


        request.machine_type = MachineTypeSchema.DRYER
        print(available_machines)
        for machine_id in available_machines:
            print("burası", machine_id)
            # Uygun makineyi getir
            # Ödünç alma süresi hesapla
            loan_date, loan_time, next_loan_time = calculate_next_loan_time()
            # Loan kaydını oluştur
            create_loan(student_id=student.id, machine_id=machine_id, loan_time=loan_time,loan_date=loan_date,
                        next_loan_time=next_loan_time,
                        machine_type=request.machine_type, db=db)
            # Her bir ödünç alınan makine için sonuçları listeye ekle
            loan_results={
                "message": "Makine başarıyla ödünç alındı.",
                "student_id": student.username,
                "machine_id": machine_id,
                "next_loan_time": str(next_loan_time)
            }

        return {"loan_results": loan_results}

def loan_multiple_machines(student: Student, request: MachineLoanRequest, db: Session):
    """
    Birden fazla makine ödünç alındığında yapılacak işlemler
    """
    print(request.machine_type)

    if request.machine_type == MachineTypeSchema.NORMAL:
        print("ilki bura")
        loan_results = []

        # Uygun makineleri al
        available_machines = get_available_machine(request.machine_type, db, request)

        # Eğer makineler mevcutsa
        if  available_machines == None:
            raise HTTPException(
                status_code=404,
                detail="Uygun makineler bulunamadı."
            )
        # Her bir makineyi ödünç al
        for machine_id in available_machines:
            # Ödünç alma süresi hesapla
            loan_date,loan_time, next_loan_time = calculate_next_loan_time()

            # Loan kaydını oluştur
            create_loan(student_id=student.id, machine_id=machine_id, loan_time=loan_time,
                        next_loan_time=next_loan_time, machine_type=request.machine_type,loan_date=loan_date, db=db)

            # Her bir ödünç alınan makine için sonuçları listeye ekle
            loan_results.append({
                "message": "Makine başarıyla ödünç alındı.",
                "student_id": student.username,
                "machine_id": machine_id,
                "next_loan_time": str(next_loan_time),
            })

        return {"loan_results": loan_results}

    else:
        loan_results = []
        available_machines = get_available_machine(request.machine_type,db,request)

        #mark_machine_unavailable(machine, db)  # Makineyi uygun değil olarak işaretle
        request.machine_type = MachineTypeSchema.DRYER

        print(available_machines)
        for machine_id in available_machines:
            print("burası",machine_id)
            loan_date, loan_time, next_loan_time = calculate_next_loan_time()
            # Loan kaydını oluştur
            create_loan(student_id=student.id, machine_id=machine_id, loan_time=loan_time,loan_date=loan_date,
                        next_loan_time=next_loan_time,
                        machine_type=request.machine_type, db=db)
            # Her bir ödünç alınan makine için sonuçları listeye ekle
            loan_results.append({
                "message": "Makine başarıyla ödünç alındı.",
                "student_id": student.username,
                "machine_id": machine_id,
                "next_loan_time": str(next_loan_time)
            })

        return {"loan_results": loan_results}