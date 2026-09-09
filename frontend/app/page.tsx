import React from "react";
import {
  TrendingUp,
  AlertTriangle,
  Sparkles,
  DollarSign,
  Package,
  Users,
  Building2,
  ArrowUpRight,
  Bot,
  Layers,
  ArrowRight,
} from "lucide-react";

export default function HomePage() {
  const kpis = [
    {
      title: "Total Revenue",
      value: "₹24.8M",
      change: "+12.4%",
      isPositive: true,
      icon: DollarSign,
      color: "text-emerald-400",
    },
    {
      title: "Net Operating Margin",
      value: "23.4%",
      change: "+2.1%",
      isPositive: true,
      icon: TrendingUp,
      color: "text-indigo-400",
    },
    {
      title: "Inventory Valuation",
      value: "₹8.4M",
      change: "-1.8%",
      isPositive: false,
      icon: Package,
      color: "text-amber-400",
    },
    {
      title: "Active Customers",
      value: "1,248",
      change: "+84 this mo",
      isPositive: true,
      icon: Users,
      color: "text-cyan-400",
    },
  ];

  const aiInsights = [
    {
      title: "Churn Risk Alert",
      description: "7 high-value accounts show 35+ days of inactivity and negative sentiment in recent emails.",
      actionText: "Review Accounts",
      badge: "High Risk",
      badgeColor: "bg-rose-500/20 text-rose-400 border-rose-500/30",
    },
    {
      title: "Inventory Stockout Forecast",
      description: "SKU-402 (Hydraulic Valve) may stock out in 11 days based on current order velocity.",
      actionText: "Draft Purchase Request",
      badge: "Stock Alert",
      badgeColor: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    },
    {
      title: "Revenue Opportunity",
      description: "Q3 sales trend projects 8.2% expansion if enterprise quotations are finalized this week.",
      actionText: "View Pipeline",
      badge: "Growth",
      badgeColor: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    },
  ];

  const modules = [
    { name: "CRM & Leads", desc: "Pipelines, deals, customer 360", icon: Users },
    { name: "Sales & Invoicing", desc: "Quotations, orders, payments", icon: TrendingUp },
    { name: "Procurement", desc: "Suppliers, POs, receipt matching", icon: Building2 },
    { name: "Inventory", desc: "Multi-warehouse, batch, ledger", icon: Package },
    { name: "Finance & Ledger", desc: "Double-entry accounts, P&L, balance sheet", icon: DollarSign },
    { name: "HR & Projects", desc: "Timesheets, tasks, attendance", icon: Layers },
  ];

  return (
    <main className="flex-1 flex flex-col min-h-screen bg-[#070a13] text-slate-100">
      {/* Top Navigation */}
      <header className="border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-md sticky top-0 z-40 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
              NEXUS AI
            </h1>
            <p className="text-xs text-slate-400 font-medium">Nexus Retail Pvt Ltd</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            System Operational
          </div>
          <button className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-all shadow-md shadow-indigo-600/20">
            <Bot className="w-4 h-4" />
            Launch Copilot
          </button>
        </div>
      </header>

      {/* Main Workspace Body */}
      <div className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full space-y-8">
        {/* Hero AI Command Prompt Box */}
        <section className="relative overflow-hidden rounded-2xl border border-indigo-500/30 bg-gradient-to-br from-indigo-950/40 via-slate-900/60 to-slate-950 p-6 md:p-8 shadow-2xl backdrop-blur-xl">
          <div className="relative z-10 max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              <Sparkles className="w-3.5 h-3.5" />
              Autonomous Enterprise Copilot
            </div>
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
              Ask anything about your business operations.
            </h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              Nexus AI queries your live general ledger, stock levels, CRM pipelines, and documents to answer complex inquiries and execute authorized actions.
            </p>
            <div className="pt-2 flex flex-col sm:flex-row gap-2">
              <div className="relative flex-1">
                <input
                  type="text"
                  placeholder='Try "Why did sales decline this month?" or "Generate executive summary"'
                  className="w-full bg-slate-900/80 border border-slate-700/70 focus:border-indigo-500 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40 transition-all shadow-inner"
                />
              </div>
              <button className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold px-6 py-3 rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30">
                Analyze
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </section>

        {/* KPI Grid */}
        <section className="space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Executive Performance Metrics
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {kpis.map((kpi, idx) => {
              const Icon = kpi.icon;
              return (
                <div
                  key={idx}
                  className="bg-slate-900/60 border border-slate-800/80 hover:border-slate-700/80 rounded-xl p-5 transition-all flex flex-col justify-between space-y-4"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-slate-400">{kpi.title}</span>
                    <div className="p-2 rounded-lg bg-slate-800/60">
                      <Icon className={`w-4 h-4 ${kpi.color}`} />
                    </div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold tracking-tight text-white">{kpi.value}</div>
                    <div className="text-xs flex items-center gap-1 font-medium mt-1">
                      <span className={kpi.isPositive ? "text-emerald-400" : "text-amber-400"}>
                        {kpi.change}
                      </span>
                      <span className="text-slate-500">vs last month</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Proactive AI Insights Section */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              Proactive AI Insights & Anomalies
            </h3>
            <span className="text-xs text-indigo-400 hover:text-indigo-300 font-medium cursor-pointer">
              View all 8 alerts →
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {aiInsights.map((insight, idx) => (
              <div
                key={idx}
                className="bg-slate-900/50 border border-slate-800/90 rounded-xl p-5 flex flex-col justify-between space-y-4 hover:border-indigo-500/40 transition-all"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${insight.badgeColor}`}>
                      {insight.badge}
                    </span>
                  </div>
                  <h4 className="text-sm font-semibold text-white">{insight.title}</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">{insight.description}</p>
                </div>
                <button className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1.5 pt-2 border-t border-slate-800">
                  {insight.actionText}
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Core ERP Modules Quick Access */}
        <section className="space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Business Operating Modules
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {modules.map((mod, idx) => {
              const Icon = mod.icon;
              return (
                <div
                  key={idx}
                  className="group bg-slate-900/40 border border-slate-800/80 hover:border-indigo-500/50 hover:bg-slate-900/70 rounded-xl p-5 transition-all cursor-pointer flex items-center justify-between"
                >
                  <div className="flex items-center gap-4">
                    <div className="p-2.5 rounded-xl bg-slate-800/80 group-hover:bg-indigo-600/20 group-hover:text-indigo-400 transition-colors text-slate-400">
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors">
                        {mod.name}
                      </h4>
                      <p className="text-xs text-slate-400">{mod.desc}</p>
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all" />
                </div>
              );
            })}
          </div>
        </section>
      </div>
    </main>
  );
}
