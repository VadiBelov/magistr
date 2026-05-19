from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.auth import get_db, hash_password, verify_password, create_access_token, get_current_user, User

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed, salt = hash_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed,
        salt=salt
    )
    db.add(user)
    db.commit()
    return {"message": "Пользователь создан"}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.salt, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email}