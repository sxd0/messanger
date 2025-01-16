import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqladmin import Admin
from app.admin.views import ChatsAdmin, MessagesAdmin, ParticipantsAdmin, RoleAdmin, UserAdmin
from app.users.router import router as router_users
from app.chats.router import router as router_chats
from app.messages.router import router as router_messages
from app.database import engine
from app.admin.auth import authentication_backend
from app.logger import logger


app = FastAPI()




origins = [
    "http://localhost/5173"
]

# origins = [
#     '*'
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                    "Access-Control-Allow-Origin", "Authorization"]
)

# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start_time = time.perf_counter()
#     response = await call_next(request)
#     process_time = time.perf_counter() - start_time
#     logger.info("Request execution time", extra={
#         "process_time": round(process_time, 4)
#     })
#     return response

# Все что ниже тестирование

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")




'''
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        #app { padding: 20px; }
        .hidden { display: none; }
        ul { list-style: none; padding: 0; }
        li { margin: 5px 0; cursor: pointer; }
        #messages { border: 1px solid #ddd; padding: 10px; height: 200px; overflow-y: auto; }
        #chat-window { border: 1px solid #ccc; padding: 10px; max-height: 400px; overflow-y: auto; }
    </style>
</head>
<body>
    <div id="app">
        <h1>Chat App</h1>
        <div id="login-section">
            <h2>Login</h2>
            <input type="email" id="email" placeholder="Email">
            <input type="password" id="password" placeholder="Password">
            <button id="login-btn">Login</button>
        </div>
        <div id="chat-section" class="hidden">
            <h2>Your Chats</h2>
            <ul id="chat-list"></ul>
            <div id="chat-window" class="hidden">
                <h3 id="chat-title"></h3>
                <div id="messages"></div>
                <input id="message-input" placeholder="Type your message">
                <button id="send-message-btn">Send</button>
            </div>
            <h2>All Users</h2>
            <ul id="user-list"></ul>
        </div>
    </div>
    <script>
        let currentUserId = null;
        let socket = null;

        document.getElementById("login-btn").onclick = async () => {
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const response = await fetch("/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            if (response.ok) {
                const user = await response.json();
                currentUserId = user.id;
                document.getElementById("login-section").classList.add("hidden");
                document.getElementById("chat-section").classList.remove("hidden");
                loadChats();
                loadUsers();
            } else {
                alert("Login failed!");
            }
        };

        async function loadChats() {
            const response = await fetch("/chats");
            const chats = await response.json();
            const chatList = document.getElementById("chat-list");
            chatList.innerHTML = "";
            chats.forEach(chat => {
                const li = document.createElement("li");
                li.textContent = chat.name;
                li.onclick = () => openChat(chat.chat_id);
                chatList.appendChild(li);
            });
        }

        async function loadUsers() {
            const response = await fetch("/auth/all");
            const users = await response.json();
            const userList = document.getElementById("user-list");
            userList.innerHTML = "";
            users.forEach(user => {
                const li = document.createElement("li");
                li.textContent = user.name;
                li.onclick = () => createChat(user.id);
                userList.appendChild(li);
            });
        }

        async function openChat(chatId) {
            const chatWindow = document.getElementById("chat-window");
            chatWindow.classList.remove("hidden");
            const messagesDiv = document.getElementById("messages");
            messagesDiv.innerHTML = "";

            const response = await fetch(`/messages/${chatId}`);
            const messages = await response.json();
            messages.forEach(msg => {
                const div = document.createElement("div");
                div.textContent = `${msg.sender_name || "Unknown"}: ${msg.content || "[No content]"}`;
                messagesDiv.appendChild(div);
            });

            if (socket) socket.close();
            socket = new WebSocket(`ws://localhost:8000/messages/ws/${chatId}`);
            socket.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    if (!message.sender_name || !message.content) {
                        console.warn("Invalid message format:", message);
                        return;
                    }

                    const div = document.createElement("div");
                    div.textContent = `${message.sender_name}: ${message.content}`;
                    messagesDiv.appendChild(div);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight; // Scroll to bottom
                } catch (error) {
                    console.error("Failed to process incoming WebSocket message:", error);
                }
            };

            document.getElementById("send-message-btn").onclick = async () => {
                const content = document.getElementById("message-input").value;
                await fetch(`/messages/${chatId}/send`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ content })
                });
                document.getElementById("message-input").value = "";
            };
        }

        async function createChat(userId) {
            const response = await fetch("/chats/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ second_user: userId })
            });
            if (response.ok) loadChats();
        }
    </script>
</body>
</html>
"""
'''

