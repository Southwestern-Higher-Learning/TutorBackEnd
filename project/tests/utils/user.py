from typing import Dict

from fastapi_jwt_auth import AuthJWT

from app.models.tortoise import User


def _create_user(first_name: str, last_name: str) -> User:
    user = User()
    user.first_name = first_name
    user.last_name = last_name
    user.username = f"{first_name}_{last_name}"
    user.email = f"{first_name}_{last_name}@southwestern.edu"
    user.profile_url = f"https://cdn.google.com/{first_name}_{last_name}.png"
    return user


def auth_normal_user(authorization: AuthJWT, event_loop) -> Dict[str, str]:
    async def get_user():
        user = await User.get_or_none(username="test_user").first()
        if not user:
            user = _create_user("test", "user")
            await user.save()
        return user

    normal_user = event_loop.run_until_complete(get_user())
    token = authorization.create_access_token(subject=normal_user.email)
    return {"Authorization": f"Bearer {token}"}


def auth_super_user(authorization: AuthJWT, event_loop) -> Dict[str, str]:
    async def get_user():
        user = await User.get_or_none(is_superuser=True).first()
        if not user:
            user = _create_user("super", "user")
            user.is_superuser = True
            await user.save()
        return user

    superuser = event_loop.run_until_complete(get_user())
    token = authorization.create_access_token(subject=superuser.email)
    return {"Authorization": f"Bearer {token}"}


def auth_tutor_user(authorization: AuthJWT, event_loop) -> Dict[str, str]:
    async def get_user():
        user = await User.get_or_none(username="tutor_user").first()
        if not user:
            user = _create_user("tutor", "user")
            user.is_tutor = True
            await user.save()
        return user

    tutor = event_loop.run_until_complete(get_user())
    token = authorization.create_access_token(subject=tutor.email)
    return {"Authorization": f"Bearer {token}"}
