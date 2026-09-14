"""
recommendations.py

Priority-ordered, rule-based recommendations from a day's wellness-score
breakdown (see wellness_score.py). This mirrors the worked examples in the
project spec: low sleep/water/exercise + high stress -> sleep & stress
suggestions first; a well-rounded profile -> maintenance-style suggestions.

Deliberately simple `if` rules rather than ML, so behaviour is predictable
and explainable for a hackathon demo.
"""

RECOMMENDATION_LIBRARY = {
    "sleep": {
        "low": "Work on a consistent sleep routine — try going to bed at the same time tonight.",
        "ok": "Your sleep is reasonable — keep the same bedtime most nights to stay consistent.",
    },
    "exercise": {
        "low": "Add a short daily activity, even a 15-20 minute walk, to build momentum.",
        "ok": "Consider progressively increasing your activity — add 5-10 minutes this week.",
    },
    "hydration": {
        "low": "Increase water intake — try keeping a bottle at your desk and sipping through the day.",
        "ok": "Hydration looks good — keep pacing your water intake across the day.",
    },
    "nutrition": {
        "low": "Try adding more vegetables and whole grains to your next few meals.",
        "ok": "Your food pattern looks balanced — keep meals regular and varied.",
    },
    "stress": {
        "low": "Try a short breathing exercise or a 5-minute break between tasks today.",
        "ok": "Stress looks manageable — a short daily wind-down can help keep it that way.",
    },
}

LOW_THRESHOLD = 65  # breakdown score below this counts as "needs attention"


def generate_recommendations(breakdown, top_n=4):
    """
    breakdown: {"sleep": int, "exercise": int, "hydration": int,
                "nutrition": int, "stress": int}  (0-100 each)

    Returns an ordered list of recommendation strings, weakest area first.
    """
    ordered_dimensions = sorted(breakdown.items(), key=lambda kv: kv[1])

    recs = []
    for dimension, score in ordered_dimensions:
        bucket = "low" if score < LOW_THRESHOLD else "ok"
        recs.append(RECOMMENDATION_LIBRARY[dimension][bucket])

    return recs[:top_n]


def generate_plan_for_tomorrow(breakdown, wellness_goal=""):
    """
    A slightly richer, single-paragraph plan (used for the
    "give me a simple plan for tomorrow" chat request in the demo script).
    """
    weakest = min(breakdown, key=breakdown.get)
    strongest = max(breakdown, key=breakdown.get)

    plan_line = {
        "sleep": "Aim to be in bed 30 minutes earlier than usual and avoid screens right before sleeping.",
        "exercise": "Schedule a 20-minute walk or light workout at a fixed time tomorrow.",
        "hydration": "Set 3 reminders through the day to drink a glass of water.",
        "nutrition": "Plan one extra vegetable-forward meal tomorrow.",
        "stress": "Block 10 minutes tomorrow for a breathing exercise or a walk outside.",
    }.get(weakest, "Keep today's routine going tomorrow.")

    goal_line = f" This also supports your goal of '{wellness_goal}'." if wellness_goal else ""

    return (
        f"For tomorrow, focus on {weakest}: {plan_line}{goal_line} "
        f"Your {strongest} habits are already solid, so keep those unchanged."
    )
