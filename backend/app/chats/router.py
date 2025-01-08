import logging
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.chats.dao import ChatsDAO, ParticipantsDAO
from app.chats.schemas import SChats
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.models import Users



router = APIRouter(
    prefix="/chats",
    tags=["Чаты"],
)

# Ручка - получение всех чатов пользователя (Нужно чтобы все чаты выводились слева) СДЕЛАТЬ ТАК ЧТОБЫ БЫЛО ИМЯ СОБЕСЕДНИКА
# @router.get("")
# async def get_chats(user: Users = Depends(get_current_user)):
#     """Получение всех чатов для пользователя"""
#     participants = await ParticipantsDAO.find_all(user_id=user.id) # ищем все чаты в которых учавствовал юзер
#     chat_ids = [participant.chat_id for participant in participants] # список в котором все id чатов в которых есть наш юзер
#     chats = await ChatsDAO.find_all_for_list('id', chat_ids) # специальный метод который ищет все чаты в которых был юзер
#     chats_dict: list
#     for i in chats: # Проходимся по чатам юзера чтобы выяснить что есть группа (i - это чат)
#         if i.is_group == False: # Если чат не группа, тогда настроить реализацию так, чтобы выводилось имя собеседника
#             for j in participants: # Идем по всей таблице участников в которой есть chat_id и user_id

#     return chats # вернули все чаты

# Как вариант сделать так, чтобы сначала выводились все словари вот так [{chat_id: [user_id, user_id]}, {chat_id: [user_id, user_id]}]
# И потом уже перезаполнить этот массив именами
# И потом уже сделать проверку, что если чат, тогда вывести то имя которые не является именем пользователя, а если группа, тогда все имена

@router.get("/")
async def get_chats(user: Users = Depends(get_current_user)) -> List[dict]:
    """Получение всех чатов для пользователя."""
    user_participants = await ParticipantsDAO.find_all(user_id=user.id)

    chat_ids = [participant.chat_id for participant in user_participants]

    # Если пользователь не состоит ни в одном чате, возвращаем пустой список.
    if not chat_ids:
        return []

    chats = await ChatsDAO.find_all_for_list("id", chat_ids)

    all_participants = await ParticipantsDAO.find_all_for_list("chat_id", chat_ids)

    chats_dict: Dict[int, List[int]] = {}
    for participant in all_participants:
        if participant.chat_id not in chats_dict:
            chats_dict[participant.chat_id] = []
        chats_dict[participant.chat_id].append(participant.user_id)

    for chat_id, user_ids in chats_dict.items():
        user_names = await UsersDAO.find_names_by_ids(user_ids)
        chats_dict[chat_id] = user_names
    chat_details = []
    for chat in chats:
        participant_names = chats_dict.get(chat.id, [])

        if chat.is_group:
            # Для группового чата отображаем всех участников.
            chat_details.append({
                "chat_id": chat.id,
                "name": ", ".join(sorted(participant_names))  # Участники по алфавиту
            })
        else:
            # Для личного чата ищем имя собеседника.
            other_user_name = next(
                (name for name in participant_names if name != user.name),
                None
            )
            if other_user_name:
                chat_details.append({
                    "chat_id": chat.id,
                    "name": other_user_name
                })

    return chat_details



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
    
    # second_name = (await UsersDAO.find_one_or_none(id=second_user)).name # Поиск второго юзера для названия чата
    # Если чат не существует, создаем новый чат
    new_chat_id = await ChatsDAO.add(is_group=False, created_by=user.id)
    print(new_chat_id)
    # Получаем ID последнего созданного чата для текущего пользователя
    # last_chat = await ChatsDAO.find_last_created_chat(user_id=user.id)
    
    # if not last_chat:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve the created chat.")
    # print(last_chat)
    # Добавляем участников в новый чат
    await ParticipantsDAO.add(user_id=user.id, chat_id=new_chat_id)
    await ParticipantsDAO.add(user_id=second_user, chat_id=new_chat_id)
    
    return {"chat_id": new_chat_id} # возвращаем новый чат



# Ручка - создание чата группы (пользователь может выбрать профили юзеров с которыми хочет создать чат)
@router.post("/create_group")
async def create_group(user_ids: List[int], user: Users = Depends(get_current_user)):
    """Создать группу"""

    # Получаем все чаты текущего пользователя
    participant_records = await ParticipantsDAO.find_all(user_id=user.id)

    # Получаем ID всех чатов, в которых участвует текущий пользователь
    chat_ids = [record.chat_id for record in participant_records]

    # Проверяем, есть ли уже группа с такими же участниками
    chats_all_user = [user.id, *user_ids] # Содержит в себе всех желаемых участников
    chats_all_test = [user.id] # список для сверки с нашим id пользователя
    for user_id in user_ids: # идем по списку с участниками
        existing_chats = await ParticipantsDAO.find_all(user_id=user_id) # список из словарей со строчками участников
        for chat in existing_chats: # сами словари из списка выше
            if chat.chat_id in chat_ids:
                chats_all_test.append(chat.chat_id) # Добавляем все чаты 
    if chats_all_test == chats_all_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group already exists with these users.")

    # Если группа не существует, создаем новую группу
    new_chat_id = await ChatsDAO.add(is_group=True, created_by=user.id)

    # Получаем ID последней созданной группы для текущего пользователя
    # last_chat = await ChatsDAO.find_last_created_chat(user_id=user.id)

    # if not last_chat:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve the created group.")
    
    # Добавляем участников в новую группу
    await ParticipantsDAO.add(user_id=user.id, chat_id=new_chat_id)
    for user_id in user_ids:
        await ParticipantsDAO.add(user_id=user_id, chat_id=new_chat_id)

    return {"chat_id": new_chat_id} # возвращаем новую группу

