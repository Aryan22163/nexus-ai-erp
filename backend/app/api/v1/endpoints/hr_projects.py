import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant
from app.core.database import get_db_session
from app.models.auth import Organization
from app.repositories.hr_projects import (
    AttendanceRepository,
    EmployeeRepository,
    LeaveApplicationRepository,
    ProjectRepository,
    TaskRepository,
)
from app.schemas.hr_projects import (
    AttendanceCreate,
    AttendanceResponse,
    EmployeeCreate,
    EmployeeResponse,
    LeaveApplicationCreate,
    LeaveApplicationResponse,
    OverdueTaskAlertItem,
    ProjectCreate,
    ProjectResponse,
    TaskCreate,
    TaskResponse,
    TimesheetCreate,
    TimesheetResponse,
)
from app.services.hr_projects import HRProjectService

router = APIRouter(prefix="/hr", tags=["HR & Project Management"])


# --- Employees ---
@router.get(
    "/employees",
    response_model=List[EmployeeResponse],
    dependencies=[Depends(RequirePermissions("hr.read"))],
)
async def list_employees(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    skip: int = 0,
    limit: int = 50,
) -> List[EmployeeResponse]:
    repo = EmployeeRepository(db, tenant.id)
    emps = await repo.list_all(skip=skip, limit=limit)
    return [EmployeeResponse.model_validate(e) for e in emps]


@router.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("hr.manage"))],
)
async def create_employee(
    payload: EmployeeCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> EmployeeResponse:
    service = HRProjectService(db, tenant.id)
    emp = await service.create_employee(payload)
    return EmployeeResponse.model_validate(emp)


# --- Attendance ---
@router.post(
    "/attendance",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("hr.manage"))],
)
async def log_attendance(
    payload: AttendanceCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AttendanceResponse:
    service = HRProjectService(db, tenant.id)
    att = await service.log_attendance(payload)
    return AttendanceResponse.model_validate(att)


# --- Leaves ---
@router.post(
    "/leaves",
    response_model=LeaveApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("hr.read"))],
)
async def apply_leave(
    payload: LeaveApplicationCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LeaveApplicationResponse:
    service = HRProjectService(db, tenant.id)
    leave = await service.apply_leave(payload)
    return LeaveApplicationResponse.model_validate(leave)


@router.post(
    "/leaves/{leave_id}/approve",
    response_model=LeaveApplicationResponse,
    dependencies=[Depends(RequirePermissions("hr.manage"))],
)
async def approve_leave(
    leave_id: uuid.UUID,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LeaveApplicationResponse:
    service = HRProjectService(db, tenant.id)
    leave = await service.approve_leave(leave_id)
    return LeaveApplicationResponse.model_validate(leave)


# --- Projects ---
@router.get(
    "/projects",
    response_model=List[ProjectResponse],
    dependencies=[Depends(RequirePermissions("projects.read"))],
)
async def list_projects(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[ProjectResponse]:
    repo = ProjectRepository(db, tenant.id)
    projs = await repo.list_all()
    return [ProjectResponse.model_validate(p) for p in projs]


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("projects.manage"))],
)
async def create_project(
    payload: ProjectCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProjectResponse:
    service = HRProjectService(db, tenant.id)
    proj = await service.create_project(payload)
    return ProjectResponse.model_validate(proj)


# --- Tasks ---
@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("projects.manage"))],
)
async def create_task(
    payload: TaskCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TaskResponse:
    service = HRProjectService(db, tenant.id)
    task = await service.create_task(payload)
    return TaskResponse.model_validate(task)


# --- Timesheets ---
@router.post(
    "/timesheets",
    response_model=TimesheetResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("projects.read"))],
)
async def log_timesheet(
    payload: TimesheetCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TimesheetResponse:
    service = HRProjectService(db, tenant.id)
    ts = await service.log_timesheet(payload)
    return TimesheetResponse.model_validate(ts)


# --- AI Overdue Task Alerts ---
@router.get(
    "/alerts/overdue-tasks",
    response_model=List[OverdueTaskAlertItem],
    dependencies=[Depends(RequirePermissions("projects.read"))],
)
async def get_overdue_tasks(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[OverdueTaskAlertItem]:
    service = HRProjectService(db, tenant.id)
    return await service.get_overdue_tasks()
