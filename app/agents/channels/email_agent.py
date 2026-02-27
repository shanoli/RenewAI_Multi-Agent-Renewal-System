"""
Email Channel Agent — Step 6 (Email)
Modular: developers can extend this independently.
"""
from app.agents.state import RenewalState
import aiosqlite
from app.core.config import get_settings
from datetime import datetime

settings = get_settings()


async def email_send_node(state: RenewalState) -> dict:
    final_message = state.get("final_message", "")
    if not final_message:
        final_message = f"{state.get('greeting','')}\n\n{state.get('draft_message','')}\n\n{state.get('closing','')}".strip()

    email_subject = f"[Suraksha Life] Renewal Reminder — {state['policy_type']} | Due {state['premium_due_date']}"
    print(f"[EMAIL SIM] Sending to {state['customer_name']} | {email_subject}")

    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        await db.execute(
            "INSERT INTO interactions (policy_id, channel, message_direction, content, sentiment_score) VALUES (?, ?, ?, ?, ?)",
            (state["policy_id"], "Email", "OUTBOUND", final_message, 0.0)
        )
        await db.execute(
            "INSERT INTO audit_logs (policy_id, action_type, action_reason, triggered_by) VALUES (?, ?, ?, ?)",
            (state["policy_id"], "EMAIL_SENT", f"Subject: {email_subject}", "Email Agent")
        )
        await db.execute(
            "UPDATE policy_state SET current_node=?, last_channel=?, updated_at=CURRENT_TIMESTAMP WHERE policy_id=?",
            ("AWAITING_RESPONSE", "Email", state["policy_id"])
        )
        await db.commit()

    return {
        "current_node": "COMPLETED",
        "messages_sent": [f"[EMAIL] {email_subject} → {state['customer_name']}"],
        "audit_trail": [f"[EMAIL_AGENT] Email sent | Policy: {state['policy_id']}"]
    }
