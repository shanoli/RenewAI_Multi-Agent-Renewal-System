"""
Centralized async Gemini client for all agents.
"""
import google.generativeai as genai
import asyncio
import json
import re
from typing import Optional
from app.core.config import get_settings
import os
from dotenv import load_dotenv
load_dotenv()

settings = get_settings()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_model = None


def get_model():
    global _model
    if _model is None:
        _model = genai.GenerativeModel(settings.gemini_model)
    return _model


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    expect_json: bool = False,
    temperature: float = 0.3
) -> str:
    """Async wrapper around Gemini generate_content."""
    model = get_model()
    full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
    
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=2048,
            )
        )
    )
    text = response.text.strip()
    
    if expect_json:
        # Strip markdown code fences if present
        text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("```").strip()
    
    return text


async def call_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """Call LLM expecting JSON response, returns parsed dict."""
    text = await call_llm(system_prompt, user_prompt, expect_json=True)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"error": "Could not parse JSON", "raw": text}
