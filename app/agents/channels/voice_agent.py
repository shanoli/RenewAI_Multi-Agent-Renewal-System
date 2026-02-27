"""
Voice Channel Agent — Step 6 (Voice)
Modular: developers can extend this independently.
"""
from app.agents.state import RenewalState
import aiosqlite
from app.core.config import get_settings

settings = get_settings()


async def voice_send_node(state: RenewalState) -> dict:
    final_message = state.get("final_message", "")
    if not final_message:
        final_message = f"{state.get('greeting','')}\n\n{state.get('draft_message','')}\n\n{state.get('closing','')}".strip()

    # Production: Twilio Voice / Exotel / Ozonetel TTS
    call_script = final_message
    print(f"[VOICE SIM] Initiating call to {state['customer_name']} | Policy: {state['policy_id']}")

    # Check for escalation markers in voice script
    escalate = "[ESCALATE]" in call_script
    
    async with aiosqlite.connect(settings.sqlite_db_path) as db:
        await db.execute(
            "INSERT INTO interactions (policy_id, channel, message_direction, content, sentiment_score) VALUES (?, ?, ?, ?, ?)",
            (state["policy_id"], "Voice", "OUTBOUND", call_script, 0.0)
        )
        await db.execute(
            "INSERT INTO audit_logs (policy_id, action_type, action_reason, triggered_by) VALUES (?, ?, ?, ?)",
            (state["policy_id"], "VOICE_CALL_INITIATED", f"IVR call initiated | Escalate: {escalate}", "Voice Agent")
        )
        await db.execute(
            "UPDATE policy_state SET current_node=?, last_channel=?, updated_at=CURRENT_TIMESTAMP WHERE policy_id=?",
            ("AWAITING_RESPONSE", "Voice", state["policy_id"])
        )
        await db.commit()

    result = {
        "current_node": "COMPLETED",
        "messages_sent": [f"[VOICE] Call initiated to {state['customer_name']} | Policy: {state['policy_id']}"],
        "audit_trail": [f"[VOICE_AGENT] Call initiated | Policy: {state['policy_id']} | Escalate: {escalate}"]
    }
    if escalate:
        result["distress_flag"] = True
        result["audit_trail"].append("[VOICE_AGENT] ⚠️ ESCALATE marker found in voice script")
    return result
