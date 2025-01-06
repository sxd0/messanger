from typing import Dict
from fastapi import Depends, WebSocket, WebSocketDisconnect

from app.users.dependencies import get_current_user

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections = {}

#     async def connect(self, chat_id: int, websocket: WebSocket):
#         await websocket.accept()
#         if chat_id not in self.active_connections:
#             self.active_connections[chat_id] = []
#         self.active_connections[chat_id].append(websocket)

#     def disconnect(self, chat_id: int, websocket: WebSocket):
#         if chat_id in self.active_connections:
#             self.active_connections[chat_id].remove(websocket)

#     async def send_message(self, chat_id: int, message: str):
#         if chat_id in self.active_connections:
#             for connection in self.active_connections[chat_id]:
#                 await connection.send_text(message)

    
    # async def broadcast(self, message: str):
    #     for connection in self.active_connections:
    #         await connection.send_text(message)

# Рабочий вариант !!!!!!!!!!!!!!!!!
# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: Dict[str, WebSocket] = {}

#     async def connect(self, websocket: WebSocket, client_id: str):
#         await websocket.accept()
#         self.active_connections[client_id] = websocket

#     def disconnect(self, client_id: str):
#         if client_id in self.active_connections:
#             del self.active_connections[client_id]

#     async def send_personal_message(self, message: dict, websocket: WebSocket):
#         await websocket.send_json(message)

#     async def broadcast(self, message: str):
#         print(f"Broadcasting message: {message}")  # Лог
#         for connection in self.active_connections.values():
#             await connection.send_text(message)

# manager = ConnectionManager()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}  # ключ - ID пользователя

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_message(self, message: dict, user_id: int):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()