import datetime
import logging
from enum import IntEnum
from typing import List, Optional

from fastapi import HTTPException
from fastapi_admin.models import AbstractUser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as Creds
from googleapiclient.discovery import build
from pydantic import BaseConfig, BaseModel
from tortoise import Tortoise, fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import NoValuesFetched

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
        await self.fetch_related("creds")
        creds = self.creds.json_field
        return Creds.from_authorized_user_info(creds)

    async def update_calendar(self):
        if self.is_tutor and self.google_calendar_id is None:
            service = await self.get_calendar_service()

            calendar = {"summary": "TutorApp Schedule", "timeZone": "America/Chicago"}

            created_calendar = service.calendars().insert(body=calendar).execute()

            self.google_calendar_id = created_calendar["id"]
            await self.save()

    async def get_calendar_service(self):
        creds = await self.get_creds()
        if creds.expired:
            creds.refresh(Request())
        self.creds.json_field = creds.to_json()
        await self.creds.save()

        return build("calendar", "v3", credentials=creds)

    async def get_events(
        self, time_min: datetime.datetime, time_max: datetime.datetime
    ):
        """
        Get the events between time_min and time_max of a tutor in a simplified dictionary format

        time_min : The start date of the events to look for
        time_max : The end date of the events to look for (inclusive)
        """

        # Don't move on if there is no calendar_id
        if self.google_calendar_id is None:
            raise HTTPException(404, "No Calendar found")

        # Get the service to call the calendar API
        service = await self.get_calendar_service()

        # See if the calendar exists
        calendar = service.calendars().get(calendarId=self.google_calendar_id).execute()

        # If the calendar does not exist for some reason, don't move on
        if "summary" not in calendar:
            raise HTTPException(404, "No Calendar found")

        # Format dates to something Google Calendar API understands
        time_min = time_min.astimezone().isoformat()
        time_max = time_max.astimezone().isoformat()

        # Store the formatted events in a list
        event_list = []
        # Used within loop to see if we can move
        page_token = None

        while True:
            # Get the events of the tutor as a list
            events = (
                service.events()
                .list(
                    calendarId=self.google_calendar_id,
                    pageToken=page_token,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                )
                .execute()
            )
            # Loop through each event and get the info we need
            for event in events["items"]:
                event_list.append(
                    {
                        "id": event["id"],
                        "start_time": event["start"]["dateTime"],
                        "end_time": event["end"]["dateTime"],
                        "summary": event["summary"],
                    }
                )
            # Get the page token
            page_token = events.get("nextPageToken")
            # If there is no page token found, then we have reached the end of the events
            if not page_token:
                break

        return event_list

    class PydanticMeta:
        exclude = [
            "password",
            "username",
            "creds",
            "usercategories",
            "studentsessions",
            "student_sessions",
            "tutor_sessions",
        ]
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
    user = fields.ForeignKeyField("models.User", related_name="reports")
    reason = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def user_id(self) -> int:
        return self.user.id

    class PydanticMeta:
        computed = ("user_id",)


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

    def tutor_id(self) -> int:
        return self.tutor.id

    def student_ids(self) -> List[int]:
        try:
            return [student.id for student in self.students]
        except NoValuesFetched:
            return []

    class PydanticMeta:
        exclude = ["tutor", "students"]
        computed = ("tutor_id", "student_ids")


Tortoise.init_models(["app.models.tortoise"], "models")

User_Pydnatic = pydantic_model_creator(User, name="User")
_UserIn_Pydnatic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)

Category_Pydnatic = pydantic_model_creator(Category, name="Category")
_CategoryIn_Pydnatic = pydantic_model_creator(
    Category, name="CategoryIn", exclude_readonly=True
)

Review_Pydnatic = pydantic_model_creator(Review, name="Reviews")
ReviewIn_Pydnatic = pydantic_model_creator(
    Review, name="ReviewIn", exclude_readonly=True
)

Report_Pydnatic = pydantic_model_creator(Report, name="Report")
ReportIn_Pydnatic = pydantic_model_creator(
    Report, name="ReportIn", exclude_readonly=True
)

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
