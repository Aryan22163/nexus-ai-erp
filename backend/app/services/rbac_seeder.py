from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.auth import Permission, Role
from app.repositories.role import RoleRepository

# Standard enterprise permissions
DEFAULT_PERMISSIONS: List[Dict[str, str]] = [
    # Organization
    {"code": "organization.read", "module": "organization", "description": "View company settings and structure"},
    {"code": "organization.update", "module": "organization", "description": "Update company settings"},
    # Users & Roles
    {"code": "users.read", "module": "users", "description": "View company users and roles"},
    {"code": "users.create", "module": "users", "description": "Invite or create company users"},
    {"code": "users.update", "module": "users", "description": "Update company user accounts and permissions"},
    {"code": "users.delete", "module": "users", "description": "Deactivate or delete users"},
    # CRM
    {"code": "crm.read", "module": "crm", "description": "View leads, opportunities, and customers"},
    {"code": "crm.create", "module": "crm", "description": "Create leads and opportunities"},
    {"code": "crm.update", "module": "crm", "description": "Update leads and sales pipelines"},
    {"code": "crm.delete", "module": "crm", "description": "Delete CRM records"},
    # Sales
    {"code": "sales.read", "module": "sales", "description": "View quotations, sales orders, and invoices"},
    {"code": "sales.create", "module": "sales", "description": "Create quotations and sales orders"},
    {"code": "sales.update", "module": "sales", "description": "Modify sales orders and update status"},
    {"code": "sales.approve", "module": "sales", "description": "Approve sales orders and special discounts"},
    # Procurement
    {"code": "procurement.read", "module": "procurement", "description": "View suppliers and purchase orders"},
    {"code": "procurement.create", "module": "procurement", "description": "Create purchase requests and orders"},
    {"code": "procurement.update", "module": "procurement", "description": "Update purchase orders and receipts"},
    {"code": "procurement.approve", "module": "procurement", "description": "Approve purchase orders"},
    # Inventory
    {"code": "inventory.read", "module": "inventory", "description": "View stock levels and warehouse ledger"},
    {"code": "inventory.create", "module": "inventory", "description": "Create stock transfers and adjustments"},
    {"code": "inventory.update", "module": "inventory", "description": "Adjust stock counts and valuation"},
    # Finance
    {"code": "finance.read", "module": "finance", "description": "View general ledger, journal entries, P&L, balance sheet"},
    {"code": "finance.create", "module": "finance", "description": "Create journal entries, invoices, and payments"},
    {"code": "finance.approve", "module": "finance", "description": "Approve financial entries and close fiscal periods"},
    # HR & Projects
    {"code": "hr.read", "module": "hr", "description": "View employees, attendance, and leave records"},
    {"code": "hr.manage", "module": "hr", "description": "Manage payroll, employee records, and leaves"},
    {"code": "projects.read", "module": "projects", "description": "View projects, tasks, and timesheets"},
    {"code": "projects.manage", "module": "projects", "description": "Create and manage projects and tasks"},
    # Documents & AI
    {"code": "documents.read", "module": "documents", "description": "View and query company knowledge documents"},
    {"code": "documents.upload", "module": "documents", "description": "Upload and index new business documents"},
    {"code": "ai.copilot", "module": "ai", "description": "Access AI Copilot and query business data"},
    {"code": "ai.execute_actions", "module": "ai", "description": "Approve and trigger AI proposed business actions"},
]

DEFAULT_ROLES: Dict[str, Dict[str, any]] = {
    "Company Admin": {
        "description": "Full administrative control over all organization data and settings",
        "permissions": "*",  # All permissions
    },
    "Finance Manager": {
        "description": "Full control of financial ledger, invoices, payments, and reporting",
        "permissions": [
            "finance.read", "finance.create", "finance.approve",
            "sales.read", "procurement.read", "inventory.read",
            "documents.read", "ai.copilot",
        ],
    },
    "Sales Manager": {
        "description": "Manage sales pipeline, quotations, orders, and sales analytics",
        "permissions": [
            "crm.read", "crm.create", "crm.update",
            "sales.read", "sales.create", "sales.update", "sales.approve",
            "inventory.read", "documents.read", "ai.copilot",
        ],
    },
    "Inventory Manager": {
        "description": "Manage warehouse operations, stock receipts, and inventory tracking",
        "permissions": [
            "inventory.read", "inventory.create", "inventory.update",
            "procurement.read", "sales.read", "documents.read", "ai.copilot",
        ],
    },
    "Viewer": {
        "description": "Read-only access across core operational reports",
        "permissions": [
            "organization.read", "sales.read", "procurement.read", "inventory.read",
            "finance.read", "projects.read", "documents.read",
        ],
    },
}


async def seed_system_permissions_and_roles(session: AsyncSession) -> None:
    """Ensure baseline system permissions and roles exist in the database."""
    role_repo = RoleRepository(session)
    existing_perms = {p.code: p for p in await role_repo.list_permissions()}

    # Insert missing permissions
    for p_def in DEFAULT_PERMISSIONS:
        if p_def["code"] not in existing_perms:
            perm = Permission(code=p_def["code"], module=p_def["module"], description=p_def["description"])
            session.add(perm)
            existing_perms[p_def["code"]] = perm

    await session.flush()

    # Seed system roles
    for role_name, role_info in DEFAULT_ROLES.items():
        role = await role_repo.get_by_name(role_name)
        if not role:
            if role_info["permissions"] == "*":
                assigned_perms = list(existing_perms.values())
            else:
                assigned_perms = [
                    existing_perms[code] for code in role_info["permissions"] if code in existing_perms
                ]
            await role_repo.create_role(
                name=role_name,
                description=role_info["description"],
                permissions=assigned_perms,
                is_system=True,
            )
