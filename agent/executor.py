from tools.trend_research import research_trends
from tools.hashtag_tool import generate_hashtags
from tools.content_analyzer import analyze_content

TOOL_LABELS = {
    "trend_research": "Trend Idea Generator",
    "hashtag_tool": "Hashtag Generator",
    "content_analyzer": "Content Analyzer",
}


def execute_plan(plan, generated_content=None, platform="Instagram", tone="Engaging"):
    results = {}
    topic = plan["topic"]
    research_data = None

    for step in plan["steps"]:
        tool_name = step["tool"]
        print(f"[Tool Called]: {TOOL_LABELS.get(tool_name, tool_name)}")

        if tool_name == "trend_research":
            research_data = research_trends(topic, platform, tone)
            results["trend_research"] = research_data

        elif tool_name == "hashtag_tool":
            trends = research_data["trends"] if research_data else []
            results["hashtag_tool"] = generate_hashtags(
                topic=topic, trends=trends, platform=platform
            )

        elif tool_name == "content_analyzer":
            if not generated_content:
                raise ValueError("Generated content is required for analysis.")
            results["content_analyzer"] = analyze_content(
                content=generated_content, topic=topic, platform=platform
            )

        else:
            raise ValueError(f"Unknown tool requested: {tool_name}")

    return results