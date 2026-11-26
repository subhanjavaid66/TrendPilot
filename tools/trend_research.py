from datetime import datetime

from agent.ollama_client import generate_response
from tools.json_utils import extract_json


def _fallback_angles(topic):
    return [
        f"The biggest mistake beginners make with {topic}",
        f"What I wish I knew before starting {topic}",
        f"{topic}: myth vs reality",
        f"Behind the scenes of {topic}",
        f"3 lessons {topic} taught me",
    ]


def research_trends(topic, platform="Instagram", tone="Engaging"):
    """
    Trend Idea Generator: returns 5 specific content angles and picks the best one.
    """
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Topic cannot be empty.")

    topic = topic.strip()

    prompt = f"""
You are a viral content strategist.

Topic: {topic}
Platform: {platform}
Tone: {tone}

Generate 5 specific, creative content angles for this topic that would
perform well on {platform}. Each angle must be one short sentence and
must be different in style (story, myth-busting, lesson, behind-the-scenes,
question, etc.). Do not invent statistics, and do not invent specific names,
brands, models or personal details that are not in the topic. Describe each angle
as a concept for the post (for example: 'Before-and-after of a build, focusing on
the biggest surprise'), not as a finished caption. Every angle must clearly refer to the topic itself and must
not start with 'Legend says'.

Then choose the single best angle for engagement.

Return ONLY valid JSON in exactly this format:
{{"angles": ["angle 1", "angle 2", "angle 3", "angle 4", "angle 5"], "best": 1}}
"""

    angles, best = [], 0
    source = "Ollama (local LLM)"

    try:
        data = extract_json(generate_response(prompt, temperature=0.8))
        if isinstance(data, dict):
            angles = [
                a.strip() for a in data.get("angles", [])
                if isinstance(a, str) and a.strip()
            ][:5]
            best = int(data.get("best", 1)) - 1
    except Exception:
        angles = []

    if len(angles) < 3:
        angles = _fallback_angles(topic)
        source = "Fallback angle templates"

    if not 0 <= best < len(angles):
        best = 0

    return {
        "topic": topic,
        "platform": platform,
        "angles": angles,
        "best_angle": angles[best],
        "trends": angles,  # kept for compatibility with older code
        "total_trends": len(angles),
        "research_date": datetime.now().strftime("%Y-%m-%d"),
        "source": source,
    }