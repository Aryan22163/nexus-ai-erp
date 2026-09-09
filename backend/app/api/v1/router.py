from fastapi import APIRouter
from app.api.v1.endpoints import (
    ai,
    approvals,
    auth,
    crm,
    dashboard,
    documents,
    finance,
    health,
    hr_projects,
    inventory,
    ml,
    organization_masters,
    organizations,
    procurement,
    roles,
    sales,
    users,
)

api_router = APIRouter()

# Health & System Status
api_router.include_router(health.router, tags=["Health"])

# Identity, Multi-Tenancy & Access Control
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)

# Organization Hierarchy & Master Data
api_router.include_router(organization_masters.router)

# CRM & Customer 360
api_router.include_router(crm.router)

# Sales & Revenue Operations
api_router.include_router(sales.router)

# Procurement & Purchasing
api_router.include_router(procurement.router)

# Inventory & Warehouse Operations
api_router.include_router(inventory.router)

# Finance & Accounting
api_router.include_router(finance.router)

# HR & Project Management
api_router.include_router(hr_projects.router)

# Document Management & Vector RAG
api_router.include_router(documents.router)

# Executive Dashboard & Analytics
api_router.include_router(dashboard.router)

# AI Copilot & Autonomous Agents
api_router.include_router(ai.router)

# Human-in-the-Loop (HITL) Approvals
api_router.include_router(approvals.router)

# Predictive Machine Learning
api_router.include_router(ml.router)
