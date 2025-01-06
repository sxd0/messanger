from jose import JWTError, jwt
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from app.users.auth import authenticate_user, create_access_token, create_refresh_token, get_password_hash
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user, get_refresh_token
from app.users.models import Users
from app.users.schemas import SUserLogin, SUserRegister
from app.config import settings


router = APIRouter(
    prefix="/auth",
    tags=["Пользователи"],
)

@router.post("/register")
async def register_user(user_data: SUserRegister):
    existing_user = await UsersDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    hashed_password = get_password_hash(user_data.password)

    await UsersDAO.add(email=user_data.email, hashed_password=hashed_password, name=user_data.name, surname=user_data.surname)


@router.post("/login")
async def login_user(response: Response, user_data: SUserLogin):
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    response.set_cookie("access_token", access_token, httponly=True, secure=True, samesite="lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="lax")
    # response.set_cookie("access_token", access_token)
    # response.set_cookie("refresh_token", refresh_token)
    return user

@router.post("/refresh")
async def refresh_token(response: Response, refresh_token: str = Depends(get_refresh_token)):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, settings.ALGORITHM)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")
    user = await UsersDAO.find_one_or_none(id=int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    # Аннулирование старого access токена
    response.delete_cookie("access_token")

    # Аннулирование старого refresh токена
    response.delete_cookie("refresh_token")

    # Создание нового access токена
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("access_token", access_token, httponly=True)

    # Создание нового refresh токена
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    response.set_cookie("refresh_token", new_refresh_token, httponly=True)

    return {"access_token": access_token}


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

class User(BaseModel):
    id: int
    name: str
    surname: str
    nickname: str

class User(BaseModel):
    id: int
    name: str
    surname: str
    nickname: str

@router.get("/search_nicknames")
async def search_nicknames(query: str | None = None, user: Users = Depends(get_current_user)):
    """Поиск пользователей по нику для автодополнения"""

    if not query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query parameter is required")

    # Поиск пользователей по части ника
    users = await UsersDAO.search_by_nickname(query=query)

    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")

    # Формирование ответа
    result = [{'id': user.id, 'name': user.name, 'surname': user.surname, 'nickname': user.nickname} for user in users]

    return result


@router.get("/me")
async def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user


@router.get("/all") # Поможет кирюхе настроить автодополнение ника
async def read_users_all():
    return await UsersDAO.find_all()
