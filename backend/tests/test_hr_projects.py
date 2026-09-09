import uuid
from datetime import date, timedelta
from decimal import Decimal
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base
from app.models.auth import Organization
from app.schemas.hr_projects import (
    AttendanceCreate,
    EmployeeCreate,
    LeaveApplicationCreate,
    ProjectCreate,
    TaskCreate,
    TimesheetCreate,
)
from app.services.hr_projects import HRProjectService

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.mark.asyncio
async def test_hr_employee_attendance_and_leaves(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-hr-test")
    async_db.add(org)
    await async_db.flush()

    service = HRProjectService(async_db, org_id)

    # 1. Create Employee
    emp = await service.create_employee(
        EmployeeCreate(
            employee_code="EMP-101",
            first_name="Priya",
            last_name="Nair",
            email="priya.nair@nexusretail.com",
            date_of_joining=date(2025, 3, 1),
        )
    )
    assert emp.id is not None
    assert emp.status == "ACTIVE"

    # 2. Log Attendance
    att = await service.log_attendance(
        AttendanceCreate(
            employee_id=emp.id,
            attendance_date=date.today(),
            status="PRESENT",
        )
    )
    assert att.id is not None
    assert att.status == "PRESENT"

    # 3. Apply Leave & Approve
    leave = await service.apply_leave(
        LeaveApplicationCreate(
            employee_id=emp.id,
            leave_type="SICK",
            start_date=date.today() + timedelta(days=2),
            end_date=date.today() + timedelta(days=3),
            total_days=Decimal("2.0"),
            reason="Medical recovery",
        )
    )
    assert leave.status == "PENDING"

    approved_leave = await service.approve_leave(leave.id)
    assert approved_leave.status == "APPROVED"


@pytest.mark.asyncio
async def test_projects_tasks_timesheets_and_overdue_alerts(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-proj-test")
    async_db.add(org)
    await async_db.flush()

    service = HRProjectService(async_db, org_id)

    # Setup Employee
    emp = await service.create_employee(
        EmployeeCreate(
            employee_code="EMP-202",
            first_name="Rohan",
            last_name="Mehta",
            email="rohan.mehta@nexusretail.com",
            date_of_joining=date(2025, 1, 10),
        )
    )

    # 1. Create Project
    project = await service.create_project(
        ProjectCreate(
            name="ERP Modernization 2.0",
            code="PRJ-ERP-01",
            budget=Decimal("500000.00"),
            start_date=date(2026, 1, 1),
        )
    )
    assert project.id is not None
    assert project.spent_amount == Decimal("0.00")

    # 2. Create Overdue Task (due 5 days ago)
    past_due = date.today() - timedelta(days=5)
    task = await service.create_task(
        TaskCreate(
            project_id=project.id,
            title="Database Sharding Strategy Doc",
            status="IN_PROGRESS",
            priority="HIGH",
            due_date=past_due,
            estimated_hours=Decimal("16.00"),
        )
    )
    assert task.id is not None

    # 3. Log Timesheet: 8 hours worked @ 800/hr = 6,400 spent
    timesheet = await service.log_timesheet(
        TimesheetCreate(
            employee_id=emp.id,
            project_id=project.id,
            task_id=task.id,
            work_date=date.today(),
            hours=Decimal("8.00"),
            activity_description="Drafted PostgreSQL horizontal sharding benchmarks",
        )
    )
    assert timesheet.id is not None
    assert task.actual_hours == Decimal("8.00")
    assert project.spent_amount == Decimal("6400.00")

    # 4. Check Proactive AI Overdue Task Alerts
    alerts = await service.get_overdue_tasks()
    assert len(alerts) == 1
    assert alerts[0].task_id == task.id
    assert alerts[0].project_name == "ERP Modernization 2.0"
    assert alerts[0].days_overdue == 5
    assert alerts[0].priority == "HIGH"
