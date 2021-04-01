from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse

from app.api.user import find_current_superuser, find_current_user
from app.models.pydnatic import ReportFilters
from app.models.tortoise import Report, Report_Pydnatic, ReportIn_Pydnatic, User
from app.models.utils import PaginateModel

router = APIRouter(prefix="/reports", tags=["reports"])

pageinate_report = PaginateModel(Report, ReportFilters)


# GET /
# must be normal user
# Get all reports
# try to use the pagination thing like in user and categories
@router.get("/", response_model=List[Report_Pydnatic])
async def get_reports(
    response: Response,
    current_superuser: User = Depends(find_current_superuser),
    reports=Depends(pageinate_report),
):
    len_reports = await reports.count()
    response.headers["X-Total-Count"] = f"{len_reports}"
    return await Report_Pydnatic.from_queryset(reports)


# GET /
# must by superuser user
# Get report by id
@router.get("/{report_id}", response_model=Report_Pydnatic)
async def get_report_id(
    report_id: int, current_superuser: User = Depends(find_current_superuser)
):
    return await Report_Pydnatic.from_queryset_single(Report.get(id=report_id))


# POST /
# must be normal user
# Create a new report
@router.post("/", response_model=Report_Pydnatic)
async def create_report(
    report: ReportIn_Pydnatic, current_user: User = Depends(find_current_user)
):
    report_obj = await Report.create(**report.dict(exclude_unset=True))
    return await Report_Pydnatic.from_tortoise_orm(report_obj)


# PUT /
# must be superuser
# update a report
@router.put("/", response_model=Report_Pydnatic)
async def update_report(
    report: ReportIn_Pydnatic,
    report_id: int,
    current_superuser: User = Depends(find_current_superuser),
):
    await Report.filter(id=report_id).update(**report.dict(exclude_unset=True))
    return await Report_Pydnatic.from_queryset_single(Report.get(id=report_id))


# DELETE /
# must be superuser
# delete a report
@router.delete("/", response_model=Report_Pydnatic)
async def delete_report(
    report_id: int, current_superuser: User = Depends(find_current_superuser)
):
    deleted_report = await Report.filter(id=report_id).delete()
    if not deleted_report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return JSONResponse(content={"message": f"Report deleted {report_id}"})
