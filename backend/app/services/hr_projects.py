import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException, NexusException
from app.models.hr_projects import (
    Attendance,
    Employee,
    LeaveApplication,
    Project,
    Task,
    Timesheet,
)
from app.repositories.hr_projects import (
    AttendanceRepository,
    DesignationRepository,
    EmployeeRepository,
    LeaveApplicationRepository,
    ProjectRepository,
    TaskRepository,
    TimesheetRepository,
)
from app.schemas.hr_projects import (
    AttendanceCreate,
    EmployeeCreate,
    LeaveApplicationCreate,
    OverdueTaskAlertItem,
    ProjectCreate,
    TaskCreate,
    TimesheetCreate,
)


class HRProjectService:
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        self.session = session
        self.organization_id = organization_id
        self.emp_repo = EmployeeRepository(session, organization_id)
        self.desig_repo = DesignationRepository(session, organization_id)
        self.att_repo = AttendanceRepository(session, organization_id)
        self.leave_repo = LeaveApplicationRepository(session, organization_id)
        self.proj_repo = ProjectRepository(session, organization_id)
        self.task_repo = TaskRepository(session, organization_id)
        self.timesheet_repo = TimesheetRepository(session, organization_id)

    async def create_employee(self, payload: EmployeeCreate) -> Employee:
        existing = await self.emp_repo.get_by_code(payload.employee_code)
        if existing:
            raise NexusException(f"Employee code '{payload.employee_code}' already exists.")

        emp = await self.emp_repo.create(**payload.model_dump())
        return emp

    async def log_attendance(self, payload: AttendanceCreate) -> Attendance:
        emp = await self.emp_repo.get_by_id(payload.employee_id)
        if not emp:
            raise EntityNotFoundException("Employee", payload.employee_id)

        att = await self.att_repo.create(**payload.model_dump())
        return att

    async def apply_leave(self, payload: LeaveApplicationCreate) -> LeaveApplication:
        emp = await self.emp_repo.get_by_id(payload.employee_id)
        if not emp:
            raise EntityNotFoundException("Employee", payload.employee_id)

        leave = await self.leave_repo.create(status="PENDING", **payload.model_dump())
        return leave

    async def approve_leave(self, leave_id: uuid.UUID) -> LeaveApplication:
        leave = await self.leave_repo.get_by_id(leave_id)
        if not leave:
            raise EntityNotFoundException("LeaveApplication", leave_id)

        leave.status = "APPROVED"
        await self.session.flush()
        return leave

    async def create_project(self, payload: ProjectCreate) -> Project:
        proj = await self.proj_repo.create(spent_amount=Decimal("0.00"), **payload.model_dump())
        return proj

    async def create_task(self, payload: TaskCreate) -> Task:
        proj = await self.proj_repo.get_by_id(payload.project_id)
        if not proj:
            raise EntityNotFoundException("Project", payload.project_id)

        task = await self.task_repo.create(actual_hours=Decimal("0.00"), **payload.model_dump())
        return task

    async def log_timesheet(self, payload: TimesheetCreate) -> Timesheet:
        emp = await self.emp_repo.get_by_id(payload.employee_id)
        if not emp:
            raise EntityNotFoundException("Employee", payload.employee_id)

        proj = await self.proj_repo.get_by_id(payload.project_id)
        if not proj:
            raise EntityNotFoundException("Project", payload.project_id)

        timesheet = await self.timesheet_repo.create(**payload.model_dump())

        if payload.task_id:
            task = await self.task_repo.get_by_id(payload.task_id)
            if task:
                task.actual_hours += payload.hours

        # Standard labor billing cost: ₹800/hr
        proj.spent_amount += payload.hours * Decimal("800.00")
        await self.session.flush()

        return timesheet

    async def get_overdue_tasks(self) -> List[OverdueTaskAlertItem]:
        """Proactive AI tracking of overdue project tasks."""
        overdue = await self.task_repo.list_overdue_tasks()
        today = date.today()

        alerts = []
        for task in overdue:
            days_late = (today - task.due_date).days if task.due_date else 0
            alerts.append(
                OverdueTaskAlertItem(
                    task_id=task.id,
                    project_id=task.project_id,
                    project_name=task.project.name if task.project else "General",
                    title=task.title,
                    due_date=task.due_date,
                    days_overdue=days_late,
                    priority=task.priority,
                )
            )

        return alerts
