"""
LangGraph Workflow Definition
Connects all agents in the correct sequence.
"""
from langgraph.graph import StateGraph, END
from app.agents.state import RenewalState
from app.agents.orchestrator import orchestrator_node
from app.agents.critique_a import critique_a_node
from app.agents.planner import planner_node
from app.agents.greeting_closing import greeting_closing_node
from app.agents.draft_agent import draft_agent_node
from app.agents.critique_b import critique_b_node
from app.agents.escalation import escalation_node
from app.agents.channels.email_agent import email_send_node
from app.agents.channels.whatsapp_agent import whatsapp_send_node
from app.agents.channels.voice_agent import voice_send_node


def route_after_orchestrator(state: RenewalState) -> str:
    node = state.get("current_node", "")
    if node == "ESCALATION":
        return "escalation"
    if node == "COMPLETED":
        return END
    return "critique_a"


def route_after_critique_b(state: RenewalState) -> str:
    node = state.get("current_node", "")
    if node == "ESCALATION":
        return "escalation"
    return "channel_router"


def route_channel(state: RenewalState) -> str:
    channel = state.get("selected_channel", "Email")
    mapping = {
        "Email": "email_send",
        "WhatsApp": "whatsapp_send",
        "Voice": "voice_send"
    }
    return mapping.get(channel, "email_send")


async def parallel_draft_and_greeting(state: RenewalState) -> dict:
    """Run Greeting/Closing and Draft Agent in parallel."""
    import asyncio
    greeting_task = asyncio.create_task(greeting_closing_node(state))
    draft_task = asyncio.create_task(draft_agent_node(state))
    
    greeting_result, draft_result = await asyncio.gather(greeting_task, draft_task)
    
    # Merge results
    merged = {}
    merged.update(greeting_result)
    merged.update(draft_result)
    
    # Merge audit trails
    merged["audit_trail"] = (
        greeting_result.get("audit_trail", []) +
        draft_result.get("audit_trail", [])
    )
    merged["current_node"] = "CRITIQUE_B"
    return merged


def build_workflow() -> StateGraph:
    graph = StateGraph(RenewalState)

    # Add nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("critique_a", critique_a_node)
    graph.add_node("planner", planner_node)
    graph.add_node("draft_and_greeting", parallel_draft_and_greeting)
    graph.add_node("critique_b", critique_b_node)
    graph.add_node("escalation", escalation_node)
    graph.add_node("email_send", email_send_node)
    graph.add_node("whatsapp_send", whatsapp_send_node)
    graph.add_node("voice_send", voice_send_node)
    graph.add_node("channel_router", lambda s: s)  # pass-through router

    # Entry point
    graph.set_entry_point("orchestrator")

    # Edges
    graph.add_conditional_edges("orchestrator", route_after_orchestrator, {
        "critique_a": "critique_a",
        "escalation": "escalation",
        END: END
    })
    graph.add_edge("critique_a", "planner")
    graph.add_edge("planner", "draft_and_greeting")
    graph.add_edge("draft_and_greeting", "critique_b")
    graph.add_conditional_edges("critique_b", route_after_critique_b, {
        "escalation": "escalation",
        "channel_router": "channel_router"
    })
    graph.add_conditional_edges("channel_router", route_channel, {
        "email_send": "email_send",
        "whatsapp_send": "whatsapp_send",
        "voice_send": "voice_send"
    })
    graph.add_edge("email_send", END)
    graph.add_edge("whatsapp_send", END)
    graph.add_edge("voice_send", END)
    graph.add_edge("escalation", END)

    return graph.compile()


# Singleton workflow instance
_workflow = None


def get_workflow():
    global _workflow
    if _workflow is None:
        _workflow = build_workflow()
    return _workflow
