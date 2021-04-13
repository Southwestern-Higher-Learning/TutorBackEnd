import datetime
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from googleapiclient.errors import HttpError

from app.api.user import find_current_superuser, find_current_user
from app.models.pydnatic import SessionFilters
from app.models.tortoise import (
    Category,
    Session,
    Session_Pydnatic,
    SessionIn_Pydnatic,
    StudentSessions,
    User,
)
from app.models.utils import PaginateModel

router = APIRouter(prefix="/session", tags=["sessions"])

paginate_sessions = PaginateModel(Session, SessionFilters)

log = logging.getLogger("uvicorn")


@router.get("/", response_model=List[Session_Pydnatic])
async def get_sessions(
    response: Response,
    current_user: User = Depends(find_current_superuser),
    sessions=Depends(paginate_sessions),
):
    len_sessions = await sessions.count()
    response.headers["X-Total-Count"] = f"{len_sessions}"
    return await Session_Pydnatic.from_queryset(sessions.prefetch_related("students"))


@router.get("/{session_id}", response_model=Session_Pydnatic)
async def get_session(session_id: int, current_user: User = Depends(find_current_superuser)):
    return await Session_Pydnatic.from_queryset_single(Session.get(id=session_id).prefetch_related("students"))


@router.post("/", response_model=Session_Pydnatic)
async def create_session(
    session_in: SessionIn_Pydnatic, current_user: User = Depends(find_current_user)
):
    tutor: User = await User.get_or_none(id=session_in.tutor_id)
    if tutor is None:
        raise HTTPException(
            status_code=404, detail=f"Tutor {session_in.tutor_id} not found"
        )

    category = await Category.get_or_none(id=session_in.category_id)

    if category is None:
        raise HTTPException(
            status_code=404, detail=f"Category {session_in.category_id} not found"
        )

    tutor_calendar = await tutor.get_calendar_service()
    try:
        event = (
            tutor_calendar.events()
            .get(calendarId=tutor.google_calendar_id, eventId=session_in.event_id)
            .execute()
        )
    except HttpError as e:
        log.info(e)
        raise HTTPException(status_code=404, detail="Calendar w/ id not found")

    event["summary"] = "[SU Guidance] Session"
    attendees = event.get("attendees", [])
    attendees.append({"email": current_user.email})
    event["attendees"] = attendees

    try:
        new_event = (
            tutor_calendar.events()
            .update(
                calendarId=tutor.google_calendar_id,
                eventId=event["id"],
                body=event,
                sendUpdates="all",
            )
            .execute()
        )
    except HttpError as e:
        log.info(e.uri)
        log.info(e.content)
        raise HTTPException(
            status_code=404, detail="Calendar w/ id not found when creating"
        )

    log.info(new_event)

    if "summary" not in new_event:
        raise HTTPException(
            status_code=500, detail=f"Event {session_in.event_id} not updated"
        )

    start = new_event["start"].get("dateTime")
    start = start[:-9]
    start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M")

    session, created = await Session.get_or_create(
        tutor=tutor, event_id=new_event["id"], start_time=start
    )
    # await session.save()

    await StudentSessions.create(session=session, category=category, user=current_user)

    return await Session_Pydnatic.from_queryset_single(Session.get(id=session.id))
