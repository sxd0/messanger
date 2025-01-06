from app.dao.base import BaseDAO
from app.messages.models import Messages, Requests



class MessagesDAO(BaseDAO):
    model = Messages


class RequestsDAO(BaseDAO):
    model = Requests
