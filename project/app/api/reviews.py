from typing import List

from fastapi import APIRouter, Depends, Response

from app.api.user import find_current_superuser, find_current_user
from app.models.pydnatic import ReviewFilters
from app.models.tortoise import Review, Review_Pydnatic
from app.models.utils import PaginateModel

router = APIRouter(prefix="/category", tags=["category"])

pageinate_review = PaginateModel(Review, ReviewFilters)

# GET /
# must by normal user
# Get all reviews
@router.get("/", response_model=List[Review_Pydnatic])
async def get_reviews(
        response: Response,
        reviews=Depends(pageinate_review),
):
    len_reviews = await reviews.count()
    response.headers["X-Total-Count"] = f"{len_reviews}"
    return await Review_Pydnatic.from_queryset(reviews)