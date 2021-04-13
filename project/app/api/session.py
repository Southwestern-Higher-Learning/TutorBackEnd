import datetime
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
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
async def get_categories(
    response: Response,
    current_user: User = Depends(find_current_superuser),
    sessions=Depends(paginate_sessions),
):
    len_sessions = await sessions.count()
    response.headers["X-Total-Count"] = f"{len_sessions}"
    return await Session_Pydnatic.from_queryset(sessions)


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
    attendees = event.get(
        "attendees", [{"email": tutor.email, "responseStatus": "accepted"}]
    )
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


@router.get("/stats/sessions", response_model=Session_Pydnatic)
async def weekly_session_stats(
    current_superuser: User = Depends(find_current_superuser),
):
    previous_week_start = datetime.datetime.now() - datetime.timedelta(days=7)
    previous_week_end = datetime.datetime.now()
    sessions = await Session.filter(start_time__gte=previous_week_start, start_time__lte=previous_week_end).all()
    data = {}
    for session in sessions:
        day = datetime.datetime.strftime(session.start_time, "%Y-%m-%d")
        if day in data:
            data[day] += 1
        else:
            data[day] = 1
    return JSONResponse(content=data)
