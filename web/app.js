/**
 * NEXUS AI - Web Application Engine
 * Pure Vanilla JavaScript Client
 */

// Global State
const API_BASE = "http://127.0.0.1:8000/api/v1";
let isApiConnected = false;

// Mock / Pre-seeded Enterprise Dataset (Nexus Retail Pvt Ltd)
const enterpriseData = {
  organization: {
    name: "Nexus Retail Pvt Ltd",
    currency: "INR",
    country: "India",
  },
  kpis: {
    revenue: "₹24,850,000",
    margin: "24.6%",
    inventory: "₹8,420,000",
    cash: "₹5,680,000",
  },
  orders: [
    { id: "SO-2026-001", customer: "Tata Consumer Products Ltd", product: "NEXUS Core POS Terminal X5", qty: 30, date: "2026-08-30", amount: "₹1,062,000", status: "CONFIRMED", paymentStatus: "PAID", invoiceNumber: "INV-2026-001" },
    { id: "SO-2026-002", customer: "Reliance Retail Ventures", product: "High-Speed Barcode Scanner Pro", qty: 150, date: "2026-09-02", amount: "₹2,450,000", status: "CONFIRMED", paymentStatus: "UNPAID", invoiceNumber: "INV-2026-002" },
    { id: "SO-2026-003", customer: "Croma (Infiniti Retail)", product: "Rugged Industrial Handheld PDA", qty: 20, date: "2026-09-05", amount: "₹890,000", status: "FULFILLED", paymentStatus: "PAID", invoiceNumber: "INV-2026-003" },
    { id: "SO-2026-004", customer: "Zepto Hyperlocal Warehouses", product: "Smart RFID Gate Reader Portal", qty: 6, date: "2026-09-07", amount: "₹540,000", status: "CONFIRMED", paymentStatus: "UNPAID", invoiceNumber: "INV-2026-004" },
  ],
  stock: [
    { sku: "POS-X5-001", name: "NEXUS Core POS Terminal X5", location: "Mumbai Central FC", qty: 100, reorder: 15, status: "Adequate", unitRate: 32000 },
    { sku: "SCN-PR-002", name: "High-Speed Barcode Scanner Pro", location: "Mumbai Central FC", qty: 350, reorder: 25, status: "Adequate", unitRate: 15000 },
    { sku: "PDA-IND-004", name: "Rugged Industrial Handheld PDA", location: "Bengaluru Tech Depot", qty: 75, reorder: 10, status: "Adequate", unitRate: 45000 },
    { sku: "RFID-GT-005", name: "Smart RFID Gate Reader Portal", location: "Bengaluru Tech Depot", qty: 20, reorder: 5, status: "Adequate", unitRate: 85000 },
    { sku: "WGH-DIM-006", name: "Automated Parcel Dimensioner Scale", location: "Delhi North Hub", qty: 4, reorder: 3, status: "Low Stock Alert", unitRate: 120000 },
    { sku: "UPS-3K-009", name: "Online UPS 3KVA Double Conversion", location: "Delhi North Hub", qty: 8, reorder: 8, status: "Reorder Required", unitRate: 28000 },
  ],
  customers: [
    { name: "Tata Consumer Products Ltd", segment: "Enterprise", contact: "Rajesh Nair (VP Ops)", credit: "₹5,000,000", churn: "5%", health: "Healthy" },
    { name: "Reliance Retail Ventures", segment: "Enterprise", contact: "Siddharth Ambani (Head Store Tech)", credit: "₹10,000,000", churn: "8%", health: "Healthy" },
    { name: "Infosys BPM Tech Supply", segment: "Enterprise", contact: "Global Procurement", credit: "₹3,500,000", churn: "12%", health: "Healthy" },
    { name: "Croma (Infiniti Retail Ltd)", segment: "Enterprise", contact: "Deepa Singhal (Director IT)", credit: "₹4,500,000", churn: "10%", health: "Healthy" },
    { name: "Zepto Hyperlocal Warehouses", segment: "SMB", contact: "Aadit Palicha (Dark Store Lead)", credit: "₹2,000,000", churn: "22%", health: "Moderate" },
    { name: "Vijay Sales Northern Region", segment: "SMB", contact: "Purchase Team", credit: "₹2,500,000", churn: "35%", health: "At Risk" },
    { name: "Titan EyePlus & Omnichannel", segment: "Enterprise", contact: "Retail Tech Lead", credit: "₹3,000,000", churn: "6%", health: "Healthy" },
  ],
  invoices: [
    { number: "INV-2026-001", customer: "Tata Consumer Products Ltd", customerEmail: "accounts.payable@tataconsumer.com", issueDate: "2026-09-01", dueDate: "2026-09-30", amount: "₹1,062,000", status: "PAID", settlementRef: "TXN-HDFC-99214" },
    { number: "INV-2026-002", customer: "Reliance Retail Ventures", customerEmail: "procurement.finance@relianceretail.com", issueDate: "2026-09-03", dueDate: "2026-10-03", amount: "₹2,450,000", status: "UNPAID" },
    { number: "INV-2026-003", customer: "Croma (Infiniti Retail Ltd)", customerEmail: "vendor.desk@croma.com", issueDate: "2026-09-05", dueDate: "2026-10-05", amount: "₹890,000", status: "PAID", settlementRef: "TXN-ICICI-88120" },
  ],
  pendingApprovals: [
    {
      id: "appr-001",
      actionType: "DISCOUNT_OVERRIDE",
      riskLevel: "HIGH RISK",
      title: "15.0% Enterprise Volume Discount Override on SO-2026-001",
      requester: "Rahul Sharma (VP Sales)",
      targetModule: "Sales & Finance Ledger",
      customer: "Tata Consumer Products Ltd",
      orderId: "SO-2026-001",
      amount: 135000,
      savings: "₹135,000.00",
      rationale: "Enterprise contract agreement for 150 terminal rollout pipeline across tier-1 regional offices.",
      affectedLedgers: "Sales Revenue & Accounts Receivable (SO-2026-001)",
      executionPlan: [
        "Apply ₹135,000 discount adjustment to Invoice INV-2026-001",
        "Post Debit to Sales Discount Expense (4020) & Credit to AR Ledger (1030)",
        "Dispatch revised tax invoice seal to client finance desk"
      ],
      status: "PENDING",
    },
    {
      id: "appr-002",
      actionType: "PURCHASE_ORDER_APPROVAL",
      riskLevel: "HIGH RISK",
      title: "Bulk Procurement & Inward Purchase Order: 50x POS-X5-001 Terminals",
      requester: "Anita Roy (CFO / Supply Chain)",
      targetModule: "Procurement & Inventory Asset",
      customer: "Honeywell Mobility Solutions India Ltd",
      orderId: "PO-2026-042",
      amount: 1250000,
      savings: "₹1,250,000.00 (Inward Capital)",
      rationale: "Prevent imminent stockout on SKU POS-X5-001 (Stock depletion horizon predicted in 20 days by ML Engine).",
      affectedLedgers: "Perpetual Inventory Asset (1040) & HDFC Bank Cash Account (1020)",
      executionPlan: [
        "Inward +50 units of POS-X5-001 into Mumbai DC Central Warehouse",
        "Capitalize +₹1,250,000 to Perpetual Inventory Asset Account",
        "Post JV-2026-042 Journal Entry and disburse vendor purchase order"
      ],
      status: "PENDING",
    }
  ],
  approvedHistory: [
    {
      id: "appr-000",
      actionType: "DISCOUNT_OVERRIDE",
      riskLevel: "MEDIUM RISK",
      title: "5.0% Volume Discount on INV-2026-003",
      requester: "Rahul Sharma (VP Sales)",
      targetModule: "Sales & Finance",
      customer: "Croma (Infiniti Retail Ltd)",
      amount: 44500,
      savings: "₹44,500.00",
      decisionBy: "Aryan Thakur (Admin)",
      decisionDate: "2026-09-08 14:32",
      status: "APPROVED",
      journalVoucher: "JV-2026-004"
    }
  ],
  projects: [
    {
      name: "Mumbai DC Automated Dimensioner Integration",
      code: "PRJ-WMS-2026",
      department: "Operations & Logistics",
      lead: "Aryan Thakur",
      priority: "HIGH",
      budget: 1500000,
      spent: 420000,
      progress: 68,
      status: "ACTIVE",
      deadline: "2026-10-15",
      description: "Deploy automated parcel dimensioners, smart weighbridges, and real-time stock ledger webhooks at Mumbai Distribution Hub.",
      tasks: [
        { title: "Deploy Smart Weighing Scale Edge Drivers", assignee: "Aryan Thakur", status: "DONE", priority: "HIGH" },
        { title: "Validate Real-Time Stock Ledger Webhook Synchronization", assignee: "Aryan Thakur", status: "IN_PROGRESS", priority: "URGENT" },
        { title: "Calibrate Volumetric Optical Sensors on Conveyor #3", assignee: "Anita Roy", status: "DONE", priority: "MEDIUM" },
        { title: "Warehouse Gateway TLS 1.3 Handshake Audit", assignee: "Rahul Sharma", status: "TODO", priority: "LOW" }
      ]
    },
    {
      name: "Real-Time Sales & Customer Churn Forecaster Engine",
      code: "PRJ-AI-2026",
      department: "AI/ML Engineering",
      lead: "Aryan Thakur",
      priority: "CRITICAL",
      budget: 1200000,
      spent: 650000,
      progress: 75,
      status: "ACTIVE",
      deadline: "2026-09-30",
      description: "Build ordinary least squares sales trend extrapolation, spending anomaly detection, and automated churn retention dispatcher.",
      tasks: [
        { title: "Train Random Forest & Gradient Boosted Sales Regressors", assignee: "Aryan Thakur", status: "DONE", priority: "HIGH" },
        { title: "Integrate Z-Score Expense Anomaly Detector", assignee: "Anita Roy", status: "DONE", priority: "MEDIUM" },
        { title: "Implement Real-time Customer Churn Dispatch System", assignee: "Aryan Thakur", status: "DONE", priority: "HIGH" },
        { title: "Deploy Local Ollama LLM Decision Agent Pipeline", assignee: "Neha Patel", status: "IN_PROGRESS", priority: "URGENT" }
      ]
    },
    {
      name: "Automated GST Multi-Currency Invoicing & Payment Gateways",
      code: "PRJ-FIN-2026",
      department: "Finance & Core",
      lead: "Anita Roy",
      priority: "HIGH",
      budget: 950000,
      spent: 380000,
      progress: 50,
      status: "IN_PROGRESS",
      deadline: "2026-11-20",
      description: "Compliance upgrade for tax invoice auto-generation, QR code embedding, custom recipient email dispatch, and settlement ledger auto-updates.",
      tasks: [
        { title: "Implement IRN QR Code Auto-Generation & Stamp", assignee: "Anita Roy", status: "DONE", priority: "HIGH" },
        { title: "Configure Razorpay / Stripe Webhook Handlers", assignee: "Rahul Sharma", status: "IN_PROGRESS", priority: "HIGH" },
        { title: "Automated Email Invoice Dispatcher with PDF Seal", assignee: "Aryan Thakur", status: "DONE", priority: "MEDIUM" },
        { title: "Multi-ledger Reconciliation Batch Cron Service", assignee: "Anita Roy", status: "TODO", priority: "MEDIUM" }
      ]
    },
    {
      name: "ISO-27001 SOC2 Type II Enterprise Security & Access Control",
      code: "PRJ-SEC-2026",
      department: "Security & Compliance",
      lead: "Rahul Sharma",
      priority: "MEDIUM",
      budget: 1200000,
      spent: 370000,
      progress: 33,
      status: "PLANNING",
      deadline: "2026-12-15",
      description: "Implement role-based access control (RBAC), multi-tenant data encryption at rest, and automated disaster recovery drills.",
      tasks: [
        { title: "Role-Based Access Control (RBAC) Audit Trail Logging", assignee: "Aryan Thakur", status: "DONE", priority: "HIGH" },
        { title: "Automated Disaster Recovery Replication Drills", assignee: "Rahul Sharma", status: "IN_PROGRESS", priority: "MEDIUM" },
        { title: "End-to-End Encryption at Rest for Customer PII", assignee: "Neha Patel", status: "TODO", priority: "HIGH" }
      ]
    }
  ],
  employees: [
    {
      code: "EMP-001",
      name: "Aryan Thakur",
      email: "admin@nexusretail.com",
      phone: "+91 98200 00001",
      dept: "Executive & Management",
      designation: "Chief Technology Officer & Admin",
      doj: "2023-01-15",
      attendance: "PRESENT",
      salary: 250000
    },
    {
      code: "EMP-002",
      name: "Anita Roy",
      email: "finance@nexusretail.com",
      phone: "+91 98200 00002",
      dept: "Finance & Accounting",
      designation: "VP Finance & CFO",
      doj: "2023-03-01",
      attendance: "PRESENT",
      salary: 180000
    },
    {
      code: "EMP-003",
      name: "Rahul Sharma",
      email: "sales@nexusretail.com",
      phone: "+91 98200 00003",
      dept: "Sales & CRM",
      designation: "VP Sales & Operations",
      doj: "2023-05-10",
      attendance: "PRESENT",
      salary: 160000
    },
    {
      code: "EMP-004",
      name: "Neha Patel",
      email: "neha.patel@nexusretail.com",
      phone: "+91 98200 00004",
      dept: "AI/ML Engineering",
      designation: "Senior AI Research Engineer",
      doj: "2023-08-20",
      attendance: "PRESENT",
      salary: 140000
    }
  ],
  finance: {
    bankCash: 5680000,
    accountsReceivable: 3340000,
    inventoryAsset: 8420000,
    accountsPayable: 4200000,
    shareCapital: 5000000,
    salesRevenue: 24850000,
    cogs: 17200000,
    opex: 1530000,
    journalEntries: [
      {
        voucher: "JV-2026-001",
        date: "2026-09-01",
        narration: "Initial Shareholder Equity Capital Injection",
        debit: "1020 • Bank HDFC Current Account",
        credit: "3020 • Paid-Up Share Capital",
        amount: "₹5,000,000.00",
        status: "Audited & Balanced",
      },
      {
        voucher: "JV-2026-002",
        date: "2026-09-01",
        narration: "Customer Settlement - Tata Consumer Products Ltd (INV-2026-001)",
        debit: "1020 • Bank HDFC Current Account",
        credit: "1030 • Accounts Receivable",
        amount: "₹1,062,000.00",
        status: "Audited & Balanced",
      },
    ]
  },
  analytics: {
    forecastHorizonDays: 30,
    revenueGrowthPercent: 14.4,
    costShockPercent: 5.0,
    historicalMonthlySales: [
      { month: "Apr", revenue: 18200000 },
      { month: "May", revenue: 20100000 },
      { month: "Jun", revenue: 21850000 },
      { month: "Jul", revenue: 23400000 },
      { month: "Aug", revenue: 24850000 },
      { month: "Sep", revenue: 26200000 },
    ],
    expenseAnomalies: [
      { category: "Hardware SLA Spares", voucher: "JV-2026-088", amount: 485000, mean: 120000, zScore: 3.42, status: "ANOMALY", explanation: "Critical Outlier: Unscheduled emergency batch air-freight replacement." },
      { category: "Cloud Compute AWS", voucher: "JV-2026-092", amount: 142000, mean: 135000, zScore: 0.45, status: "NORMAL", explanation: "Nominal operational variance within 0.5-sigma boundary." },
      { category: "Legal & Compliance", voucher: "JV-2026-095", amount: 280000, mean: 160000, zScore: 1.88, status: "ELEVATED", explanation: "Elevated variance due to annual MCA GST audit filing fees." },
      { category: "Marketing Demos", voucher: "JV-2026-098", amount: 95000, mean: 90000, zScore: 0.22, status: "NORMAL", explanation: "Well within projected quarterly brand allocation." },
    ],
    churnClients: [
      { name: "Vijay Sales Northern Region", recencyDays: 52, frequency: 1, monetary: "₹2,500,000", churnProb: 0.35, riskLevel: "HIGH", action: "Dispatch Key Account Manager for urgent on-site retention review & 10% renewal incentive" },
      { name: "Zepto Hyperlocal Warehouses", recencyDays: 34, frequency: 2, monetary: "₹2,000,000", churnProb: 0.22, riskLevel: "MODERATE", action: "Send automated quarterly account pulse check & SLA performance report" },
      { name: "Tata Consumer Products Ltd", recencyDays: 8, frequency: 4, monetary: "₹5,000,000", churnProb: 0.05, riskLevel: "LOW", action: "Healthy Tier-1 engagement; schedule standard bi-annual executive review" },
      { name: "Reliance Retail Ventures", recencyDays: 6, frequency: 3, monetary: "₹10,000,000", churnProb: 0.08, riskLevel: "LOW", action: "Strategic enterprise partner; expand POS deployment pipeline" },
    ]
  }
};

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupSidebarToggle();
  setupThemeSwitcher();
  setupLucideIcons();
  checkApiConnectivity();
  updateStockDropdowns();
  updateCustomerDropdowns();
  renderDashboard();
  renderCRM();
  renderSales();
  renderInventory();
  renderFinance();
  renderHR();
  renderApprovals();
  renderAnalytics();
  setupChatHandlers();
  setupDrawerHandlers();
});

