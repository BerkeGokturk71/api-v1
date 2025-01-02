from datetime import timedelta
from fastapi import HTTPException, Depends, APIRouter,status
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from schemas.camasir import StudentSign, StudentLogin
from sqlalchemy.orm import Session
from db_functions import get_password_hash, verify_password
from model.model_camasir import Student
from config.create_db_camasir import get_db
router = APIRouter(
    prefix="/user",
    tags=["Users"],
)
@router.post("/sign", status_code=status.HTTP_201_CREATED)
async def sign(sign:StudentSign, session:Session = Depends(get_db)):
    if (user_controller(sign.username,sign.password)== True):
        db_user = session.query(Student).filter(Student.username == sign.username).first()
        if db_user is not None:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="user name already exists",headers="Not")

        new_user = Student(
            username=sign.username,
            password=get_password_hash(sign.password),
        )
        session.add(new_user)
        session.commit()
        return {"message": "Login successful"}
    return HTTPException(status_code=405, detail="Kullanıcı Adı Veya Şifresi 3 Karakterden Az Olamaz",headers="Not")

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user:StudentLogin,session:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    if (user_controller(user.username,user.password) == True):
        db_user = session.query(Student).filter(Student.username == user.username).first()
        if db_user and verify_password(db_user.password,user.password):
            access_token = Authorize.create_access_token(subject=db_user.username, expires_time=timedelta(days=365*100))
            response = {
                "status_code":200,
                "user_token": access_token,
                "username":user.username
            }
            return jsonable_encoder(response)

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid username or password")
    return HTTPException(status_code=405, detail="Kullanıcı Adı Veya Şifresi 3 Karakterden Az Olamaz", headers="Not")
def user_controller(username,password):
    if len(username) >3 and len(password)>3:
        return True
    else:
        return False