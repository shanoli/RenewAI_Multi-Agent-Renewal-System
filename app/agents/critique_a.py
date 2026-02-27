"""
Critique Agent Phase A — Step 2
Verifies Orchestrator's channel selection with evidence-based reasoning.
"""
from app.agents.state import RenewalState
from app.core.gemini_client import call_llm_json
from app.rag.chroma_store import hybrid_search_and_rerank
import json

CRITIQUE_A_SYSTEM_PROMPT = """
You are the RenewAI Critique Agent, Phase A — the evidence verifier.
Your job: Verify the Orchestrator's channel selection against hard evidence.

Check ALL of:
1. Is there interaction data supporting this channel choice?
2. Has this channel been EXHAUSTED (3+ attempts, no result)?
3. Does the customer segment/preference align with this channel?
4. Is escalation threshold already met (distress or objection_count >= 3)?

Respond ONLY with valid JSON:
{
  "verdict": "APPROVED|OVERRIDE",
  "confidence": 0.0-1.0,
  "evidence": "specific evidence from data",
  "alternative_channel": "Email|WhatsApp|Voice|null",
  "override_reason": "reason if OVERRIDE else null"
}
"""


async def critique_a_node(state: RenewalState) -> dict:
    """Step 2: Verify channel selection with evidence."""
    
    # Retrieve regulatory guidelines for reference
    reg_results = hybrid_search_and_rerank(
        "regulatory_guidelines",
        query=f"channel communication policy IRDAI {state.get('selected_channel', '')}",
        n_results=3,
        rerank_top_k=2
    )
    reg_context = "\n".join([r["document"] for r in reg_results]) if reg_results else ""

    # Count channel attempts
    history = state.get("interaction_history", [])
    channel = state.get("selected_channel", "")
    channel_attempts = sum(1 for h in history if h.get("channel") == channel and h.get("direction") == "OUTBOUND")

    user_prompt = f"""
Orchestrator Decision:
- Selected Channel: {channel}
- Justification: {state.get('channel_justification', '')}

Customer:
- Preferred Channel: {state['preferred_channel']}
- Segment: {state['segment']}
- Distress Flag: {state.get('distress_flag', False)}
- Objection Count: {state.get('objection_count', 0)}

Channel Attempts for "{channel}": {channel_attempts}
Total Interaction History Count: {len(history)}

Recent History:
{json.dumps(history[-5:], indent=2)}

Regulatory Context:
{reg_context}
"""

    result = await call_llm_json(CRITIQUE_A_SYSTEM_PROMPT, user_prompt)
    verdict = result.get("verdict", "APPROVED")

    updates = {
        "critique_a_result": verdict,
        "rag_regulations": reg_context,
        "audit_trail": [f"[CRITIQUE_A] Verdict: {verdict} | Confidence: {result.get('confidence')} | Evidence: {result.get('evidence')}"]
    }

    if verdict == "OVERRIDE":
        # Provide alternative channel back to orchestrator
        alt_channel = result.get("alternative_channel")
        if alt_channel:
            updates["selected_channel"] = alt_channel
            updates["channel_justification"] = result.get("override_reason", "Critique A override")
        updates["current_node"] = "PLANNER"  # Proceed with override channel
    else:
        updates["current_node"] = "PLANNER"

    return updates
