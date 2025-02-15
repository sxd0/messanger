import logging
from typing import Dict, List
from fastapi import Depends, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from app.users.dependencies import get_current_user

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)

# manager = ConnectionManager()

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

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)
        logger.info(f"WebSocket connected for client ID: {client_id}. Active connections: {self.active_connections}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            self.active_connections[client_id] = [
                conn for conn in self.active_connections[client_id]
                if conn.client_state != WebSocketState.DISCONNECTED
            ]
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
            logger.info(f"WebSocket disconnected for client ID: {client_id}. Active connections: {self.active_connections}")

    async def broadcast(self, message: str):
        logger.info(f"Broadcasting message to {len(self.active_connections)} clients: {message}")
        for client_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(message)
                    logger.debug(f"Message sent to client {client_id}")
                except Exception as e:
                    logger.error(f"Error broadcasting message to client {client_id}: {e}")
                    connections.remove(connection)
                    if not connections:
                        del self.active_connections[client_id]
                        logger.warning(f"Removed inactive connection for client {client_id}")

    async def send_personal_message(self, client_id: str, message: str):
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_text(message)
                    logger.debug(f"Message sent to client {client_id}")
                except Exception as e:
                    logger.error(f"Error sending message to client {client_id}: {e}")
                    self.active_connections[client_id].remove(connection)
                    if not self.active_connections[client_id]:
                        del self.active_connections[client_id]
                        logger.warning(f"Removed inactive connection for client {client_id}")


manager = ConnectionManager()



# class ConnectionManager:
#     def __init__(self):
#         self.connections = []
    
#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.connections.remove(websocket)

#     async def broadcast(self, message: str):
#         for connection in self.connections:
#             await connection.send_text(message)

# manager = ConnectionManager()