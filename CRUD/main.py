from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from database import engine, Base, get_db, get_password_hash, verify_password, create_access_token, get_current_user
from sqlalchemy.orm import Session
from models import User


app = FastAPI()
Base.metadata.create_all(bind=engine)


class UserCreate(BaseModel):
    name: str
    password: str
    age: int = Field(gt=0)
    
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        name=user.name,
        hashed_password=get_password_hash(user.password),
        age=user.age
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login")
def login_user(name: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == name).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(401, "Invalid password")
    acces_token = create_access_token(user.id)
    return {"access_token": acces_token, "token_type": "bearer"}

@app.get("/protected")
def get_user_from_token(user: dict = Depends(get_current_user)):
    return {"message": "This is a protected route", "user_id": user["user_id"]}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/users/{user_id}")
def get_user_id(user_id: int, db: Session = Depends(get_db)):
    query = db.query(User).filter(User.id == user_id).first()
    if query is None:
        raise HTTPException(status_code=404, detail="User not found")
    return query

@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    query = db.query(User).filter(User.id == user_id).first()
    if query is None:
        raise HTTPException(status_code=404, detail="User not found")
    query.name = user.name
    query.age = user.age
    db.commit()
    db.refresh(query)
    return {"message": "user updated successfully"} 

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    query = db.query(User).filter(User.id == user_id).first()
    if query is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(query)
    db.commit()
    return {"message": "user deleted successfully"}
