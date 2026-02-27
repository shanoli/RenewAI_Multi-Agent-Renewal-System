"""
Test Agent: Email Channel
Tests email draft generation, template assembly, and logging.
"""
import pytest
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.state import RenewalState
from app.agents.channels.email_agent import email_send_node


def make_email_state(**overrides) -> RenewalState:
    base = RenewalState(
        policy_id="SLI-TEST-EMAIL",
        customer_id="CUST-TEST",
        customer_name="Vikram Desai",
        customer_age=35,
        customer_city="Pune",
        preferred_channel="Email",
        preferred_language="English",
        segment="High Value Investor",
        policy_type="ULIP Growth Advantage",
        sum_assured=2000000,
        annual_premium=50000,
        premium_due_date="2026-04-01",
        payment_mode="Annual",
        fund_value=1245000,
        policy_status="ACTIVE",
        current_node="CHANNEL_SEND",
        selected_channel="Email",
        channel_justification="Customer prefers email, tech-savvy",
        critique_a_result="APPROVED",
        execution_plan={"tone": "friendly", "language": "English", "cta_type": "payment_link"},
        draft_message="Your ULIP fund is up 12.4%. Premium ₹50,000 due April 1. [CTA_BUTTON] [PAYMENT_LINK]",
        greeting="Dear Vikram,",
        closing="Warm regards,\nSuraksha Life Insurance\n\nThis message is from an AI assistant. Reply HUMAN anytime to speak with a specialist.",
        final_message="Dear Vikram,\n\nYour ULIP fund is up 12.4%. Premium ₹50,000 due April 1. [CTA_BUTTON] [PAYMENT_LINK]\n\nThis message is from an AI assistant. Reply HUMAN anytime to speak with a specialist.",
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
async def test_email_send_returns_completed():
    """Email agent should return COMPLETED node."""
    state = make_email_state()
    result = await email_send_node(state)
    assert result["current_node"] == "COMPLETED"
    assert len(result["messages_sent"]) > 0
    assert "[EMAIL]" in result["messages_sent"][0]


@pytest.mark.asyncio
async def test_email_audit_trail():
    """Email agent should log audit trail."""
    state = make_email_state()
    result = await email_send_node(state)
    assert any("[EMAIL_AGENT]" in t for t in result["audit_trail"])


@pytest.mark.asyncio
async def test_email_assembles_from_parts_if_no_final():
    """If final_message is empty, agent should assemble from parts."""
    state = make_email_state(final_message=None)
    result = await email_send_node(state)
    assert result["current_node"] == "COMPLETED"


@pytest.mark.asyncio
async def test_email_subject_contains_policy_type():
    """Email subject should mention policy type."""
    state = make_email_state()
    result = await email_send_node(state)
    assert "ULIP" in result["messages_sent"][0] or "Reminder" in result["messages_sent"][0]


@pytest.mark.asyncio
async def test_email_with_hni_segment():
    """HNI segment should work correctly with email."""
    state = make_email_state(segment="High Value Investor", annual_premium=200000)
    result = await email_send_node(state)
    assert result["current_node"] == "COMPLETED"
