from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPBearer
from fastapi_jwt_auth import AuthJWT

from app.models.pydnatic import NormalUserUpdate, UserFilters
from app.models.tortoise import User, User_Pydnatic, UserIn_Pydnatic
from app.models.utils import PaginateModel

router = APIRouter(prefix="/user", tags=["user"])

bearer = HTTPBearer()

pageinate_user = PaginateModel(User, UserFilters)


async def find_current_user(
    Authorize: AuthJWT = Depends(), bearer=Depends(bearer)
) -> User:
    Authorize.jwt_required()

    access_token_subject = Authorize.get_jwt_subject()

    user = await User.get_or_none(email=access_token_subject).first()

    if user is None:
        raise HTTPException(403, "JWT subject not found")

    return user


async def find_current_superuser(
    current_user: User = Depends(find_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(403, "Not a superuser")
    return current_user


# GET /user/me find the current user based on the access_token
@router.get("/me", response_model=User_Pydnatic, operation_id="authorize")
async def get_current_user(current_user: User = Depends(find_current_user)):
    return await User_Pydnatic.from_tortoise_orm(current_user)


# PATCH /user/me update user profile based on current user
@router.patch("/me", response_model=User_Pydnatic, operation_id="authorize")
async def patch_current_user(
    user_update: NormalUserUpdate, current_user: User = Depends(find_current_user)
):
    await User.get(id=current_user.id).update(**user_update.dict(exclude_unset=True))
    return await User_Pydnatic.from_queryset_single(User.get(id=current_user.id))


# GET /user/{user_id}
@router.get("/{user_id}", response_model=User_Pydnatic, operation_id="authorize")
async def get_user_id(user_id: int, current_user: User = Depends(find_current_user)):
    return await User_Pydnatic.from_queryset_single(User.get(id=user_id))


@router.get("/", response_model=List[User_Pydnatic])
async def get_all_users(
    response: Response,
    current_user: User = Depends(find_current_user),
    users=Depends(pageinate_user),
):
    len_users = await users.count()
    response.headers["X-Total-Count"] = f"{len_users}"
    return await User_Pydnatic.from_queryset(users)


@router.put("/{user_id}", response_model=User_Pydnatic)
async def put_user_id(
    user: UserIn_Pydnatic,
    user_id: int,
    current_superuser: User = Depends(find_current_superuser),
):
    await User.filter(id=user_id).update(**user.dict(exclude_unset=True))
    return await User_Pydnatic.from_queryset_single(User.get(id=user_id))
