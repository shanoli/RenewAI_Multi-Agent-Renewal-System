"""
Orchestrator Agent — Step 1
Decides the best channel (Email/WhatsApp/Voice) for a policyholder renewal.
"""
from app.agents.state import RenewalState
from app.core.gemini_client import call_llm_json
from app.rag.chroma_store import hybrid_search_and_rerank
import json

ORCHESTRATOR_SYSTEM_PROMPT = """
You are the RenewAI Renewal Orchestrator for Suraksha Life Insurance.
Your job: Given a customer profile, policy data, and full interaction history, 
decide the NEXT BEST communication channel (Email / WhatsApp / Voice) for renewal outreach.

Rules:
1. Check if payment_done = True → set payment_done flag, no more outreach needed
2. If distress_flag is True OR objection_count >= 3 → set escalate: true
3. Consider preferred_channel first, then interaction history to see what worked
4. If a channel has been tried 3+ times with no result, switch to fallback

Respond ONLY with valid JSON:
{
  "channel": "WhatsApp|Email|Voice",
  "justification": "specific evidence from history",
  "priority": "high|medium|low",
  "fallback_channel": "Email|WhatsApp|Voice",
  "escalate": false,
  "payment_done": false
}
"""


async def orchestrator_node(state: RenewalState) -> dict:
    """Step 1: Select best communication channel."""
    
    # Check escalation conditions upfront
    if state.get("distress_flag") or state.get("objection_count", 0) >= 3:
        return {
            "current_node": "ESCALATION",
            "escalate": True,
            "escalation_reason": "distress_flag" if state.get("distress_flag") else "objection_threshold",
            "mode": "HUMAN_CONTROL",
            "audit_trail": [f"[ORCHESTRATOR] Direct escalation: distress={state.get('distress_flag')}, objections={state.get('objection_count')}"]
        }

    # Build RAG context for objection library
    rag_results = hybrid_search_and_rerank(
        "objection_library",
        query=f"{state.get('segment', '')} {state.get('policy_type', '')} renewal",
        n_results=5,
        rerank_top_k=3
    )
    rag_context = "\n".join([r["document"] for r in rag_results]) if rag_results else "No objection context available"

    history_str = json.dumps(state.get("interaction_history", [])[-10:], indent=2)
    
    user_prompt = f"""
Customer Profile:
- Name: {state['customer_name']}
- Age: {state['customer_age']}
- City: {state['customer_city']}
- Preferred Channel: {state['preferred_channel']}
- Preferred Language: {state['preferred_language']}
- Segment: {state['segment']}

Policy Details:
- Policy ID: {state['policy_id']}
- Type: {state['policy_type']}
- Premium: ₹{state['annual_premium']}
- Due Date: {state['premium_due_date']}
- Status: {state['policy_status']}

Interaction History (last 10):
{history_str}

Objection Context from RAG:
{rag_context}

Distress Flag: {state.get('distress_flag', False)}
Objection Count: {state.get('objection_count', 0)}
"""

    result = await call_llm_json(ORCHESTRATOR_SYSTEM_PROMPT, user_prompt)
    
    if result.get("payment_done"):
        return {
            "current_node": "COMPLETED",
            "audit_trail": [f"[ORCHESTRATOR] Payment already done for {state['policy_id']}"]
        }
    
    if result.get("escalate"):
        return {
            "current_node": "ESCALATION",
            "escalate": True,
            "escalation_reason": result.get("justification", "Orchestrator escalation"),
            "mode": "HUMAN_CONTROL",
            "audit_trail": [f"[ORCHESTRATOR] Escalation flagged: {result.get('justification')}"]
        }

    return {
        "current_node": "CRITIQUE_A",
        "selected_channel": result.get("channel", state["preferred_channel"]),
        "channel_justification": result.get("justification", ""),
        "rag_objections": rag_context,
        "audit_trail": [f"[ORCHESTRATOR] Selected channel: {result.get('channel')} | Reason: {result.get('justification')}"]
    }
