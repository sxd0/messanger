import json
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.messages.dao import MessagesDAO
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.messages.websocket import manager


router = APIRouter(
    prefix="/messages",
    tags=["Сообщения"],
)

# Ручка - получение всех сообщений из чата (При выборе чата слева прогружаются все сообщения)
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
    logger.info(f"User: {user.id}, Chat ID: {chat_id}")
    
    try:
        message = await MessagesDAO.add(chat_id=chat_id, sender_id=user.id, text=request.content)
        await manager.broadcast(json.dumps({
            "chat_id": chat_id,
            "sender_id": user.id,
            "content": request.content,
        }))
        return message
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    await manager.connect(websocket, chat_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast({"chat_id": chat_id, "content": data})
    except WebSocketDisconnect:
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