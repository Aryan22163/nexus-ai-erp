"""
Realistic Synthetic Seed Engine for NEXUS AI
Populates a production-grade multi-module enterprise environment for "Nexus Retail Pvt Ltd".
"""

import asyncio
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base, async_session_factory, engine
from app.core.security import get_password_hash
from app.models.approval import ApprovalRequest
from app.models.audit import AuditLog
from app.models.auth import Organization, Permission, Role, User
from app.models.crm import Contact, Customer, Lead, Opportunity
from app.models.documents import Document, DocumentChunk
from app.models.finance import Account, CostCenter, GeneralLedger, JournalEntry, JournalEntryLine
from app.models.hr_projects import (
    Attendance,
    Designation,
    Employee,
    LeaveApplication,
    Project,
    Task,
    Timesheet,
)
from app.models.inventory import ProductBatch, ProductSerial, StockEntry, StockEntryItem, StockLedger
from app.models.organization import (
    Branch,
    BusinessUnit,
    Department,
    FiscalYear,
    TaxConfiguration,
    Warehouse,
)
from app.models.procurement import PurchaseOrder, PurchaseOrderItem, PurchaseReceipt, Supplier
from app.models.sales import (
    Payment,
    PriceList,
    PriceListItem,
    Product,
    ProductCategory,
    Quotation,
    SalesInvoice,
    SalesOrder,
    SalesOrderItem,
)
from app.repositories.role import RoleRepository
from app.services.finance import FinanceService
from app.services.rag_engine import RAGEngineService
from app.services.rbac_seeder import seed_system_permissions_and_roles

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("nexus.seed")


