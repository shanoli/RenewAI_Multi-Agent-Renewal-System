"""
Test Agent: Voice Channel
Tests voice script generation, ESCALATE marker detection, and logging.
"""
import pytest
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.state import RenewalState
from app.agents.channels.voice_agent import voice_send_node


def make_voice_state(**overrides) -> RenewalState:
    base = RenewalState(
        policy_id="SLI-TEST-VOICE",
        customer_id="CUST-TEST-V",
        customer_name="Lakshmi Krishnan",
        customer_age=62,
        customer_city="Coimbatore",
        preferred_channel="Voice",
        preferred_language="Tamil",
        segment="Senior Citizen",
        policy_type="Secure Endowment Plan",
        sum_assured=200000,
        annual_premium=25000,
        premium_due_date="2026-02-25",
        payment_mode="Annual",
        fund_value=None,
        policy_status="ACTIVE",
        current_node="CHANNEL_SEND",
        selected_channel="Voice",
        channel_justification="Senior citizen prefers voice calls",
        critique_a_result="APPROVED",
        execution_plan={"tone": "empathetic", "language": "Tamil", "cta_type": "ivr_press1"},
        draft_message="Vanakkam Lakshmi amma. [PAUSE] Ungal Secure Endowment Plan February 25 due aaguthu. [PAUSE] Premium: 25,000 rupees. [PAUSE] Pay panna 1 press pannunga.",
        greeting="Vanakkam! Naan Suraksha Life Insurance AI assistant pesukirean.",
        closing="Nandri Lakshmi amma. Neenga human agent venum endral HELP sollunga.\n\nThis message is from an AI assistant. Reply HUMAN anytime.",
        final_message="Vanakkam! Naan Suraksha Life Insurance.\n\nUngal policy February 25 due aaguthu. Premium: 25,000. [PAUSE] 1 press pannunga.\n\nThis message is from an AI assistant.",
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
async def test_voice_send_returns_completed():
    """Voice agent should return COMPLETED node."""
    state = make_voice_state()
    result = await voice_send_node(state)
    assert result["current_node"] == "COMPLETED"


@pytest.mark.asyncio
async def test_voice_message_logged():
    """Voice call should be in messages_sent."""
    state = make_voice_state()
    result = await voice_send_node(state)
    assert any("[VOICE]" in m for m in result["messages_sent"])


@pytest.mark.asyncio
async def test_voice_escalate_marker_detection():
    """If [ESCALATE] in script, distress_flag should be set True."""
    state = make_voice_state(
        draft_message="Customer said husband died. [ESCALATE] Route to human immediately.",
        final_message="Vanakkam.\n\nCustomer said husband died. [ESCALATE] Route to human.\n\nThis is AI."
    )
    result = await voice_send_node(state)
    assert result.get("distress_flag") is True


@pytest.mark.asyncio
async def test_voice_no_escalate_when_clean():
    """Clean voice script should not set distress_flag."""
    state = make_voice_state()
    result = await voice_send_node(state)
    assert result.get("distress_flag") is not True


@pytest.mark.asyncio
async def test_voice_audit_trail_logged():
    """Voice agent should log audit trail."""
    state = make_voice_state()
    result = await voice_send_node(state)
    assert any("[VOICE_AGENT]" in t for t in result["audit_trail"])


@pytest.mark.asyncio
async def test_voice_senior_citizen_segment():
    """Senior citizen segment should work with voice."""
    state = make_voice_state(segment="Senior Citizen", preferred_language="Malayalam")
    result = await voice_send_node(state)
    assert result["current_node"] == "COMPLETED"