// Setup Lucide Icons
function setupLucideIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Navigation Tab Switching
function setupNavigation() {
  const navItems = document.querySelectorAll(".sidebar-nav .nav-item");
  navItems.forEach((item) => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const tabKey = item.getAttribute("data-tab");
      switchTab(tabKey);
    });
  });

  // Handle hash change
  window.addEventListener("hashchange", () => {
    const hash = window.location.hash.replace("#", "");
    if (hash) switchTab(hash);
  });
}

function switchTab(tabKey) {
  // Update sidebar active class
  document.querySelectorAll(".sidebar-nav .nav-item").forEach((el) => {
    if (el.getAttribute("data-tab") === tabKey) {
      el.classList.add("active");
    } else {
      el.classList.remove("active");
    }
  });

  // Update tab views
  document.querySelectorAll(".tab-view").forEach((view) => {
    view.classList.remove("active");
  });

  const targetView = document.getElementById(`tab-${tabKey}`);
  if (targetView) {
    targetView.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  setupLucideIcons();
}

// Backend Health Telemetry
async function checkApiConnectivity() {
  const statusPill = document.getElementById("api-status-pill");
  const statusText = document.getElementById("api-status-text");

  try {
    const res = await fetch(`${API_BASE}/health`, { method: "GET" });
    if (res.ok) {
      isApiConnected = true;
      statusPill.innerHTML = `
        <span class="status-indicator live"></span>
        <span>FastAPI Live: 8000</span>
      `;
      fetchLiveDashboardData();
    } else {
      throw new Error("Offline");
    }
  } catch (err) {
    isApiConnected = false;
    statusPill.innerHTML = `
      <span class="status-indicator" style="background-color: #3B82F6;"></span>
      <span>Demo Seed Mode</span>
    `;
  }
}

// Fetch Live Dashboard Data from FastAPI backend if online
async function fetchLiveDashboardData() {
  try {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    if (res.ok) {
      const data = await res.json();
      if (data.total_revenue) {
        document.getElementById("kpi-revenue").innerText = `₹${(Number(data.total_revenue) / 1000000).toFixed(2)}M`;
      }
      if (data.net_operating_margin_percentage) {
        document.getElementById("kpi-margin").innerText = `${Number(data.net_operating_margin_percentage).toFixed(1)}%`;
      }
      if (data.total_inventory_valuation) {
        document.getElementById("kpi-inventory").innerText = `₹${(Number(data.total_inventory_valuation) / 1000000).toFixed(2)}M`;
      }
    }
  } catch (e) {
    console.log("Using seeded fallback telemetry", e);
  }
}

// Render Dashboard
function renderDashboard() {
  const totalStockAsset = enterpriseData.stock.reduce((acc, s) => acc + (s.qty * (s.unitRate || 32000)), 0);
  enterpriseData.finance.inventoryAsset = totalStockAsset;
  const kpiInv = document.getElementById("kpi-inventory");
  if (kpiInv) kpiInv.textContent = "₹" + (totalStockAsset / 1000000).toFixed(2) + "M";

  const ordersTbody = document.getElementById("dashboard-orders-tbody");
  if (ordersTbody) {
    ordersTbody.innerHTML = enterpriseData.orders.map(o => `
      <tr>
        <td class="item-bold">${o.id}</td>
        <td>${o.customer}</td>
        <td>${o.date}</td>
        <td class="item-bold">${o.amount}</td>
        <td>
          <span class="status-pill ${o.status === 'CONFIRMED' ? 'success' : 'info'}">
            ${o.status}
          </span>
        </td>
      </tr>
    `).join("");
  }

  const stockTbody = document.getElementById("dashboard-stock-tbody");
  if (stockTbody) {
    stockTbody.innerHTML = enterpriseData.stock.slice(0, 5).map(s => {
      const statusClass = s.qty <= 0 ? 'danger' : (s.qty <= (s.reorder || 10) ? 'warning' : 'success');
      const statusLabel = s.qty <= 0 ? 'Out of Stock' : (s.qty <= (s.reorder || 10) ? 'Low Stock' : 'Adequate');
      return `
      <tr>
        <td class="item-bold">${s.name} <br/><small class="text-muted">${s.sku}</small></td>
        <td>${s.location}</td>
        <td class="item-bold">${s.qty} units</td>
        <td>${s.reorder} units</td>
        <td>
          <span class="status-pill ${statusClass}">
            ${statusLabel}
          </span>
        </td>
      </tr>
    `;
    }).join("");
  }
}

// Render CRM
function renderCRM() {
  const tbody = document.getElementById("crm-table-tbody");
  if (!tbody) return;

  function drawRows(items) {
    tbody.innerHTML = items.map(c => `
      <tr>
        <td class="item-bold">${c.name}</td>
        <td><span class="status-pill ${c.segment === 'Enterprise' ? 'info' : 'warning'}">${c.segment}</span></td>
        <td>${c.contact}</td>
        <td class="item-bold">${c.credit}</td>
        <td>${c.churn}</td>
        <td>
          <span class="status-pill ${c.health === 'Healthy' ? 'success' : (c.health === 'At Risk' ? 'danger' : 'warning')}">
            ${c.health}
          </span>
        </td>
      </tr>
    `).join("");
  }

  drawRows(enterpriseData.customers);

  const filterInput = document.getElementById("crm-filter-input");
  if (filterInput) {
    filterInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      const filtered = enterpriseData.customers.filter(c => 
        c.name.toLowerCase().includes(q) || c.segment.toLowerCase().includes(q)
      );
      drawRows(filtered);
    });
  }
}

// Render Sales
function renderSales() {
  const ordersTbody = document.getElementById("sales-orders-tbody");
  const invoicesTbody = document.getElementById("sales-invoices-tbody");

  // 1. Render Confirmed Sales Orders
  if (ordersTbody) {
    ordersTbody.innerHTML = enterpriseData.orders.map(ord => `
      <tr>
        <td class="item-bold">${ord.id}</td>
        <td>${ord.customer}</td>
        <td>${ord.product || 'NEXUS Core POS Terminal X5'}</td>
        <td class="item-bold">${ord.qty || 1}</td>
        <td>${ord.date}</td>
        <td class="item-bold">${ord.amount}</td>
        <td>
          <span class="status-pill ${ord.status === 'CONFIRMED' ? 'success' : (ord.status === 'FULFILLED' ? 'info' : 'warning')}">
            ${ord.status}
          </span>
        </td>
        <td>
          <span class="status-pill ${ord.paymentStatus === 'PAID' ? 'success' : 'danger'}">
            ${ord.paymentStatus || 'UNPAID'}
          </span>
        </td>
        <td>
          <div style="display:inline-flex; align-items:center; gap:6px;">
            <button class="btn btn-xs btn-outline" onclick="openReceiptModal('${ord.invoiceNumber || 'INV-2026-001'}')" title="View Linked GST Invoice & Receipt">
              <i data-lucide="file-text" style="width:13px; height:13px; margin-right:4px;"></i> Invoice
            </button>
            ${ord.paymentStatus !== 'PAID' ? `
              <button class="btn-pay-settlement" onclick="quickSettleOrder('${ord.id}')" title="Realize Revenue & Settle Payment">
                <i data-lucide="credit-card" style="width:12px; height:12px;"></i> Settle Payment
              </button>
            ` : ''}
            ${ord.status !== 'FULFILLED' ? `
              <button class="btn btn-xs btn-secondary" onclick="fulfillSalesOrder('${ord.id}')" title="Mark Order Fulfilled & Dispatched">
                <i data-lucide="truck" style="width:13px; height:13px; margin-right:4px;"></i> Fulfill
              </button>
            ` : ''}
          </div>
        </td>
      </tr>
    `).join("");
  }

  // 2. Render GST Tax Invoices
  if (invoicesTbody) {
    invoicesTbody.innerHTML = enterpriseData.invoices.map(inv => `
      <tr>
        <td class="item-bold">${inv.number}</td>
        <td>${inv.customer}</td>
        <td>${inv.issueDate}</td>
        <td>${inv.dueDate}</td>
        <td class="item-bold">${inv.amount}</td>
        <td>
          <div style="display:inline-flex; align-items:center; gap:6px;">
            <span class="status-pill ${inv.status === 'PAID' ? 'success' : 'danger'}">
              ${inv.status}
            </span>
            ${inv.status !== 'PAID' ? `
              <button class="btn-pay-settlement" onclick="openSettlePaymentModal('${inv.number}')" title="Settle Invoice ${inv.number}">
                <i data-lucide="credit-card" style="width:12px; height:12px;"></i> Pay Now
              </button>
            ` : ''}
          </div>
        </td>
        <td>
          <div style="display:inline-flex; align-items:center; gap:6px;">
            <button class="btn btn-xs btn-outline" onclick="openReceiptModal('${inv.number}')" title="View & Print Receipt">
              <i data-lucide="receipt" style="width:13px; height:13px; margin-right:4px;"></i> View Receipt
            </button>
            <button class="btn btn-xs btn-secondary" onclick="openEmailInvoiceModal('${inv.number}')" title="Send Invoice & Receipt to Customer Email">
              <i data-lucide="mail" style="width:13px; height:13px; margin-right:4px;"></i> Email
            </button>
          </div>
        </td>
      </tr>
    `).join("");
  }

  // 3. Update Sales KPI Summary Cards
  const revEl = document.getElementById("sales-kpi-revenue");
  if (revEl) {
    revEl.textContent = "₹" + (enterpriseData.finance.salesRevenue / 1000000).toFixed(2) + "M";
  }
  const countEl = document.getElementById("sales-kpi-orders-count");
  if (countEl) {
    countEl.textContent = enterpriseData.orders.length;
  }
  const arEl = document.getElementById("sales-kpi-ar");
  if (arEl) {
    arEl.textContent = "₹" + (enterpriseData.finance.accountsReceivable / 1000000).toFixed(2) + "M";
  }
  const settEl = document.getElementById("sales-kpi-settlement-rate");
  if (settEl) {
    const paidCount = enterpriseData.invoices.filter(i => i.status === "PAID").length;
    const rate = enterpriseData.invoices.length > 0 ? Math.round((paidCount / enterpriseData.invoices.length) * 100) : 100;
    settEl.textContent = rate + "%";
  }

  const ordBadge = document.getElementById("sales-orders-badge");
  if (ordBadge) ordBadge.textContent = enterpriseData.orders.length + " Orders";

  const invBadge = document.getElementById("sales-invoices-badge");
  if (invBadge) invBadge.textContent = enterpriseData.invoices.length + " Invoices";

  setupLucideIcons();
}

window.fulfillSalesOrder = function(orderId) {
  const ord = enterpriseData.orders.find(o => o.id === orderId);
  if (ord) {
    ord.status = "FULFILLED";
    renderSales();
    renderDashboard();
    showToast(`Sales Order ${orderId} status updated to FULFILLED!`, "success");
  }
};

window.quickSettleOrder = function(orderId) {
  const ord = enterpriseData.orders.find(o => o.id === orderId);
  if (!ord) return;

  ord.paymentStatus = "PAID";
  
  // Find linked invoice
  const inv = enterpriseData.invoices.find(i => i.number === ord.invoiceNumber || (i.customer === ord.customer && i.status === "UNPAID"));
  if (inv) {
    inv.status = "PAID";
    inv.settlementDate = "2026-09-09";
    inv.settlementRef = "HDFC-NEFT-" + Math.floor(10000000 + Math.random() * 90000000);
    inv.settlementMethod = "NEFT / RTGS Online";
  }

  const rawAmt = parseFloat(ord.amount.replace(/[^0-9.]/g, "")) || 0;
  enterpriseData.finance.bankCash += rawAmt;
  enterpriseData.finance.accountsReceivable = Math.max(0, enterpriseData.finance.accountsReceivable - rawAmt);

  const jvNum = "JV-2026-00" + (enterpriseData.finance.journalEntries.length + 1);
  enterpriseData.finance.journalEntries.unshift({
    voucher: jvNum,
    date: "2026-09-09",
    narration: `Quick Revenue Realization - ${ord.customer} (${ord.id})`,
    debit: "1020 • Bank HDFC Current Account",
    credit: "1030 • Accounts Receivable",
    amount: ord.amount.includes("₹") ? ord.amount : "₹" + ord.amount,
    status: "Audited & Balanced",
  });

  renderSales();
  renderFinance();
  renderDashboard();
  showToast(`Revenue realized for Sales Order ${ord.id}! ${ord.amount} credited into HDFC Treasury Bank Account.`, "success");
};

// Render Inventory
function renderInventory() {
  const tbody = document.getElementById("inventory-table-tbody");
  if (!tbody) return;

  tbody.innerHTML = enterpriseData.stock.map(item => {
    const rate = item.unitRate || 32000;
    const totalVal = item.qty * rate;
    const statusClass = item.qty <= 0 ? 'danger' : (item.qty <= (item.reorder || 10) ? 'warning' : 'success');
    const statusLabel = item.qty <= 0 ? 'Out of Stock' : (item.qty <= (item.reorder || 10) ? 'Low Stock' : 'Adequate');
    return `
    <tr>
      <td class="item-bold">${item.sku}</td>
      <td>${item.name}</td>
      <td>${item.location}</td>
      <td class="item-bold">
        <span>${item.qty} units</span>
        <span class="status-pill ${statusClass}" style="margin-left:8px; font-size:0.7rem;">${statusLabel}</span>
      </td>
      <td>₹${rate.toLocaleString("en-IN")}</td>
      <td class="item-bold">₹${totalVal.toLocaleString("en-IN")}</td>
    </tr>
  `;
  }).join("");
  setupLucideIcons();
}

