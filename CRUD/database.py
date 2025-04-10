import datetime
from fastapi import Depends, HTTPException
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import bcrypt
from fastapi.security import OAuth2PasswordBearer


DATABASE_URL = "postgresql+psycopg2://postgres:Jarcrisron18@localhost:5432/learn_fastapi"

engine = create_engine(
    url=DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_password_hash(password: str):
    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(password.encode(), salt)
    return hash_password.decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
   
SECRET_KEY = "my_secret_key" 
def create_access_token(user_id: int):
    payload = {
        "sub": user_id,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
        "iat": datetime.datetime.now(datetime.timezone.utc)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload =  jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if  user_id is None:
            raise HTTPException(401, "Unauthorized")
        return{"user_id": user_id}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    
    