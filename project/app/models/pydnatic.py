from typing import Optional

from pydantic import AnyHttpUrl, BaseModel


class SwapCodeIn(BaseModel):
    code: str
    redirect_uri: AnyHttpUrl


class NormalUserUpdate(BaseModel):
    description: Optional[str]
    is_tutor: Optional[bool]


class UserFilters(BaseModel):
    is_tutor: Optional[bool]
    is_superuser: Optional[bool]
    first_name__icontains: Optional[str]
    email__icontains: Optional[str]
    categories__name__icontains: Optional[str]


class CategoryFilters(BaseModel):
    name__icontains: Optional[str]


class ReviewFilters(BaseModel):
    reviewee_id: Optional[int]


class ReportFilters(BaseModel):
    pass


class SessionFilters(BaseModel):
    pass
