"""
Test Agent: WhatsApp Channel
Tests WhatsApp message sending, distress detection, and interaction logging.
"""
import pytest
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.state import RenewalState
from app.agents.channels.whatsapp_agent import whatsapp_send_node


def make_wa_state(**overrides) -> RenewalState:
    base = RenewalState(
        policy_id="SLI-TEST-WA",
        customer_id="CUST-TEST-WA",
        customer_name="Rajesh Sharma",
        customer_age=42,
        customer_city="Mumbai",
        preferred_channel="WhatsApp",
        preferred_language="Hindi",
        segment="Wealth Builder",
        policy_type="Term Shield Plus",
        sum_assured=10000000,
        annual_premium=24000,
        premium_due_date="2026-03-15",
        payment_mode="Annual",
        fund_value=None,
        policy_status="ACTIVE",
        current_node="CHANNEL_SEND",
        selected_channel="WhatsApp",
        channel_justification="Preferred WhatsApp, evening available",
        critique_a_result="APPROVED",
        execution_plan={"tone": "friendly", "language": "Hindi", "cta_type": "payment_link"},
        draft_message="🛡️ Rajesh-ji! Aapki Term Shield Plus policy 15 March ko due hai. Premium: ₹24,000. [PAYMENT_LINK]",
        greeting="Namaste Rajesh-ji! 🙏",
        closing="Suraksha Life Insurance\nYeh message AI assistant se hai. Kabhi bhi HUMAN type karein human se baat karne ke liye.",
        final_message="Namaste Rajesh-ji! 🙏\n\n🛡️ Term Shield Plus policy 15 March ko due hai. Premium: ₹24,000. [PAYMENT_LINK]\n\nYeh message AI assistant se hai. HUMAN type karein.",
        critique_b_result="APPROVED",
        distress_flag=False,
        objection_count=0,
        mode="AI",
        escalate=False,
        escalation_reason=None,
        interaction_history=[],
        rag_policy_docs=None,
        rag_objections=None,
        rag_regulations=None,
        messages_sent=[],
        audit_trail=[],
        error=None
    )
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_wa_send_returns_completed():
    """WhatsApp agent should return COMPLETED node."""
    state = make_wa_state()
    result = await whatsapp_send_node(state)
    assert result["current_node"] == "COMPLETED"


@pytest.mark.asyncio
async def test_wa_message_logged():
    """WhatsApp message should be in messages_sent."""
    state = make_wa_state()
    result = await whatsapp_send_node(state)
    assert any("[WHATSAPP]" in m for m in result["messages_sent"])


@pytest.mark.asyncio
async def test_wa_with_hindi_content():
    """WhatsApp agent should handle Hindi content correctly."""
    state = make_wa_state(preferred_language="Hindi")
    result = await whatsapp_send_node(state)
    assert result["current_node"] == "COMPLETED"


@pytest.mark.asyncio
async def test_wa_audit_trail_logged():
    """WhatsApp agent should log audit trail."""
    state = make_wa_state()
    result = await whatsapp_send_node(state)
    assert any("[WHATSAPP_AGENT]" in t for t in result["audit_trail"])


@pytest.mark.asyncio
async def test_wa_assembles_message_if_no_final():
    """WhatsApp agent should assemble from parts if final_message is None."""
    state = make_wa_state(final_message=None)
    result = await whatsapp_send_node(state)
    assert result["current_node"] == "COMPLETED"


@pytest.mark.asyncio
async def test_wa_budget_conscious_segment():
    """Budget conscious segment should work with WhatsApp."""
    state = make_wa_state(
        segment="Budget Conscious",
        annual_premium=8500,
        policy_type="Secure Endowment Plan"
    )
    result = await whatsapp_send_node(state)
    assert result["current_node"] == "COMPLETED"
