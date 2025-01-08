from sqladmin import ModelView
from app.chats.models import Chats
from app.chats.models import Participants
from app.messages.models import Messages
from app.users.models import Users
from app.users.role.models import Role

class UserAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.email, Users.name, Users.surname, Users.role_id]
    column_details_exclude_list = [Users.hashed_password]
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"

class RoleAdmin(ModelView, model=Role):
    column_list = [Role.id, Role.name]
    name = "Роль"
    name_plural = "Роли"
    icon = "fa-solid fa-user-tag"

class ChatsAdmin(ModelView, model=Chats):
    column_list = [Chats.id, Chats.is_group, Chats.created_by, Chats.created_at]
    name = "Чат"
    name_plural = "Чаты"
    icon = "fa-solid fa-comments"

class ParticipantsAdmin(ModelView, model=Participants):
    column_list = [Participants.id, Participants.user_id, Participants.chat_id]
    name = "Участник"
    name_plural = "Участники"
    icon = "fa-solid fa-users"

class MessagesAdmin(ModelView, model=Messages):
    column_list = [Messages.id, Messages.chat_id, Messages.sender_id, Messages.text, Messages.is_read, Messages.created_at]
    name = "Сообщение"
    name_plural = "Сообщения"
    icon = "fa-solid fa-envelope"
