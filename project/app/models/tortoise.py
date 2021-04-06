import datetime
from enum import IntEnum
from typing import List, Optional, Type
import logging

from fastapi import HTTPException
from fastapi_admin.models import AbstractUser
from pydantic import BaseConfig, BaseModel
from tortoise import Tortoise, fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import NoValuesFetched
from google.oauth2.credentials import Credentials as Creds
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from tortoise.signals import pre_save

from app.config import get_settings

log = logging.getLogger("uvicorn")


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
    google_calendar_id = fields.CharField(max_length=255, null=True)

    creds: fields.OneToOneRelation["Credentials"]

    categories: fields.ManyToManyRelation["Category"] = fields.ManyToManyField(
        "models.Category",
        related_name="users",
        through="user_categories",
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


    async def get_creds(self) -> Creds:
        settings = get_settings()
        await self.fetch_related("creds")
        creds = self.creds.json_field
        # return Creds(
        #     token=creds['token'],
        #     refresh_token=creds['refresh_token'],
        #     token_uri=creds['token_uri'],
        #     client_id=settings.google_client_id,
        #     client_secret=settings.google_client_secret,
        #     expiry=datetime.datetime.fromisoformat(creds['expiry'].replace("Z", "+00:00")),
        #     scopes=creds['scopes']
        # )
        return Creds.from_authorized_user_info(creds)

    async def update_calendar(self):
        if self.is_tutor and self.google_calendar_id is None:
            service = await self.get_calendar_service()

            calendar = {
                "summary": "TutorApp Schedule",
                "timeZone": "America/Chicago"
            }

            created_calendar = service.calendars().insert(body=calendar).execute()

            self.google_calendar_id = created_calendar['id']
            await self.save()

    async def get_calendar_service(self):
        creds = await self.get_creds()
        if creds.expired:
            creds.refresh(Request())
        self.creds.json_field = creds.to_json()
        await self.creds.save()

        return build('calendar', 'v3', credentials=creds)

    async def get_events(self, time_min: datetime.datetime, time_max: datetime.datetime):
        if self.google_calendar_id is None:
            raise HTTPException(404, "No Calendar found")

        service = await self.get_calendar_service()

        calendar = service.calendars().get(calendarId=self.google_calendar_id).execute()

        if 'summary' not in calendar:
            raise HTTPException(404, "No Calendar found")

        time_min = time_min.astimezone().isoformat()
        time_max = time_max.astimezone().isoformat()

        event_list = []
        page_token = None

        while True:
            events = service.events().list(calendarId=self.google_calendar_id, pageToken=page_token, timeMin=time_min, timeMax=time_max, singleEvents=True).execute()
            event_list.extend(events['items'])
            page_token = events.get('nextPageToken')
            if not page_token:
                break

        return event_list

    class PydanticMeta:
        exclude = ["password", "username", "creds", "usercategories", "studentsessions", "student_sessions", "tutor_sessions"]
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
        exclude = ["usercategories", "users", "studentsessions"]
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
    review = 1


class Report(models.Model):
    id = fields.BigIntField(pk=True)
    type = fields.IntEnumField(ReportType)
    reference_id = fields.BigIntField()
    user = fields.OneToOneField("models.User")
    reason = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class StudentSessions(models.Model):
    session = fields.ForeignKeyField("models.Session", related_name="studentsessions")
    user = fields.ForeignKeyField("models.User", related_name="studentsessions")
    category = fields.ForeignKeyField("models.Category", related_name="studentsessions")

    class Meta:
        table = "student_session"
        unique_together = (("session_id", "student_id"),)


class Session(models.Model):
    id = fields.BigIntField(pk=True)
    tutor = fields.ForeignKeyField("models.User", related_name="tutor_sessions")
    students: fields.ManyToManyRelation["Category"] = fields.ManyToManyField(
        "models.User",
        related_name="student_sessions",
        through="student_session",
        backward_key="session_id",
    )
    start_time = fields.DatetimeField(null=True)
    event_id = fields.CharField(max_length=255)

    def tutor_id(self):
        return self.tutor.id

    def student_ids(self) -> List[int]:
        try:
            return [student.id for student in self.students]
        except NoValuesFetched:
            return []

    class PydanticMeta:
        exclude = ["tutor", "students", "studentsessions"]
        computed = ("tutor_id", "student_ids")


Tortoise.init_models(["app.models.tortoise"], "models")

User_Pydnatic = pydantic_model_creator(User, name="User")
_UserIn_Pydnatic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)

Category_Pydnatic = pydantic_model_creator(Category, name="Category")
_CategoryIn_Pydnatic = pydantic_model_creator(
    Category, name="CategoryIn", exclude_readonly=True
)

Review_Pydnatic = pydantic_model_creator(Review, name="Reviews")
ReviewIn_Pydnatic = pydantic_model_creator(Review, name="ReviewIn", exclude_readonly=True)

Report_Pydnatic = pydantic_model_creator(Report, name="Report")
ReportIn_Pydnatic = pydantic_model_creator(Report, name="ReportIn", exclude_readonly=True)

Session_Pydnatic = pydantic_model_creator(Session, name="Sessions")
# _SessionIn_Pydnatic = pydantic_model_creator(Session, name="SessionIn", exclude_readonly=True)


class UserIn_Pydnatic(_UserIn_Pydnatic):
    categories_ids: Optional[List[int]]

    class Config(BaseConfig):
        extra = "ignore"


class CategoryIn_Pydnatic(_CategoryIn_Pydnatic):
    class Config(BaseConfig):
        extra = "ignore"


class SessionIn_Pydnatic(BaseModel):
    tutor_id: int
    event_id: str
    category_id: int


class UserCreate(BaseModel):
    user: User_Pydnatic
    access_token: str
    refresh_token: str

    class Config:
        validate_assignment = True
