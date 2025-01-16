import json
import logging
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError
from fastapi.logger import logger
from app.chats.dao import ChatsDAO
from app.messages.dao import MessagesDAO
from app.messages.schemas import MessageRequest, WebSocketMessage
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.messages.websocket import manager
from fastapi import status

router = APIRouter(
    prefix="/messages",
    tags=["Сообщения"],
)

logging.basicConfig(level=logging.INFO)

# Ручка - получение всех сообщений из чата (При выборе чата слева прогружаются все сообщения) Исправно
@router.get("/{chat_id}")
async def get_messages(chat_id: int, current_user: Users = Depends(get_current_user)):
    try:
        # Используем DAO для получения сообщений с именами отправителей
        messages = await MessagesDAO.find_all_with_senders(chat_id=chat_id)
        return messages
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ручка - отправка сообщения в определенном чате
@router.post("/{chat_id}/send")
async def send_message(chat_id: int, request: MessageRequest, user=Depends(get_current_user)):
    logger.info(f"Received message: {request.content}")
    logger.info(f"User ID: {user.id}, Chat ID: {chat_id}")

    try:
        message = await MessagesDAO.add(chat_id=chat_id, sender_id=user.id, text=request.content)
        logger.info(f"Message saved in DB: {message}")

        broadcast_message = WebSocketMessage(
            chat_id=chat_id,
            sender_id=user.id,
            content=request.content,
            sender_name=user.name,
        ).model_dump() 

        chat = await ChatsDAO.find_one_or_none(id=chat_id)
        if chat.is_group:
            await manager.broadcast(json.dumps(broadcast_message))
        else:
            await manager.send_personal_message(str(chat_id), json.dumps(broadcast_message))
        logger.info(f"Message sent: {broadcast_message}")

        return broadcast_message
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send message")


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    logger.info(f"WebSocket connection requested for chat ID: {chat_id}")
    await manager.connect(websocket, chat_id)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")

            try:
                parsed_data = json.loads(data)
                try:
                    broadcast_message = WebSocketMessage(
                        chat_id=int(chat_id),
                        content=parsed_data["content"],
                        sender_id=parsed_data.get("sender_id"),
                        sender_name=parsed_data.get("sender_name")
                    ).model_dump()
                except ValidationError as e:
                    logger.warning(f"Invalid message format: {e}")
                    continue 

                await manager.broadcast(json.dumps(broadcast_message))
                logger.info(f"Broadcasted WebSocket message: {broadcast_message}")

            except json.JSONDecodeError as decode_error:
                logger.error(f"Failed to decode WebSocket message: {decode_error}")
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for chat ID: {chat_id}")
        manager.disconnect(chat_id)


