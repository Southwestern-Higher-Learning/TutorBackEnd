from typing import List

from fastapi import APIRouter, Depends

from app.api.user import find_current_superuser, find_current_user
from app.models.tortoise import (Category, Category_Pydnatic,
                                 CategoryIn_Pydnatic, User)

router = APIRouter(prefix="/category", tags=["category"])


# GET /
# Must be normal user (find_current_user)
# Get all categories

# GET /{id}
# Must be normal user
# Get category by ID
@router.get("/{id}", response_model=Category_Pydnatic)
async def get_category_id(
    category_id: int, current_user: User = Depends(find_current_user)
):
    return await Category_Pydnatic.from_queryset_single(Category.get(id=category_id))


# POST /
# Must be superuser (find_current_superuser)
# Create new category
@router.post("/", response_model=Category_Pydnatic)
async def creat_category(category: CategoryIn_Pydnatic):
    category_obj = await category.create(**category.dict(exclude_unset=True))
    return await Category_Pydnatic.from_tortoise_orm(category_obj)


# PUT /{id}
# Must be superuser
# Update individual category
@router.put("/{id}", response_model=Category_Pydnatic)
async def put_user_id(
    category: CategoryIn_Pydnatic,
    category_id: int,
    current_superuser: User = Depends(find_current_superuser),
):
    await Category.filter(id=category_id).update(**category.dict(exclude_unset=True))
    return await Category_Pydnatic.from_queryset_single(Category.get(id=category_id))
