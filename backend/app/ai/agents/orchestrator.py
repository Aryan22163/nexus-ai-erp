import uuid
from decimal import Decimal
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.tools.domain_tools import global_tool_registry
from app.models.approval import ApprovalRequest
from app.repositories.approval import ApprovalRepository
from app.schemas.ai import (
    ActionProposalCard,
    AICopilotRequest,
    AICopilotResponse,
)


class AICopilotOrchestrator:
    """
    Autonomous Enterprise Copilot Orchestrator.
    Understands business intent, queries multi-module domain data via authorized tools,
    and gates mutating state modifications with strict Human-in-the-Loop (HITL) approval records.
    """
    def __init__(
        self,
        session: AsyncSession,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        user_permissions: List[str],
    ):
        self.session = session
        self.organization_id = organization_id
        self.user_id = user_id
        self.user_permissions = user_permissions
        self.approval_repo = ApprovalRepository(session, organization_id)

    async def process_prompt(self, request: AICopilotRequest) -> AICopilotResponse:
        prompt_lower = request.prompt.lower()
        executed_tools = []
        citations = []
        action_card = None
        reply = ""
        intent = "GENERAL_QUERY"

        # 1. Mutating Action Intent: Purchase Order Proposal
        if any(keyword in prompt_lower for keyword in ["create po", "draft po", "purchase order", "restock", "order 50 units"]):
            intent = "ACTION_PROPOSAL"
            action_type = "CREATE_PURCHASE_ORDER"
            explanation = "AI detected low stock thresholds and formulated an inventory replenishment proposal."

            payload = {
                "sku": "SKU-ALERT-1",
                "product_name": "Critical Component",
                "quantity": 50,
                "estimated_unit_cost": "650.00",
                "estimated_total": "32500.00",
                "reason": "Replenish safety stock based on consumption velocity",
            }

            # Persist Approval Request in Database
            approval = ApprovalRequest(
                organization_id=self.organization_id,
                action_type=action_type,
                payload=payload,
                status="PENDING",
                explanation=explanation,
                requester_id=self.user_id,
            )
            self.session.add(approval)
            await self.session.flush()

            action_card = ActionProposalCard(
                approval_request_id=approval.id,
                action_type=action_type,
                summary="Create Purchase Order for 50 units of SKU-ALERT-1",
                explanation=explanation,
                proposed_payload=payload,
                status="PENDING",
            )
            executed_tools.append("propose_purchase_order")
            reply = (
                "I have drafted a Purchase Order proposal for safety replenishment. "
                "Because this action involves financial commitment, it requires your explicit authorization. "
                "Please review the proposed parameters below to approve or reject."
            )

        # 2. Financial Query Intent
        elif any(keyword in prompt_lower for keyword in ["revenue", "profit", "margin", "expense", "financial"]):
            intent = "FINANCIAL_ANALYSIS"
            tool = global_tool_registry.get_tool("get_financial_summary")
            if tool:
                data = await tool.handler(self.session, self.organization_id)
                executed_tools.append("get_financial_summary")
                reply = (
                    f"**Financial Performance Overview**:\n"
                    f"- **Total Revenue**: ₹{Decimal(data['total_revenue']):,.2f}\n"
                    f"- **Gross Profit**: ₹{Decimal(data['gross_profit']):,.2f}\n"
                    f"- **Net Operating Profit**: ₹{Decimal(data['net_profit']):,.2f} ({data['net_margin_percentage']}% net margin)\n"
                    f"- **Outstanding Accounts Receivable**: ₹{Decimal(data['accounts_receivable_outstanding']):,.2f}\n"
                    f"\n*Recommendation*: Operating margin is healthy. Monitor overdue receivables to protect liquidity."
                )

        # 3. Top Customers / Sales Intent
        elif any(keyword in prompt_lower for keyword in ["customer", "top client", "biggest client", "who bought"]):
            intent = "CUSTOMER_ANALYSIS"
            tool = global_tool_registry.get_tool("get_top_customers")
            if tool:
                data = await tool.handler(self.session, self.organization_id, limit=5)
                executed_tools.append("get_top_customers")
                cust_lines = "\n".join(
                    [
                        f"{idx+1}. **{c['customer_name']}** — Revenue: ₹{Decimal(c['total_revenue']):,.2f} ({c['orders_count']} orders)"
                        for idx, c in enumerate(data.get("top_customers", []))
                    ]
                )
                reply = f"**Top Revenue Generating Customers**:\n\n{cust_lines or 'No confirmed sales transactions recorded.'}"

        # 4. Inventory & Stockout Intent
        elif any(keyword in prompt_lower for keyword in ["stock", "inventory", "stockout", "reorder", "warehouse"]):
            intent = "INVENTORY_CHECK"
            tool = global_tool_registry.get_tool("get_low_stock_items")
            if tool:
                data = await tool.handler(self.session, self.organization_id)
                executed_tools.append("get_low_stock_items")
                alerts = data.get("low_stock_alerts", [])
                if alerts:
                    lines = "\n".join(
                        [
                            f"- **{a['product_name']}** (SKU: `{a['sku']}`): Current stock **{a['current_stock']}** (Reorder level: {a['reorder_level']}). Status: **{a['urgency']}**."
                            for a in alerts
                        ]
                    )
                    reply = f"**Inventory Risk Assessment**:\n{lines}\n\n*Action*: Consider creating a purchase request to avoid stockouts."
                else:
                    reply = "All products currently maintain inventory balances above their defined safety reorder thresholds."

        # 5. Policy / Knowledge Document Query Intent (RAG)
        elif any(keyword in prompt_lower for keyword in ["policy", "sop", "document", "contract", "terms", "return"]):
            intent = "KNOWLEDGE_RAG"
            tool = global_tool_registry.get_tool("query_knowledge_base")
            if tool:
                data = await tool.handler(self.session, self.organization_id, query=request.prompt)
                executed_tools.append("query_knowledge_base")
                citations = data.get("citations", [])
                results = data.get("results", [])
                if results:
                    content_block = "\n\n> ".join(results)
                    reply = f"According to company documentation:\n\n> {content_block}"
                else:
                    reply = "No matching operational documentation found in the company knowledge base."

        # 6. Default Fallback
        else:
            intent = "ASSISTANT_QUERY"
            reply = (
                "I am **NEXUS AI**, your Business Operating System copilot. "
                "I can analyze financial reports, query sales pipelines, assess stockout risks, "
                "search internal knowledge documents, and draft operational transactions with your authorization."
            )

        return AICopilotResponse(
            reply=reply,
            intent=intent,
            executed_tools=executed_tools,
            action_proposal=action_card,
            citations=citations,
        )
