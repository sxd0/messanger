from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.chats.dao import ChatsDAO, ParticipantsDAO
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.models import Users



router = APIRouter(
    prefix="/chats",
    tags=["Чаты"],
)

# Ручка - получение всех чатов пользователя (Нужно чтобы все чаты выводились слева)
@router.get("")
async def get_chats(user: Users = Depends(get_current_user)):
    """Получение всех чатов для пользователя"""
    participants = await ParticipantsDAO.find_all(user_id=user.id) # ищем все чаты в которых учавствовал юзер
    chat_ids = [participant.chat_id for participant in participants] # список в котором все id чатов в которых есть наш юзер
    chats = await ChatsDAO.find_all_for_list('id', chat_ids) # специальный метод который ищет все чаты в которых был юзер
    return chats # вернули все чаты

# Ручка - создание чата для двух пользователей (По нажамтию на профиль другого пользователя)
@router.post("/add")
async def create_chat(second_user: int, user: Users = Depends(get_current_user)):
    """Создать чат"""
    
    # Получаем все чаты текущего пользователя
    participant_records = await ParticipantsDAO.find_all(user_id=user.id)
    
    # Получаем ID всех чатов, в которых участвует текущий пользователь
    chat_ids = [record.chat_id for record in participant_records]
    
    # Проверяем, есть ли уже чат с пользователем second_user
    existing_chats = await ParticipantsDAO.find_all(user_id=second_user) # все чаты второго юзера
    
    for chat in existing_chats: # проходимся и проверяем есть ли такой чат
        if chat.chat_id in chat_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chat already exists with this user.")
    
    second_name = (await UsersDAO.find_one_or_none(id=second_user)).name # Поиск второго юзера для названия чата
    # Если чат не существует, создаем новый чат
    await ChatsDAO.add(name=user.name, second_name=second_name, is_group=False, created_by=user.id)
    
    # Получаем ID последнего созданного чата для текущего пользователя
    last_chat = await ChatsDAO.find_last_created_chat(user_id=user.id)
    
    if not last_chat:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve the created chat.")
    
    # Добавляем участников в новый чат
    await ParticipantsDAO.add(user_id=user.id, chat_id=last_chat.id)
    await ParticipantsDAO.add(user_id=second_user, chat_id=last_chat.id)
    
    return last_chat # возвращаем новый чат

# Ручка - создание чата группы (пользователь может выбрать профили юзеров с которыми хочет создать чат)
class CreateGroupRequest(BaseModel):
    user_ids: List[int]
    group_name: str

@router.post("/create_group")
async def create_group(request: CreateGroupRequest, user: Users = Depends(get_current_user)):
    """Создать группу"""

    # Получаем все чаты текущего пользователя
    participant_records = await ParticipantsDAO.find_all(user_id=user.id)

    # Получаем ID всех чатов, в которых участвует текущий пользователь
    chat_ids = [record.chat_id for record in participant_records]

    # Проверяем, есть ли уже группа с такими же участниками
    for user_id in request.user_ids:
        existing_chats = await ParticipantsDAO.find_all(user_id=user_id)
        for chat in existing_chats:
            if chat.chat_id in chat_ids:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group already exists with these users.")

    # Если группа не существует, создаем новую группу
    await ChatsDAO.add(name=request.group_name, is_group=True, created_by=user.id)

    # Получаем ID последней созданной группы для текущего пользователя
    last_chat = await ChatsDAO.find_last_created_chat(user_id=user.id)

    if not last_chat:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve the created group.")

    # Добавляем участников в новую группу
    await ParticipantsDAO.add(user_id=user.id, chat_id=last_chat.id)
    for user_id in request.user_ids:
        await ParticipantsDAO.add(user_id=user_id, chat_id=last_chat.id)

    return last_chat  # возвращаем новую группу

"""
Чаты
Создание чата:

POST /chats/
Указать ID участников.
Если чат не групповой, проверять существование уже созданного чата между этими пользователями.
Получение списка чатов:

GET /chats/
Возвращать чаты, где пользователь является участником.
"""