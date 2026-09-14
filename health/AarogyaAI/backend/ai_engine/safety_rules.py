"""
safety_rules.py

Deterministic, keyword-based safety layer. This runs BEFORE any LLM call so
that emergency escalation never depends on model behaviour. Keep this layer
simple, auditable, and easy for a reviewer/judge to read end-to-end.

Two independent checks:
  1. Medical red flags -> "seek urgent medical attention" message
  2. Crisis / self-harm indicators -> crisis-resource message

Both return short, non-diagnostic, action-oriented text.
"""

# Phrases that should always trigger an urgent-care recommendation.
# Keep this list conservative (favor false positives over false negatives).
MEDICAL_RED_FLAGS = [
    "chest pain", "can't breathe", "cannot breathe", "difficulty breathing",
    "shortness of breath", "severe bleeding", "coughing blood", "blood in vomit",
    "blood in stool", "sudden numbness", "slurred speech", "face drooping",
    "loss of consciousness", "fainted", "seizure", "severe allergic reaction",
    "swelling of throat", "high fever with stiff neck", "suicidal", "overdose",
    "poisoning", "severe burn", "uncontrolled bleeding", "sudden vision loss",
]

CRISIS_INDICATORS = [
    "want to die", "kill myself", "end my life", "suicidal", "self harm",
    "self-harm", "hurt myself", "no reason to live", "can't go on",
]

MEDICAL_MESSAGE = (
    "🚨 What you're describing could be a medical emergency. Please seek "
    "urgent medical attention now — contact your local emergency number or "
    "go to the nearest emergency room. This app cannot assess emergencies."
)

CRISIS_MESSAGE = (
    "🚨 It sounds like you might be going through something very difficult. "
    "Please reach out right now to a crisis helpline or emergency services in "
    "your area, or talk to someone you trust. You deserve immediate support "
    "from a real person, not just an app."
)


def _matches_any(text, phrases):
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def check_red_flags(text):
    """
    Inspect free-text user input (symptom description or chat message).

    Returns a dict:
        {
          "is_emergency": bool,
          "category": "medical" | "crisis" | None,
          "message": str | None
        }
    Callers should short-circuit on is_emergency=True and skip any
    LLM-generated response for that turn.
    """
    if not text:
        return {"is_emergency": False, "category": None, "message": None}

    if _matches_any(text, CRISIS_INDICATORS):
        return {"is_emergency": True, "category": "crisis", "message": CRISIS_MESSAGE}

    if _matches_any(text, MEDICAL_RED_FLAGS):
        return {"is_emergency": True, "category": "medical", "message": MEDICAL_MESSAGE}

    return {"is_emergency": False, "category": None, "message": None}
