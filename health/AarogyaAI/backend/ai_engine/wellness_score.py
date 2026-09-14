"""
wellness_score.py

Turns one day's raw log values into:
  - a per-dimension score (0-100) for sleep, exercise, hydration, nutrition, stress
  - a single overall wellness score (weighted average)

This is a transparent, rule-based scoring function on purpose (not an ML
black box) so the AI's explanation in chat/dashboard can always be traced
back to a concrete number. Thresholds are simple defaults and are meant to
be tuned against real user data later.
"""

NUTRITION_RATING_SCORES = {
    "excellent": 95,
    "good": 82,
    "fair": 60,
    "poor": 35,
}

STRESS_LEVEL_SCORES = {
    "great": 95,
    "good": 82,
    "okay": 65,
    "stressed": 45,
    "very low": 30,
}


def _scale(value, target, cap_at_target=True):
    """Simple linear scale: value/target * 100, capped at 100."""
    if target <= 0:
        return 0
    score = (value / target) * 100
    return min(100, round(score)) if cap_at_target else round(score)


def score_sleep(sleep_hours, sleep_goal_hrs=8):
    if sleep_hours is None:
        return 0
    # Too little AND too much sleep both reduce the score slightly.
    if sleep_hours <= sleep_goal_hrs:
        return _scale(sleep_hours, sleep_goal_hrs)
    overshoot_penalty = min(20, (sleep_hours - sleep_goal_hrs) * 8)
    return max(0, round(100 - overshoot_penalty))


def score_exercise(exercise_minutes, daily_goal_minutes=30):
    if exercise_minutes is None:
        return 0
    return _scale(exercise_minutes, daily_goal_minutes)


def score_hydration(water_ml, water_goal_ml=2000):
    if water_ml is None:
        return 0
    return _scale(water_ml, water_goal_ml)


def score_nutrition(nutrition_rating):
    if not nutrition_rating:
        return 60  # neutral default when no meals logged yet
    return NUTRITION_RATING_SCORES.get(nutrition_rating.strip().lower(), 60)


def score_stress(stress_level):
    if not stress_level:
        return 60
    return STRESS_LEVEL_SCORES.get(stress_level.strip().lower(), 60)


# Relative importance of each dimension in the overall score.
WEIGHTS = {
    "sleep": 0.25,
    "exercise": 0.25,
    "hydration": 0.20,
    "nutrition": 0.15,
    "stress": 0.15,
}


def compute_wellness_score(daily_log, sleep_goal_hrs=8, water_goal_ml=2000):
    """
    daily_log: dict with keys sleep_hours, exercise_minutes, water_ml,
               nutrition_rating, stress_level (any may be None/missing).

    Returns: {"overall": int, "breakdown": {dimension: int, ...}}
    """
    breakdown = {
        "sleep": score_sleep(daily_log.get("sleep_hours"), sleep_goal_hrs),
        "exercise": score_exercise(daily_log.get("exercise_minutes")),
        "hydration": score_hydration(daily_log.get("water_ml"), water_goal_ml),
        "nutrition": score_nutrition(daily_log.get("nutrition_rating")),
        "stress": score_stress(daily_log.get("stress_level")),
    }
    overall = round(sum(breakdown[k] * WEIGHTS[k] for k in WEIGHTS))
    return {"overall": overall, "breakdown": breakdown}


def strongest_and_weakest(breakdown):
    """Return (strongest_dimension, weakest_dimension) for the AI insight text."""
    strongest = max(breakdown, key=breakdown.get)
    weakest = min(breakdown, key=breakdown.get)
    return strongest, weakest
