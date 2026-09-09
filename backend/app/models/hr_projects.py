import uuid
from datetime import date, datetime, time
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Numeric,
    String,
    Text,
    Time,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.auth import User
from app.models.base import IdMixin, TenantBaseModel
from app.models.crm import Customer
from app.models.organization import Department


class Designation(TenantBaseModel):
    """Job title/designation within the company."""
    __tablename__ = "designations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Employee(TenantBaseModel):
    """Employee personal, organizational, and employment record."""
    __tablename__ = "employees"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    employee_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    designation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("designations.id", ondelete="SET NULL"),
        nullable=True,
    )
    date_of_joining: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
        nullable=False,
    )  # ACTIVE, ON_LEAVE, RESIGNED, TERMINATED

    department: Mapped[Optional["Department"]] = relationship("Department")
    designation: Mapped[Optional["Designation"]] = relationship("Designation")


class Attendance(TenantBaseModel):
    """Daily check-in / check-out attendance ledger."""
    __tablename__ = "attendance"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attendance_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="PRESENT",
        nullable=False,
    )  # PRESENT, ABSENT, HALF_DAY, ON_LEAVE
    check_in: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    check_out: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    employee: Mapped["Employee"] = relationship("Employee")


class LeaveApplication(TenantBaseModel):
    """Time-off request and approval lifecycle."""
    __tablename__ = "leave_applications"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    leave_type: Mapped[str] = mapped_column(String(50), default="CASUAL", nullable=False)  # CASUAL, SICK, PRIVILEGE
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_days: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
    )  # PENDING, APPROVED, REJECTED

    employee: Mapped["Employee"] = relationship("Employee")


class Project(TenantBaseModel):
    """Project workspace tracking scope, milestones, and profitability."""
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
    )
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="PLANNING",
        nullable=False,
    )  # PLANNING, ACTIVE, ON_HOLD, COMPLETED, CANCELLED
    budget: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    spent_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(TenantBaseModel):
    """Kanban work item under a project."""
    __tablename__ = "tasks"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="TODO",
        nullable=False,
        index=True,
    )  # TODO, IN_PROGRESS, REVIEW, DONE
    priority: Mapped[str] = mapped_column(
        String(50),
        default="MEDIUM",
        nullable=False,
    )  # LOW, MEDIUM, HIGH, URGENT
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    estimated_hours: Mapped[float] = mapped_column(Numeric(6, 2), default=0.00, nullable=False)
    actual_hours: Mapped[float] = mapped_column(Numeric(6, 2), default=0.00, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")


class Timesheet(TenantBaseModel):
    """Labor hour logs per project and task."""
    __tablename__ = "timesheets"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
    )
    work_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    hours: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    activity_description: Mapped[str] = mapped_column(String(500), nullable=False)
    is_billable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    employee: Mapped["Employee"] = relationship("Employee")
    project: Mapped["Project"] = relationship("Project")
