import uuid
from datetime import date
from typing import List, Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.auth import User
from app.models.hr_projects import (
    Attendance,
    Designation,
    Employee,
    LeaveApplication,
    Project,
    Task,
    Timesheet,
)
from app.repositories.base import BaseTenantRepository


class EmployeeRepository(BaseTenantRepository[Employee]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Employee, session, organization_id)

    async def get_by_code(self, code: str) -> Optional[Employee]:
        stmt = select(Employee).where(
            Employee.organization_id == self.organization_id,
            Employee.employee_code == code.upper(),
            Employee.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class DesignationRepository(BaseTenantRepository[Designation]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Designation, session, organization_id)


class AttendanceRepository(BaseTenantRepository[Attendance]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Attendance, session, organization_id)

    async def list_by_date(self, attendance_date: date) -> Sequence[Attendance]:
        stmt = select(Attendance).where(
            Attendance.organization_id == self.organization_id,
            Attendance.attendance_date == attendance_date,
            Attendance.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class LeaveApplicationRepository(BaseTenantRepository[LeaveApplication]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(LeaveApplication, session, organization_id)


class ProjectRepository(BaseTenantRepository[Project]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Project, session, organization_id)

    async def get_with_tasks(self, project_id: uuid.UUID) -> Optional[Project]:
        stmt = (
            select(Project)
            .options(selectinload(Project.tasks))
            .where(
                Project.id == project_id,
                Project.organization_id == self.organization_id,
                Project.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class TaskRepository(BaseTenantRepository[Task]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Task, session, organization_id)

    async def list_overdue_tasks(self) -> Sequence[Task]:
        """Fetch incomplete tasks past due date."""
        today = date.today()
        stmt = (
            select(Task)
            .options(selectinload(Task.project))
            .where(
                Task.organization_id == self.organization_id,
                Task.status.in_(["TODO", "IN_PROGRESS", "REVIEW"]),
                Task.due_date < today,
                Task.is_deleted.is_(False),
            )
            .order_by(Task.due_date.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class TimesheetRepository(BaseTenantRepository[Timesheet]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Timesheet, session, organization_id)
