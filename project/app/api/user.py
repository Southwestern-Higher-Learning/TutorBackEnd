from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT

from app.models.pydnatic import NormalUserUpdate
from app.models.tortoise import User, User_Pydnatic

router = APIRouter(prefix="/user", tags=["auth"])


async def find_current_user(Authorize: AuthJWT = Depends()) -> User:
    Authorize.jwt_required()

    access_token_subject = Authorize.get_jwt_subject()

    user = await User.get_or_none(email=access_token_subject).first()

    if user is None:
        raise HTTPException(403, "JWT subject not found")

    return user


# GET /user/me find the current user based on the access_token
@router.get("/me", response_model=User_Pydnatic)
async def get_current_user(current_user: User = Depends(find_current_user)):
    return await User_Pydnatic.from_tortoise_orm(current_user)


# PATCH /user/me update user profile based on current user
@router.patch("/me", response_model=User_Pydnatic)
async def patch_current_user(
    user_update: NormalUserUpdate, current_user: User = Depends(find_current_user)
):
    await User.get(id=current_user.id).update(**user_update.dict(exclude_unset=True))
    return await User_Pydnatic.from_queryset_single(User.get(id=current_user.id))


# GET /user/{user_id}
@router.get("/{user_id}", response_model=User_Pydnatic)
async def get_user_id(user_id: int, current_user: User = Depends(find_current_user)):
    return await User_Pydnatic.from_queryset_single(User.get(id=user_id))
