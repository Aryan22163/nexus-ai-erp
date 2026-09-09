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
    { id: "SO-2026-001", customer: "Tata Consumer Products Ltd", date: "2026-08-30", amount: "₹1,062,000", status: "CONFIRMED" },
    { id: "SO-2026-002", customer: "Reliance Retail Ventures", date: "2026-09-02", amount: "₹2,450,000", status: "CONFIRMED" },
    { id: "SO-2026-003", customer: "Croma (Infiniti Retail)", date: "2026-09-05", amount: "₹890,000", status: "FULFILLED" },
    { id: "SO-2026-004", customer: "Zepto Hyperlocal Warehouses", date: "2026-09-07", amount: "₹540,000", status: "CONFIRMED" },
  ],
  stock: [
    { sku: "POS-X5-001", name: "NEXUS Core POS Terminal X5", location: "Mumbai Central FC", qty: 100, reorder: 15, status: "Adequate" },
    { sku: "SCN-PR-002", name: "High-Speed Barcode Scanner Pro", location: "Mumbai Central FC", qty: 350, reorder: 25, status: "Adequate" },
    { sku: "PDA-IND-004", name: "Rugged Industrial Handheld PDA", location: "Bengaluru Tech Depot", qty: 75, reorder: 10, status: "Adequate" },
    { sku: "RFID-GT-005", name: "Smart RFID Gate Reader Portal", location: "Bengaluru Tech Depot", qty: 20, reorder: 5, status: "Adequate" },
    { sku: "WGH-DIM-006", name: "Automated Parcel Dimensioner Scale", location: "Delhi North Hub", qty: 4, reorder: 3, status: "Low Stock Alert" },
    { sku: "UPS-3K-009", name: "Online UPS 3KVA Double Conversion", location: "Delhi North Hub", qty: 8, reorder: 8, status: "Reorder Required" },
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
    { number: "INV-2026-001", customer: "Tata Consumer Products Ltd", issueDate: "2026-09-01", dueDate: "2026-09-30", amount: "₹1,062,000", status: "PAID" },
    { number: "INV-2026-002", customer: "Reliance Retail Ventures", issueDate: "2026-09-03", dueDate: "2026-10-03", amount: "₹2,450,000", status: "UNPAID" },
    { number: "INV-2026-003", customer: "Croma (Infiniti Retail Ltd)", issueDate: "2026-09-05", dueDate: "2026-10-05", amount: "₹890,000", status: "PAID" },
  ],
  pendingApprovals: [
    {
      id: "appr-001",
      actionType: "DISCOUNT_OVERRIDE",
      title: "15.0% Enterprise Volume Discount Override",
      requester: "Rahul Sharma (Sales Manager)",
      customer: "Tata Consumer Products Ltd",
      orderId: "SO-2026-001",
      savings: "₹135,000.00",
      rationale: "Enterprise contract agreement for 150 terminal rollout pipeline across tier-1 regional offices.",
      status: "PENDING",
    }
  ],
  projects: [
    {
      name: "Mumbai DC Automated Dimensioner Integration",
      code: "PRJ-WMS-2026",
      budget: "₹1,500,000",
      spent: "₹420,000",
      progress: 68,
      status: "ACTIVE",
      tasks: [
        { title: "Deploy Smart Weighing Scale Drivers", assignee: "Vikram Aditya", status: "DONE" },
        { title: "Validate Real-Time Stock Ledger Webhook Synchronization", assignee: "Vikram Aditya", status: "IN_PROGRESS" }
      ]
    }
  ]
};

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupLucideIcons();
  checkApiConnectivity();
  renderDashboard();
  renderCRM();
  renderSales();
  renderInventory();
  renderFinance();
  renderHR();
  renderApprovals();
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
    stockTbody.innerHTML = enterpriseData.stock.slice(0, 4).map(s => `
      <tr>
        <td class="item-bold">${s.name} <br/><small class="text-muted">${s.sku}</small></td>
        <td>${s.location}</td>
        <td class="item-bold">${s.qty}</td>
        <td>${s.reorder}</td>
        <td>
          <span class="status-pill ${s.status === 'Adequate' ? 'success' : 'warning'}">
            ${s.status}
          </span>
        </td>
      </tr>
    `).join("");
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
  const tbody = document.getElementById("sales-invoices-tbody");
  if (!tbody) return;

  tbody.innerHTML = enterpriseData.invoices.map(inv => `
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
        <button class="btn btn-xs btn-outline" onclick="openReceiptModal('${inv.number}')">
          <i data-lucide="receipt" style="width:13px; height:13px; margin-right:4px;"></i> View Receipt
        </button>
      </td>
    </tr>
  `).join("");
  setupLucideIcons();
}

