"""
chat_engine.py

Order of operations for every incoming chat message:
  1. safety_rules.check_red_flags()  — deterministic, always runs first
  2. if not an emergency: try the configured LLM API (if LLM_API_KEY is set)
  3. if no LLM configured, or the call fails: fall back to rule-based
     canned responses keyed on simple keyword matching

This keeps the app fully functional offline/without any API key, which
matters for a hackathon demo on venue wifi.
"""
import requests

from ai_engine.safety_rules import check_red_flags
from ai_engine.recommendations import generate_plan_for_tomorrow

SYSTEM_PROMPT = (
    "You are AarogyaAI, a supportive wellness assistant. You are NOT a "
    "doctor. Never diagnose a disease or name a condition. Give general, "
    "practical lifestyle suggestions about sleep, exercise, hydration, "
    "nutrition, and stress. For anything serious, persistent, or "
    "concerning, tell the user to consult a qualified healthcare "
    "professional. Keep responses short (3-5 sentences)."
)


def _call_llm(app_config, message, history):
    """Calls an OpenAI-compatible chat-completions endpoint. Raises on failure."""
    if not app_config.get("LLM_API_KEY"):
        raise RuntimeError("No LLM_API_KEY configured")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in history[-6:]:  # small rolling window for context
        role = "user" if turn["sender"] == "user" else "assistant"
        messages.append({"role": role, "content": turn["message"]})
    messages.append({"role": "user", "content": message})

    resp = requests.post(
        app_config["LLM_API_URL"],
        headers={"Authorization": f"Bearer {app_config['LLM_API_KEY']}"},
        json={"model": app_config["LLM_MODEL"], "messages": messages, "max_tokens": 300},
        timeout=8,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def _rule_based_reply(message, breakdown=None, wellness_goal=""):
    """Keyword-matched canned responses — the offline fallback."""
    text = message.lower()

    if "plan for tomorrow" in text or "plan tomorrow" in text:
        if breakdown:
            return generate_plan_for_tomorrow(breakdown, wellness_goal)
        return (
            "Log today's sleep, water, exercise, and stress first — "
            "then I can build a specific plan for tomorrow."
        )

    if any(w in text for w in ("sleep", "slept", "sleeping", "insomnia", "bedtime")):
        return (
            "It may help to maintain a consistent sleep schedule and wind "
            "down screens 30 minutes before bed. If tiredness continues or "
            "feels concerning, consider speaking with a healthcare "
            "professional."
        )

    if any(w in text for w in ("exercise", "exercised", "workout", "routine", "gym", "walk", "run")):
        return (
            "A simple beginner routine: a 15-20 minute walk most days, plus "
            "two short bodyweight sessions (squats, push-ups, planks) each "
            "week. Increase gradually rather than all at once."
        )

    if any(w in text for w in ("water", "hydration", "hydrate", "thirsty")):
        return (
            "Try spacing water intake across the day rather than drinking "
            "it all at once — a glass with each meal and one between meals "
            "is an easy pattern to start with."
        )

    if any(w in text for w in ("stress", "stressed", "anxious", "overwhelmed", "anxiety")):
        return (
            "A short breathing exercise (4 seconds in, 6 seconds out, for "
            "a couple of minutes) or a 5-minute break can help in the "
            "moment. Breaking tasks into smaller steps often reduces the "
            "feeling of being overwhelmed."
        )

    if any(w in text for w in ("headache", "tired", "tiredness", "fatigue", "pain", "symptom")):
        return (
            "That can have many everyday causes — sleep, hydration, stress, "
            "or screen time are common ones. Consider addressing those "
            "first. If it's severe, persistent, or concerning, please seek "
            "medical care."
        )

    if any(w in text for w in ("breakfast", "diet", "food", "eat", "meal", "nutrition")):
        return (
            "A balanced plate — some protein, whole grains, and a "
            "vegetable or fruit — is a good general target for any meal. "
            "Tell me your food preferences (vegetarian, budget, allergies) "
            "for more specific ideas."
        )

    return (
        "I can help with sleep, exercise, hydration, nutrition, and stress "
        "questions, or build you a simple plan for tomorrow. What would "
        "you like to focus on?"
    )


def handle_chat_message(message, history, app_config, breakdown=None, wellness_goal=""):
    """
    Main entry point used by the /api/chat route.

    Returns: {"reply": str, "is_red_flag": bool}
    """
    safety = check_red_flags(message)
    if safety["is_emergency"]:
        return {"reply": safety["message"], "is_red_flag": True}

    try:
        reply = _call_llm(app_config, message, history)
    except Exception:
        # No API key configured, no network, or the call failed —
        # fall back to the deterministic rule-based responder.
        reply = _rule_based_reply(message, breakdown, wellness_goal)

    return {"reply": reply, "is_red_flag": False}