// Render Finance
function renderFinance() {
  const fin = enterpriseData.finance;
  const totalAssets = fin.bankCash + fin.accountsReceivable + fin.inventoryAsset;
  const grossProfit = fin.salesRevenue - fin.cogs;
  const netProfit = grossProfit - fin.opex;
  const marginPct = ((netProfit / fin.salesRevenue) * 100).toFixed(1);

  // Update 5-Pillar Chart of Accounts Tree
  const coaTree = document.getElementById("coa-tree-view");
  if (coaTree) {
    coaTree.innerHTML = `
      <div class="coa-node group">
        <div class="coa-node-header"><span>1000 • ASSETS</span><span style="font-weight:700;">₹${totalAssets.toLocaleString("en-IN")}.00</span></div>
      </div>
      <div class="coa-node" style="margin-left: 18px;">
        <div class="coa-node-header"><span>1020 • Bank HDFC Current Account</span><span class="text-emerald-600" style="font-weight:700;">₹${fin.bankCash.toLocaleString("en-IN")}.00</span></div>
      </div>
      <div class="coa-node" style="margin-left: 18px;">
        <div class="coa-node-header"><span>1030 • Accounts Receivable (Trade Debtors)</span><span style="font-weight:600;">₹${fin.accountsReceivable.toLocaleString("en-IN")}.00</span></div>
      </div>
      <div class="coa-node" style="margin-left: 18px;">
        <div class="coa-node-header"><span>1040 • Inventory Perpetual Asset</span><span style="font-weight:600;">₹${fin.inventoryAsset.toLocaleString("en-IN")}.00</span></div>
      </div>
      <div class="coa-node group" style="margin-top: 10px;">
        <div class="coa-node-header"><span>2000 • LIABILITIES</span><span style="font-weight:700;">₹${fin.accountsPayable.toLocaleString("en-IN")}.00</span></div>
      </div>
      <div class="coa-node" style="margin-left: 18px;">
        <div class="coa-node-header"><span>2010 • Accounts Payable (OEM Creditors)</span><span style="font-weight:600;">₹${fin.accountsPayable.toLocaleString("en-IN")}.00</span></div>
      </div>
      <div class="coa-node group" style="margin-top: 10px;">
        <div class="coa-node-header"><span>3000 • EQUITY</span><span style="font-weight:700;">₹${fin.shareCapital.toLocaleString("en-IN")}.00</span></div>
      </div>
      <div class="coa-node" style="margin-left: 18px;">
        <div class="coa-node-header"><span>3020 • Paid-Up Share Capital</span><span style="font-weight:600;">₹${fin.shareCapital.toLocaleString("en-IN")}.00</span></div>
      </div>
    `;
  }

  // Update Real-Time Financial Statement Balances
  const preview = document.getElementById("financial-preview");
  if (preview) {
    preview.innerHTML = `
      <div class="stmt-row"><span>Total Gross Sales Revenue</span><span class="item-bold">₹${fin.salesRevenue.toLocaleString("en-IN")}.00</span></div>
      <div class="stmt-row"><span>Cost of Goods Sold (COGS)</span><span class="text-muted">- ₹${fin.cogs.toLocaleString("en-IN")}.00</span></div>
      <div class="stmt-row total"><span>Gross Operating Profit</span><span class="text-emerald-600">₹${grossProfit.toLocaleString("en-IN")}.00</span></div>
      <div class="stmt-row"><span>Operating Overhead & Cloud Infrastructure</span><span class="text-muted">- ₹${fin.opex.toLocaleString("en-IN")}.00</span></div>
      <div class="stmt-row total"><span>Net Operating Profit</span><span class="text-primary">₹${netProfit.toLocaleString("en-IN")}.00 (${marginPct}%)</span></div>
      <div class="stmt-row" style="margin-top:8px; border-top:1px dashed var(--border-light); padding-top:8px;">
        <span>Liquid Bank Cash (HDFC Treasury)</span>
        <strong style="color:var(--emerald-600); font-size:0.95rem;">₹${(fin.bankCash / 1000000).toFixed(2)}M</strong>
      </div>
    `;
  }

  // Update General Ledger / Posted Journal Vouchers Table
  const jvTbody = document.getElementById("journal-vouchers-tbody");
  if (jvTbody && fin.journalEntries) {
    jvTbody.innerHTML = fin.journalEntries.map(jv => `
      <tr>
        <td class="item-bold">${jv.voucher}</td>
        <td>${jv.date}</td>
        <td>
          <div style="font-weight:600;">${escapeHtml(jv.narration)}</div>
        </td>
        <td><span class="badge badge-info" style="font-size:0.75rem;">${escapeHtml(jv.debit)}</span></td>
        <td><span class="badge" style="background:#F1F5F9; color:var(--text-secondary); font-size:0.75rem;">${escapeHtml(jv.credit)}</span></td>
        <td class="item-bold">${jv.amount}</td>
        <td>
          <span class="status-pill success"><i data-lucide="check" style="width:11px; height:11px; margin-right:3px;"></i> ${jv.status}</span>
        </td>
      </tr>
    `).join("");
    setupLucideIcons();
  }

  // Synchronize Top Executive Cockpit KPI cards
  const kpiCash = document.getElementById("kpi-cash");
  if (kpiCash) {
    kpiCash.textContent = "₹" + (fin.bankCash / 1000000).toFixed(2) + "M";
    kpiCash.style.transition = "color 0.3s ease";
  }
  const kpiRev = document.getElementById("kpi-revenue");
  if (kpiRev) {
    kpiRev.textContent = "₹" + (fin.salesRevenue / 1000000).toFixed(2) + "M";
  }
}

// Globals & Handlers for HR & Project Management
let projectStatusFilter = "ALL";

