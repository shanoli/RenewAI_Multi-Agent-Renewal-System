import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from app.agents.workflow import get_workflow
from app.agents.state import RenewalState

async def test():
    print("Testing workflow...")
    workflow = get_workflow()
    
    state = RenewalState(
        policy_id="TEST-001",
        customer_id="CUST-TEST",
        customer_name="Test User",
        customer_age=30,
        customer_city="Mumbai",
        preferred_channel="Email",
        preferred_language="English",
        segment="Standard",
        policy_type="Term Insurance",
        sum_assured=1000000,
        annual_premium=10000,
        premium_due_date="2026-12-31",
        payment_mode="Annual",
        fund_value=None,
        policy_status="ACTIVE",
        current_node="ORCHESTRATOR",
        selected_channel=None,
        channel_justification=None,
        critique_a_result=None,
        execution_plan=None,
        draft_message=None,
        greeting=None,
        closing=None,
        final_message=None,
        critique_b_result=None,
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
    
    try:
        async for chunk in workflow.astream(state, stream_mode="updates"):
            print(f"CHUNK: {chunk}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test())
