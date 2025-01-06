from app.dao.base import BaseDAO
from app.users.role.models import Role


class RoleDAO(BaseDAO):
    model = Role