function setProjectStatusFilter(status, btnEl) {
  projectStatusFilter = status;
  document.querySelectorAll(".project-filter-btn").forEach(b => b.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");
  filterProjects();
}

function filterProjects() {
  const deptFilter = document.getElementById("project-dept-filter")?.value || "ALL";
  const searchQuery = (document.getElementById("project-search-input")?.value || "").toLowerCase().trim();
  renderHR(projectStatusFilter, deptFilter, searchQuery);
}

// Render HR & Projects Tab
function renderHR(statusFilter = "ALL", deptFilter = "ALL", searchQuery = "") {
  const container = document.getElementById("projects-container-view");
  if (!container) return;

  // Filter projects
  let filtered = (enterpriseData.projects || []);

  if (statusFilter !== "ALL") {
    filtered = filtered.filter(p => p.status === statusFilter);
  }
  if (deptFilter !== "ALL") {
    filtered = filtered.filter(p => p.department === deptFilter);
  }
  if (searchQuery) {
    filtered = filtered.filter(p =>
      p.name.toLowerCase().includes(searchQuery) ||
      p.code.toLowerCase().includes(searchQuery) ||
      (p.description || "").toLowerCase().includes(searchQuery) ||
      (p.tasks || []).some(t => t.title.toLowerCase().includes(searchQuery) || t.assignee.toLowerCase().includes(searchQuery))
    );
  }

  // Populate top KPI cards
  const allProjects = enterpriseData.projects || [];
  const totalCount = allProjects.length;
  const totalBudget = allProjects.reduce((acc, p) => acc + (typeof p.budget === "number" ? p.budget : parseFloat(String(p.budget).replace(/[^0-9.]/g, "")) || 0), 0);
  const totalSpent = allProjects.reduce((acc, p) => acc + (typeof p.spent === "number" ? p.spent : parseFloat(String(p.spent).replace(/[^0-9.]/g, "")) || 0), 0);

  let totalTasks = 0;
  let doneTasks = 0;
  allProjects.forEach(p => {
    (p.tasks || []).forEach(t => {
      totalTasks++;
      if (t.status === "DONE") doneTasks++;
    });
  });
  const milestoneVelocity = totalTasks > 0 ? Math.round((doneTasks / totalTasks) * 100) : 0;
  const utilPct = totalBudget > 0 ? ((totalSpent / totalBudget) * 100).toFixed(1) : 0;

  const countEl = document.getElementById("kpi-projects-count");
  const budgetEl = document.getElementById("kpi-projects-budget");
  const spentBadge = document.getElementById("kpi-projects-spent-badge");
  const burnRateEl = document.getElementById("kpi-projects-burn-rate");
  const velocityEl = document.getElementById("kpi-projects-velocity");
  const tasksCompletedEl = document.getElementById("kpi-projects-tasks-completed");

  if (countEl) countEl.textContent = totalCount;
  if (budgetEl) budgetEl.textContent = "₹" + (totalBudget / 1000000).toFixed(2) + "M";
  if (spentBadge) spentBadge.textContent = "₹" + (totalSpent / 1000000).toFixed(2) + "M Spent";
  if (burnRateEl) burnRateEl.textContent = `(${utilPct}% Utilized)`;
  if (velocityEl) velocityEl.textContent = milestoneVelocity + "%";
  if (tasksCompletedEl) tasksCompletedEl.textContent = `${doneTasks} of ${totalTasks} Tasks Done`;

  // Render Projects Grid Cards
  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 48px 24px; background: var(--card-bg); border-radius: var(--radius-lg); border: 1px dashed var(--border-medium);">
        <i data-lucide="folder-search" style="width: 40px; height: 40px; color: var(--text-muted); margin-bottom: 12px;"></i>
        <h4 style="font-weight: 700; font-size: 1.1rem; margin-bottom: 4px;">No Projects Found</h4>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 16px;">No project records match the active status or department filter.</p>
        <button class="btn btn-secondary btn-sm" onclick="setProjectStatusFilter('ALL', document.querySelector('[data-status=ALL]'))">Reset Filters</button>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  container.innerHTML = filtered.map(p => {
    const pTotal = (p.tasks || []).length;
    const pDone = (p.tasks || []).filter(t => t.status === 'DONE').length;
    const progressPct = pTotal > 0 ? Math.round((pDone / pTotal) * 100) : (p.progress || 0);
    p.progress = progressPct;

    const numBudget = typeof p.budget === 'number' ? p.budget : parseFloat(String(p.budget).replace(/[^0-9.]/g, "")) || 0;
    const numSpent = typeof p.spent === 'number' ? p.spent : parseFloat(String(p.spent).replace(/[^0-9.]/g, "")) || 0;
    const remaining = Math.max(0, numBudget - numSpent);

    const priorityBadge = p.priority === 'CRITICAL' ? '<span class="status-pill danger">CRITICAL</span>' :
                          p.priority === 'HIGH' ? '<span class="status-pill warning">HIGH</span>' :
                          '<span class="status-pill info">MEDIUM</span>';

    return `
      <div class="project-card">
        <div class="project-card-header">
          <div>
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px; flex-wrap:wrap;">
              <span class="pill-badge pill-purple" style="font-size:0.7rem; font-weight:700;">${p.code}</span>
              <span class="pill-badge" style="background:#F1F5F9; color:#475569; font-size:0.7rem;">${p.department || 'Operations'}</span>
              ${priorityBadge}
            </div>
            <h3 class="project-card-title">${p.name}</h3>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <select class="pill-select" style="font-size:0.75rem; padding:4px 8px;" onchange="updateProjectStatus('${p.code}', this.value)">
              <option value="ACTIVE" ${p.status === 'ACTIVE' ? 'selected' : ''}>ACTIVE</option>
              <option value="IN_PROGRESS" ${p.status === 'IN_PROGRESS' ? 'selected' : ''}>IN_PROGRESS</option>
              <option value="PLANNING" ${p.status === 'PLANNING' ? 'selected' : ''}>PLANNING</option>
              <option value="ON_HOLD" ${p.status === 'ON_HOLD' ? 'selected' : ''}>ON_HOLD</option>
              <option value="COMPLETED" ${p.status === 'COMPLETED' ? 'selected' : ''}>COMPLETED</option>
            </select>
            <button class="icon-btn-danger" title="Delete Project" onclick="deleteProject('${p.code}')">
              <i data-lucide="trash-2" style="width:14px; height:14px;"></i>
            </button>
          </div>
        </div>

        <p class="project-card-desc">${p.description || 'Enterprise strategic deliverable tracking and resource allocation.'}</p>

        <!-- Progress Gauge -->
        <div style="margin-bottom:14px;">
          <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; font-weight:600; margin-bottom:6px;">
            <span style="color:var(--text-secondary);">Milestone Progress (${pDone}/${pTotal} Deliverables)</span>
            <span class="text-indigo-600" style="font-weight:700;">${progressPct}%</span>
          </div>
          <div class="project-progress-bar">
            <div class="project-progress-fill" style="width: ${progressPct}%;"></div>
          </div>
        </div>

        <!-- Budget & Meta Grid -->
        <div class="project-meta-grid">
          <div class="project-meta-item">
            <span class="meta-label">Capital Budget</span>
            <span class="meta-val">₹${numBudget.toLocaleString('en-IN')}</span>
          </div>
          <div class="project-meta-item">
            <span class="meta-label">Total Spent</span>
            <span class="meta-val text-amber-600">₹${numSpent.toLocaleString('en-IN')}</span>
          </div>
          <div class="project-meta-item">
            <span class="meta-label">Remaining Funds</span>
            <span class="meta-val text-emerald-600">₹${remaining.toLocaleString('en-IN')}</span>
          </div>
          <div class="project-meta-item">
            <span class="meta-label">Project Owner</span>
            <span class="meta-val" style="display:flex; align-items:center; gap:4px;">
              <span class="user-avatar-tiny">${(p.lead || 'AT').split(' ').map(n=>n[0]).join('')}</span>
              ${p.lead || 'Aryan Thakur'}
            </span>
          </div>
        </div>

        <!-- Deliverable Tasks Section -->
        <div class="project-tasks-section">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <h4 style="font-size:0.78rem; text-transform:uppercase; font-weight:700; letter-spacing:0.04em; color:var(--text-muted);">Deliverable Tasks (${pTotal})</h4>
            <button class="btn btn-secondary btn-sm" style="font-size:0.75rem; padding:3px 8px;" onclick="openAddProjectTaskModal('${p.code}')">
              <i data-lucide="plus" style="width:12px; height:12px;"></i> + Task
            </button>
          </div>

          <div class="project-tasks-list">
            ${(p.tasks || []).map((t, idx) => `
              <div class="project-task-row ${t.status === 'DONE' ? 'task-done' : ''}">
                <div style="display:flex; align-items:center; gap:10px;">
                  <button class="task-checkbox-btn ${t.status === 'DONE' ? 'checked' : ''}" onclick="toggleProjectTaskStatus('${p.code}', ${idx})" title="Toggle Completion">
                    <i data-lucide="${t.status === 'DONE' ? 'check-square' : t.status === 'IN_PROGRESS' ? 'clock' : 'square'}" style="width:16px; height:16px;"></i>
                  </button>
                  <div>
                    <span class="task-title-text">${t.title}</span>
                    <div style="font-size:0.72rem; color:var(--text-muted); display:flex; align-items:center; gap:8px; margin-top:2px;">
                      <span><i data-lucide="user" style="width:11px; height:11px; display:inline; vertical-align:-1px;"></i> ${t.assignee}</span>
                      ${t.priority ? `<span class="pill-badge-sm">${t.priority}</span>` : ''}
                    </div>
                  </div>
                </div>
                <div style="display:flex; align-items:center; gap:6px;">
                  <span class="status-pill ${t.status === 'DONE' ? 'success' : t.status === 'IN_PROGRESS' ? 'info' : 'warning'}" style="font-size:0.7rem; cursor:pointer;" onclick="toggleProjectTaskStatus('${p.code}', ${idx})">
                    ${t.status}
                  </span>
                  <button class="icon-btn-ghost" title="Delete Task" onclick="deleteProjectTask('${p.code}', ${idx})">
                    <i data-lucide="x" style="width:13px; height:13px;"></i>
                  </button>
                </div>
              </div>
            `).join("")}
          </div>
        </div>

        <div class="project-card-footer">
          <div style="font-size:0.75rem; color:var(--text-muted); display:flex; align-items:center; gap:6px;">
            <i data-lucide="calendar" style="width:13px; height:13px;"></i> Target: <strong>${p.deadline || '2026-10-30'}</strong>
          </div>
          <div style="display:flex; gap:6px;">
            <button class="btn btn-secondary btn-sm" style="font-size:0.75rem; padding:4px 10px;" onclick="openLogProjectExpenseModal('${p.code}')">
              <i data-lucide="receipt" style="width:12px; height:12px;"></i> Log Expense
            </button>
            <button class="btn btn-secondary btn-sm" style="font-size:0.75rem; padding:4px 10px;" onclick="openAddProjectTaskModal('${p.code}')">
              <i data-lucide="plus" style="width:12px; height:12px;"></i> Task
            </button>
          </div>
        </div>
      </div>
    `;
  }).join("");

  if (window.lucide) {
    lucide.createIcons();
  }
}

// Project Modal Popups & CRUD Operations
function populateProjectDropdowns() {
  const taskSel = document.getElementById("task-target-project");
  const expSel = document.getElementById("expense-target-project");
  const projects = enterpriseData.projects || [];

  const opts = projects.map(p => `<option value="${p.code}">${p.name} (${p.code})</option>`).join("");

  if (taskSel) taskSel.innerHTML = opts;
  if (expSel) expSel.innerHTML = opts;
}

function openAddProjectTaskModal(projectCode = "") {
  populateProjectDropdowns();
  if (projectCode) {
    const taskSel = document.getElementById("task-target-project");
    if (taskSel) taskSel.value = projectCode;
  }
  openModal("modal-add-project-task");
}

function openLogProjectExpenseModal(projectCode = "") {
  populateProjectDropdowns();
  if (projectCode) {
    const expSel = document.getElementById("expense-target-project");
    if (expSel) expSel.value = projectCode;
  }
  const dateInp = document.getElementById("expense-date");
  if (dateInp) dateInp.value = new Date().toISOString().split("T")[0];
  openModal("modal-log-project-expense");
}

function handleCreateProject(event) {
  event.preventDefault();
  const name = document.getElementById("new-project-name").value.trim();
  const code = document.getElementById("new-project-code").value.trim().toUpperCase();
  const department = document.getElementById("new-project-dept").value;
  const lead = document.getElementById("new-project-lead").value;
  const priority = document.getElementById("new-project-priority").value;
  const budget = parseFloat(document.getElementById("new-project-budget").value) || 0;
  const spent = parseFloat(document.getElementById("new-project-spent").value) || 0;
  const status = document.getElementById("new-project-status").value;
  const deadline = document.getElementById("new-project-deadline").value;
  const description = document.getElementById("new-project-desc").value.trim();

  const initTaskTitle = document.getElementById("new-project-initial-task").value.trim();
  const initTaskAssignee = document.getElementById("new-project-task-assignee").value;

  const tasks = [];
  if (initTaskTitle) {
    tasks.push({ title: initTaskTitle, assignee: initTaskAssignee, status: "IN_PROGRESS", priority: "HIGH" });
  }

  const newProj = {
    name,
    code,
    department,
    lead,
    priority,
    budget,
    spent,
    progress: 0,
    status,
    deadline,
    description,
    tasks
  };

  enterpriseData.projects.unshift(newProj);

  closeModal("modal-add-project");
  document.getElementById("form-add-project").reset();
  showToast(`Project "${name}" (${code}) created successfully!`, "success");
  filterProjects();
}

function handleCreateProjectTask(event) {
  event.preventDefault();
  const code = document.getElementById("task-target-project").value;
  const title = document.getElementById("task-title").value.trim();
  const assignee = document.getElementById("task-assignee").value;
  const priority = document.getElementById("task-priority").value;
  const status = document.getElementById("task-status").value;

  const proj = enterpriseData.projects.find(p => p.code === code);
  if (proj) {
    if (!proj.tasks) proj.tasks = [];
    proj.tasks.push({ title, assignee, priority, status });
    closeModal("modal-add-project-task");
    document.getElementById("form-add-project-task").reset();
    showToast(`Deliverable task added to ${proj.name}!`, "success");
    filterProjects();
  }
}

function handleLogProjectExpense(event) {
  event.preventDefault();
  const code = document.getElementById("expense-target-project").value;
  const amount = parseFloat(document.getElementById("expense-amount").value) || 0;
  const category = document.getElementById("expense-category").value;
  const narration = document.getElementById("expense-narration").value.trim();

  const proj = enterpriseData.projects.find(p => p.code === code);
  if (proj) {
    const currentSpent = typeof proj.spent === "number" ? proj.spent : parseFloat(String(proj.spent).replace(/[^0-9.]/g, "")) || 0;
    proj.spent = currentSpent + amount;

    closeModal("modal-log-project-expense");
    document.getElementById("form-log-project-expense").reset();
    showToast(`Recorded ₹${amount.toLocaleString('en-IN')} expense (${category}) for project ${proj.code}`, "success");
    filterProjects();
  }
}

function toggleProjectTaskStatus(code, taskIdx) {
  const proj = enterpriseData.projects.find(p => p.code === code);
  if (proj && proj.tasks && proj.tasks[taskIdx]) {
    const current = proj.tasks[taskIdx].status;
    const nextStatus = current === "TODO" ? "IN_PROGRESS" : current === "IN_PROGRESS" ? "DONE" : "TODO";
    proj.tasks[taskIdx].status = nextStatus;

    showToast(`Deliverable status updated to ${nextStatus}`, "info");
    filterProjects();
  }
}

function deleteProjectTask(code, taskIdx) {
  const proj = enterpriseData.projects.find(p => p.code === code);
  if (proj && proj.tasks && proj.tasks[taskIdx]) {
    proj.tasks.splice(taskIdx, 1);
    showToast("Deliverable task removed.", "info");
    filterProjects();
  }
}

function updateProjectStatus(code, newStatus) {
  const proj = enterpriseData.projects.find(p => p.code === code);
  if (proj) {
    proj.status = newStatus;
    showToast(`Project ${code} status updated to ${newStatus}`, "success");
    filterProjects();
  }
}

function deleteProject(code) {
  if (confirm(`Are you sure you want to delete project ${code}? This action cannot be undone.`)) {
    enterpriseData.projects = enterpriseData.projects.filter(p => p.code !== code);
    showToast(`Project ${code} deleted.`, "warning");
    filterProjects();
  }
}

// HR & Project Management Sub-Tab Switcher
let activeHRSubTab = "projects";

function switchHRSubTab(tabName) {
  activeHRSubTab = tabName;

  ["projects", "kanban", "employees"].forEach(t => {
    const btn = document.getElementById(`subtab-btn-${t}`);
    const panel = document.getElementById(`hr-subpanel-${t}`);
    if (btn) btn.classList.toggle("active", t === tabName);
    if (panel) panel.style.display = t === tabName ? "block" : "none";
  });

  const projControls = document.getElementById("projects-subtab-controls");
  if (projControls) {
    projControls.style.display = tabName === "employees" ? "none" : "flex";
  }

  // Update header action buttons dynamically
  const headerActions = document.getElementById("hr-header-actions");
  if (headerActions) {
    if (tabName === "employees") {
      headerActions.innerHTML = `
        <button class="btn btn-primary" onclick="openModal('modal-add-employee')">
          <i data-lucide="user-plus"></i>
          <span>+ Add Employee</span>
        </button>
      `;
    } else {
      headerActions.innerHTML = `
        <button class="btn btn-secondary" onclick="openModal('modal-add-project-task')">
          <i data-lucide="check-square"></i>
          <span>+ Quick Task</span>
        </button>
        <button class="btn btn-primary" onclick="openModal('modal-add-project')">
          <i data-lucide="folder-plus"></i>
          <span>+ Create Project</span>
        </button>
      `;
    }
    if (window.lucide) lucide.createIcons();
  }

  if (tabName === "kanban") {
    renderKanban();
  } else if (tabName === "employees") {
    renderEmployees();
  } else {
    filterProjects();
  }
}

// Render Agile Kanban Board
function renderKanban() {
  const container = document.getElementById("kanban-board-view");
  if (!container) return;

  const searchQuery = (document.getElementById("project-search-input")?.value || "").toLowerCase().trim();
  const deptFilter = document.getElementById("project-dept-filter")?.value || "ALL";

  // Flatten all tasks with project context
  const allTasks = [];
  (enterpriseData.projects || []).forEach(p => {
    if (deptFilter !== "ALL" && p.department !== deptFilter) return;
    (p.tasks || []).forEach((t, idx) => {
      if (searchQuery) {
        const matches = t.title.toLowerCase().includes(searchQuery) ||
                        t.assignee.toLowerCase().includes(searchQuery) ||
                        p.name.toLowerCase().includes(searchQuery) ||
                        p.code.toLowerCase().includes(searchQuery);
        if (!matches) return;
      }
      allTasks.push({ ...t, projectCode: p.code, projectName: p.name, taskIdx: idx });
    });
  });

  const todoTasks = allTasks.filter(t => t.status === "TODO");
  const inProgressTasks = allTasks.filter(t => t.status === "IN_PROGRESS");
  const doneTasks = allTasks.filter(t => t.status === "DONE");

  const renderColumnCards = (taskList) => {
    if (taskList.length === 0) {
      return `<div style="text-align:center; padding:24px 12px; color:var(--text-muted); font-size:0.8rem; border:1px dashed var(--border-medium); border-radius:var(--radius-md);">No tasks in this lane</div>`;
    }
    return taskList.map(t => {
      const initials = (t.assignee || "AT").split(" ").map(n => n[0]).join("");
      const priorityClass = t.priority === "URGENT" || t.priority === "CRITICAL" ? "danger" : t.priority === "HIGH" ? "warning" : "info";

      return `
        <div class="kanban-card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span class="pill-badge pill-purple" style="font-size:0.65rem; font-weight:700;">${t.projectCode}</span>
            <span class="status-pill ${priorityClass}" style="font-size:0.65rem;">${t.priority || 'NORMAL'}</span>
          </div>
          <div class="kanban-card-title">${t.title}</div>
          <div style="font-size:0.75rem; color:var(--text-secondary); margin-bottom:8px; line-height:1.3;">
            <i data-lucide="folder" style="width:11px; height:11px; display:inline; vertical-align:-1px;"></i> ${t.projectName}
          </div>
          <div class="kanban-card-footer">
            <div style="display:flex; align-items:center; gap:6px;">
              <span class="employee-avatar-circle">${initials}</span>
              <span style="font-weight:600; color:var(--text-primary); font-size:0.75rem;">${t.assignee}</span>
            </div>
            <div style="display:flex; gap:4px;">
              ${t.status !== 'TODO' ? `<button class="btn btn-secondary btn-sm" style="padding:2px 6px; font-size:0.7rem;" title="Move Back" onclick="moveKanbanTask('${t.projectCode}', ${t.taskIdx}, 'PREV')">←</button>` : ''}
              ${t.status !== 'DONE' ? `<button class="btn btn-primary btn-sm" style="padding:2px 6px; font-size:0.7rem;" title="Advance" onclick="moveKanbanTask('${t.projectCode}', ${t.taskIdx}, 'NEXT')">→</button>` : ''}
            </div>
          </div>
        </div>
      `;
    }).join("");
  };

  container.innerHTML = `
    <div class="kanban-column">
      <div class="kanban-column-header">
        <div class="kanban-column-title">
          <span style="width:10px; height:10px; border-radius:50%; background:#F59E0B; display:inline-block;"></span>
          To Do
        </div>
        <span class="kanban-count-pill">${todoTasks.length}</span>
      </div>
      <div class="kanban-cards-container">
        ${renderColumnCards(todoTasks)}
      </div>
    </div>

    <div class="kanban-column">
      <div class="kanban-column-header">
        <div class="kanban-column-title">
          <span style="width:10px; height:10px; border-radius:50%; background:#3B82F6; display:inline-block;"></span>
          In Progress
        </div>
        <span class="kanban-count-pill">${inProgressTasks.length}</span>
      </div>
      <div class="kanban-cards-container">
        ${renderColumnCards(inProgressTasks)}
      </div>
    </div>

    <div class="kanban-column">
      <div class="kanban-column-header">
        <div class="kanban-column-title">
          <span style="width:10px; height:10px; border-radius:50%; background:#10B981; display:inline-block;"></span>
          Completed
        </div>
        <span class="kanban-count-pill">${doneTasks.length}</span>
      </div>
      <div class="kanban-cards-container">
        ${renderColumnCards(doneTasks)}
      </div>
    </div>
  `;

  if (window.lucide) lucide.createIcons();
}

function moveKanbanTask(code, taskIdx, direction) {
  const proj = enterpriseData.projects.find(p => p.code === code);
  if (proj && proj.tasks && proj.tasks[taskIdx]) {
    const current = proj.tasks[taskIdx].status;
    let next = current;
    if (direction === "NEXT") {
      next = current === "TODO" ? "IN_PROGRESS" : "DONE";
    } else {
      next = current === "DONE" ? "IN_PROGRESS" : "TODO";
    }
    proj.tasks[taskIdx].status = next;
    showToast(`Task moved to ${next}`, "info");
    renderKanban();
  }
}

// Render HR & Employee Directory Table
function renderEmployees() {
  const tbody = document.getElementById("employees-table-tbody");
  if (!tbody) return;

  const employees = enterpriseData.employees || [];

  // Update headcount KPI card
  const countEl = document.getElementById("kpi-hr-headcount");
  const attBadge = document.getElementById("kpi-hr-attendance-badge");

  const presentCount = employees.filter(e => e.attendance === "PRESENT").length;
  if (countEl) countEl.textContent = `${employees.length} Staff`;
  if (attBadge) attBadge.textContent = `${Math.round((presentCount / employees.length) * 100)}% Present Today`;

  if (employees.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align:center; padding:30px; color:var(--text-muted);">
          No employee records found. Click "+ Add Employee" to register staff.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = employees.map(e => {
    const initials = (e.name || "AT").split(" ").map(n => n[0]).join("");
    const attStatusClass = e.attendance === "PRESENT" ? "success" : "warning";

    return `
      <tr>
        <td><strong class="item-bold">${e.code}</strong></td>
        <td>
          <div style="display:flex; align-items:center; gap:10px;">
            <span class="user-avatar-tiny" style="width:28px; height:28px; font-size:0.75rem;">${initials}</span>
            <div>
              <span style="font-weight:700; color:var(--text-primary); display:block;">${e.name}</span>
            </div>
          </div>
        </td>
        <td>
          <span style="font-weight:600; color:var(--text-primary); display:block;">${e.designation}</span>
          <small class="text-muted">${e.dept}</small>
        </td>
        <td>
          <div style="font-size:0.8rem;">
            <a href="mailto:${e.email}" style="color:var(--primary); text-decoration:none;">${e.email}</a>
            <div style="color:var(--text-muted); font-size:0.75rem;">${e.phone}</div>
          </div>
        </td>
        <td><span style="font-size:0.82rem;">${e.doj}</span></td>
        <td>
          <button class="status-pill ${attStatusClass}" style="border:none; cursor:pointer;" onclick="toggleEmployeeAttendance('${e.code}')" title="Click to toggle attendance">
            ${e.attendance === 'PRESENT' ? '🟢 PRESENT' : '🟡 ON LEAVE'}
          </button>
        </td>
        <td><strong class="item-bold">₹${(e.salary || 120000).toLocaleString('en-IN')}/mo</strong></td>
        <td>
          <button class="btn btn-secondary btn-sm" style="font-size:0.72rem; padding:3px 8px;" onclick="toggleEmployeeAttendance('${e.code}')">
            Toggle Attendance
          </button>
        </td>
      </tr>
    `;
  }).join("");

  if (window.lucide) lucide.createIcons();
}

function toggleEmployeeAttendance(empCode) {
  const emp = (enterpriseData.employees || []).find(e => e.code === empCode);
  if (emp) {
    emp.attendance = emp.attendance === "PRESENT" ? "ON_LEAVE" : "PRESENT";
    showToast(`Updated ${emp.name}'s attendance status to ${emp.attendance}`, "info");
    renderEmployees();
  }
}

function handleCreateEmployee(event) {
  event.preventDefault();
  const firstName = document.getElementById("emp-first-name").value.trim();
  const lastName = document.getElementById("emp-last-name").value.trim();
  const name = `${firstName} ${lastName}`;
  const email = document.getElementById("emp-email").value.trim();
  const phone = document.getElementById("emp-phone").value.trim();
  const dept = document.getElementById("emp-dept").value;
  const designation = document.getElementById("emp-designation").value.trim();
  const salary = parseFloat(document.getElementById("emp-salary").value) || 120000;
  const doj = document.getElementById("emp-doj").value;
  const attendance = document.getElementById("emp-status").value;

  const empCount = (enterpriseData.employees || []).length + 1;
  const code = `EMP-00${empCount}`;

  const newEmp = {
    code,
    name,
    email,
    phone,
    dept,
    designation,
    doj,
    attendance,
    salary
  };

  if (!enterpriseData.employees) enterpriseData.employees = [];
  enterpriseData.employees.push(newEmp);

  closeModal("modal-add-employee");
  document.getElementById("form-add-employee").reset();
  showToast(`Employee ${name} (${code}) registered successfully!`, "success");
  renderEmployees();
}

// HITL Approvals & Governance Logic
let activeHITLSubTab = "pending";

function switchHITLSubTab(tabName) {
  activeHITLSubTab = tabName;

  const pendingBtn = document.getElementById("hitl-subtab-btn-pending");
  const historyBtn = document.getElementById("hitl-subtab-btn-history");

  if (pendingBtn) pendingBtn.classList.toggle("active", tabName === "pending");
  if (historyBtn) historyBtn.classList.toggle("active", tabName === "history");

  renderApprovals();
}

function renderApprovals() {
  const container = document.getElementById("approvals-container-view");
  if (!container) return;

  const categoryFilter = document.getElementById("hitl-category-filter")?.value || "ALL";

  const pendingList = enterpriseData.pendingApprovals || [];
  const historyList = enterpriseData.approvedHistory || [];

  // Update top KPI cards
  const pendingCountEl = document.getElementById("kpi-hitl-pending-count");
  const badgeCountEl = document.getElementById("pending-approval-count");
  const historyCountEl = document.getElementById("history-approval-count");
  const impactAmountEl = document.getElementById("kpi-hitl-impact-amount");

  if (pendingCountEl) pendingCountEl.textContent = `${pendingList.length} Pending`;
  if (badgeCountEl) badgeCountEl.textContent = pendingList.length;
  if (historyCountEl) historyCountEl.textContent = historyList.length;

  const totalImpact = pendingList.reduce((sum, p) => sum + (p.amount || 0), 0);
  if (impactAmountEl) impactAmountEl.textContent = "₹" + totalImpact.toLocaleString("en-IN");

  // RENDER SUB-TAB 1: PENDING PROPOSALS
  if (activeHITLSubTab === "pending") {
    let filteredPending = pendingList;
    if (categoryFilter !== "ALL") {
      filteredPending = filteredPending.filter(p => p.actionType === categoryFilter);
    }

    if (filteredPending.length === 0) {
      container.innerHTML = `
        <div class="panel-card" style="padding: 48px; text-align: center;">
          <i data-lucide="shield-check" style="width: 48px; height: 48px; color: var(--emerald-600); margin-bottom: 12px;"></i>
          <h3 class="panel-title" style="font-size:1.1rem; font-weight:700;">All Action Proposals Authorized &amp; Executed</h3>
          <p class="text-muted" style="font-size: 0.86rem; margin-top: 6px;">Zero pending Human-in-the-Loop financial mutations requiring your sign-off.</p>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
      return;
    }

    container.innerHTML = filteredPending.map(appr => {
      const riskBadge = appr.riskLevel === 'HIGH RISK' ? '<span class="status-pill danger">🔴 HIGH RISK</span>' :
                        '<span class="status-pill warning">🟠 MEDIUM RISK</span>';

      const typeBadge = appr.actionType === 'DISCOUNT_OVERRIDE' ? 'pill-purple' :
                        appr.actionType === 'PURCHASE_ORDER_APPROVAL' ? 'pill-indigo' : 'pill-emerald';

      return `
        <div class="panel-card" style="margin-bottom: 20px; padding: 24px; border: 1px solid var(--border-medium); box-shadow: var(--shadow-md);">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
            <div>
              <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span class="pill-badge ${typeBadge}" style="font-size:0.7rem; font-weight:700;">${appr.actionType}</span>
                ${riskBadge}
                <span class="pill-badge" style="background:#F1F5F9; color:#475569; font-size:0.7rem;">Target: ${appr.targetModule || 'Finance Ledger'}</span>
              </div>
              <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-top: 4px; line-height: 1.3;">${appr.title}</h3>
              <p style="font-size: 0.84rem; color: var(--text-muted); margin-top: 4px;">
                Requested by: <strong style="color:var(--text-primary);">${appr.requester}</strong> • Entity: <strong style="color:var(--text-primary);">${appr.customer || 'Internal Vendor'}</strong>
              </p>
            </div>
            <div style="text-align: right;">
              <span class="status-pill warning" style="font-size:0.75rem;">Awaiting Human Approval</span>
              <div style="font-size:1.05rem; font-weight:700; color:#EF4444; margin-top:6px;">${appr.savings}</div>
            </div>
          </div>

          <div style="background: var(--bg-hover); padding: 14px 16px; border-radius: var(--radius-md); border: 1px solid var(--border-light); margin-bottom: 16px;">
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 8px;">
              <strong style="color:var(--text-primary);">AI Rationale &amp; Audit Trigger:</strong> ${appr.rationale}
            </p>
            <p style="font-size: 0.85rem; color: var(--text-secondary);">
              <strong style="color:var(--text-primary);">Affected Financial Ledgers:</strong> <span class="item-bold text-indigo-600">${appr.affectedLedgers || 'General Ledger & Accounts Receivable'}</span>
            </p>
          </div>

          ${appr.executionPlan ? `
            <div style="margin-bottom: 18px;">
              <h4 style="font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px; letter-spacing: 0.03em;">Execution Plan Steps:</h4>
              <ul style="margin: 0; padding-left: 20px; font-size: 0.82rem; color: var(--text-secondary); line-height: 1.6;">
                ${appr.executionPlan.map(step => `<li>${step}</li>`).join("")}
              </ul>
            </div>
          ` : ''}

          <div class="proposal-actions" style="display:flex; gap:12px; border-top:1px solid var(--border-light); padding-top:16px;">
            <button class="btn btn-success" onclick="approveProposal('${appr.id}')" style="padding: 10px 20px; font-weight:700;">
              <i data-lucide="check-circle"></i> Approve &amp; Execute Mutation
            </button>
            <button class="btn btn-danger" onclick="rejectProposal('${appr.id}')" style="padding: 10px 18px; font-weight:600;">
              <i data-lucide="x-circle"></i> Reject Proposal
            </button>
          </div>
        </div>
      `;
    }).join("");

    if (window.lucide) lucide.createIcons();
    return;
  }

  // RENDER SUB-TAB 2: APPROVED AUDIT TRAIL LOG
  let filteredHistory = historyList;
  if (categoryFilter !== "ALL") {
    filteredHistory = filteredHistory.filter(h => h.actionType === categoryFilter);
  }

  if (filteredHistory.length === 0) {
    container.innerHTML = `
      <div class="panel-card" style="padding: 40px; text-align: center;">
        <i data-lucide="history" style="width: 40px; height: 40px; color: var(--text-muted); margin-bottom: 12px;"></i>
        <h4 style="font-weight: 700; font-size: 1rem;">No Historical Audit Logs Yet</h4>
        <p class="text-muted" style="font-size: 0.84rem;">Approved and rejected proposal actions will be archived here with GL voucher references.</p>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  container.innerHTML = `
    <div class="panel-card">
      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Proposal Code &amp; Type</th>
              <th>Title &amp; Target</th>
              <th>Impact Amount</th>
              <th>Decision Maker</th>
              <th>Decision Status</th>
              <th>GL Voucher Ref</th>
            </tr>
          </thead>
          <tbody>
            ${filteredHistory.map(h => `
              <tr>
                <td><span style="font-size:0.8rem; color:var(--text-muted);">${h.decisionDate}</span></td>
                <td>
                  <span class="pill-badge pill-purple" style="font-size:0.68rem; font-weight:700;">${h.id}</span>
                  <div style="font-size:0.72rem; color:var(--text-muted); font-weight:600; margin-top:2px;">${h.actionType}</div>
                </td>
                <td>
                  <span style="font-weight:700; color:var(--text-primary); font-size:0.85rem;">${h.title}</span>
                  <div style="font-size:0.78rem; color:var(--text-secondary);">${h.customer || h.targetModule}</div>
                </td>
                <td><strong class="item-bold">${h.savings || '₹' + (h.amount || 0).toLocaleString('en-IN')}</strong></td>
                <td><span style="font-weight:600; font-size:0.82rem;">${h.decisionBy}</span></td>
                <td>
                  <span class="status-pill ${h.status === 'APPROVED' ? 'success' : 'danger'}" style="font-size:0.72rem;">
                    ${h.status === 'APPROVED' ? '✓ APPROVED' : '✗ REJECTED'}
                  </span>
                </td>
                <td><strong class="item-bold text-indigo-600">${h.journalVoucher || 'JV-2026-AUD'}</strong></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;

  if (window.lucide) lucide.createIcons();
}

function approveProposal(id) {
  const proposal = enterpriseData.pendingApprovals.find(p => p.id === id);
  if (!proposal) return;

  const nowStr = new Date().toISOString().replace("T", " ").substring(0, 16);
  const jvNum = "JV-2026-00" + (enterpriseData.finance.journalEntries.length + 1);

  // EXECUTE FINANCIAL & MODULE MUTATIONS ACCORDING TO PROPOSAL TYPE
  if (proposal.actionType === "PURCHASE_ORDER_APPROVAL") {
    // 1. Inward Stock into Inventory
    let stockItem = enterpriseData.stock.find(s => s.sku === "POS-X5-001");
    if (stockItem) {
      stockItem.qty += 50;
      stockItem.status = "Adequate";
    } else {
      enterpriseData.stock.unshift({
        sku: "POS-X5-001",
        name: "POS Touch Terminal X5",
        location: "Mumbai DC",
        qty: 50,
        reorder: 10,
        status: "Adequate",
        unitRate: 25000
      });
    }

    // 2. Update Finance Balances
    const purchaseAmount = proposal.amount || 1250000;
    enterpriseData.finance.inventoryAsset += purchaseAmount;
    enterpriseData.finance.bankCash = Math.max(0, enterpriseData.finance.bankCash - purchaseAmount);

    // 3. Post Journal Voucher to Finance
    enterpriseData.finance.journalEntries.unshift({
      voucher: jvNum,
      date: "2026-09-09",
      narration: `HITL Approved Bulk Purchase Order Execution - ${proposal.title}`,
      debit: "1040 • Perpetual Inventory Asset",
      credit: "1020 • Bank HDFC Current Account",
      amount: "₹" + purchaseAmount.toLocaleString("en-IN") + ".00",
      status: "Audited & Balanced"
    });

    showToast(`Bulk Purchase Order Approved! +50 POS Terminals inwarded to stock. Bank Cash adjusted -₹${(purchaseAmount/1000000).toFixed(2)}M and GL Voucher ${jvNum} posted.`, "success");
  } else if (proposal.actionType === "DISCOUNT_OVERRIDE") {
    // Discount adjustment
    const discountAmt = proposal.amount || 135000;
    enterpriseData.finance.salesRevenue = Math.max(0, enterpriseData.finance.salesRevenue - discountAmt);

    // Post Journal Voucher
    enterpriseData.finance.journalEntries.unshift({
      voucher: jvNum,
      date: "2026-09-09",
      narration: `HITL Approved Discount Override - ${proposal.title} (${proposal.customer})`,
      debit: "4020 • Sales Discounts Allowed",
      credit: "1030 • Accounts Receivable",
      amount: "₹" + discountAmt.toLocaleString("en-IN") + ".00",
      status: "Audited & Balanced"
    });

    showToast(`Discount Override Approved! ₹${discountAmt.toLocaleString('en-IN')} discount applied to invoice with GL Voucher ${jvNum}.`, "success");
  } else {
    showToast(`Action Proposal APPROVED by Aryan Thakur (Admin).`, "success");
  }

  // Remove from pending, add to audit history
  enterpriseData.pendingApprovals = enterpriseData.pendingApprovals.filter(p => p.id !== id);
  if (!enterpriseData.approvedHistory) enterpriseData.approvedHistory = [];

  enterpriseData.approvedHistory.unshift({
    ...proposal,
    status: "APPROVED",
    decisionBy: "Aryan Thakur (Admin)",
    decisionDate: nowStr,
    journalVoucher: jvNum
  });

  renderApprovals();
  renderFinance();
  renderInventory();
  renderSales();
  renderDashboard();
}

function rejectProposal(id) {
  const proposal = enterpriseData.pendingApprovals.find(p => p.id === id);
  if (!proposal) return;

  const nowStr = new Date().toISOString().replace("T", " ").substring(0, 16);

  enterpriseData.pendingApprovals = enterpriseData.pendingApprovals.filter(p => p.id !== id);
  if (!enterpriseData.approvedHistory) enterpriseData.approvedHistory = [];

  enterpriseData.approvedHistory.unshift({
    ...proposal,
    status: "REJECTED",
    decisionBy: "Aryan Thakur (Admin)",
    decisionDate: nowStr,
    journalVoucher: "N/A (Rejected)"
  });

  showToast(`Action Proposal REJECTED by Aryan Thakur (Admin). Standard catalog terms preserved.`, "danger");
  renderApprovals();
}

// ==============================================================================
// 9. Predictive Analytics & Machine Learning Dashboard Engine
// ==============================================================================
function renderAnalytics() {
  const a = enterpriseData.analytics;
  if (!a) return;

  const horizon = a.forecastHorizonDays || 30;
  const growthMultiplier = 1 + (a.revenueGrowthPercent / 100);
  const costShockMultiplier = 1 + (a.costShockPercent / 100);

  // Horizon multiplier: 30 days = 1 mo, 90 days = 3 mo, 365 days = 12 mo
  const horizonMonths = horizon === 365 ? 12 : (horizon === 90 ? 3 : 1);
  const baseMonthlySales = 24850000;
  const projectedRevenue = Math.round(baseMonthlySales * growthMultiplier * horizonMonths);
  const lowerRev = Math.round(projectedRevenue * 0.92);
  const upperRev = Math.round(projectedRevenue * 1.08);

  // Projected operational costs and spending
  const baseMonthlySpend = 18900000;
  const projectedSpend = Math.round(baseMonthlySpend * costShockMultiplier * horizonMonths);
  const projectedProfit = Math.max(0, projectedRevenue - projectedSpend);
  const marginPct = ((projectedProfit / projectedRevenue) * 100).toFixed(1);
  const burnRatePct = ((projectedSpend / projectedRevenue) * 100).toFixed(1);

  // Update KPI Cards
  const revEl = document.getElementById("analytics-proj-rev");
  if (revEl) revEl.textContent = "₹" + projectedRevenue.toLocaleString("en-IN");

  const growthBadge = document.getElementById("analytics-growth-badge");
  if (growthBadge) {
    const isPositive = a.revenueGrowthPercent >= 0;
    growthBadge.className = `status-pill ${isPositive ? 'success' : 'danger'}`;
    growthBadge.textContent = `${isPositive ? '↑ +' : '↓ '}${a.revenueGrowthPercent.toFixed(1)}% ${isPositive ? 'Expansion' : 'Contraction'}`;
  }

  const ciRevEl = document.getElementById("analytics-ci-rev");
  if (ciRevEl) ciRevEl.textContent = `95% Range: ₹${(lowerRev / 1000000).toFixed(2)}M – ₹${(upperRev / 1000000).toFixed(2)}M`;

  const spendEl = document.getElementById("analytics-proj-spend");
  if (spendEl) spendEl.textContent = "₹" + projectedSpend.toLocaleString("en-IN");

  const spendBadge = document.getElementById("analytics-spend-badge");
  if (spendBadge) {
    spendBadge.className = a.costShockPercent > 15 ? "status-pill danger" : (a.costShockPercent > 8 ? "status-pill warning" : "status-pill success");
    spendBadge.textContent = a.costShockPercent > 15 ? "High Inflation Risk" : (a.costShockPercent > 8 ? "Elevated Variance" : "Normal Baseline");
  }

  const spendRatioEl = document.getElementById("analytics-spend-ratio");
  if (spendRatioEl) spendRatioEl.textContent = `Projected Burn Rate: ${burnRatePct}% of Revenue`;

  const profitEl = document.getElementById("analytics-proj-profit");
  if (profitEl) profitEl.textContent = "₹" + projectedProfit.toLocaleString("en-IN");

  const marginBadge = document.getElementById("analytics-margin-badge");
  if (marginBadge) marginBadge.textContent = `${marginPct}% Margin`;

  const churnRevEl = document.getElementById("analytics-churn-rev");
  if (churnRevEl) churnRevEl.textContent = "₹2,500,000";

  // Sub-modules
  renderForecastChart(horizonMonths, growthMultiplier);
  renderSpendingBreakdown(projectedSpend, horizonMonths, projectedProfit);
  renderExpenseAnomalies();
  renderChurnMatrix();
  renderStockoutHorizon();

  setupLucideIcons();
}

// 9A. Render SVG Revenue Forecast Chart with Confidence Ribbon
function renderForecastChart(horizonMonths, growthMultiplier) {
  const svg = document.getElementById("forecast-svg-canvas");
  if (!svg) return;

  const historical = [
    { label: "Apr", val: 18200000 },
    { label: "May", val: 20100000 },
    { label: "Jun", val: 21850000 },
    { label: "Jul", val: 23400000 },
    { label: "Aug", val: 24850000 },
    { label: "Sep (Act)", val: 26200000 },
  ];

  const future = [
    { label: "Oct (Proj)", val: Math.round(26200000 * (1 + (growthMultiplier - 1) * 0.35)) },
    { label: "Nov (Proj)", val: Math.round(26200000 * (1 + (growthMultiplier - 1) * 0.70)) },
    { label: "Dec (Proj)", val: Math.round(26200000 * (1 + (growthMultiplier - 1) * 1.05)) },
    { label: "Jan (Proj)", val: Math.round(26200000 * (1 + (growthMultiplier - 1) * 1.40)) },
  ];

  const allPoints = [...historical, ...future];
  const minVal = 14000000;
  const maxVal = 44000000;
  const range = maxVal - minVal;

  const leftPadding = 75;
  const rightPadding = 45;
  const topPadding = 30;
  const bottomPadding = 45;
  const plotWidth = 1000 - leftPadding - rightPadding;
  const plotHeight = 270 - topPadding - bottomPadding;

  const getX = (index) => Math.round(leftPadding + (index * (plotWidth / (allPoints.length - 1))));
  const getY = (val) => Math.round(topPadding + plotHeight - (((val - minVal) / range) * plotHeight));

  // Build gridlines
  let gridSvg = `
    <!-- Grid Reference Lines -->
    <line x1="${leftPadding}" y1="${getY(20000000)}" x2="${1000 - rightPadding}" y2="${getY(20000000)}" stroke="#E2E8F0" stroke-dasharray="3,3" stroke-width="1" />
    <text x="${leftPadding - 10}" y="${getY(20000000) + 4}" font-size="10" fill="#94A3B8" text-anchor="end">₹20M</text>

    <line x1="${leftPadding}" y1="${getY(30000000)}" x2="${1000 - rightPadding}" y2="${getY(30000000)}" stroke="#E2E8F0" stroke-dasharray="3,3" stroke-width="1" />
    <text x="${leftPadding - 10}" y="${getY(30000000) + 4}" font-size="10" fill="#94A3B8" text-anchor="end">₹30M</text>

    <line x1="${leftPadding}" y1="${getY(40000000)}" x2="${1000 - rightPadding}" y2="${getY(40000000)}" stroke="#E2E8F0" stroke-dasharray="3,3" stroke-width="1" />
    <text x="${leftPadding - 10}" y="${getY(40000000) + 4}" font-size="10" fill="#94A3B8" text-anchor="end">₹40M</text>

    <!-- Forecast Horizon Demarcation Line -->
    <line x1="${getX(5)}" y1="${topPadding - 10}" x2="${getX(5)}" y2="${270 - bottomPadding}" stroke="#818CF8" stroke-dasharray="4,4" stroke-width="1.5" />
    <text x="${getX(5) + 6}" y="${topPadding + 6}" font-size="10" font-weight="700" fill="#6366F1">Horizon Split</text>
  `;

  // Confidence Ribbon Polygon for projected segment (indices 5 to 9)
  const upperCoords = [];
  const lowerCoords = [];
  for (let i = 5; i < allPoints.length; i++) {
    const x = getX(i);
    const upperVal = allPoints[i].val * (i === 5 ? 1.0 : 1.09);
    const lowerVal = allPoints[i].val * (i === 5 ? 1.0 : 0.91);
    upperCoords.push(`${x},${getY(upperVal)}`);
    lowerCoords.push(`${x},${getY(lowerVal)}`);
  }
  const ribbonPolygon = `<polygon points="${upperCoords.join(' ')} ${lowerCoords.reverse().join(' ')}" fill="rgba(79, 70, 229, 0.12)" stroke="rgba(79, 70, 229, 0.3)" stroke-dasharray="3,3" />`;

  // Historical Path (indices 0 to 5)
  const histPathD = historical.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(p.val)}`).join(' ');
  const histPath = `<path d="${histPathD}" fill="none" stroke="#4F46E5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />`;

  // Projected Path (indices 5 to 9)
  const projPoints = [historical[historical.length - 1], ...future];
  const projPathD = projPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(5 + i)} ${getY(p.val)}`).join(' ');
  const projPath = `<path d="${projPathD}" fill="none" stroke="#10B981" stroke-width="3" stroke-dasharray="6,4" stroke-linecap="round" stroke-linejoin="round" />`;

  // Data Points & Text Labels
  let pointsSvg = "";
  allPoints.forEach((p, i) => {
    const cx = getX(i);
    const cy = getY(p.val);
    const isProjected = i > 5;
    const fillColor = isProjected ? "#10B981" : "#4F46E5";
    const labelVal = `₹${(p.val / 1000000).toFixed(1)}M`;

    pointsSvg += `
      <circle cx="${cx}" cy="${cy}" r="4.5" fill="${fillColor}" stroke="#FFFFFF" stroke-width="2" class="svg-point-circle">
        <title>${p.label}: ${labelVal}</title>
      </circle>
      <text x="${cx}" y="${cy - 9}" font-size="10" font-weight="700" fill="${fillColor}" text-anchor="middle">${labelVal}</text>
      <text x="${cx}" y="${270 - 16}" font-size="10.5" font-weight="${isProjected ? '600' : '500'}" fill="${isProjected ? '#059669' : '#475569'}" text-anchor="middle">${p.label}</text>
    `;
  });

  svg.innerHTML = gridSvg + ribbonPolygon + histPath + projPath + pointsSvg;
}

// 9B. Render Projected Expenditure Breakdown & Category Burn Rate
function renderSpendingBreakdown(projectedSpend, horizonMonths, projectedProfit) {
  const bar = document.getElementById("spending-proportional-bar");
  const grid = document.getElementById("spending-categories-grid");
  const runwayPill = document.getElementById("treasury-runway-pill");

  const categories = [
    { title: "COGS / Inventory Procurement", pct: 67, color: "#4F46E5" },
    { title: "Operations & Freight Logistics", pct: 15, color: "#06B6D4" },
    { title: "Corporate Payroll & Staffing", pct: 12, color: "#10B981" },
    { title: "Cloud & Information Systems", pct: 6, color: "#8B5CF6" },
  ];

  if (bar) {
    bar.innerHTML = categories.map(c => `
      <div class="spending-category-segment" style="width: ${c.pct}%; background-color: ${c.color};" title="${c.title}: ${c.pct}%"></div>
    `).join("");
  }

  if (grid) {
    grid.innerHTML = categories.map(c => {
      const catAmount = Math.round(projectedSpend * (c.pct / 100));
      return `
        <div class="spending-item-card" style="border-left: 3px solid ${c.color};">
          <div class="spending-item-title">${c.title}</div>
          <div class="spending-item-amount">₹${catAmount.toLocaleString("en-IN")}</div>
          <div class="spending-item-pct" style="color: ${c.color};">${c.pct}% of Outflows</div>
        </div>
      `;
    }).join("");
  }

  if (runwayPill) {
    const liquidCash = enterpriseData.finance.bankCash || 5680000;
    const monthlyBurn = Math.max(1, (projectedSpend / horizonMonths) * 0.35);
    const months = ((liquidCash + (projectedProfit * 0.45)) / monthlyBurn).toFixed(1);
    runwayPill.textContent = `Cash Runway: ${months} Months (Treasury Secure)`;
  }
}

// 9C. Render Statistical Expense Anomaly Detection (Z-Score Outlier Guard)
function renderExpenseAnomalies() {
  const tbody = document.getElementById("analytics-anomalies-tbody");
  if (!tbody) return;

  const anomalies = enterpriseData.analytics.expenseAnomalies || [];
  tbody.innerHTML = anomalies.map(a => {
    let pillClass = "normal";
    let pillLabel = "Normal Variance";
    if (a.status === "ANOMALY" || Math.abs(a.zScore) >= 2.5) {
      pillClass = "anomaly";
      pillLabel = "Outlier Anomaly";
    } else if (a.status === "ELEVATED" || Math.abs(a.zScore) >= 1.5) {
      pillClass = "elevated";
      pillLabel = "Elevated Variance";
    }

    return `
      <tr>
        <td>
          <div style="font-weight:700;">${a.category}</div>
          <small class="text-muted">${a.voucher}</small>
        </td>
        <td class="item-bold">₹${a.amount.toLocaleString("en-IN")}.00</td>
        <td>
          <span class="z-score-pill ${pillClass}">
            Z = ${a.zScore > 0 ? '+' : ''}${a.zScore.toFixed(2)}σ • ${pillLabel}
          </span>
        </td>
        <td style="font-size:0.8rem; color:var(--text-secondary); max-width:320px;">
          ${a.explanation}
        </td>
      </tr>
    `;
  }).join("");
}

// 9D. Render Predictive Customer Churn & Retention Matrix
function renderChurnMatrix() {
  const tbody = document.getElementById("analytics-churn-tbody");
  if (!tbody) return;

  const clients = enterpriseData.analytics.churnClients || [];
  tbody.innerHTML = clients.map(c => {
    const pct = Math.round(c.churnProb * 100);
    const color = pct >= 30 ? "var(--rose-600)" : (pct >= 15 ? "var(--amber-600)" : "var(--emerald-600)");
    const badgeClass = pct >= 30 ? "danger" : (pct >= 15 ? "warning" : "success");

    return `
      <tr>
        <td>
          <div style="font-weight:700;">${c.name}</div>
          <small class="text-muted">Lifetime Value: ${c.monetary}</small>
        </td>
        <td>
          <span style="font-size:0.85rem;">${c.recencyDays} days ago</span>
          <br/><small class="text-muted">${c.frequency} orders booked</small>
        </td>
        <td>
          <div class="churn-bar-container">
            <span class="status-pill ${badgeClass}" style="min-width:48px; text-align:center;">${pct}%</span>
            <div class="churn-progress-track">
              <div class="churn-progress-fill" style="width: ${pct}%; background-color: ${color};"></div>
            </div>
          </div>
        </td>
        <td style="font-size:0.78rem;">
          <div style="margin-bottom:6px; color:var(--text-secondary);">${c.action}</div>
          ${pct >= 20 ? `
            <button class="btn btn-xs btn-outline" onclick="dispatchRetentionAction('${c.name.replace(/'/g, "\\'")}')">
              <i data-lucide="send" style="width:12px; height:12px; margin-right:4px;"></i> Dispatch Retention Strategy
            </button>
          ` : `
            <span class="status-pill success" style="font-size:0.68rem;">Healthy Engagement</span>
          `}
        </td>
      </tr>
    `;
  }).join("");
}

// 9E. Render Predictive Inventory Demand & Stockout Horizon
function renderStockoutHorizon() {
  const tbody = document.getElementById("analytics-stockout-tbody");
  if (!tbody) return;

  const demandForecasts = [
    { sku: "WGH-DIM-006", name: "Automated Parcel Dimensioner Scale", hub: "Delhi North Hub", stock: 4, monthlyDemand: 6, daysUntilStockout: 20, reorderQty: 10, estCost: "₹1,200,000" },
    { sku: "UPS-3K-009", name: "Online UPS 3KVA Double Conversion", hub: "Delhi North Hub", stock: 8, monthlyDemand: 10, daysUntilStockout: 24, reorderQty: 15, estCost: "₹420,000" },
    { sku: "POS-X5-001", name: "NEXUS Core POS Terminal X5", hub: "Mumbai Central FC", stock: 125, monthlyDemand: 45, daysUntilStockout: 83, reorderQty: 50, estCost: "₹1,600,000" },
    { sku: "SCN-PR-002", name: "High-Speed Barcode Scanner Pro", hub: "Mumbai Central FC", stock: 350, monthlyDemand: 80, daysUntilStockout: 131, reorderQty: 100, estCost: "₹1,500,000" },
  ];

  tbody.innerHTML = demandForecasts.map(item => {
    const isCritical = item.daysUntilStockout <= 20;
    const isWarning = item.daysUntilStockout <= 30;
    const pillClass = isCritical ? "danger" : (isWarning ? "warning" : "success");
    const label = isCritical ? `Critical: Stockout in ${item.daysUntilStockout} Days` : (isWarning ? `Warning: Stockout in ${item.daysUntilStockout} Days` : `Healthy: ${item.daysUntilStockout} Days Buffer`);

    return `
      <tr>
        <td>
          <div class="item-bold">${item.sku}</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">${item.name}</div>
        </td>
        <td>${item.hub}</td>
        <td class="item-bold">${item.stock} units</td>
        <td>${item.monthlyDemand} units / mo</td>
        <td>
          <span class="status-pill ${pillClass}">${label}</span>
        </td>
        <td>
          <span style="font-weight:600;">+${item.reorderQty} units</span>
          <span style="font-size:0.75rem; color:var(--text-muted);">(${item.estCost})</span>
        </td>
      </tr>
    `;
  }).join("");
}

// 9F. Interactive Predictive Controls
window.setForecastHorizon = function(days) {
  enterpriseData.analytics.forecastHorizonDays = days;
  [30, 90, 365].forEach(d => {
    const btn = document.getElementById(`horizon-btn-${d}`);
    if (btn) {
      if (d === days) btn.classList.add("active");
      else btn.classList.remove("active");
    }
  });

  renderAnalytics();
  showToast(`Forecast projection horizon set to next ${days} days.`, "info");
};

window.handleScenarioSliderChange = function() {
  const growthSlider = document.getElementById("slider-growth");
  const costSlider = document.getElementById("slider-cost-shock");

  if (growthSlider) {
    const gVal = parseFloat(growthSlider.value);
    enterpriseData.analytics.revenueGrowthPercent = gVal;
    const label = document.getElementById("label-growth-val");
    if (label) label.textContent = `${gVal >= 0 ? '+' : ''}${gVal.toFixed(1)}%`;
  }

  if (costSlider) {
    const cVal = parseFloat(costSlider.value);
    enterpriseData.analytics.costShockPercent = cVal;
    const label = document.getElementById("label-cost-val");
    if (label) label.textContent = `+${cVal.toFixed(1)}%`;
  }

  renderAnalytics();
};

window.recalculateAnalytics = function() {
  const icon = document.getElementById("btn-recalc-icon");
  if (icon) icon.classList.add("spin");

  setTimeout(() => {
    renderAnalytics();
    if (icon) icon.classList.remove("spin");
    showToast("Predictive ML algorithms recalibrated with 95% confidence intervals and latest ERP transactions!", "success");
  }, 650);
};

window.exportForecastReport = function() {
  window.print();
};

window.dispatchRetentionAction = function(clientName) {
  if (enterpriseData.projects && enterpriseData.projects[0]) {
    enterpriseData.projects[0].tasks.unshift({
      title: `Urgent Retention Outreach & 10% Incentive: ${clientName}`,
      assignee: "Rahul Sharma (Sales Lead)",
      status: "IN_PROGRESS"
    });
  }
  showToast(`Retention action for "${clientName}" dispatched to Key Account Manager with priority SLA!`, "success");
  renderHR();
};

// AI Copilot Chat
function setupChatHandlers() {
  const sendBtn = document.getElementById("send-copilot-btn");
  const input = document.getElementById("copilot-input");

  if (sendBtn && input) {
    sendBtn.addEventListener("click", () => handleSendMessage(input));
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") handleSendMessage(input);
    });
  }
}

function sendPrompt(promptText) {
  const input = document.getElementById("copilot-input");
  if (input) {
    input.value = promptText;
    handleSendMessage(input);
  }
}

function handleSendMessage(input) {
  const text = input.value.trim();
  if (!text) return;

  const container = document.getElementById("chat-messages-container");
  if (!container) return;

  // Append user message
  const userMsg = document.createElement("div");
  userMsg.className = "message-bubble user";
  userMsg.innerHTML = `<p>${escapeHtml(text)}</p>`;
  container.appendChild(userMsg);
  input.value = "";
  container.scrollTop = container.scrollHeight;

  // Simulate AI Thinking & Execution
  setTimeout(() => {
    generateAIResponse(text, container);
  }, 500);
}

window.currentLLMModel = "llama3.1";

window.changeLLMModel = function(model) {
  window.currentLLMModel = model;
  const display = document.getElementById("active-model-display");
  const modelLabels = {
    "llama3.1": "Llama 3.1 8B (Ollama)",
    "deepseek-r1": "DeepSeek-R1 (Open-Weights)",
    "mistral": "Mistral 7B (Open-Source)",
    "qwen2.5": "Qwen 2.5 (Open-Source)",
  };
  if (display) display.textContent = modelLabels[model] || model;
  showToast(`Active Open-Source Model: ${modelLabels[model] || model}`, "success");
};

function generateAIResponse(query, container) {
  const q = query.toLowerCase();
  let botReply = "";

  if (q.includes("revenue") || q.includes("margin") || q.includes("profit")) {
    botReply = `
      <div style="display:flex; align-items:center; gap:6px; margin-bottom:8px;">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10B981;"></span>
        <span style="font-size:0.75rem; font-weight:600; color:var(--primary); background:#EEF2FF; padding:2px 8px; border-radius:12px;">🦙 Llama 3.1 (Open-Source) + Double-Entry Tool</span>
      </div>
      <p>Here is your current financial performance breakdown:</p>
      <ul style="margin: 8px 0 8px 18px;">
        <li><strong>Total Revenue:</strong> ₹24.85M (+14.2% MoM expansion)</li>
        <li><strong>Gross Margin:</strong> 30.7%</li>
        <li><strong>Net Operating Profit:</strong> ₹6.12M (24.6% margin)</li>
        <li><strong>Liquid Bank Cash:</strong> ₹5.68M in HDFC Bank current account</li>
      </ul>
      <p>Financial ledger integrity is 100% balanced across all debits and credits.</p>
    `;
  } else if (q.includes("reorder") || q.includes("stock") || q.includes("low")) {
    botReply = `
      <div style="display:flex; align-items:center; gap:6px; margin-bottom:8px;">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10B981;"></span>
        <span style="font-size:0.75rem; font-weight:600; color:var(--primary); background:#EEF2FF; padding:2px 8px; border-radius:12px;">🦙 Llama 3.1 (Open-Source) + Stock Ledger Tool</span>
      </div>
      <p>I inspected physical stock levels across all 3 warehouses:</p>
      <ul style="margin: 8px 0 8px 18px;">
        <li><strong>POS-X5-001 (Mumbai):</strong> 100 units on hand (Safety threshold: 15). Stable for 12 days.</li>
        <li><strong>WGH-DIM-006 (Delhi):</strong> 4 units on hand (Safety threshold: 3). <strong>Low Stock Warning.</strong></li>
        <li><strong>UPS-3K-009 (Delhi):</strong> 8 units on hand (Reorder level: 8). <strong>Reorder Trigger Active.</strong></li>
      </ul>
      <p>Would you like me to formulate a Purchase Order proposal for Honeywell or Zebra?</p>
    `;
  } else if (q.includes("policy") || q.includes("return") || q.includes("warranty")) {
    botReply = `
      <div style="display:flex; align-items:center; gap:6px; margin-bottom:8px;">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10B981;"></span>
        <span style="font-size:0.75rem; font-weight:600; color:var(--primary); background:#EEF2FF; padding:2px 8px; border-radius:12px;">🦙 Llama 3.1 + pgvector RAG Tool</span>
      </div>
      <p><strong>Retrieved from Vector RAG Store (Customer Return Policy 2026):</strong></p>
      <blockquote style="border-left: 3px solid var(--primary); padding-left: 10px; margin: 8px 0; color: var(--text-secondary);">
        "All POS Terminals and Scanners carry a comprehensive 24-month on-site replacement warranty. Damaged or defective items must be reported within 14 calendar days of delivery. Upon QA inspection approval, credit note or replacement dispatch is completed within 48 business hours."
      </blockquote>
      <p style="font-size: 0.78rem; color: var(--text-muted);">Citation: Standard Customer Return & Warranty SLA Policy 2026 (Chunk #0)</p>
    `;
  } else if (q.includes("discount") || q.includes("tata") || q.includes("propose")) {
    botReply = `
      <div style="display:flex; align-items:center; gap:6px; margin-bottom:8px;">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#F59E0B;"></span>
        <span style="font-size:0.75rem; font-weight:600; color:#B45309; background:#FEF3C7; padding:2px 8px; border-radius:12px;">⚡ HITL Action Proposal Formulated</span>
      </div>
      <p>I have verified client <strong>Tata Consumer Products Ltd</strong> has a credit limit of ₹5.0M and healthy RFM engagement (5% churn risk). Since this involves a financial mutation, I formulated a <strong>Human-in-the-Loop Action Proposal</strong>:</p>
      <div class="action-proposal-card">
        <span class="proposal-badge">Pending Approval Request</span>
        <h4 class="proposal-title">15% Volume Discount Override on SO-2026-001</h4>
        <p class="proposal-rationale">Commercial incentive for 150 terminal rollout pipeline.</p>
        <div class="proposal-details">
          Amount Impact: <strong>₹135,000.00</strong> savings for customer.
        </div>
        <div class="proposal-actions">
          <button class="btn btn-sm btn-success" onclick="approveProposal('appr-001')">Approve Action</button>
          <button class="btn btn-sm btn-danger" onclick="rejectProposal('appr-001')">Reject</button>
        </div>
      </div>
    `;
  } else {
    const modelLabels = {
      "llama3.1": "Llama 3.1 8B (Open-Source)",
      "deepseek-r1": "DeepSeek-R1 Reasoning (Open-Weights)",
      "mistral": "Mistral 7B (Open-Source)",
      "qwen2.5": "Qwen 2.5 (Open-Source)",
    };
    const activeLabel = modelLabels[window.currentLLMModel] || "Open-Source LLM";
    botReply = `
      <div style="display:flex; align-items:center; gap:6px; margin-bottom:8px;">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10B981;"></span>
        <span style="font-size:0.75rem; font-weight:600; color:var(--primary); background:#EEF2FF; padding:2px 8px; border-radius:12px;">🦙 ${activeLabel}</span>
      </div>
      <p>I have evaluated your query: <em>"${escapeHtml(query)}"</em> using the <strong>${activeLabel}</strong> open-source pipeline.</p>
      <p><strong>Executive Business Analysis:</strong></p>
      <ul style="margin: 8px 0 8px 18px;">
        <li><strong>Working Capital Velocity:</strong> Target Cash Conversion Cycle (CCC) under 42 days by enforcing 30-day AR terms for Tier-2 distributors.</li>
        <li><strong>Inventory Protection:</strong> Safety stock buffers are actively synchronized across Mumbai, Delhi, and Bengaluru nodes.</li>
        <li><strong>Double-Entry Auditing:</strong> Every proposed journal entry satisfies balanced debit/credit invariants before posting.</li>
      </ul>
      <p style="font-size:0.8rem; color:var(--text-muted); margin-top:6px;">Connected to local Open-Source engine at <code>http://localhost:11434/v1</code> (Ollama)</p>
    `;
  }

  const botMsg = document.createElement("div");
  botMsg.className = "message-bubble bot";
  botMsg.innerHTML = botReply;
  container.appendChild(botMsg);
  container.scrollTop = container.scrollHeight;
  setupLucideIcons();
}

// Sidebar Toggle (3-Dot Menu) & Mobile Backdrop Handler
function setupSidebarToggle() {
  const toggleBtn = document.getElementById("sidebar-toggle-btn");
  const sidebar = document.getElementById("app-sidebar");
  const backdrop = document.getElementById("sidebar-backdrop");
  const navItems = document.querySelectorAll(".sidebar-nav .nav-item");

  if (!toggleBtn || !sidebar) return;

  toggleBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    if (window.innerWidth <= 768) {
      // Mobile behavior: Toggle off-canvas drawer
      const isOpen = sidebar.classList.contains("mobile-open");
      if (isOpen) {
        sidebar.classList.remove("mobile-open");
        if (backdrop) backdrop.classList.remove("active");
      } else {
        sidebar.classList.add("mobile-open");
        if (backdrop) backdrop.classList.add("active");
      }
    } else {
      // Desktop behavior: Collapse to slim icon bar
      sidebar.classList.toggle("collapsed");
    }
  });

  if (backdrop) {
    backdrop.addEventListener("click", () => {
      sidebar.classList.remove("mobile-open");
      backdrop.classList.remove("active");
    });
  }

  // Close mobile sidebar when clicking any navigation link
  navItems.forEach((item) => {
    item.addEventListener("click", () => {
      if (window.innerWidth <= 768) {
        sidebar.classList.remove("mobile-open");
        if (backdrop) backdrop.classList.remove("active");
      }
    });
  });
}

// Light & Dark Theme Switcher Handler
function setupThemeSwitcher() {
  const themeBtn = document.getElementById("theme-toggle-btn");
  const themeIcon = document.getElementById("theme-toggle-icon");
  if (!themeBtn) return;

  // Read saved theme from localStorage
  const savedTheme = localStorage.getItem("nexus_theme") || "light";
  applyTheme(savedTheme);

  themeBtn.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    applyTheme(newTheme);
    localStorage.setItem("nexus_theme", newTheme);
    if (typeof showToast === "function") {
      showToast(`Switched to ${newTheme === "dark" ? "Dark" : "Light"} Mode`, "info");
    }
  });

  function applyTheme(theme) {
    if (theme === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
      if (themeIcon) {
        themeIcon.setAttribute("data-lucide", "sun");
      }
      themeBtn.setAttribute("title", "Switch to Light Mode");
    } else {
      document.documentElement.removeAttribute("data-theme");
      if (themeIcon) {
        themeIcon.setAttribute("data-lucide", "moon");
      }
      themeBtn.setAttribute("title", "Switch to Dark Mode");
    }
    setupLucideIcons();
  }
}

// Drawer Handlers
function setupDrawerHandlers() {
  const openBtn = document.getElementById("open-ai-drawer-btn");
  const closeBtn = document.getElementById("close-ai-drawer-btn");
  const drawer = document.getElementById("ai-drawer");

  if (openBtn && drawer) {
    openBtn.addEventListener("click", () => drawer.classList.add("open"));
  }
  if (closeBtn && drawer) {
    closeBtn.addEventListener("click", () => drawer.classList.remove("open"));
  }
}

function openAIDrawerWithPrompt(promptText) {
  const drawer = document.getElementById("ai-drawer");
  const drawerInput = document.getElementById("drawer-input");
  if (drawer && drawerInput) {
    drawer.classList.add("open");
    drawerInput.value = promptText;
  }
}

// Toast Helper
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <i data-lucide="${type === 'success' ? 'check-circle' : 'alert-circle'}"></i>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  setupLucideIcons();

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(12px)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Utility
function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ==============================================================================
// Modal Window Management & Form Submissions
// ==============================================================================

const DATA = enterpriseData;
window.DATA = enterpriseData;

window.openModal = function(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    if (modalId === 'modal-add-sales-order') {
      updateStockDropdowns();
      updateCustomerDropdowns();
    }
    modal.classList.add("active");
    setupLucideIcons();
    const firstInput = modal.querySelector("input, select");
    if (firstInput) setTimeout(() => firstInput.focus(), 50);
  }
};

window.closeModal = function(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("active");
  }
};

// Global escape key and backdrop click listener
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    document.querySelectorAll(".modal-backdrop.active").forEach((m) => {
      m.classList.remove("active");
    });
  }
});

document.addEventListener("click", (e) => {
  if (e.target.classList && e.target.classList.contains("modal-backdrop")) {
    e.target.classList.remove("active");
  }
});

// 1. Submit: Add Customer (CRM)
window.submitAddCustomer = function() {
  const name = document.getElementById("cust-name").value.trim();
  const segment = document.getElementById("cust-segment").value;
  const contact = document.getElementById("cust-contact").value.trim();
  const email = document.getElementById("cust-email").value.trim();
  const phone = document.getElementById("cust-phone").value.trim();
  const limitVal = parseFloat(document.getElementById("cust-credit-limit").value) || 3500000;
  const city = document.getElementById("cust-city").value.trim();

  if (!name || !contact) {
    showToast("Please enter company name and primary contact person.", "danger");
    return;
  }

  const creditFormatted = "₹" + (limitVal / 1000000).toFixed(2) + "M";

  const newCustomer = {
    name: name,
    segment: segment.includes("Enterprise") ? "Enterprise" : "SMB",
    contact: `${contact} (${email || phone || 'Direct'})`,
    credit: creditFormatted,
    churn: "3%",
    health: "Healthy",
  };

  enterpriseData.customers.unshift(newCustomer);
  renderCRM();

  // Highlight the newly created row
  const tbody = document.getElementById("crm-table-tbody");
  if (tbody && tbody.firstElementChild) {
    tbody.firstElementChild.style.backgroundColor = "rgba(79, 70, 229, 0.08)";
    tbody.firstElementChild.style.transition = "background-color 2s ease";
    setTimeout(() => {
      if (tbody.firstElementChild) tbody.firstElementChild.style.backgroundColor = "";
    }, 2500);
  }

  // Add customer to Sales Order dropdown
  const soCustomer = document.getElementById("so-customer");
  if (soCustomer) {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    soCustomer.prepend(opt);
    soCustomer.value = name;
  }

  document.getElementById("form-add-customer").reset();
  closeModal("modal-add-customer");
  showToast(`New client "${name}" registered successfully in CRM!`, "success");
};

// 2. Submit: Create Sales Order
window.submitAddSalesOrder = function() {
  const customer = document.getElementById("so-customer").value;
  const product = document.getElementById("so-product").value;
  const qty = parseInt(document.getElementById("so-qty").value) || 1;
  const price = parseFloat(document.getElementById("so-price").value) || 15000;
  const terms = document.getElementById("so-terms").value;

  const total = qty * price;
  const totalFormatted = "₹" + total.toLocaleString("en-IN");
  const invNumber = "INV-2026-00" + (enterpriseData.invoices.length + 1);
  const customEmailEl = document.getElementById("so-custom-email");
  const customEmail = customEmailEl && customEmailEl.value.trim() ? customEmailEl.value.trim() : (customer.toLowerCase().replace(/[^a-z0-9]/g, '') + "@enterprise.in");

  const newInvoice = {
    number: invNumber,
    customer: customer,
    customerEmail: customEmail,
    issueDate: "2026-09-09",
    dueDate: "2026-10-09",
    amount: totalFormatted,
    status: terms.includes("Advance") ? "PAID" : "UNPAID",
  };

  enterpriseData.invoices.unshift(newInvoice);
  const newOrder = {
    id: "SO-2026-00" + (enterpriseData.orders.length + 1),
    customer: customer,
    product: product,
    qty: qty,
    date: "2026-09-09",
    amount: totalFormatted,
    status: "CONFIRMED",
    paymentStatus: terms.includes("Advance") ? "PAID" : "UNPAID",
    invoiceNumber: invNumber,
  };
  enterpriseData.orders.unshift(newOrder);

  // DEDUCT STOCK FROM INVENTORY
  let matchedItem = enterpriseData.stock.find(s => product.includes(s.sku));
  if (!matchedItem) {
    matchedItem = enterpriseData.stock.find(s => product.toLowerCase().includes(s.name.toLowerCase()));
  }
  if (!matchedItem && enterpriseData.stock.length > 0) {
    matchedItem = enterpriseData.stock[0];
  }

  let stockNote = "";
  if (matchedItem) {
    const priorQty = matchedItem.qty;
    matchedItem.qty = Math.max(0, matchedItem.qty - qty);
    if (matchedItem.qty === 0) {
      matchedItem.status = "Out of Stock";
    } else if (matchedItem.qty <= (matchedItem.reorder || 10)) {
      matchedItem.status = "Low Stock Alert";
    } else {
      matchedItem.status = "Adequate";
    }
    const valuationDrop = Math.min(priorQty, qty) * (matchedItem.unitRate || 32000);
    enterpriseData.finance.inventoryAsset = Math.max(0, enterpriseData.finance.inventoryAsset - valuationDrop);
    stockNote = ` • Stock updated: ${matchedItem.sku} (${matchedItem.location}) reduced by ${qty} units (Remaining: ${matchedItem.qty} units)`;
  }

  // AUTOMATED FINANCIAL SYNCHRONIZATION FOR SALE
  const isPaid = terms.includes("Advance");
  enterpriseData.finance.salesRevenue += total;

  if (isPaid) {
    enterpriseData.finance.bankCash += total;
  } else {
    enterpriseData.finance.accountsReceivable += total;
  }

  const cogsValuation = Math.round(total * 0.65);
  enterpriseData.finance.cogs += cogsValuation;

  const jvNo = "JV-2026-00" + (enterpriseData.finance.journalEntries.length + 1);
  enterpriseData.finance.journalEntries.unshift({
    voucher: jvNo,
    date: "2026-09-09",
    narration: `Automated Sales Order Revenue Booking - ${invNumber} (${customer})`,
    debit: isPaid ? "1020 • Bank HDFC Current Account" : "1030 • Accounts Receivable",
    credit: "4010 • Product Sales Revenue",
    amount: totalFormatted + ".00",
    status: "Audited & Balanced",
  });

  // Switch view to Sales tab immediately
  switchTab("sales");

  renderSales();
  renderInventory();
  renderFinance();
  renderDashboard();
  updateStockDropdowns();

  // Highlight first row in both orders and invoices tables
  const ordTbody = document.getElementById("sales-orders-tbody");
  if (ordTbody && ordTbody.firstElementChild) {
    ordTbody.firstElementChild.style.backgroundColor = "rgba(79, 70, 229, 0.08)";
    ordTbody.firstElementChild.style.transition = "background-color 2s ease";
    setTimeout(() => {
      if (ordTbody.firstElementChild) ordTbody.firstElementChild.style.backgroundColor = "";
    }, 2500);
  }

  const invTbody = document.getElementById("sales-invoices-tbody");
  if (invTbody && invTbody.firstElementChild) {
    invTbody.firstElementChild.style.backgroundColor = "rgba(79, 70, 229, 0.08)";
    invTbody.firstElementChild.style.transition = "background-color 2s ease";
    setTimeout(() => {
      if (invTbody.firstElementChild) invTbody.firstElementChild.style.backgroundColor = "";
    }, 2500);
  }

  document.getElementById("form-add-sales-order").reset();
  closeModal("modal-add-sales-order");
  showToast(`Sales Order ${newOrder.id} & Tax Invoice ${invNumber} created for ${customer}!${stockNote}`, "success");
};

// 3. Submit: Stock Transfer
window.submitStockTransfer = function() {
  const product = document.getElementById("transfer-product").value;
  const from = document.getElementById("transfer-from").value;
  const to = document.getElementById("transfer-to").value;
  const qty = parseInt(document.getElementById("transfer-qty").value) || 10;

  if (from === to) {
    showToast("Source and destination warehouses must be different.", "danger");
    return;
  }

  const sku = product.split(" - ")[0] || "SKU-TRF";
  const name = product.split(" - ")[1] || product;

  // Add stock transfer record into stock array
  enterpriseData.stock.unshift({
    sku: sku,
    name: `${name} (Transfer)`,
    location: to,
    qty: qty,
    reorder: 5,
    status: "Adequate",
  });

  renderInventory();

  // Highlight first row
  const tbody = document.getElementById("inventory-table-tbody");
  if (tbody && tbody.firstElementChild) {
    tbody.firstElementChild.style.backgroundColor = "rgba(16, 185, 129, 0.08)";
    tbody.firstElementChild.style.transition = "background-color 2s ease";
    setTimeout(() => {
      if (tbody.firstElementChild) tbody.firstElementChild.style.backgroundColor = "";
    }, 2500);
  }

  document.getElementById("form-stock-transfer").reset();
  closeModal("modal-stock-transfer");
  showToast(`Dispatched transfer of ${qty} units to ${to}!`, "success");
};

// 4. Submit: Journal Entry
window.submitJournalEntry = function() {
  const title = document.getElementById("jv-title").value.trim();
  const debit = document.getElementById("jv-debit").value;
  const credit = document.getElementById("jv-credit").value;
  const amount = parseFloat(document.getElementById("jv-amount").value) || 50000;

  if (!title) {
    showToast("Please enter an entry narration memo.", "danger");
    return;
  }

  const amountFormatted = "₹" + amount.toLocaleString("en-IN") + ".00";
  const jvNo = "JV-2026-00" + (enterpriseData.finance.journalEntries.length + 1);

  // If entry touches Bank Account, update bank cash
  if (debit.includes("1110") || debit.includes("1020")) {
    enterpriseData.finance.bankCash += amount;
  } else if (credit.includes("1110") || credit.includes("1020")) {
    enterpriseData.finance.bankCash = Math.max(0, enterpriseData.finance.bankCash - amount);
  }

  enterpriseData.finance.journalEntries.unshift({
    voucher: jvNo,
    date: "2026-09-09",
    narration: title,
    debit: debit,
    credit: credit,
    amount: amountFormatted,
    status: "Audited & Balanced",
  });

  renderFinance();
  document.getElementById("form-journal-entry").reset();
  closeModal("modal-journal-entry");
  showToast(`Balanced Journal Voucher ${jvNo} (${amountFormatted}) posted! Updated Chart of Accounts & General Ledger.`, "success");
};

// 5. Open Settle Payment Modal
window.openSettlePaymentModal = function(invNumber) {
  const inv = enterpriseData.invoices.find(i => i.number === invNumber);
  if (!inv) return;

  document.getElementById("settle-inv-number").value = inv.number;
  document.getElementById("settle-display-inv").textContent = inv.number;
  document.getElementById("settle-display-customer").textContent = inv.customer;
  document.getElementById("settle-amount").value = inv.amount;
  document.getElementById("settle-ref").value = "HDFC-NEFT-" + Math.floor(10000000 + Math.random() * 90000000);

  openModal("modal-settle-invoice");
};

// 6. Submit Invoice Settlement & Sync to Finance
window.submitInvoiceSettlement = function() {
  const invNum = document.getElementById("settle-inv-number").value;
  const method = document.getElementById("settle-method").value;
  const bank = document.getElementById("settle-bank").value;
  const ref = document.getElementById("settle-ref").value;
  const payDate = document.getElementById("settle-date").value;

  const inv = enterpriseData.invoices.find(i => i.number === invNum);
  if (!inv) return;

  inv.status = "PAID";
  inv.settlementDate = payDate;
  inv.settlementRef = ref;
  inv.settlementMethod = method;

  // Extract raw amount to update Finance
  const rawAmt = parseFloat(inv.amount.replace(/[^0-9.]/g, "")) || 0;

  // 1. Debit Bank Cash (Liquid Treasury Increases)
  enterpriseData.finance.bankCash += rawAmt;

  // 2. Credit Accounts Receivable (Trade Debtors Decreases)
  enterpriseData.finance.accountsReceivable = Math.max(0, enterpriseData.finance.accountsReceivable - rawAmt);

  // 3. Post double-entry General Ledger entry
  const jvNum = "JV-2026-00" + (enterpriseData.finance.journalEntries.length + 1);
  enterpriseData.finance.journalEntries.unshift({
    voucher: jvNum,
    date: payDate,
    narration: `Customer Settlement - ${inv.customer} (${inv.number}) via ${method.split(' ')[0]}`,
    debit: "1020 • Bank HDFC Current Account",
    credit: "1030 • Accounts Receivable",
    amount: inv.amount.includes("₹") ? inv.amount : "₹" + inv.amount,
    status: "Audited & Balanced",
  });

  // 4. Also update matching sales order if present
  const order = enterpriseData.orders.find(o => o.customer === inv.customer);
  if (order) {
    order.payment = "Paid";
  }

  // Synchronize both modules in the DOM
  renderSales();
  renderFinance();
  closeModal("modal-settle-invoice");

  showToast(`Settlement recorded! ${invNum} marked PAID. Realized ₹${(rawAmt/1000000).toFixed(2)}M into HDFC Bank Account. Double-entry GL Voucher ${jvNum} posted to Finance.`, "success");
};

// 7. View Receipt Modal
window.openReceiptModal = function(invNumber) {
  const inv = enterpriseData.invoices.find(i => i.number === invNumber) || {
    number: invNumber,
    customer: "Tata Consumer Products Ltd",
    issueDate: "2026-09-01",
    dueDate: "2026-09-30",
    amount: "₹1,062,000",
    status: "PAID",
    settlementRef: "TXN-HDFC-99214"
  };

  document.getElementById("receipt-inv-num").textContent = inv.number;
  document.getElementById("receipt-inv-date").textContent = inv.issueDate;
  document.getElementById("receipt-inv-due").textContent = inv.dueDate;
  document.getElementById("receipt-cust-name").textContent = inv.customer;

  const stampContainer = document.getElementById("receipt-status-stamp-container");
  const isPaid = inv.status === "PAID";

  if (stampContainer) {
    stampContainer.innerHTML = isPaid
      ? `<span class="receipt-status-stamp paid" id="receipt-stamp">✓ PAID &amp; SETTLED</span>`
      : `<span class="receipt-status-stamp unpaid" id="receipt-stamp">⚠ UNPAID / OUTSTANDING</span>`;
  }

  document.getElementById("receipt-inv-ref").textContent = isPaid
    ? (inv.settlementRef || "HDFC-RTGS-89104812")
    : "Pending Payment Settlement";

  // Parse amount for table display
  const rawNum = parseFloat(inv.amount.replace(/[^0-9.]/g, "")) || 1062000;
  const taxable = Math.round(rawNum / 1.18);
  const gst = rawNum - taxable;

  document.getElementById("receipt-subtotal").textContent = "₹" + taxable.toLocaleString("en-IN") + ".00";
  document.getElementById("receipt-gst").textContent = "₹" + gst.toLocaleString("en-IN") + ".00";
  document.getElementById("receipt-grand-total").textContent = inv.amount.includes("₹") ? inv.amount : "₹" + inv.amount;

  const itemsTbody = document.getElementById("receipt-items-tbody");
  if (itemsTbody) {
    itemsTbody.innerHTML = `
      <tr>
        <td>
          <div style="font-weight:700;">NEXUS POS Terminal Duo Hardware Deployment</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">SKU: POS-X5-001 • Comprehensive 24-Month On-Site SLA</div>
        </td>
        <td>8471</td>
        <td>15 Units</td>
        <td>₹${Math.round(taxable / 15).toLocaleString("en-IN")}.00</td>
        <td>18% IGST</td>
        <td style="font-weight:700;">₹${taxable.toLocaleString("en-IN")}.00</td>
      </tr>
    `;
  }

  openModal("modal-view-receipt");
};

// 8. Print Receipt Handler
window.printReceipt = function() {
  window.print();
};

// 9. Open Email Invoice / Receipt Modal
window.openEmailInvoiceModal = function(invNumber) {
  const inv = enterpriseData.invoices.find(i => i.number === invNumber) || {
    number: invNumber || "INV-2026-001",
    customer: "Tata Consumer Products Ltd",
    customerEmail: "accounts.payable@tataconsumer.com",
    issueDate: "2026-09-01",
    dueDate: "2026-09-30",
    amount: "₹1,062,000",
    status: "PAID",
    settlementRef: "TXN-HDFC-99214"
  };

  // Populate metadata fields
  const invInput = document.getElementById("email-inv-number");
  const dispInv = document.getElementById("email-display-inv");
  const dispCust = document.getElementById("email-display-customer");
  const emailTo = document.getElementById("email-to-address");
  const emailSubj = document.getElementById("email-subject");
  const emailBody = document.getElementById("email-body-text");
  const emailAttach = document.getElementById("email-attachment-name");

  if (invInput) invInput.value = inv.number;
  if (dispInv) dispInv.textContent = inv.number;
  if (dispCust) dispCust.textContent = inv.customer;

  // Resolve custom email: preference to invoice's saved customerEmail, then customer list match
  let targetEmail = inv.customerEmail || "";
  if (!targetEmail) {
    const cust = enterpriseData.customers.find(c => c.name.toLowerCase() === inv.customer.toLowerCase());
    if (cust && cust.contact && cust.contact.includes("@")) {
      targetEmail = cust.contact;
    } else {
      targetEmail = inv.customer.toLowerCase().replace(/[^a-z0-9]/g, '') + "@enterprise.in";
    }
  }

  if (emailTo) emailTo.value = targetEmail;
  if (emailSubj) emailSubj.value = `Tax Invoice & Settlement Receipt: ${inv.number} - Nexus Retail Pvt Ltd`;

  const isPaid = inv.status === "PAID";
  const refText = isPaid ? (inv.settlementRef ? ` | Payment Ref: ${inv.settlementRef}` : " | Settled via Bank Wire") : " | Payment Due: 30 Days";

  if (emailBody) {
    emailBody.value = `Dear ${inv.customer} Accounts & Finance Team,

Please find attached the official computerized Tax Invoice & Settlement Summary issued by Nexus Retail Pvt Ltd.

• Invoice Number: ${inv.number}
• Total Valuation: ${inv.amount}
• Issue Date: ${inv.issueDate}
• Due Date: ${inv.dueDate}
• Settlement Status: ${inv.status}${refText}

An audited digital copy (PDF) is attached to this transmission. If you need updated statement ledgers or alternate billing breakdowns, reply directly to this notification.

Kind regards,
Corporate Accounts & Treasury Desk
Nexus Retail Pvt Ltd • Automated Enterprise Engine`;
  }

  if (emailAttach) emailAttach.textContent = `Tax_Invoice_${inv.number}.pdf`;

  // Reset submit button state
  const sendBtn = document.getElementById("btn-send-invoice-email");
  if (sendBtn) {
    sendBtn.innerHTML = `<i data-lucide="send"></i><span>Send Email Now</span>`;
    sendBtn.disabled = false;
  }

  openModal("modal-email-invoice");
  setupLucideIcons();
};

// 10. Submit Email Invoice Dispatch
window.submitEmailInvoice = function() {
  const invNumber = document.getElementById("email-inv-number") ? document.getElementById("email-inv-number").value : "";
  const recipientEmail = document.getElementById("email-to-address") ? document.getElementById("email-to-address").value.trim() : "";
  const subject = document.getElementById("email-subject") ? document.getElementById("email-subject").value.trim() : "";
  const sendBtn = document.getElementById("btn-send-invoice-email");

  if (!recipientEmail || !recipientEmail.includes("@") || !recipientEmail.includes(".")) {
    showToast("Please enter a valid recipient email address.", "danger");
    return;
  }

  // Update target invoice's recipient in data store
  const inv = enterpriseData.invoices.find(i => i.number === invNumber);
  if (inv) {
    inv.customerEmail = recipientEmail;
    inv.lastDispatched = new Date().toISOString();
  }

  // Animate sending button
  if (sendBtn) {
    sendBtn.innerHTML = `<i data-lucide="loader" class="spin" style="width:14px; height:14px; margin-right:4px;"></i><span>Dispatching Email...</span>`;
    sendBtn.disabled = true;
    setupLucideIcons();
  }

  setTimeout(() => {
    if (sendBtn) {
      sendBtn.innerHTML = `<i data-lucide="check" style="width:14px; height:14px; margin-right:4px;"></i><span>Dispatched!</span>`;
    }

    setTimeout(() => {
      closeModal("modal-email-invoice");
      if (sendBtn) {
        sendBtn.innerHTML = `<i data-lucide="send"></i><span>Send Email Now</span>`;
        sendBtn.disabled = false;
      }
      showToast(`Invoice ${invNumber} and receipt PDF successfully dispatched to ${recipientEmail}!`, "success");
      renderSales();
    }, 450);
  }, 750);
};
// 11. Synchronize Live Stock Quantities in Dropdown Selectors
function updateStockDropdowns() {
  const soProductSelect = document.getElementById("so-product");
  const inwardExistingSelect = document.getElementById("inward-existing-sku");

  if (soProductSelect) {
    soProductSelect.innerHTML = enterpriseData.stock.map(s => `
      <option value="${s.sku} - ${s.name}">
        ${s.sku} • ${s.name} (${s.location} — Stock: ${s.qty} units)
      </option>
    `).join("");
  }

  if (inwardExistingSelect) {
    const seen = new Set();
    const uniqueItems = [];
    for (const s of enterpriseData.stock) {
      if (!seen.has(s.sku)) {
        seen.add(s.sku);
        uniqueItems.push(s);
      }
    }
    inwardExistingSelect.innerHTML = uniqueItems.map(s => `
      <option value="${s.sku}">
        ${s.sku} • ${s.name}
      </option>
    `).join("");
  }
}

function updateCustomerDropdowns() {
  const soCustomerSelect = document.getElementById("so-customer");
  if (soCustomerSelect) {
    const currVal = soCustomerSelect.value;
    soCustomerSelect.innerHTML = enterpriseData.customers.map(c => `
      <option value="${escapeHtml(c.name)}">${escapeHtml(c.name)} (${c.segment})</option>
    `).join("");
    if (currVal && enterpriseData.customers.some(c => c.name === currVal)) {
      soCustomerSelect.value = currVal;
    }
  }
}

// 12. Toggle Inward Product Catalog Mode
window.handleInwardProductChange = function() {
  const type = document.getElementById("inward-product-type").value;
  const existingGroup = document.getElementById("group-existing-stock");
  const newGroup = document.getElementById("group-new-stock");

  if (type === "NEW") {
    if (existingGroup) existingGroup.style.display = "none";
    if (newGroup) newGroup.style.display = "block";
  } else {
    if (existingGroup) existingGroup.style.display = "block";
    if (newGroup) newGroup.style.display = "none";
  }
};

// 13. Submit: Inward Stock Receipt / Add Stock to Inventory
window.submitAddStock = function() {
  const type = document.getElementById("inward-product-type") ? document.getElementById("inward-product-type").value : "EXISTING";
  const location = document.getElementById("inward-location").value;
  const qty = parseInt(document.getElementById("inward-qty").value) || 1;
  const unitRate = parseFloat(document.getElementById("inward-unit-cost").value) || 20000;
  const supplier = document.getElementById("inward-supplier").value.trim() || "Foxconn Electronics India Pvt Ltd";
  const notes = document.getElementById("inward-notes") ? document.getElementById("inward-notes").value.trim() : "";

  let targetSku = "";
  let productName = "";

  if (type === "NEW") {
    targetSku = (document.getElementById("inward-new-sku").value.trim() || "SKU-NEW-001").toUpperCase();
    productName = document.getElementById("inward-new-name").value.trim() || "Enterprise Hardware Asset";
  } else {
    targetSku = document.getElementById("inward-existing-sku").value;
    const existing = enterpriseData.stock.find(s => s.sku === targetSku);
    productName = existing ? existing.name : "Enterprise Equipment";
  }

  // Check if item exists at the specific warehouse
  const existingAtLocation = enterpriseData.stock.find(s => s.sku === targetSku && s.location === location);

  if (existingAtLocation) {
    existingAtLocation.qty += qty;
    existingAtLocation.unitRate = unitRate;
    existingAtLocation.status = existingAtLocation.qty <= (existingAtLocation.reorder || 10) ? "Low Stock Alert" : "Adequate";
  } else {
    // Add new inventory record for this SKU at warehouse
    enterpriseData.stock.unshift({
      sku: targetSku,
      name: productName,
      location: location,
      qty: qty,
      reorder: 10,
      status: "Adequate",
      unitRate: unitRate,
    });
  }

  // Post addition into Finance and modules
  const assetValuationIncrease = qty * unitRate;
  enterpriseData.finance.inventoryAsset += assetValuationIncrease;
  enterpriseData.finance.bankCash = Math.max(0, enterpriseData.finance.bankCash - assetValuationIncrease);

  const jvNo = "JV-2026-00" + (enterpriseData.finance.journalEntries.length + 1);
  enterpriseData.finance.journalEntries.unshift({
    voucher: jvNo,
    date: "2026-09-09",
    narration: `Inward Stock Inventory Purchase - ${targetSku} (${qty} units @ ₹${unitRate.toLocaleString('en-IN')} from ${supplier})`,
    debit: "1040 • Perpetual Inventory Asset",
    credit: "1020 • Bank HDFC Current Account",
    amount: "₹" + assetValuationIncrease.toLocaleString("en-IN") + ".00",
    status: "Audited & Balanced",
  });

  renderInventory();
  renderFinance();
  renderDashboard();
  updateStockDropdowns();

  // Highlight first row in inventory table
  const tbody = document.getElementById("inventory-table-tbody");
  if (tbody && tbody.firstElementChild) {
    tbody.firstElementChild.style.backgroundColor = "rgba(16, 185, 129, 0.15)";
    tbody.firstElementChild.style.transition = "background-color 2s ease";
    setTimeout(() => {
      if (tbody.firstElementChild) tbody.firstElementChild.style.backgroundColor = "";
    }, 2500);
  }

  document.getElementById("form-add-stock").reset();
  closeModal("modal-add-stock");
  showToast(`Inward stock booked! +${qty} units of ${targetSku} added to ${location}. Total asset value +₹${assetValuationIncrease.toLocaleString("en-IN")}.`, "success");
};

