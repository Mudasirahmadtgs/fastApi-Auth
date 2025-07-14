# =============================================
# FASTAPI AUTHENTICATION SYSTEM - SINGLE FILE
# =============================================

# INSTALL DEPENDENCIES (run this command first)
"""
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] psycopg2-binary sqlalchemy python-dotenv
"""

# ======================
# 1. ENVIRONMENT SETUP
# ======================
```python
Create a .env file with these contents:
DATABASE_URL=postgresql://postgres:passowrd@localhost/db-name
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
---

# ======================
# 2. CONFIGURATION
# ======================
#app/config/config.py
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"

settings = Settings()

                      OR
     #if .env file path shows error the put that code:

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = ""
    SECRET_KEY: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 0

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

settings = Settings()

```
---
# ======================
# 3. DATABASE SETUP
# ======================
#app/database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

# Database engine
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
---

# ======================
# 4. USER MODEL
# ======================
#app/models/user.py
```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
```
---

# ======================
# 5. JWT HANDLER
# ======================
#app/utils/jwt_handler.py
```python

from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

```
---

# ======================
# 6. AUTH CONTROLLER
# ======================
#app/controllers/auth_controller.py
```python

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import timedelta
from app.models.user import User
from app.database import get_db
from app.utils.jwt_handler import create_access_token
from app.config.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def signup_user(username: str, email: str, password: str, db: Session):
    existing_user = db.query(User).filter((User.email == email) | (User.username == username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already registered")

    user = User(username=username, email=email, password=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": "User created successfully"}

def login_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}

```
---

# ======================
# 7. ROUTES
# ======================
#app/routes/auth_routes.py
```python

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

```
---

# ======================
# 8. MAIN APPLICATION
# ======================
#app/main.py
```python

from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth_routes

app = FastAPI()

# Create all tables
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(auth_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Authentication System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
---
## testing the application   
The API will be available at http://localhost:8000 with:

POST (http://localhost:8000/auth/signup) - User registration

POST http://localhost:8000/auth/login - User login
