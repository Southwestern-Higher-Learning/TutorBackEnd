from typing import List

from fastapi import APIRouter, Depends, Response

from app.api.user import find_current_superuser, find_current_user
from app.models.pydnatic import ReviewFilters
from app.models.tortoise import Review, Review_Pydnatic, ReviewIn_Pydnatic, User
from app.models.utils import PaginateModel

router = APIRouter(prefix="/category", tags=["category"])

pageinate_review = PaginateModel(Review, ReviewFilters)

# GET /
# must by normal user
# Get all reviews
@router.get("/", response_model=List[Review_Pydnatic])
async def get_reviews(
    response: Response,
    current_user: User = Depends(find_current_user),
    reviews=Depends(pageinate_review),
):
    len_reviews = await reviews.count()
    response.headers["X-Total-Count"] = f"{len_reviews}"
    return await Review_Pydnatic.from_queryset(reviews)

# GET /
# must by normal user
# Get reviews by id
@router.get("/", response_model=Review_Pydnatic)
async def get_review_id(
    review_id: int, current_user: User = Depends(find_current_user)
):
    return await Review_Pydnatic.from_queryset_single(Review.get(id=review_id))

# POST /
# must be normal user
# make a new review
@router.post("/", response_model=Review_Pydnatic)
async def create_review(review: ReviewIn_Pydnatic):
    review_obj = await Review.create(**review.dict(exclude_unset=True))
    return await Review_Pydnatic.from_tortoise_orm(review_obj)

