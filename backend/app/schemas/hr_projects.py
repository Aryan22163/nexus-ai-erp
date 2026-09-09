import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Designation Schemas ---
class DesignationBase(BaseModel):
    name: str = Field(..., examples=["Senior Systems Architect"])
    description: Optional[str] = None


class DesignationCreate(DesignationBase):
    pass


class DesignationResponse(DesignationBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Employee Schemas ---
class EmployeeBase(BaseModel):
    employee_code: str = Field(..., examples=["EMP-1001"])
    first_name: str = Field(..., examples=["Arjun"])
    last_name: str = Field(..., examples=["Deshmukh"])
    email: EmailStr = Field(..., examples=["arjun.d@nexusretail.com"])
    phone: Optional[str] = Field(None, examples=["+91 98200 11223"])
    department_id: Optional[uuid.UUID] = None
    designation_id: Optional[uuid.UUID] = None
    date_of_joining: date = Field(..., examples=["2024-01-15"])
    status: str = Field(default="ACTIVE", examples=["ACTIVE"])


class EmployeeCreate(EmployeeBase):
    user_id: Optional[uuid.UUID] = None


class EmployeeResponse(EmployeeBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Attendance Schemas ---
class AttendanceCreate(BaseModel):
    employee_id: uuid.UUID
    attendance_date: date
    status: str = Field(default="PRESENT", examples=["PRESENT"])  # PRESENT, ABSENT, HALF_DAY, ON_LEAVE
    check_in: Optional[time] = None
    check_out: Optional[time] = None


class AttendanceResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    attendance_date: date
    status: str
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Leave Application Schemas ---
class LeaveApplicationCreate(BaseModel):
    employee_id: uuid.UUID
    leave_type: str = Field(default="CASUAL", examples=["CASUAL"])
    start_date: date
    end_date: date
    total_days: Decimal = Field(..., examples=[Decimal("2.0")])
    reason: str = Field(..., examples=["Family event"])


class LeaveApplicationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    leave_type: str
    start_date: date
    end_date: date
    total_days: Decimal
    reason: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str = Field(..., examples=["Warehouse Automation v2"])
    code: str = Field(..., examples=["PRJ-AUTO-02"])
    customer_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    status: str = Field(default="PLANNING", examples=["ACTIVE"])
    budget: Decimal = Field(default=Decimal("0.00"), examples=[Decimal("1500000.00")])
    start_date: date = Field(..., examples=["2026-06-01"])
    end_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    spent_amount: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Task Schemas ---
class TaskBase(BaseModel):
    project_id: uuid.UUID
    title: str = Field(..., examples=["Design Conveyor Controller Schematic"])
    description: Optional[str] = None
    status: str = Field(default="TODO", examples=["IN_PROGRESS"])  # TODO, IN_PROGRESS, REVIEW, DONE
    priority: str = Field(default="MEDIUM", examples=["HIGH"])
    assigned_to_id: Optional[uuid.UUID] = None
    due_date: Optional[date] = None
    estimated_hours: Decimal = Field(default=Decimal("0.00"))


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    actual_hours: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Timesheet Schemas ---
class TimesheetCreate(BaseModel):
    employee_id: uuid.UUID
    project_id: uuid.UUID
    task_id: Optional[uuid.UUID] = None
    work_date: date
    hours: Decimal = Field(..., gt=0, examples=[Decimal("7.50")])
    activity_description: str = Field(..., examples=["PLC firmware logic implementation"])
    is_billable: bool = True


class TimesheetResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    project_id: uuid.UUID
    task_id: Optional[uuid.UUID] = None
    work_date: date
    hours: Decimal
    activity_description: str
    is_billable: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- AI Overdue Task / Project Summary ---
class OverdueTaskAlertItem(BaseModel):
    task_id: uuid.UUID
    project_id: uuid.UUID
    project_name: str
    title: str
    due_date: date
    days_overdue: int
    assigned_to_email: Optional[str] = None
    priority: str
