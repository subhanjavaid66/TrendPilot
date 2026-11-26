# The tool order and purposes are fixed; asking an LLM to describe them adds
# latency without changing which tools the executor runs.
DEFAULT_STEPS = [
    ("trend_research", "Generate content angles and pick the best one"),
    ("hashtag_tool", "Generate niche hashtags for the platform"),
    ("content_analyzer", "Score the draft with rule-based quality checks"),
]


def create_plan(topic, platform, tone, output_type):
    return {
        "topic": topic,
        "platform": platform,
        "tone": tone,
        "output_type": output_type,
        "steps": [
            {"tool": tool, "purpose": default}
            for tool, default in DEFAULT_STEPS
        ],
    }
