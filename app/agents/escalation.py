"""
Escalation / Human Queue Manager
Routes distressed or complex cases to human agents.
"""
from app.agents.state import RenewalState
import aiosqlite
from app.core.config import get_settings
from datetime import datetime, timedelta

settings = get_settings()

PRIORITY_MAP = {
    "distress_flag": 1.0,
    "objection_threshold": 0.8,
    "hni_grievance": 0.9,
    "Critique B escalation": 0.7
}


async def escalation_node(state: RenewalState) -> dict:
    """Create escalation case and route to human queue."""
    
    reason = state.get("escalation_reason", "Auto escalation")
    priority = PRIORITY_MAP.get(reason, 0.6)
    sla_hours = 2 if priority >= 0.9 else 4 if priority >= 0.7 else 8
    sla_deadline = (datetime.utcnow() + timedelta(hours=sla_hours)).isoformat()

    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        cursor = await db.execute("""
            INSERT INTO escalation_cases 
            (policy_id, escalation_reason, priority_score, status, sla_deadline)
            VALUES (?, ?, ?, ?, ?)
        """, (state["policy_id"], reason, priority, "OPEN", sla_deadline))
        case_id = cursor.lastrowid
        
        await db.execute(
            "INSERT INTO audit_logs (policy_id, action_type, action_reason, triggered_by) VALUES (?, ?, ?, ?)",
            (state["policy_id"], "ESCALATION_CREATED", f"Case #{case_id} | Reason: {reason} | SLA: {sla_deadline}", "Escalation Manager")
        )
        await db.execute(
            "UPDATE policy_state SET current_node=?, mode=?, distress_flag=?, updated_at=CURRENT_TIMESTAMP WHERE policy_id=?",
            ("HUMAN_QUEUE", "HUMAN_CONTROL", 1 if state.get("distress_flag") else 0, state["policy_id"])
        )
        await db.commit()

    print(f"[ESCALATION] Case #{case_id} created | Policy: {state['policy_id']} | Priority: {priority} | SLA: {sla_deadline}")

    return {
        "current_node": "HUMAN_QUEUE",
        "mode": "HUMAN_CONTROL",
        "messages_sent": [f"[ESCALATION] Case #{case_id} created for {state['customer_name']} | SLA: {sla_hours}h"],
        "audit_trail": [f"[ESCALATION_MGR] Case #{case_id} | Priority: {priority} | Reason: {reason}"]
    }
