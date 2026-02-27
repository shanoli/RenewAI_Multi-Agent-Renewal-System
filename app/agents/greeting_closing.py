"""
Greeting/Closing Agent — Step 4a (runs in parallel with Draft Agent)
Generates culturally appropriate greetings and compliant closings.
"""
from app.agents.state import RenewalState
from app.core.gemini_client import call_llm
import json

GREETING_SYSTEM_PROMPT = """
You are the RenewAI Greeting Agent for Suraksha Life Insurance.
Generate a culturally appropriate, warm greeting in the specified language.
Use the customer's first name and policy type. Match the tone from the plan.
Do NOT be robotic. Be warm and human.

For Hindi: Use respectful honorifics like "जी"
For Tamil: Use appropriate respectful terms
For other regional languages: Use culturally appropriate greetings

Output ONLY the greeting text (1-2 sentences max).
"""

CLOSING_SYSTEM_PROMPT = """
You are the RenewAI Closing Agent for Suraksha Life Insurance.
Generate a compliant closing for a renewal communication.

MANDATORY: Always end with this exact line:
"This message is from an AI assistant of Suraksha Life Insurance. Reply HUMAN anytime to speak with a specialist."

Also include: next step, payment link placeholder [PAYMENT_LINK], and a warm sign-off.
Output ONLY the closing text.
"""


async def greeting_closing_node(state: RenewalState) -> dict:
    """Step 4a: Generate greeting and closing."""
    
    plan = state.get("execution_plan", {})
    channel = state.get("selected_channel", "Email")
    language = plan.get("language", state.get("preferred_language", "English"))
    tone = plan.get("tone", "friendly")
    first_name = state["customer_name"].split()[0]

    greeting_prompt = f"""
Customer First Name: {first_name}
Policy Type: {state['policy_type']}
Language: {language}
Tone: {tone}
Channel: {channel}
Greeting Style: {plan.get('greeting_style', 'warm')}
"""

    closing_prompt = f"""
Customer Name: {state['customer_name']}
Channel: {channel}
Language: {language}
Tone: {tone}
Due Date: {state['premium_due_date']}
CTA Type: {plan.get('cta_type', 'payment_link')}
"""

    greeting = await call_llm(GREETING_SYSTEM_PROMPT, greeting_prompt, temperature=0.4)
    closing = await call_llm(CLOSING_SYSTEM_PROMPT, closing_prompt, temperature=0.2)

    return {
        "current_node": "DRAFT_AND_GREETING",
        "greeting": greeting.strip(),
        "closing": closing.strip(),
        "audit_trail": [f"[GREETING_CLOSING] Greeting/Closing generated for {channel} in {language}"]
    }
