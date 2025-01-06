import json
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.messages.dao import MessagesDAO
from app.messages.models import Messages
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.messages.websocket import manager
from fastapi import status

router = APIRouter(
    prefix="/messages",
    tags=["Сообщения"],
)

# Ручка - получение всех сообщений из чата (При выборе чата слева прогружаются все сообщения) Исправно
@router.get("/{chat_id}")
async def get_messages(chat_id: int, current_user: Users = Depends(get_current_user)):
    """Получение всех сообщений в определенном чате"""
    messages = await MessagesDAO.find_all(chat_id=chat_id)
    return messages

# active_connections = {}

# Ручка - отправка сообщения в определенном чате
class MessageRequest(BaseModel):
    content: str


from fastapi.logger import logger

@router.post("/{chat_id}/send")
async def send_message(chat_id: int, request: MessageRequest, user=Depends(get_current_user)):
    logger.info(f"Received message: {request.content}")
    logger.info(f"User ID: {user.id}, Chat ID: {chat_id}")

    try:
        message = await MessagesDAO.add(chat_id=chat_id, sender_id=user.id, text=request.content)
        logger.info(f"Message saved in DB: {message}")

        broadcast_message = {
            "chat_id": chat_id,
            "sender_id": user.id,
            "content": request.content,
        }
        await manager.broadcast(json.dumps(broadcast_message))
        logger.info(f"Broadcasted message: {broadcast_message}")

        return message
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
                if not parsed_data.get("content"):
                    logger.warning("Received invalid message format.")
                    continue

                broadcast_message = {
                    "chat_id": chat_id,
                    "content": parsed_data["content"],
                }
                await manager.broadcast(json.dumps(broadcast_message))
                logger.info(f"Broadcasted WebSocket message: {broadcast_message}")

            except json.JSONDecodeError as decode_error:
                logger.error(f"Failed to decode WebSocket message: {decode_error}")
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for chat ID: {chat_id}")
        manager.disconnect(chat_id)





"""
Сообщения
Отправка сообщения:

POST /messages/
Указать chat_id, текст, отправителя.
Отправлять сообщение через WebSocket.
Получение сообщений чата:

GET /messages/?chat_id=<id>
"""