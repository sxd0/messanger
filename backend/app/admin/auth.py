from typing import Optional
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.users.auth import authenticate_user, create_access_token
from app.users.dependencies import get_current_user
from app.users.role.dao import RoleDAO


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]

        # Аутентификация пользователя
        user = await authenticate_user(email, password)
        if user:
            # Проверяем, имеет ли пользователь роль "admin"
            role = await RoleDAO.find_one_or_none(id=user.role_id)
            if role and role.name == "Admin":
                access_token = create_access_token({"sub": str(user.id)})
                request.session.update({"token": access_token})
                return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        token = request.session.get("token")

        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        user = await get_current_user(token)
        if not user:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        role = await RoleDAO.find_one_or_none(id=user.role_id)
        if not role or role.name != "Admin":
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        return True

authentication_backend = AdminAuth(secret_key="...")