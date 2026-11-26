
from tools.trend_research import research_trends
from tools.hashtag_tool import generate_hashtags

try:

    # First research the topic
    research = research_trends("Artificial Intelligence")

    # Generate hashtags using research results
    result = generate_hashtags(
        topic="Artificial Intelligence",
        trends=research["trends"]
    )

    print("\n========== HASHTAG RESULTS ==========")

    print("Topic:", result["topic"])
    print("Total Hashtags:", result["total_hashtags"])

    print("\nGenerated Hashtags:")

    for hashtag in result["hashtags"]:
        print(hashtag)

except Exception as error:
    print("Hashtag Error:", error)