html = """ # email: user1@example.com pass: 123; email: user2@example.com pass: 456
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        #app { padding: 20px; }
        .hidden { display: none; }
        ul { list-style: none; padding: 0; }
        li { margin: 5px 0; cursor: pointer; }
        #messages { border: 1px solid #ddd; padding: 10px; height: 200px; overflow-y: auto; }
        #chat-window { border: 1px solid #ccc; padding: 10px; max-height: 400px; overflow-y: auto; }
    </style>
</head>
<body>
    <div id="app">
        <h1>Chat App</h1>
        <div id="login-section">
            <h2>Login</h2>
            <input type="email" id="email" placeholder="Email">
            <input type="password" id="password" placeholder="Password">
            <button id="login-btn">Login</button>
        </div>
        <div id="chat-section" class="hidden">
            <h2>Your Chats</h2>
            <ul id="chat-list"></ul>
            <div id="chat-window" class="hidden">
                <h3 id="chat-title"></h3>
                <div id="messages"></div>
                <input id="message-input" placeholder="Type your message">
                <button id="send-message-btn">Send</button>
            </div>
            <h2>All Users</h2>
            <ul id="user-list"></ul>
        </div>
    </div>
    <script>
        let currentUserId = null;
        let socket = null;

        document.getElementById("login-btn").onclick = async () => {
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const response = await fetch("/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            if (response.ok) {
                const user = await response.json();
                currentUserId = user.id;
                document.getElementById("login-section").classList.add("hidden");
                document.getElementById("chat-section").classList.remove("hidden");
                loadChats();
                loadUsers();
            } else {
                alert("Login failed!");
            }
        };

        async function loadChats() {
            const response = await fetch("/chats");
            const chats = await response.json();
            const chatList = document.getElementById("chat-list");
            chatList.innerHTML = "";
            chats.forEach(chat => {
                const li = document.createElement("li");
                li.textContent = chat.name;
                li.onclick = () => openChat(chat.chat_id);
                chatList.appendChild(li);
            });
        }

        async function loadUsers() {
            const response = await fetch("/auth/all");
            const users = await response.json();
            const userList = document.getElementById("user-list");
            userList.innerHTML = "";
            users.forEach(user => {
                const li = document.createElement("li");
                li.textContent = user.name;
                li.onclick = () => createChat(user.id);
                userList.appendChild(li);
            });
        }

        async function openChat(chatId) {
            const chatWindow = document.getElementById("chat-window");
            chatWindow.classList.remove("hidden");
            const messagesDiv = document.getElementById("messages");
            messagesDiv.innerHTML = "";

            // Загружаем сообщения
            const response = await fetch(`/messages/${chatId}`);
            if (!response.ok) {
                console.error("Failed to load messages:", response.statusText);
                return;
            }

            const messages = await response.json();
            messages.forEach(msg => {
                const div = document.createElement("div");
                // Используем поле "text" вместо "content"
                div.textContent = `${msg.sender_name || "Unknown"}: ${msg.text || "[No content]"}`;
                messagesDiv.appendChild(div);
            });

            if (socket) socket.close();
            socket = new WebSocket(`ws://localhost:8080/messages/ws/${chatId}`);
            socket.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    if (!message.sender_name || !message.content) {
                        console.warn("Invalid message format:", message);
                        return;
                    }

                    const div = document.createElement("div");
                    div.textContent = `${message.sender_name}: ${message.content}`;
                    messagesDiv.appendChild(div);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight; // Scroll to bottom
                } catch (error) {
                    console.error("Failed to process incoming WebSocket message:", error);
                }
            };

            document.getElementById("send-message-btn").onclick = async () => {
                const content = document.getElementById("message-input").value;
                await fetch(`/messages/${chatId}/send`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ content })
                });
                document.getElementById("message-input").value = "";
            };
        }

        async function createChat(userId) {
            const response = await fetch("/chats/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ second_user: userId })
            });
            if (response.ok) loadChats();
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_html():
    return HTMLResponse(html)




app.include_router(router_users)
app.include_router(router_chats)
app.include_router(router_messages)

admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)
admin.add_view(RoleAdmin)
admin.add_view(ChatsAdmin)
admin.add_view(ParticipantsAdmin)
admin.add_view(MessagesAdmin)