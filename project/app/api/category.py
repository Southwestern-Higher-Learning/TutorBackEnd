from typing import List

from fastapi import APIRouter, Depends

from app.api.user import find_current_user
from app.models.tortoise import Category, Category_Pydnatic, CategoryIn_Pydnatic, User
from app.models.pydnatic import CategoryFilters
from app.models.utils import PaginateModel

router = APIRouter(prefix="/category", tags=["category"])

pageinate_category = PaginateModel(Category, CategoryFilters)


# GET /
# Must be normal user (find_current_user)
# Get all categories
@router.get("/", response_model=List[Category_Pydnatic])
async def get_categories(current_user: User = Depends(find_current_user), categories=Depends(pageinate_category)):
    len_categories = await categories.count()
    response.headers["X-Total-Count"] = f"{len_categories}"
    return await Category_Pydnatic.from_queryset(categories)


# GET /{id}
# Must be normal user
# Get category by ID

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