// Render Inventory
function renderInventory() {
  const tbody = document.getElementById("inventory-table-tbody");
  if (!tbody) return;

  tbody.innerHTML = enterpriseData.stock.map(item => `
    <tr>
      <td class="item-bold">${item.sku}</td>
      <td>${item.name}</td>
      <td>${item.location}</td>
      <td class="item-bold">${item.qty} units</td>
      <td>₹${(item.qty * 320).toLocaleString()}</td>
      <td class="item-bold">₹${(item.qty * 32000).toLocaleString()}</td>
    </tr>
  `).join("");
}

// Render Finance
function renderFinance() {
  const coaTree = document.getElementById("coa-tree-view");
  if (coaTree) {
    coaTree.innerHTML = `
      <div class="coa-node group">
        <div class="coa-node-header"><span>1000 • ASSETS</span><span>₹14,100,000.00</span></div>
      </div>
      <div class="coa-node" style="margin-left: 18px;">
        <div class="coa-node-header"><span>1020 • Bank HDFC Current Account</span><span>₹5,680,000.00</span></div>
      </div>
      <div class="coa-node" style="margin-left: 18px;">
        <div class="coa-node-header"><span>1040 • Inventory Perpetual Asset</span><span>₹8,420,000.00</span></div>
      </div>
      <div class="coa-node group" style="margin-top: 10px;">
        <div class="coa-node-header"><span>2000 • LIABILITIES</span><span>₹4,200,000.00</span></div>
      </div>
      <div class="coa-node" style="margin-left: 18px;">
        <div class="coa-node-header"><span>2010 • Accounts Payable (OEM Creditors)</span><span>₹4,200,000.00</span></div>
      </div>
      <div class="coa-node group" style="margin-top: 10px;">
        <div class="coa-node-header"><span>3000 • EQUITY</span><span>₹5,000,000.00</span></div>
      </div>
      <div class="coa-node" style="margin-left: 18px;">
        <div class="coa-node-header"><span>3020 • Paid-Up Share Capital</span><span>₹5,000,000.00</span></div>
      </div>
    `;
  }

  const preview = document.getElementById("financial-preview");
  if (preview) {
    preview.innerHTML = `
      <div class="stmt-row"><span>Total Gross Sales Revenue</span><span class="item-bold">₹24,850,000.00</span></div>
      <div class="stmt-row"><span>Cost of Goods Sold (COGS)</span><span class="text-muted">- ₹17,200,000.00</span></div>
      <div class="stmt-row total"><span>Gross Profit</span><span class="text-emerald-600">₹7,650,000.00</span></div>
      <div class="stmt-row"><span>Operating Overhead & Cloud Infrastructure</span><span class="text-muted">- ₹1,530,000.00</span></div>
      <div class="stmt-row total"><span>Net Operating Profit</span><span class="text-primary">₹6,120,000.00 (24.6%)</span></div>
    `;
  }
}

// Render HR & Projects
function renderHR() {
  const container = document.getElementById("projects-container-view");
  if (!container) return;

  container.innerHTML = enterpriseData.projects.map(p => `
    <div style="padding: 16px 20px; border-bottom: 1px solid var(--border-light);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <h4 style="font-weight: 700;">${p.name} <span class="text-muted" style="font-size: 0.8rem;">(${p.code})</span></h4>
        <span class="status-pill success">${p.status}</span>
      </div>
      <div style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 12px;">
        Budget: <strong class="item-bold">${p.budget}</strong> | Spent: <strong class="item-bold">${p.spent}</strong> | Progress: <strong>${p.progress}%</strong>
      </div>
      <div style="background: #E2E8F0; border-radius: 999px; height: 7px; overflow: hidden; margin-bottom: 16px;">
        <div style="width: ${p.progress}%; background: var(--primary); height: 100%;"></div>
      </div>
      <h5 style="font-size: 0.78rem; text-transform: uppercase; font-weight: 700; color: var(--text-muted); margin-bottom: 8px;">Deliverable Tasks</h5>
      ${p.tasks.map(t => `
        <div style="display: flex; justify-content: space-between; padding: 6px 0; font-size: 0.82rem; border-top: 1px dashed var(--border-light);">
          <span>${t.title} <small class="text-muted">(${t.assignee})</small></span>
          <span class="status-pill ${t.status === 'DONE' ? 'success' : 'warning'}">${t.status}</span>
        </div>
      `).join("")}
    </div>
  `).join("");
}