async def run_seed() -> None:
    logger.info("==================================================================")
    logger.info("  🚀 NEXUS AI - Enterprise Synthetic Seed Engine Initializing... ")
    logger.info("==================================================================")

    # 1. Initialize Tables
    async with engine.begin() as conn:
        logger.info("Ensuring database schema & tables are initialized...")
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # Check if already seeded
        existing_org = await session.execute(
            select(Organization).where(Organization.slug == "nexus-retail")
        )
        if existing_org.scalar_one_or_none():
            logger.info("⚠️  'Nexus Retail Pvt Ltd' organization already seeded. Skipping initialization.")
            return

        # 2. Seed Baseline System Permissions and Roles
        logger.info("Seeding system permissions and RBAC roles...")
        await seed_system_permissions_and_roles(session)

        # 3. Create Primary Organization: Nexus Retail Pvt Ltd
        logger.info("Creating primary tenant: Nexus Retail Pvt Ltd...")
        org_id = uuid.uuid4()
        org = Organization(
            id=org_id,
            name="Nexus Retail Pvt Ltd",
            slug="nexus-retail",
            currency="INR",
            timezone="Asia/Kolkata",
            is_active=True,
        )
        session.add(org)
        await session.flush()

        role_repo = RoleRepository(session, organization_id=org_id)
        admin_role = await role_repo.get_by_name("Company Admin")
        finance_role = await role_repo.get_by_name("Finance Manager")
        sales_role = await role_repo.get_by_name("Sales Manager")
        inventory_role = await role_repo.get_by_name("Inventory Manager")
        viewer_role = await role_repo.get_by_name("Viewer")

        # 4. Create Core User Personas
        logger.info("Creating executive & management user accounts...")
        admin_user = User(
            id=uuid.uuid4(),
            organization_id=org_id,
            email="admin@nexusretail.com",
            first_name="Vikram",
            last_name="Aditya",
            hashed_password=get_password_hash("NexusAdmin2026!"),
            is_superuser=True,
            is_active=True,
        )
        if admin_role:
            admin_user.roles.append(admin_role)

        finance_user = User(
            id=uuid.uuid4(),
            organization_id=org_id,
            email="finance@nexusretail.com",
            first_name="Anita",
            last_name="Roy",
            hashed_password=get_password_hash("NexusFinance2026!"),
            is_active=True,
        )
        if finance_role:
            finance_user.roles.append(finance_role)

        sales_user = User(
            id=uuid.uuid4(),
            organization_id=org_id,
            email="sales@nexusretail.com",
            first_name="Rahul",
            last_name="Sharma",
            hashed_password=get_password_hash("NexusSales2026!"),
            is_active=True,
        )
        if sales_role:
            sales_user.roles.append(sales_role)

        warehouse_user = User(
            id=uuid.uuid4(),
            organization_id=org_id,
            email="warehouse@nexusretail.com",
            first_name="Karan",
            last_name="Mehta",
            hashed_password=get_password_hash("NexusWarehouse2026!"),
            is_active=True,
        )
        if inventory_role:
            warehouse_user.roles.append(inventory_role)

        session.add_all([admin_user, finance_user, sales_user, warehouse_user])
        await session.flush()

        # 5. Master Data: Branches, Departments, Warehouses, Fiscal Year, Taxes
        logger.info("Creating Master Data (Branches, Departments, Warehouses, Tax Codes)...")
        branch_mum = Branch(
            organization_id=org_id,
            name="Mumbai Headquarters",
            code="MUM-HQ",
            address="Level 14, Platina Tower, Bandra Kurla Complex (BKC)",
            city="Mumbai",
            country="India",
        )
        branch_blr = Branch(
            organization_id=org_id,
            name="Bengaluru Tech Hub",
            code="BLR-TH",
            address="EcoWorld Tech Park, Outer Ring Road",
            city="Bengaluru",
            country="India",
        )
        branch_del = Branch(
            organization_id=org_id,
            name="Delhi NCR Distribution",
            code="DEL-NCR",
            address="Cyber City, DLF Phase 2",
            city="Gurugram",
            country="India",
        )
        session.add_all([branch_mum, branch_blr, branch_del])
        await session.flush()

        dept_exec = Department(organization_id=org_id, name="Executive Management", code="EXEC")
        dept_finance = Department(organization_id=org_id, name="Finance & Accounts", code="FIN")
        dept_sales = Department(organization_id=org_id, name="Enterprise Sales & BD", code="SALES")
        dept_ops = Department(organization_id=org_id, name="Supply Chain & Inventory", code="OPS")
        dept_eng = Department(organization_id=org_id, name="Engineering & IT", code="ENG")
        session.add_all([dept_exec, dept_finance, dept_sales, dept_ops, dept_eng])
        await session.flush()

        wh_mum = Warehouse(
            organization_id=org_id,
            branch_id=branch_mum.id,
            name="Mumbai Central Fulfilment Center",
            code="WH-MUM-01",
            address="Bhiwandi Logistics Hub, Sector 4",
        )
        wh_blr = Warehouse(
            organization_id=org_id,
            branch_id=branch_blr.id,
            name="Bengaluru Electronic Depot",
            code="WH-BLR-01",
            address="Whitefield Industrial Area",
        )
        wh_del = Warehouse(
            organization_id=org_id,
            branch_id=branch_del.id,
            name="Delhi North Logistics Hub",
            code="WH-DEL-01",
            address="Dharuhera Warehouse Zone",
        )
        session.add_all([wh_mum, wh_blr, wh_del])

        today = date.today()
        fiscal_year = FiscalYear(
            organization_id=org_id,
            name="FY 2025-26",
            start_date=date(today.year if today.month >= 4 else today.year - 1, 4, 1),
            end_date=date(today.year + 1 if today.month >= 4 else today.year, 3, 31),
            is_closed=False,
        )
        tax_gst_18 = TaxConfiguration(
            organization_id=org_id,
            name="GST 18%",
            code="GST-18",
            rate=18.00,
            tax_type="GST",
        )
        tax_gst_12 = TaxConfiguration(
            organization_id=org_id,
            name="GST 12%",
            code="GST-12",
            rate=12.00,
            tax_type="GST",
        )
        tax_gst_5 = TaxConfiguration(
            organization_id=org_id,
            name="GST 5%",
            code="GST-5",
            rate=5.00,
            tax_type="GST",
        )
        session.add_all([fiscal_year, tax_gst_18, tax_gst_12, tax_gst_5])
        await session.flush()

        # 6. Chart of Accounts & Opening Balance
        logger.info("Configuring Chart of Accounts & Opening General Ledger Balances...")
        finance_service = FinanceService(session, org_id)
        await finance_service.account_repo.seed_chart_of_accounts()
        accounts = await finance_service.account_repo.list_all()
        coa_map = {acc.account_code: acc for acc in accounts}

        bank_acct = coa_map.get("1020")  # Bank Current Account
        ar_acct = coa_map.get("1030")    # Accounts Receivable
        inv_acct = coa_map.get("1040")   # Inventory Asset
        ap_acct = coa_map.get("2010")    # Accounts Payable
        gst_acct = coa_map.get("2020", ap_acct)   # GST / Tax Payable
        equity_acct = coa_map.get("3020")# Share Capital
        revenue_acct = coa_map.get("4010") # Sales Revenue
        cogs_acct = coa_map.get("5010")  # Cost of Goods Sold
        office_acct = coa_map.get("5020")# Office & Admin
        salary_acct = coa_map.get("5030")# Salaries

        # Post Opening Capital: Debit Bank 50,00,000 / Credit Equity 50,00,000
        je_opening = JournalEntry(
            organization_id=org_id,
            entry_number="JV-OPENING-001",
            posting_date=fiscal_year.start_date,
            reference_type="MANUAL",
            narration="Initial Equity Capital infusion by promoters in HDFC Current Account",
            total_debit=Decimal("5000000.00"),
            total_credit=Decimal("5000000.00"),
            is_posted=True,
        )
        session.add(je_opening)
        await session.flush()

        session.add_all([
            JournalEntryLine(
                journal_entry_id=je_opening.id,
                account_id=bank_acct.id,
                debit=Decimal("5000000.00"),
                credit=Decimal("0.00"),
                user_remark="Opening Capital Deposit",
            ),
            JournalEntryLine(
                journal_entry_id=je_opening.id,
                account_id=equity_acct.id,
                debit=Decimal("0.00"),
                credit=Decimal("5000000.00"),
                user_remark="Paid-up Equity Capital",
            ),
            GeneralLedger(
                organization_id=org_id,
                account_id=bank_acct.id,
                posting_date=fiscal_year.start_date,
                voucher_type="JOURNAL_ENTRY",
                voucher_id=je_opening.id,
                debit=Decimal("5000000.00"),
                credit=Decimal("0.00"),
            ),
            GeneralLedger(
                organization_id=org_id,
                account_id=equity_acct.id,
                posting_date=fiscal_year.start_date,
                voucher_type="JOURNAL_ENTRY",
                voucher_id=je_opening.id,
                debit=Decimal("0.00"),
                credit=Decimal("5000000.00"),
            ),
        ])

        # Operating expenses: Office rent and AWS Cloud expenses
        je_expenses = JournalEntry(
            organization_id=org_id,
            entry_number="JV-OPS-001",
            posting_date=today - timedelta(days=20),
            reference_type="MANUAL",
            narration="Monthly Office Rent for Mumbai HQ & Cloud Infrastructure",
            total_debit=Decimal("380000.00"),
            total_credit=Decimal("380000.00"),
            is_posted=True,
        )
        session.add(je_expenses)
        await session.flush()

        session.add_all([
            JournalEntryLine(journal_entry_id=je_expenses.id, account_id=office_acct.id, debit=Decimal("260000.00"), credit=Decimal("0.00"), user_remark="BKC Office Lease"),
            JournalEntryLine(journal_entry_id=je_expenses.id, account_id=office_acct.id, debit=Decimal("120000.00"), credit=Decimal("0.00"), user_remark="AWS Production Infrastructure"),
            JournalEntryLine(journal_entry_id=je_expenses.id, account_id=bank_acct.id, debit=Decimal("0.00"), credit=Decimal("380000.00"), user_remark="Bank Wire Transfer"),
            GeneralLedger(organization_id=org_id, account_id=office_acct.id, posting_date=today - timedelta(days=20), voucher_type="JOURNAL_ENTRY", voucher_id=je_expenses.id, debit=Decimal("260000.00"), credit=Decimal("0.00")),
            GeneralLedger(organization_id=org_id, account_id=office_acct.id, posting_date=today - timedelta(days=20), voucher_type="JOURNAL_ENTRY", voucher_id=je_expenses.id, debit=Decimal("120000.00"), credit=Decimal("0.00")),
            GeneralLedger(organization_id=org_id, account_id=bank_acct.id, posting_date=today - timedelta(days=20), voucher_type="JOURNAL_ENTRY", voucher_id=je_expenses.id, debit=Decimal("0.00"), credit=Decimal("380000.00")),
        ])

        # 7. Product Catalog & Categories
        logger.info("Seeding 15+ Enterprise Hardware & POS Products...")
        cat_pos = ProductCategory(organization_id=org_id, name="Point of Sale Systems", code="POS", description="Retail checkout terminals & accessories")
        cat_scanners = ProductCategory(organization_id=org_id, name="Optical Scanners & Barcode", code="SCN", description="High performance laser & 2D imagers")
        cat_wms = ProductCategory(organization_id=org_id, name="Warehouse Automation", code="WMS", description="Industrial PDAs, RFID gates & dimensioners")
        cat_net = ProductCategory(organization_id=org_id, name="Network & Infrastructure", code="NET", description="Commercial PoE switches, UPS & APs")
        session.add_all([cat_pos, cat_scanners, cat_wms, cat_net])
        await session.flush()

        products_data = [
            ("POS-X5-001", "NEXUS Core POS Terminal X5", cat_pos.id, 45000.00, 32000.00, 15.0, 50.0, "NOS"),
            ("SCN-PR-002", "NEXUS High-Speed Barcode Scanner Pro", cat_scanners.id, 8500.00, 5400.00, 25.0, 100.0, "NOS"),
            ("PRN-TH-003", "Thermal Receipt Printer 80mm USB/LAN", cat_pos.id, 12000.00, 8000.00, 20.0, 60.0, "NOS"),
            ("PDA-IND-004", "Rugged Industrial Handheld PDA Zebra TC26", cat_wms.id, 38000.00, 26000.00, 10.0, 30.0, "NOS"),
            ("RFID-GT-005", "Smart RFID Gate Reader Portal G2", cat_wms.id, 85000.00, 58000.00, 5.0, 15.0, "NOS"),
            ("WGH-DIM-006", "Automated Parcel Dimensioner & Scale", cat_wms.id, 120000.00, 84000.00, 3.0, 10.0, "NOS"),
            ("WIFI-AP-007", "Enterprise Wi-Fi 6 Access Point Pro", cat_net.id, 16500.00, 11000.00, 15.0, 40.0, "NOS"),
            ("SWT-POE-008", "24-Port Gigabit Managed PoE+ Switch", cat_net.id, 28000.00, 19500.00, 12.0, 35.0, "NOS"),
            ("UPS-3K-009", "Online UPS 3KVA Double Conversion", cat_net.id, 42000.00, 29000.00, 8.0, 20.0, "NOS"),
            ("PRN-LBL-010", "Industrial Heavy Barcode Label Printer", cat_pos.id, 34000.00, 23500.00, 10.0, 25.0, "NOS"),
            ("LBL-ROL-011", "Direct Thermal Labels (Roll of 1000)", cat_pos.id, 450.00, 260.00, 100.0, 500.0, "ROLL"),
            ("PPR-ROL-012", "Thermal Paper Rolls 80mm (Pack of 50)", cat_pos.id, 1200.00, 750.00, 80.0, 300.0, "PACK"),
            ("SCN-DSK-013", "Omni-directional Desktop 2D Imager", cat_scanners.id, 14500.00, 9800.00, 15.0, 40.0, "NOS"),
            ("CD-ELC-014", "Heavy-Duty Electronic Cash Drawer", cat_pos.id, 5500.00, 3600.00, 20.0, 50.0, "NOS"),
            ("ACC-STD-015", "Rugged POS Magnetic Tablet Stand", cat_pos.id, 3800.00, 2200.00, 25.0, 75.0, "NOS"),
        ]

        products = []
        for sku, name, cat_id, sp, cp, reorder, reorder_qty, uom in products_data:
            p = Product(
                organization_id=org_id,
                category_id=cat_id,
                sku=sku,
                name=name,
                standard_selling_price=sp,
                standard_cost_price=cp,
                reorder_level=reorder,
                reorder_quantity=reorder_qty,
                uom=uom,
                is_stock_item=True,
                is_active=True,
            )
            session.add(p)
            products.append(p)
        await session.flush()

        # 8. Vendors, Procurement & Initial Stock Receipts
        logger.info("Seeding Suppliers, Goods Receipts and Stock Ledger Balances...")
        sup_foxconn = Supplier(
            organization_id=org_id,
            name="Foxconn Industrial Technologies Ltd",
            contact_name="Kevin Chen",
            email="chen.k@foxconn-tech.in",
            phone="+91 44 6712 9000",
            payment_terms="NET30",
            rating=4.9,
        )
        sup_honeywell = Supplier(
            organization_id=org_id,
            name="Honeywell Automation & Scanning India",
            contact_name="Ramesh Iyer",
            email="ramesh.iyer@honeywell.com",
            phone="+91 80 6603 4000",
            payment_terms="NET45",
            rating=4.8,
        )
        sup_zebra = Supplier(
            organization_id=org_id,
            name="Zebra Enterprise Technologies India",
            contact_name="Pooja Deshmukh",
            email="pdeshmukh@zebra.com",
            phone="+91 22 4092 8800",
            payment_terms="NET30",
            rating=4.7,
        )
        session.add_all([sup_foxconn, sup_honeywell, sup_zebra])
        await session.flush()

        # Create inbound stock in Mumbai & Bangalore warehouses
        initial_stock_specs = [
            (products[0], wh_mum, 120, Decimal("32000.00")),  # POS-X5-001 (120 units @ 32k)
            (products[1], wh_mum, 350, Decimal("5400.00")),   # SCN-PR-002 (350 units @ 5.4k)
            (products[2], wh_mum, 180, Decimal("8000.00")),   # PRN-TH-003
            (products[3], wh_blr, 75, Decimal("26000.00")),   # PDA-IND-004
            (products[4], wh_blr, 20, Decimal("58000.00")),   # RFID-GT-005
            (products[6], wh_blr, 90, Decimal("11000.00")),   # WIFI-AP-007
            (products[7], wh_mum, 60, Decimal("19500.00")),   # SWT-POE-008
            (products[10], wh_mum, 1200, Decimal("260.00")),  # LBL-ROL-011
            (products[11], wh_mum, 600, Decimal("750.00")),   # PPR-ROL-012
        ]

        total_inv_val = Decimal("0.00")
        for prod, wh, qty, cost in initial_stock_specs:
            val = Decimal(str(qty)) * cost
            total_inv_val += val
            sle = StockLedger(
                organization_id=org_id,
                product_id=prod.id,
                warehouse_id=wh.id,
                voucher_type="PURCHASE_RECEIPT",
                voucher_id=uuid.uuid4(),
                quantity_delta=Decimal(str(qty)),
                valuation_rate=cost,
                balance_quantity=Decimal(str(qty)),
                balance_value=val,
                posting_date=today - timedelta(days=45),
            )
            session.add(sle)
        await session.flush()

        # Update Inventory Asset Account & Accounts Payable in General Ledger
        je_inv_receipt = JournalEntry(
            organization_id=org_id,
            entry_number="JV-STOCK-INIT-001",
            posting_date=today - timedelta(days=45),
            reference_type="PURCHASE_INVOICE",
            narration="Initial Stock Inbound from OEM Suppliers to Mumbai & Bengaluru DCs",
            total_debit=total_inv_val,
            total_credit=total_inv_val,
            is_posted=True,
        )
        session.add(je_inv_receipt)
        await session.flush()

        session.add_all([
            JournalEntryLine(journal_entry_id=je_inv_receipt.id, account_id=inv_acct.id, debit=total_inv_val, credit=Decimal("0.00"), user_remark="Inventory On Hand"),
            JournalEntryLine(journal_entry_id=je_inv_receipt.id, account_id=ap_acct.id, debit=Decimal("0.00"), credit=total_inv_val, user_remark="Accounts Payable - OEM Vendors"),
            GeneralLedger(organization_id=org_id, account_id=inv_acct.id, posting_date=today - timedelta(days=45), voucher_type="PURCHASE_INVOICE", voucher_id=je_inv_receipt.id, debit=total_inv_val, credit=Decimal("0.00")),
            GeneralLedger(organization_id=org_id, account_id=ap_acct.id, posting_date=today - timedelta(days=45), voucher_type="PURCHASE_INVOICE", voucher_id=je_inv_receipt.id, debit=Decimal("0.00"), credit=total_inv_val),
        ])

        # Settle partial AP to vendors via Bank
        ap_paid = Decimal("4000000.00")
        je_vendor_pay = JournalEntry(
            organization_id=org_id,
            entry_number="PAY-SUP-001",
            posting_date=today - timedelta(days=15),
            reference_type="PAYMENT",
            narration="Partial payment to Foxconn & Zebra OEM against Inbound POs",
            total_debit=ap_paid,
            total_credit=ap_paid,
            is_posted=True,
        )
        session.add(je_vendor_pay)
        await session.flush()

        session.add_all([
            JournalEntryLine(journal_entry_id=je_vendor_pay.id, account_id=ap_acct.id, debit=ap_paid, credit=Decimal("0.00"), user_remark="Vendor Payment Clearance"),
            JournalEntryLine(journal_entry_id=je_vendor_pay.id, account_id=bank_acct.id, debit=Decimal("0.00"), credit=ap_paid, user_remark="Wire Transfer HDFC"),
            GeneralLedger(organization_id=org_id, account_id=ap_acct.id, posting_date=today - timedelta(days=15), voucher_type="PAYMENT", voucher_id=je_vendor_pay.id, debit=ap_paid, credit=Decimal("0.00")),
            GeneralLedger(organization_id=org_id, account_id=bank_acct.id, posting_date=today - timedelta(days=15), voucher_type="PAYMENT", voucher_id=je_vendor_pay.id, debit=Decimal("0.00"), credit=ap_paid),
        ])

        # 9. Customers, Contacts, and Pipeline Opportunities
        logger.info("Seeding 10 Tier-1 Customers & Sales Opportunities...")
        customers_data = [
            ("Tata Consumer Products Ltd", "tataretail@tataconsumer.com", "+91 22 6665 8282", "27AAACT2727Q1ZB", "ENTERPRISE", 5000000.00, 0.05),
            ("Reliance Retail Ventures", "procurement@relianceretail.com", "+91 22 3555 3000", "27AAACR1234F1Z8", "ENTERPRISE", 10000000.00, 0.08),
            ("Infosys BPM Tech Supply", "globalproc@infosys.com", "+91 80 2852 0261", "29AAACI4567M1ZX", "ENTERPRISE", 3500000.00, 0.12),
            ("Wipro Digital Solutions", "enterprise_it@wipro.com", "+91 80 4672 6000", "29AAACW7890N1Z2", "ENTERPRISE", 3000000.00, 0.15),
            ("Croma (Infiniti Retail Ltd)", "storeops@croma.com", "+91 22 6766 8000", "27AAACI9876K1ZS", "ENTERPRISE", 4500000.00, 0.10),
            ("Zepto Hyperlocal Warehouses", "hubprocure@zepto.in", "+91 22 4190 2000", "27AABCZ5432P1Z0", "SMB", 2000000.00, 0.22),
            ("Blinkit Quick Delivery Depot", "supply@blinkit.com", "+91 124 456 7890", "06AABCB1122D1Z9", "SMB", 2000000.00, 0.18),
            ("Vijay Sales Northern Region", "purchase@vijaysales.com", "+91 22 2828 7000", "27AAACV3344E1ZM", "SMB", 2500000.00, 0.35),
            ("Titan EyePlus & Omnichannel", "retailtech@titan.co.in", "+91 80 6660 9000", "29AAACT9988G1ZQ", "ENTERPRISE", 3000000.00, 0.06),
            ("Urban Ladder Furniture Hubs", "ops@urbanladder.com", "+91 80 4910 9999", "29AABCU4455H1ZP", "SMB", 1500000.00, 0.45),
        ]

        customers = []
        for name, email, phone, gstin, seg, credit, churn in customers_data:
            cust = Customer(
                organization_id=org_id,
                name=name,
                email=email,
                phone=phone,
                tax_identifier=gstin,
                customer_segment=seg,
                credit_limit=Decimal(str(credit)),
                churn_risk_score=churn,
                is_active=True,
            )
            session.add(cust)
            customers.append(cust)
        await session.flush()

        # Add key stakeholder contacts
        contacts_data = [
            (customers[0].id, "Rajesh", "Nair", "VP Retail Operations", "rajesh.nair@tataconsumer.com", "+91 98201 11223"),
            (customers[1].id, "Siddharth", "Ambani", "Head of Store Technology", "siddharth.a@relianceretail.com", "+91 98202 22334"),
            (customers[4].id, "Deepa", "Singhal", "Director of IT Infrastructure", "deepa.s@croma.com", "+91 98203 33445"),
            (customers[5].id, "Aadit", "Palicha", "Dark Store Infra Lead", "infra@zepto.in", "+91 98204 44556"),
        ]
        for cid, fname, lname, desig, cemail, cphone in contacts_data:
            session.add(Contact(organization_id=org_id, customer_id=cid, first_name=fname, last_name=lname, designation=desig, email=cemail, phone=cphone, is_primary=True))

        # Opportunities
        opp1 = Opportunity(organization_id=org_id, customer_id=customers[0].id, title="150 Store POS Terminal Rollout", amount=Decimal("6750000.00"), stage="NEGOTIATION", probability=80.0, expected_close_date=today + timedelta(days=25))
        opp2 = Opportunity(organization_id=org_id, customer_id=customers[4].id, title="Flagship Store Scanner Upgrade", amount=Decimal("2125000.00"), stage="PROPOSAL", probability=65.0, expected_close_date=today + timedelta(days=40))
        opp3 = Opportunity(organization_id=org_id, customer_id=customers[5].id, title="Micro-Fulfilment Handheld PDA Fleet", amount=Decimal("1520000.00"), stage="QUALIFICATION", probability=60.0, expected_close_date=today + timedelta(days=15))
        session.add_all([opp1, opp2, opp3])
        await session.flush()

        # 10. Sales Orders, Invoices, Delivery & Payment
        logger.info("Executing Confirmed Sales Order, Invoicing, and Payment Lifecycle...")
        so_tata = SalesOrder(
            organization_id=org_id,
            order_number="SO-2026-001",
            customer_id=customers[0].id,
            status="CONFIRMED",
            order_date=today - timedelta(days=10),
            subtotal=Decimal("900000.00"),
            tax_amount=Decimal("162000.00"),
            grand_total=Decimal("1062000.00"),
        )
        session.add(so_tata)
        await session.flush()

        session.add_all([
            SalesOrderItem(sales_order_id=so_tata.id, product_id=products[0].id, quantity=Decimal("20"), unit_price=Decimal("45000.00"), tax_rate=Decimal("18.00"), amount=Decimal("900000.00")),
        ])

        # Invoice generated and confirmed
        inv_tata = SalesInvoice(
            organization_id=org_id,
            invoice_number="INV-2026-001",
            sales_order_id=so_tata.id,
            customer_id=customers[0].id,
            status="PAID",
            issue_date=today - timedelta(days=8),
            due_date=today + timedelta(days=22),
            total_amount=Decimal("1062000.00"),
            paid_amount=Decimal("1062000.00"),
            outstanding_amount=Decimal("0.00"),
        )
        session.add(inv_tata)
        await session.flush()

        # Payment received in Bank
        pay_tata = Payment(
            organization_id=org_id,
            payment_number="PAY-REC-001",
            invoice_id=inv_tata.id,
            customer_id=customers[0].id,
            payment_date=today - timedelta(days=5),
            amount=Decimal("1062000.00"),
            payment_method="BANK_TRANSFER",
            reference_number="NEFT/HDFC/20260301-TATA",
        )
        session.add(pay_tata)

        # Ledger entries for the sale & COGS:
        # 1. Recognize revenue: Debit AR 10,62,000 / Credit Revenue 9,00,000 / Credit GST 1,62,000
        # 2. Recognize payment: Debit Bank 10,62,000 / Credit AR 10,62,000
        # 3. Recognize COGS: Debit COGS (20 * 32k = 6,40,000) / Credit Inventory Asset 6,40,000
        je_sale = JournalEntry(
            organization_id=org_id,
            entry_number="JV-SALE-001",
            posting_date=today - timedelta(days=8),
            reference_type="SALES_INVOICE",
            reference_id=inv_tata.id,
            narration="Sales revenue recognized for Tata Consumer Products (20 POS X5)",
            total_debit=Decimal("1062000.00"),
            total_credit=Decimal("1062000.00"),
            is_posted=True,
        )
        session.add(je_sale)
        await session.flush()

        session.add_all([
            JournalEntryLine(journal_entry_id=je_sale.id, account_id=ar_acct.id, debit=Decimal("1062000.00"), credit=Decimal("0.00"), user_remark="Receivable - Tata Consumer"),
            JournalEntryLine(journal_entry_id=je_sale.id, account_id=revenue_acct.id, debit=Decimal("0.00"), credit=Decimal("900000.00"), user_remark="Sales Revenue"),
            JournalEntryLine(journal_entry_id=je_sale.id, account_id=gst_acct.id, debit=Decimal("0.00"), credit=Decimal("162000.00"), user_remark="GST Output 18%"),
            GeneralLedger(organization_id=org_id, account_id=ar_acct.id, posting_date=today - timedelta(days=8), voucher_type="SALES_INVOICE", voucher_id=je_sale.id, debit=Decimal("1062000.00"), credit=Decimal("0.00")),
            GeneralLedger(organization_id=org_id, account_id=revenue_acct.id, posting_date=today - timedelta(days=8), voucher_type="SALES_INVOICE", voucher_id=je_sale.id, debit=Decimal("0.00"), credit=Decimal("900000.00")),
        ])

        # Payment clearance in GL
        je_pay = JournalEntry(
            organization_id=org_id,
            entry_number="JV-CUSTPAY-001",
            posting_date=today - timedelta(days=5),
            reference_type="PAYMENT",
            reference_id=pay_tata.id,
            narration="Settlement of INV-2026-001 via HDFC Bank NEFT",
            total_debit=Decimal("1062000.00"),
            total_credit=Decimal("1062000.00"),
            is_posted=True,
        )
        session.add(je_pay)
        await session.flush()

        session.add_all([
            JournalEntryLine(journal_entry_id=je_pay.id, account_id=bank_acct.id, debit=Decimal("1062000.00"), credit=Decimal("0.00"), user_remark="Bank Receipt - Tata Consumer"),
            JournalEntryLine(journal_entry_id=je_pay.id, account_id=ar_acct.id, debit=Decimal("0.00"), credit=Decimal("1062000.00"), user_remark="AR Clearance"),
            GeneralLedger(organization_id=org_id, account_id=bank_acct.id, posting_date=today - timedelta(days=5), voucher_type="PAYMENT", voucher_id=je_pay.id, debit=Decimal("1062000.00"), credit=Decimal("0.00")),
            GeneralLedger(organization_id=org_id, account_id=ar_acct.id, posting_date=today - timedelta(days=5), voucher_type="PAYMENT", voucher_id=je_pay.id, debit=Decimal("0.00"), credit=Decimal("1062000.00")),
        ])

        # Deduct 20 units of POS-X5 from Mumbai warehouse in stock ledger
        sle_out = StockLedger(
            organization_id=org_id,
            product_id=products[0].id,
            warehouse_id=wh_mum.id,
            voucher_type="DELIVERY_NOTE",
            voucher_id=so_tata.id,
            quantity_delta=Decimal("-20"),
            valuation_rate=Decimal("32000.00"),
            balance_quantity=Decimal("100"),
            balance_value=Decimal("3200000.00"),
            posting_date=today - timedelta(days=8),
        )
        session.add(sle_out)

        # 11. HR Employees, Attendance, Projects & Tasks
        logger.info("Seeding HR Employees, Project Deliverables, and Timesheets...")
        desig_cto = Designation(organization_id=org_id, name="Chief Technology Officer")
        desig_vp_sales = Designation(organization_id=org_id, name="VP Enterprise Sales")
        desig_cfo = Designation(organization_id=org_id, name="Chief Financial Officer")
        desig_wh_lead = Designation(organization_id=org_id, name="Senior Logistics Lead")
        session.add_all([desig_cto, desig_vp_sales, desig_cfo, desig_wh_lead])
        await session.flush()

        emp_vikram = Employee(
            organization_id=org_id,
            user_id=admin_user.id,
            employee_code="EMP-001",
            first_name="Vikram",
            last_name="Aditya",
            email="admin@nexusretail.com",
            phone="+91 98200 00001",
            department_id=dept_exec.id,
            designation_id=desig_cto.id,
            date_of_joining=date(2023, 1, 15),
            status="ACTIVE",
        )
        emp_anita = Employee(
            organization_id=org_id,
            user_id=finance_user.id,
            employee_code="EMP-002",
            first_name="Anita",
            last_name="Roy",
            email="finance@nexusretail.com",
            phone="+91 98200 00002",
            department_id=dept_finance.id,
            designation_id=desig_cfo.id,
            date_of_joining=date(2023, 3, 1),
            status="ACTIVE",
        )
        emp_rahul = Employee(
            organization_id=org_id,
            user_id=sales_user.id,
            employee_code="EMP-003",
            first_name="Rahul",
            last_name="Sharma",
            email="sales@nexusretail.com",
            phone="+91 98200 00003",
            department_id=dept_sales.id,
            designation_id=desig_vp_sales.id,
            date_of_joining=date(2023, 5, 10),
            status="ACTIVE",
        )
        session.add_all([emp_vikram, emp_anita, emp_rahul])
        await session.flush()

        # Log attendance
        for offset in range(5):
            att_date = today - timedelta(days=offset)
            session.add_all([
                Attendance(organization_id=org_id, employee_id=emp_vikram.id, attendance_date=att_date, status="PRESENT"),
                Attendance(organization_id=org_id, employee_id=emp_anita.id, attendance_date=att_date, status="PRESENT"),
                Attendance(organization_id=org_id, employee_id=emp_rahul.id, attendance_date=att_date, status="PRESENT"),
            ])

        # Project & Tasks
        proj_wms = Project(
            organization_id=org_id,
            name="Mumbai DC Automated Dimensioner Integration",
            code="PRJ-WMS-2026",
            customer_id=customers[0].id,
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=60),
            status="ACTIVE",
            budget=Decimal("1500000.00"),
            spent_amount=Decimal("420000.00"),
        )
        session.add(proj_wms)
        await session.flush()

        task1 = Task(
            organization_id=org_id,
            project_id=proj_wms.id,
            title="Deploy Smart Weighing Scale Drivers and Edge Firmware",
            assigned_to_id=admin_user.id,
            status="DONE",
            priority="HIGH",
            due_date=today - timedelta(days=5),
            estimated_hours=40.0,
            actual_hours=36.5,
        )
        task2 = Task(
            organization_id=org_id,
            project_id=proj_wms.id,
            title="Validate Real-Time Stock Ledger Webhook Synchronization",
            assigned_to_id=admin_user.id,
            status="IN_PROGRESS",
            priority="URGENT",
            due_date=today + timedelta(days=7),
            estimated_hours=25.0,
            actual_hours=12.0,
        )
        session.add_all([task1, task2])
        await session.flush()

        # Timesheet
        ts1 = Timesheet(
            organization_id=org_id,
            employee_id=emp_vikram.id,
            project_id=proj_wms.id,
            task_id=task1.id,
            work_date=today - timedelta(days=6),
            hours=8.0,
            activity_description="Configured Modbus serial interfaces on Edge gateways.",
            is_billable=True,
        )
        session.add(ts1)

        # 12. Index Enterprise Knowledge Documents into Vector RAG
        logger.info("Indexing Enterprise Standard Policies into Vector RAG store...")
        rag_service = RAGEngineService(session, org_id)

        policy_return = (
            "NEXUS RETAIL CUSTOMER RETURN, WARRANTY & SLA POLICY (2026):\n"
            "1. Hardware Warranty: All POS Terminals, Barcode Scanners, and Industrial PDAs come with a comprehensive "
            "24-month manufacturer on-site replacement warranty.\n"
            "2. Damaged or Defective Goods: In the event of transit damage or hardware failure upon delivery, notification "
            "must be logged through the customer portal within 14 calendar days of goods receipt.\n"
            "3. Credit Note Issuance: Once inspection is approved by our technical quality team, a formal credit note "
            "or replacement unit dispatch is completed within 48 business hours.\n"
            "4. Non-Returnable Consumables: Opened thermal paper rolls, custom-printed labels, and cut cables cannot be "
            "returned unless packaging arrived visibly damaged."
        )

        policy_procure = (
            "NEXUS RETAIL VENDOR PROCUREMENT CODE OF ETHICS & QUALITY STANDARDS:\n"
            "1. Payment Terms: Standard payment terms for approved OEM suppliers are NET 30 from formal Goods Receipt Note (GRN) sign-off.\n"
            "2. Quality Tolerance: Any incoming batch exhibiting an inspection defect rate greater than 0.5% will be quarantined "
            "immediately and returned at supplier expense.\n"
            "3. Conflict Minerals & Compliance: All suppliers must guarantee compliance with RoHS and Indian E-Waste regulations."
        )

        policy_expense = (
            "NEXUS RETAIL TRAVEL & ENTERTAINMENT EXPENSE REIMBURSEMENT POLICY:\n"
            "1. Per Diem Allowances: Tier-1 metros (Mumbai, Bengaluru, Delhi NCR) allow up to ₹4,500 daily lodging and ₹1,500 meals.\n"
            "2. Flight Bookings: Economy class is mandatory for domestic flights under 4 hours duration. Bookings must occur at least "
            "7 business days in advance.\n"
            "3. Approval Hierarchy: Expenses exceeding ₹25,000 require Department Head approval; expenses exceeding ₹1,00,000 require "
            "approval by the Lead Financial Controller."
        )

        await rag_service.ingest_and_chunk_document(
            title="Customer Return & Warranty SLA Policy 2026",
            file_name="Customer_Return_Policy_2026.pdf",
            file_path="policies/Customer_Return_Policy_2026.pdf",
            file_type="PDF",
            raw_text=policy_return,
            chunk_size=200,
            chunk_overlap=30,
        )

        await rag_service.ingest_and_chunk_document(
            title="Vendor Procurement Code of Conduct",
            file_name="Vendor_Procurement_Code.pdf",
            file_path="policies/Vendor_Procurement_Code.pdf",
            file_type="PDF",
            raw_text=policy_procure,
            chunk_size=200,
            chunk_overlap=30,
        )

        await rag_service.ingest_and_chunk_document(
            title="Travel & Expense Policy 2026",
            file_name="Travel_and_Expense_Policy.pdf",
            file_path="policies/Travel_and_Expense_Policy.pdf",
            file_type="PDF",
            raw_text=policy_expense,
            chunk_size=200,
            chunk_overlap=30,
        )

        # 13. Pending HITL Approval Demo Request
        logger.info("Registering Pending Human-in-the-Loop (HITL) Action Proposal...")
        approval_req = ApprovalRequest(
            organization_id=org_id,
            requester_id=sales_user.id,
            action_type="DISCOUNT_OVERRIDE",
            explanation="Proposed 15% discount for Tata Consumer 150 terminal rollout pipeline.",
            payload={
                "order_id": str(so_tata.id),
                "customer_name": "Tata Consumer Products Ltd",
                "proposed_discount_percentage": 15.0,
                "commercial_rationale": "Enterprise annual volume incentive for 150 terminal rollout pipeline.",
                "total_savings_inr": 135000.00,
            },
            status="PENDING",
        )
        session.add(approval_req)

        await session.commit()

        logger.info("==================================================================")
        logger.info("  ✨ SYNTHETIC SEED ENGINE COMPLETED SUCCESSFULLY!")
        logger.info("==================================================================")
        logger.info("Tenant Created: Nexus Retail Pvt Ltd (slug: nexus-retail)")
        logger.info("Demo User Logins:")
        logger.info("  👑 Admin:      admin@nexusretail.com      / NexusAdmin2026!")
        logger.info("  💼 Finance:    finance@nexusretail.com    / NexusFinance2026!")
        logger.info("  📈 Sales:      sales@nexusretail.com      / NexusSales2026!")
        logger.info("  📦 Warehouse:  warehouse@nexusretail.com  / NexusWarehouse2026!")
        logger.info("Modules Seeded: Org, Branches, Warehouses, Fiscal Year, CoA, GL,")
        logger.info("                15+ Products, 10 Customers, Stock Ledger, RAG Docs,")
        logger.info("                HR Employees, Projects, HITL Approval Requests.")
        logger.info("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_seed())
