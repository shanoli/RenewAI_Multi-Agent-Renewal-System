"""
WhatsApp Channel Agent — Step 6 (WhatsApp)
Modular: developers can extend this independently.
"""
from app.agents.state import RenewalState
import aiosqlite
from app.core.config import get_settings

settings = get_settings()


async def whatsapp_send_node(state: RenewalState) -> dict:
    final_message = state.get("final_message", "")
    if not final_message:
        final_message = f"{state.get('greeting','')}\n\n{state.get('draft_message','')}\n\n{state.get('closing','')}".strip()

    # Truncate for WhatsApp (production: Twilio/Meta Business API)
    wa_message = final_message[:1000]
    print(f"[WHATSAPP SIM] Sending to {state['customer_name']} | Policy: {state['policy_id']}")

    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        await db.execute(
            "INSERT INTO interactions (policy_id, channel, message_direction, content, sentiment_score) VALUES (?, ?, ?, ?, ?)",
            (state["policy_id"], "WhatsApp", "OUTBOUND", wa_message, 0.0)
        )
        await db.execute(
            "INSERT INTO audit_logs (policy_id, action_type, action_reason, triggered_by) VALUES (?, ?, ?, ?)",
            (state["policy_id"], "WHATSAPP_SENT", "WhatsApp renewal message sent", "WhatsApp Agent")
        )
        await db.execute(
            "UPDATE policy_state SET current_node=?, last_channel=?, updated_at=CURRENT_TIMESTAMP WHERE policy_id=?",
            ("AWAITING_RESPONSE", "WhatsApp", state["policy_id"])
        )
        await db.commit()

    return {
        "current_node": "COMPLETED",
        "messages_sent": [f"[WHATSAPP] Sent to {state['customer_name']} | Policy: {state['policy_id']}"],
        "audit_trail": [f"[WHATSAPP_AGENT] WA message sent | Policy: {state['policy_id']}"]
    }