// Render Approvals
function renderApprovals() {
  const container = document.getElementById("approvals-container-view");
  if (!container) return;

  const countBadge = document.getElementById("pending-approval-count");
  if (countBadge) {
    countBadge.innerText = enterpriseData.pendingApprovals.length;
  }

  if (enterpriseData.pendingApprovals.length === 0) {
    container.innerHTML = `
      <div class="panel-card" style="padding: 40px; text-align: center;">
        <i data-lucide="check-circle" style="width: 48px; height: 48px; color: var(--emerald-600); margin-bottom: 12px;"></i>
        <h3 class="panel-title">All Action Proposals Reviewed</h3>
        <p class="text-muted" style="font-size: 0.86rem; margin-top: 6px;">No pending Human-in-the-Loop mutations requiring your authorization.</p>
      </div>
    `;
    setupLucideIcons();
    return;
  }

  container.innerHTML = enterpriseData.pendingApprovals.map(appr => `
    <div class="panel-card" style="margin-bottom: 16px; padding: 22px;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
        <div>
          <span class="proposal-badge">Pending Review • High Value Override</span>
          <h3 style="font-size: 1.05rem; font-weight: 700; margin-top: 4px;">${appr.title}</h3>
          <p style="font-size: 0.84rem; color: var(--text-muted);">Requested by: <strong>${appr.requester}</strong> for <strong>${appr.customer}</strong></p>
        </div>
        <span class="status-pill warning">Requires Approval</span>
      </div>
      <div class="proposal-details">
        <p><strong>Rationale:</strong> ${appr.rationale}</p>
        <p style="margin-top: 4px;"><strong>Financial Impact:</strong> Client savings of <strong class="item-bold text-rose-600">${appr.savings}</strong> against base catalog pricing.</p>
      </div>
      <div class="proposal-actions">
        <button class="btn btn-success" onclick="approveProposal('${appr.id}')">
          <i data-lucide="check"></i> Approve & Execute Mutation
        </button>
        <button class="btn btn-danger" onclick="rejectProposal('${appr.id}')">
          <i data-lucide="x"></i> Reject
        </button>
      </div>
    </div>
  `).join("");

  setupLucideIcons();
}

// Approve / Reject Proposal
function approveProposal(id) {
  enterpriseData.pendingApprovals = enterpriseData.pendingApprovals.filter(p => p.id !== id);
  renderApprovals();
  showToast("Action Proposal APPROVED: 15% discount applied to SO-2026-001 with audit log.", "success");
}

function rejectProposal(id) {
  enterpriseData.pendingApprovals = enterpriseData.pendingApprovals.filter(p => p.id !== id);
  renderApprovals();
  showToast("Action Proposal REJECTED: Order preserved at standard catalog pricing.", "danger");
}

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

  const newInvoice = {
    number: invNumber,
    customer: customer,
    issueDate: "2026-09-09",
    dueDate: "2026-10-09",
    amount: totalFormatted,
    status: terms.includes("Advance") ? "PAID" : "UNPAID",
  };

  enterpriseData.invoices.unshift(newInvoice);
  enterpriseData.orders.unshift({
    id: "SO-2026-00" + (enterpriseData.orders.length + 1),
    customer: customer,
    date: "2026-09-09",
    amount: totalFormatted,
    status: "CONFIRMED",
  });

  renderSales();

  // Highlight first row
  const tbody = document.getElementById("sales-invoices-tbody");
  if (tbody && tbody.firstElementChild) {
    tbody.firstElementChild.style.backgroundColor = "rgba(79, 70, 229, 0.08)";
    tbody.firstElementChild.style.transition = "background-color 2s ease";
    setTimeout(() => {
      if (tbody.firstElementChild) tbody.firstElementChild.style.backgroundColor = "";
    }, 2500);
  }

  document.getElementById("form-add-sales-order").reset();
  closeModal("modal-add-sales-order");
  showToast(`Sales invoice ${invNumber} generated for ${customer}!`, "success");
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

  const amountFormatted = "₹" + amount.toLocaleString("en-IN");
  const jvNo = "JV-2026-00" + Math.floor(10 + Math.random() * 90);

  document.getElementById("form-journal-entry").reset();
  closeModal("modal-journal-entry");
  showToast(`Balanced Journal Voucher ${jvNo} (${amountFormatted}) posted! (Dr: ${debit.split(' - ')[1] || debit} / Cr: ${credit.split(' - ')[1] || credit})`, "success");
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

// 6. Submit Invoice Settlement
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

  // Also update matching order if present
  const order = enterpriseData.orders.find(o => o.customer === inv.customer);
  if (order) {
    order.payment = "Paid";
  }

  renderSales();
  closeModal("modal-settle-invoice");

  showToast(`Settlement recorded! Invoice ${invNum} marked as PAID via ${method.split(' ')[0]}.`, "success");
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



