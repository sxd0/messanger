from datetime import datetime
from jose import jwt, JWTError

from fastapi import Depends, HTTPException, Request, status
from app.config import settings
from app.users.dao import UsersDAO
from app.users.models import Users

def get_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return token


def get_refresh_token(request: Request): # Получение рефреш токена new
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token not found")
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) #

    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    user = await UsersDAO.find_one_or_none(id=int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return user