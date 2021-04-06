from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse

from app.api.user import find_current_superuser, find_current_user
from app.models.pydnatic import CategoryFilters
from app.models.tortoise import Category, Category_Pydnatic, CategoryIn_Pydnatic, User
from app.models.utils import PaginateModel

router = APIRouter(prefix="/category", tags=["category"])

pageinate_category = PaginateModel(Category, CategoryFilters)


# GET /
# Must be normal user (find_current_user)
# Get all categories
@router.get("/", response_model=List[Category_Pydnatic])
async def get_categories(
    response: Response,
    current_user: User = Depends(find_current_user),
    categories=Depends(pageinate_category),
):
    len_categories = await categories.count()
    response.headers["X-Total-Count"] = f"{len_categories}"
    return await Category_Pydnatic.from_queryset(categories)


# GET /{id}
# Must be normal user
# Get category by ID
@router.get("/{category_id}", response_model=Category_Pydnatic)
async def get_category_id(
    category_id: int, current_user: User = Depends(find_current_user)
):
    return await Category_Pydnatic.from_queryset_single(Category.get(id=category_id))


# POST /
# Must be superuser (find_current_superuser)
# Create new category
@router.post("/", response_model=Category_Pydnatic)
async def create_category(category: CategoryIn_Pydnatic):
    category_obj = await Category.create(**category.dict(exclude_unset=True))
    return await Category_Pydnatic.from_tortoise_orm(category_obj)


# PUT /{id}
# Must be superuser
# Update individual category
@router.put("/{category_id}", response_model=Category_Pydnatic)
async def put_user_id(
    category: CategoryIn_Pydnatic,
    category_id: int,
    current_superuser: User = Depends(find_current_superuser),
):
    await Category.filter(id=category_id).update(**category.dict(exclude_unset=True))
    return await Category_Pydnatic.from_queryset_single(Category.get(id=category_id))


# DELETE /
# must be superuser
# delete a report
@router.delete("/", response_model=Category_Pydnatic)
async def delete_category(
    category_id: int, current_superuser: User = Depends(find_current_superuser)
):
    deleted_category = await Category.filter(id=category_id).delete()
    if not deleted_category:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")
    return JSONResponse(content={"message": f"Category deleted {category_id}"})
