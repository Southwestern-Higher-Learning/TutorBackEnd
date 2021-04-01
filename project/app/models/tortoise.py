from enum import IntEnum
from typing import List, Optional

from fastapi_admin.models import AbstractUser
from pydantic import BaseConfig, BaseModel
from tortoise import Tortoise, fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import NoValuesFetched


class User(AbstractUser):
    id = fields.BigIntField(pk=True)
    email = fields.CharField(unique=True, max_length=100)
    first_name = fields.CharField(max_length=100)
    last_name = fields.CharField(max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    profile_url = fields.TextField()
    description = fields.TextField(null=True)
    is_tutor = fields.BooleanField(default=False)
    password = fields.CharField(
        max_length=200,
        description="Will auto hash with raw password when change",
        null=True,
    )

    creds: fields.OneToOneRelation["Credentials"]

    categories: fields.ManyToManyRelation["Category"] = fields.ManyToManyField(
        "models.Category",
        related_name="users",
        through="user_gategories",
        backward_key="user_id",
    )

    reviews: fields.ReverseRelation["Review"]

    written_reviews: fields.ReverseRelation["Review"]

    def categories_ids(self) -> List[int]:
        try:
            return [category.id for category in self.categories]
        except NoValuesFetched:
            return []

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class PydanticMeta:
        exclude = ["password", "username", "creds", "usercategories"]
        extra = "ignore"
        computed = ("categories_ids",)


class Credentials(models.Model):
    id = fields.BigIntField(pk=True)
    json_field = fields.JSONField(null=True)
    user = fields.OneToOneField("models.User", related_name="creds")


class Category(models.Model):
    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=30, unique=True)
    locked = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name

    class PydanticMeta:
        exclude = ["usercategories", "users"]
        extra = "ignore"


class UserCategories(models.Model):
    user = fields.ForeignKeyField("models.User", related_name="usercategories")
    category = fields.ForeignKeyField("models.Category", related_name="usercategories")

    class Meta:
        table = "user_categories"
        unique_together = (("user_id", "category_id"),)


class Review(models.Model):
    id = fields.BigIntField(pk=True)
    reviewer = fields.ForeignKeyField("models.User", related_name="written_reviews")
    reviewee = fields.ForeignKeyField("models.User", related_name="reviews")
    rating = fields.IntField()
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class PydanticMeta:
        exclude = ["userwrittenreviews, userreviews"]
        extra = "ignore"

    class Meta:
        unique_together = (("reviewer_id", "reviewee_id"),)


class ReportType(IntEnum):
    user = 0
    review = 0


class Report(models.Model):
    id = fields.BigIntField(pk=True)
    type = fields.IntEnumField(ReportType)
    reference_id = fields.BigIntField()
    user = fields.OneToOneField("models.User")
    reason = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


Tortoise.init_models(["app.models.tortoise"], "models")

User_Pydnatic = pydantic_model_creator(User, name="User")
_UserIn_Pydnatic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)

Category_Pydnatic = pydantic_model_creator(Category, name="Category")
_CategoryIn_Pydnatic = pydantic_model_creator(
    Category, name="CategoryIn", exclude_readonly=True
)

Review_Pydnatic = pydantic_model_creator(Review, name="Reviews")
ReviewIn_Pydnatic = pydantic_model_creator(Review, name="ReviewIn")

Report_Pydnatic = pydantic_model_creator(Report, name="Report")
ReportIn_Pydnatic = pydantic_model_creator(Report, name="ReportIn")


class UserIn_Pydnatic(_UserIn_Pydnatic):
    categories_ids: Optional[List[int]]

    class Config(BaseConfig):
        extra = "ignore"


class CategoryIn_Pydnatic(_CategoryIn_Pydnatic):
    class Config(BaseConfig):
        extra = "ignore"


class UserCreate(BaseModel):
    user: User_Pydnatic
    access_token: str
    refresh_token: str

    class Config:
        validate_assignment = True
