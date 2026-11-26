
from agent.generator import generate_content
from tools.trend_research import research_trends
from tools.hashtag_tool import generate_hashtags

try:

    topic = "Artificial Intelligence"

    # Research trends
    research = research_trends(topic)

    # Generate hashtags
    hashtag_result = generate_hashtags(
        topic,
        research["trends"]
    )

    # Generate final content using Gemma
    content = generate_content(
        topic=topic,
        platform="Instagram",
        tone="Professional",
        output_type="Social Media Post",
        trends=research["trends"],
        hashtags=hashtag_result["hashtags"]
    )

    print("\n========== GENERATED CONTENT ==========")
    print(content)

except Exception as error:

    print("\nGenerator Error:", error)
