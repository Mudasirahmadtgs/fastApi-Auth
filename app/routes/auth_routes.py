from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.controllers.auth_controller import signup_user, login_user
from app.database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])

class SignupSchema(BaseModel):
    username: str
    email: str
    password: str

class LoginSchema(BaseModel):
    username: str
    password: str

@router.post("/signup")
def signup(payload: SignupSchema, db: Session = Depends(get_db)):
    return signup_user(payload.username, payload.email, payload.password, db)

@router.post("/login")
def login(payload: LoginSchema, db: Session = Depends(get_db)):
    return login_user(payload.username, payload.password, db)
