from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse

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


# GET /{review_id}
# must by normal user
# Get reviews by id
@router.get("/{review_id}", response_model=Review_Pydnatic)
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


# PUT /{review_id}
# must be superuser
# update a review
@router.put("/{review_id}", response_model=Review_Pydnatic)
async def put_review_id(
    review: ReviewIn_Pydnatic,
    review_id: int,
    current_superuser: User = Depends(find_current_superuser),
):
    await Review.filter(id=review_id).update(**review.dict(exclude_unset=True))
    return await Review_Pydnatic.from_queryset_single(Review.get(id=review_id))


# DELETE /{review_id}
# must be superuser
# delete a review
@router.delete("/{review_id}", response_model=Review_Pydnatic)
async def delete_review(
    review_id: int, current_superuser: User = Depends(find_current_superuser)
):
    deleted_count = await Review.filter(id=review_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {review_id} not found")
    return JSONResponse(content={"message": f"Review deleted {review_id}"})
