from fastapi_admin.models import AbstractUser
from pydantic import BaseConfig, BaseModel
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


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

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class PydanticMeta:
        exclude = ["password", "username"]
        extra = "ignore"


class Credentials(models.Model):
    id = fields.BigIntField(pk=True)
    json_field = fields.JSONField(null=True)
    user = fields.OneToOneField("models.User", related_name="creds")


User_Pydnatic = pydantic_model_creator(User, name="User")
_UserIn_Pydnatic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)


class UserIn_Pydnatic(_UserIn_Pydnatic):
    class Config(BaseConfig):
        extra = "ignore"


class UserCreate(BaseModel):
    user: User_Pydnatic
    access_token: str
    refresh_token: str

    class Config:
        validate_assignment = True
