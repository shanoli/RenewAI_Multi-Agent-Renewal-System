"""
Planner Agent — Step 3
Builds a detailed execution plan for the selected channel.
RAG retrieves policy documents + objection playbooks.
"""
from app.agents.state import RenewalState
from app.core.gemini_client import call_llm_json
from app.rag.chroma_store import hybrid_search_and_rerank
import json

PLANNER_SYSTEM_PROMPT = """
You are the RenewAI Planner Agent.
The Orchestrator has selected a channel. Build a DETAILED execution plan for the Draft Agent.
Do NOT generate the final message — only the plan.

Output ONLY valid JSON:
{
  "tone": "formal|friendly|empathetic|hni",
  "language": "English|Hindi|Tamil|...",
  "key_facts": ["fact1","fact2","fact3"],
  "objection_playbook_id": "id or description",
  "objection_responses": ["response1","response2"],
  "greeting_style": "formal|warm|regional",
  "timing_window": "morning|evening|anytime",
  "cta_type": "payment_link|callback|whatsapp_reply|ivr_press1",
  "personalization_elements": ["name","policy_type","fund_value"],
  "distress_watch_keywords": ["lost job","death","can't pay","hardship"],
  "language_note": "any regional language nuance"
}
"""


async def planner_node(state: RenewalState) -> dict:
    """Step 3: Build channel-specific execution plan."""
    
    channel = state.get("selected_channel", "Email")
    
    # RAG: policy documents
    policy_results = hybrid_search_and_rerank(
        "policy_documents",
        query=f"{state['policy_type']} renewal benefits premium due",
        n_results=5,
        rerank_top_k=3
    )
    policy_context = "\n".join([r["document"] for r in policy_results]) if policy_results else "No policy document found."

    # RAG: objection library — language + segment aware
    obj_query = f"{state.get('preferred_language','')} {state.get('segment','')} objection renewal premium"
    obj_results = hybrid_search_and_rerank(
        "objection_library",
        query=obj_query,
        n_results=5,
        rerank_top_k=3
    )
    obj_context = "\n".join([r["document"] for r in obj_results]) if obj_results else "Standard objection handling."

    user_prompt = f"""
Channel: {channel}
Customer: {state['customer_name']}, {state['customer_age']}y, {state['customer_city']}
Segment: {state['segment']}
Language: {state['preferred_language']}
Policy Type: {state['policy_type']}
Premium: ₹{state['annual_premium']}
Due Date: {state['premium_due_date']}
Fund Value: {state.get('fund_value', 'N/A')}
Distress Flag: {state.get('distress_flag', False)}
Objection Count: {state.get('objection_count', 0)}

Retrieved Policy Documents:
{policy_context}

Retrieved Objection Playbooks:
{obj_context}

Recent Interactions: {json.dumps(state.get('interaction_history', [])[-3:], indent=2)}
"""

    plan = await call_llm_json(PLANNER_SYSTEM_PROMPT, user_prompt)

    return {
        "current_node": "DRAFT_AND_GREETING",
        "execution_plan": plan,
        "rag_policy_docs": policy_context,
        "rag_objections": obj_context,
        "audit_trail": [f"[PLANNER] Plan built for {channel} | Tone: {plan.get('tone')} | Language: {plan.get('language')}"]
    }
